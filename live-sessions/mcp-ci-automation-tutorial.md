# MCP + CI/CD & Programmatic Automation Tutorial

> How to invoke MCP servers from Jenkins pipelines and automate MCP tool calls without an LLM in the loop.

---

## Table of Contents

1. [Overview](#overview)
2. [Part 1: Invoking MCP Servers from Jenkins](#part-1-invoking-mcp-servers-from-jenkins)
   - [Approach A: Jenkins MCP Server Plugin](#approach-a-jenkins-mcp-server-plugin-jenkins-as-mcp-server)
   - [Approach B: Jenkinsfile Cloning & Running Your MCP Server](#approach-b-jenkinsfile-cloning--running-your-mcp-server)
   - [Approach C: External MCP Wrappers for Jenkins](#approach-c-external-mcp-wrappers-for-jenkins)
3. [Part 2: Programmatic MCP Tool Invocation (No LLM Required)](#part-2-programmatic-mcp-tool-invocation-no-llm-required)
   - [Core Client API](#core-client-api---clientsession)
   - [Transport 1: stdio (Subprocess)](#transport-1-stdio-subprocess)
   - [Transport 2: Streamable HTTP (Remote)](#transport-2-streamable-http-remote)
   - [Parsing Tool Results](#parsing-tool-results)
   - [Long-Lived Connections with AsyncExitStack](#long-lived-connections-with-asyncexitstack)
   - [Standalone CI Automation Script](#standalone-ci-automation-script)
4. [Bonus: GitHub Actions + MCP](#bonus-github-actions--mcp)
5. [Architecture Decision Matrix](#architecture-decision-matrix)
6. [References](#references)

---

## Overview

The MCP Python SDK has a fully functional **client API** that works entirely **without any LLM**. You connect to an MCP server, list tools, call them, and process results — all programmatically. This makes MCP a natural fit for CI/CD pipelines, automation scripts, and scheduled jobs.

There are **three architectural layers** for Jenkins + MCP integration:

| Layer | Description |
|---|---|
| **Jenkins as MCP Server** | Official plugin turns Jenkins into an MCP server that AI clients can query |
| **MCP Server inside Jenkinsfile** | Pipeline clones your MCP server repo and drives it via Python SDK |
| **External MCP wrappers** | Standalone Python/Node packages that wrap the Jenkins REST API as MCP tools |

---

## Part 1: Invoking MCP Servers from Jenkins

### Approach A: Jenkins MCP Server Plugin (Jenkins AS MCP Server)

The [official Jenkins MCP plugin](https://plugins.jenkins.io/mcp-server) (`jenkinsci/mcp-server-plugin`) turns your running Jenkins instance into an MCP server. AI clients (Claude Desktop, Cursor, VS Code Copilot) connect to Jenkins and control it via MCP tools.

**Install**: Jenkins Update Center → search "MCP Server" → Install

**Requires**: Jenkins 2.533+

**Exposed Tools**:
```
getJob, getJobs, triggerBuild, getQueueItem
getBuild, updateBuild, getBuildLog, searchBuildLog
getJobScm, getBuildScm, getBuildChangeSets, findJobsWithScmUrl
whoAmI, getStatus
```

**Transport Endpoints** (all enabled by default):

| Transport | Endpoint | Best For |
|---|---|---|
| SSE | `/mcp-server/sse` | Streaming (Copilot) |
| Streamable HTTP | `/mcp-server/mcp` | Production |
| Stateless | `/mcp-server/stateless` | Lightweight requests |

**Claude Desktop Configuration**:
```json
{
  "mcpServers": {
    "jenkins": {
      "url": "http://jenkins.example.com:8080/mcp-server/mcp",
      "headers": {
        "Authorization": "Basic <base64(username:api-token)>"
      }
    }
  }
}
```

> **Key distinction**: This makes Jenkins a *server* that AI clients talk *to*. It does NOT help Jenkins pipelines call *out* to external MCP servers. For that, see Approach B.

---

### Approach B: Jenkinsfile Cloning & Running Your MCP Server

This is the most common scenario: **your MCP server is hosted on GitHub, and you want a Jenkins pipeline to clone it, spin it up, and invoke its tools.**

The pattern uses the MCP Python SDK's `stdio_client` to launch your server as a subprocess and call tools directly.

#### Step 1: Create a Reusable Invocation Script

Save this as `invoke_mcp_tool.py` in your MCP server repo:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["mcp>=1.0.0"]
# ///
"""
CI helper: invoke a single MCP tool and print the result.
Usage: uv run invoke_mcp_tool.py <server_script> <tool_name> '<json_args>'
"""

import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run_mcp_tool(server_script: str, tool_name: str, arguments: dict):
    server_params = StdioServerParameters(
        command="uv",
        args=["run", server_script],
        env=None,  # inherits environment (Jenkins credentials, etc.)
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List tools for debugging
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}", file=sys.stderr)

            # Call the target tool
            result = await session.call_tool(tool_name, arguments=arguments)

            if result.is_error:
                print(f"ERROR: Tool returned an error", file=sys.stderr)
                for content in result.content:
                    print(content.text, file=sys.stderr)
                sys.exit(1)

            # Print result to stdout
            for content in result.content:
                if hasattr(content, "text"):
                    print(content.text)

            return result


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: uv run invoke_mcp_tool.py <server.py> <tool_name> ['{\"arg\": \"val\"}']")
        sys.exit(1)

    server_script = sys.argv[1]
    tool_name = sys.argv[2]
    args_json = sys.argv[3] if len(sys.argv) > 3 else "{}"

    asyncio.run(run_mcp_tool(server_script, tool_name, json.loads(args_json)))
```

#### Step 2: Jenkinsfile

```groovy
pipeline {
    agent any

    environment {
        // Inject secrets via Jenkins credentials
        OPENAI_API_KEY   = credentials('openai-api-key')
        DATABASE_URL     = credentials('database-url')
    }

    stages {

        stage('Checkout MCP Server') {
            steps {
                git url: 'https://github.com/your-org/your-mcp-server.git',
                    branch: 'main',
                    credentialsId: 'github-credentials'
            }
        }

        stage('Install uv') {
            steps {
                sh '''
                    curl -LsSf https://astral.sh/uv/install.sh | sh
                    export PATH="$HOME/.cargo/bin:$PATH"
                    uv --version
                '''
            }
        }

        stage('List Available MCP Tools') {
            steps {
                sh '''
                    export PATH="$HOME/.cargo/bin:$PATH"
                    uv run invoke_mcp_tool.py \
                        ./mcp_server.py \
                        __list_tools__ \
                        '{}' || true
                '''
            }
        }

        stage('Run MCP Tool - Query Data') {
            steps {
                sh '''
                    export PATH="$HOME/.cargo/bin:$PATH"
                    uv run invoke_mcp_tool.py \
                        ./mcp_server.py \
                        query_sales_data \
                        '{"category": "Electronics", "limit": 10}' \
                        > query_results.json
                    cat query_results.json
                '''
            }
        }

        stage('Run MCP Tool - Generate Report') {
            steps {
                sh '''
                    export PATH="$HOME/.cargo/bin:$PATH"
                    uv run invoke_mcp_tool.py \
                        ./mcp_server.py \
                        generate_report \
                        '{"format": "pdf", "date_range": "last_30_days"}' \
                        > report_output.txt
                '''
            }
        }

        stage('Archive Results') {
            steps {
                archiveArtifacts artifacts: '*.json,*.txt', fingerprint: true
            }
        }
    }

    post {
        failure {
            echo 'Pipeline failed — check MCP tool output above for details'
        }
    }
}
```

#### How It Works

```
┌──────────────────────────────────────────────┐
│              Jenkins Agent                   │
│                                              │
│  1. git clone your-mcp-server.git            │
│  2. uv run invoke_mcp_tool.py                │
│       │                                      │
│       ├──► spawns mcp_server.py (subprocess)  │
│       │         stdin/stdout (stdio transport)│
│       │                                      │
│       ├──► session.initialize()              │
│       ├──► session.call_tool("query_data")   │
│       ├──► parse result                      │
│       └──► subprocess exits                  │
│                                              │
│  3. Archive artifacts                        │
└──────────────────────────────────────────────┘
```

---

### Approach C: External MCP Wrappers for Jenkins

Pre-built packages that wrap the Jenkins REST API as MCP tools:

#### `mcp-jenkins` (Python, recommended)

```bash
# Install and run
pip install mcp-jenkins
# or
uvx mcp-jenkins

# Configure
mcp-jenkins \
  --jenkins-url http://jenkins.example.com:8080 \
  --jenkins-username admin \
  --jenkins-password <api-token> \
  --transport stdio
```

**Tools**: `get_item`, `build_item`, `get_build`, `get_build_console_output`, `get_running_builds`, `stop_build`, and 14 more.

**Raw JSON-RPC invocation** (useful in shell scripts):
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_build","arguments":{"job":"my-job","build":42}}}' \
  | JENKINS_URL=http://jenkins:8080 \
    JENKINS_USERNAME=admin \
    JENKINS_PASSWORD=token \
    uvx mcp-jenkins
```

#### `@kud/mcp-jenkins` (TypeScript)
```bash
npx --yes @kud/mcp-jenkins@latest \
  --jenkins-url http://jenkins:8080 \
  --jenkins-username admin \
  --jenkins-token <api-token>
```

---

## Part 2: Programmatic MCP Tool Invocation (No LLM Required)

This is the answer to: **"How do I call MCP tools from pure Python code as automation?"**

### Core Client API - `ClientSession`

The MCP Python SDK provides `ClientSession` as the main interface. No API keys, no LLM — just direct tool calls.

| Method | What it does |
|---|---|
| `await session.initialize()` | MCP handshake (must be first call) |
| `await session.list_tools()` | Returns all available tools |
| `await session.call_tool(name, arguments)` | Invokes a tool and returns result |
| `await session.list_resources()` | Returns available resources |
| `await session.read_resource(uri)` | Reads a specific resource |
| `await session.list_prompts()` | Returns available prompts |
| `await session.get_prompt(name, args)` | Gets a specific prompt |

---

### Transport 1: stdio (Subprocess)

The client launches the MCP server as a subprocess. Best for local automation and CI/CD.

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["mcp>=1.0.0"]
# ///

import asyncio
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="uv",
    args=["run", "path/to/my_mcp_server.py"],
    env=None,  # inherits current environment
)


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 1. Mandatory handshake
            await session.initialize()

            # 2. Discover tools
            tools = await session.list_tools()
            print(f"Tools: {[t.name for t in tools.tools]}")

            # 3. Call a tool directly — NO LLM needed
            result = await session.call_tool("add", arguments={"a": 5, "b": 3})

            # 4. Parse the result
            for content in result.content:
                if isinstance(content, types.TextContent):
                    print(f"Result: {content.text}")


asyncio.run(main())
```

**Key `StdioServerParameters` fields:**
- `command` — executable (`python`, `node`, `uv`, etc.)
- `args` — arguments passed to the command
- `env` — `dict | None`; `None` inherits the current process environment

---

### Transport 2: Streamable HTTP (Remote)

For MCP servers deployed as web services (e.g., on Vercel, Docker, or a remote VM).

```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def main():
    async with streamable_http_client("http://localhost:8000/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print(f"Tools: {[t.name for t in tools.tools]}")

            result = await session.call_tool("my_tool", arguments={"key": "value"})
            for content in result.content:
                print(content.text)


asyncio.run(main())
```

> **Note**: `streamable_http_client` yields a 3-tuple `(read, write, _)`. The third element is session metadata — discard with `_`.

---

### Parsing Tool Results

`call_tool()` returns a `CallToolResult`. The `.content` list can hold multiple typed blocks:

```python
from mcp import types

result = await session.call_tool("my_tool", arguments={"input": "hello"})

# --- Plain text ---
for content in result.content:
    if isinstance(content, types.TextContent):
        print(content.text)

# --- Structured JSON (if server defines outputSchema) ---
if result.structured_content:
    data = result.structured_content  # plain dict
    print(data.get("field_name"))

# --- Embedded resource ---
for content in result.content:
    if isinstance(content, types.EmbeddedResource):
        resource = content.resource
        if isinstance(resource, types.TextResourceContents):
            print(f"{resource.uri}: {resource.text}")

# --- Image data ---
for content in result.content:
    if isinstance(content, types.ImageContent):
        print(f"Image ({content.mime_type}): {len(content.data)} bytes")

# --- Error handling ---
if result.is_error:
    for content in result.content:
        if isinstance(content, types.TextContent):
            print(f"Error: {content.text}")
```

---

### Long-Lived Connections with AsyncExitStack

For scripts that call many tools sequentially, use `AsyncExitStack` to keep the connection open:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["mcp>=1.0.0"]
# ///

import asyncio
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPAutomation:
    def __init__(self):
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()

    async def connect(self, server_script: str):
        params = StdioServerParameters(command="uv", args=["run", server_script])
        read, write = await self.exit_stack.enter_async_context(stdio_client(params))
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        await self.session.initialize()

        tools = await self.session.list_tools()
        print(f"Connected. Tools: {[t.name for t in tools.tools]}")

    async def call(self, tool_name: str, **kwargs) -> str:
        result = await self.session.call_tool(tool_name, arguments=kwargs)
        if result.is_error:
            raise RuntimeError(f"Tool '{tool_name}' failed")
        return result.content[0].text if result.content else ""

    async def disconnect(self):
        await self.exit_stack.aclose()


async def main():
    bot = MCPAutomation()
    await bot.connect("my_mcp_server.py")

    # Call multiple tools on the same connection
    data = await bot.call("query_sample_data_from_csv", csv_path="sales.csv")
    summary = await bot.call("get_sales_summary", csv_path="sales.csv")
    top = await bot.call("top_products_by_category", csv_path="sales.csv", category="Electronics")

    print(data)
    print(summary)
    print(top)

    await bot.disconnect()


asyncio.run(main())
```

---

### Standalone CI Automation Script

A complete, self-contained script you can run with `uv run` in any CI pipeline — no virtualenv setup needed:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["mcp>=1.0.0"]
# ///
"""
CI smoke test: verify MCP server tools work and return expected results.
Run with: uv run ci_smoke_test.py ./mcp_server.py
"""

import asyncio
import sys
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client


async def smoke_test(server_script: str):
    params = StdioServerParameters(command="uv", args=["run", server_script])

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Test 1: Tools are discoverable
            tools = await session.list_tools()
            tool_names = [t.name for t in tools.tools]
            print(f"[PASS] Found {len(tool_names)} tools: {tool_names}")
            assert len(tool_names) > 0, "No tools found!"

            # Test 2: Each tool can be called without crashing
            for tool in tools.tools:
                print(f"  Testing tool: {tool.name}...", end=" ")
                try:
                    # Build minimal arguments from schema
                    args = {}
                    if tool.inputSchema and "required" in tool.inputSchema:
                        for param in tool.inputSchema["required"]:
                            prop = tool.inputSchema.get("properties", {}).get(param, {})
                            param_type = prop.get("type", "string")
                            if param_type == "string":
                                args[param] = "test"
                            elif param_type in ("integer", "number"):
                                args[param] = 1

                    result = await session.call_tool(tool.name, arguments=args)
                    status = "ERROR" if result.is_error else "OK"
                    print(f"[{status}]")
                except Exception as e:
                    print(f"[EXCEPTION] {e}")

            print("\n[DONE] Smoke test complete.")


if __name__ == "__main__":
    server = sys.argv[1] if len(sys.argv) > 1 else "mcp_server.py"
    asyncio.run(smoke_test(server))
```

---

## Bonus: GitHub Actions + MCP

### Run MCP Tools in a GitHub Actions Workflow

```yaml
name: MCP Automation
on: [push]

jobs:
  mcp-ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Run MCP tool - Query data
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: |
          uv run invoke_mcp_tool.py \
            ./mcp_server.py \
            query_sales_data \
            '{"category": "Electronics"}'

      - name: Run MCP tool - Generate report
        run: |
          uv run invoke_mcp_tool.py \
            ./mcp_server.py \
            generate_report \
            '{"format": "json"}' > report.json

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: mcp-report
          path: report.json
```

### Docker Sidecar Pattern (HTTP Transport)

```yaml
jobs:
  mcp-sidecar:
    runs-on: ubuntu-latest
    services:
      mcp-server:
        image: your-org/your-mcp-server:latest
        ports:
          - 8000:8000

    steps:
      - uses: actions/checkout@v4

      - name: Call MCP server via HTTP
        run: |
          curl -X POST http://localhost:8000/mcp \
            -H "Content-Type: application/json" \
            -d '{
              "jsonrpc": "2.0",
              "id": 1,
              "method": "tools/call",
              "params": {
                "name": "get_sales_summary",
                "arguments": {"csv_path": "data/sales.csv"}
              }
            }'
```

---

## Architecture Decision Matrix

| Approach | Best For | Pros | Cons |
|---|---|---|---|
| **Jenkins MCP Plugin** | AI IDEs querying Jenkins | Official, no custom code | Jenkins serves AI, not the reverse |
| **stdio_client in Jenkinsfile** | Pipeline invoking your MCP tools | Full control, no infra needed | Requires Python/uv on agent |
| **Streamable HTTP** | Shared/deployed MCP servers | Multi-client, persistent | Network setup, Docker |
| **External wrappers (mcp-jenkins)** | Querying Jenkins from Claude | Pre-built, installable | REST API only |
| **GitHub Actions + MCP** | GitHub-native teams | Native CI, simple YAML | GitHub-specific |

### Transport Decision Guide

| Scenario | Transport | Import |
|---|---|---|
| Local server, CI/CD, automation | `stdio` | `from mcp.client.stdio import stdio_client` |
| Remote/deployed server | `streamable_http` | `from mcp.client.streamable_http import streamable_http_client` |
| Legacy server (pre-2025) | `sse` (deprecated) | `from mcp.client.sse import sse_client` |

---

## References

- [MCP Python SDK — GitHub](https://github.com/modelcontextprotocol/python-sdk)
- [Build an MCP Client — Official Docs](https://modelcontextprotocol.io/docs/develop/build-client)
- [MCP Transports Specification (2025-03-26)](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports)
- [Jenkins MCP Server Plugin](https://plugins.jenkins.io/mcp-server)
- [lanbaoshen/mcp-jenkins (Python)](https://github.com/lanbaoshen/mcp-jenkins)
- [kud/mcp-jenkins (TypeScript)](https://github.com/kud/mcp-jenkins)
- [github/github-mcp-server](https://github.com/github/github-mcp-server)
- [Building AI CI/CD Pipelines with MCP — Glama](https://glama.ai/blog/2025-08-16-building-ai-cicd-pipelines-with-mcp)
- [Build a Python MCP Client — Real Python](https://realpython.com/python-mcp-client/)
- [MCP Python SDK — PyPI](https://pypi.org/project/mcp/)
