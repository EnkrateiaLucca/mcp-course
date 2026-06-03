# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is an O'Reilly Live Training course repository: **"Building AI Agents with MCP: The HTTP Moment of AI?"** It contains hands-on demos and examples for learning the Model Context Protocol (MCP) and AI agent development.

The first four demos (`00` → `02`, then `04`) build a **single coherent use case** — a personal research assistant with web search + filesystem — and grow it one layer at a time: hand-rolled agent loop → MCP server → Claude Agent SDK → production-shaped (HTTP, auth, hooks, evals).

## Development Setup

### Package Manager
- **Primary method**: UV package manager (recommended)
- Every script includes inline UV metadata headers with dependencies
- Run scripts directly with: `uv run <script_name>.py`
- No virtualenv management needed when using UV

### Traditional Setup (Alternative)
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements/requirements.txt
```

### Environment Variables
Create `.env` at the repo root:
- `ANTHROPIC_API_KEY` — Claude agent demos
- `REPLICATE_API_TOKEN` — optional, image-generation extras
- `MCP_AUTH_TOKEN` — demo 04 (bearer auth on HTTP transport)

## Common Commands

### Running Demos
```bash
# UV handles dependencies automatically
uv run demos/01-introduction-to-mcp/mcp_server.py
uv run demos/03-query-tabular-data/claude_agents_sdk_demo.py

# Inspect any MCP server interactively
mcp dev <path-to-mcp-server.py>
```

### Makefile Commands
```bash
make conda-create     # create conda env
make env-setup        # pip-tools + UV
make notebook-setup   # install Jupyter kernel
make env-update       # rebuild requirements from requirements.in
make freeze           # freeze current deps
make clean            # remove conda env
```

## Project Architecture

### Demo Organization

Demos are organized sequentially by learning progression:

1. **`00-intro-agents/`** — Hand-rolled agent loop, tools as plain Python functions (~70 LOC). `web_search` (DuckDuckGo) + sandboxed filesystem tools.
2. **`01-introduction-to-mcp/`** — Same tools, now behind a FastMCP server. Agent loop becomes a thin host. Files: `mcp_server.py`, `mcp_client.py`, `mcp_host.py`.
3. **`02-research-agent-sdk/`** — Agent loop replaced by the **Claude Agent SDK**, same MCP server. Collapses to ~15 LOC.
4. **`03-query-tabular-data/`** — Branch into real use case: CSV/tabular queries via in-process MCP server + Agent SDK.
5. **`04-production-research-agent/`** — Production shape: HTTP transport (`streamable-http`), bearer auth, `PreToolUse`/`PostToolUse` hooks, `ExecutionTracker` evals, intent-grouped tools (7 → 3).
6. **`05-link-checker-agent/`** — Automations example: agent audits markdown files for broken links via a dedicated MCP server (`list_markdown_files`, `extract_links`, `check_url`, `write_report`).
7. **`06-deploy-simple-agent-mcp-vercel/`** — Data analysis agent deployed to **Vercel serverless** (FastAPI + SSE streaming, in-process MCP server, pandas-backed tools, base64 PNG plots).
8. **`07-hacks-tips-tools-workflows/`** — Curated tips, ecosystem tools, and the **`mcp-builder-skill/`** Claude skill for scaffolding MCP servers.

**`demos/archive/`** — older versions kept for reference (e.g. `02-study-case-anthropic-tools-resources-prompts-chat-app/`). Not part of the current course flow.

**`demos/assets-resources/`** — `MCP_TECHNICAL_CHEATSHEET.md`, `mcp_server_prompt_templates.md`, `mcp_security_report.pdf`, `diagram.excalidraw`, architecture PNGs.

### MCP Server Patterns

**FastMCP** (external stdio/HTTP servers — demos 01, 04, 05):
```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp[cli]>=1.0.0"]
# ///

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("server-name")

@mcp.tool()
def tool_function(param: type) -> return_type:
    """Tool description for LLM"""
    return result

@mcp.resource("uri://resource-path")
def get_resource() -> str:
    """Resource description"""
    return data

if __name__ == "__main__":
    mcp.run(transport="stdio")         # or "streamable-http" for production
```

**In-process MCP server via the Agent SDK** (demos 03, 06):
```python
from claude_agent_sdk import create_sdk_mcp_server, tool

@tool
async def query_data(args): ...

server = create_sdk_mcp_server(name="data-tools", tools=[query_data])
options = ClaudeAgentOptions(mcp_servers={"data": server})
```
Tools run in the same Python process — fastest, single deployment artifact, ideal for serverless.

### Agent Integration Patterns

**Claude Agent SDK** (demos 02, 03, 04, 05, 06):
- The SDK *is* an MCP host — point it at any MCP server config
- `allowed_tools=["mcp__<server_name>__*"]` for tool gating
- Tool permissions + `PreToolUse`/`PostToolUse` hooks for security and logging
- Streaming response handling via `async for message in query(...)`

**Pattern: Agent SDK consuming an external MCP server** (demo 02):
```python
options = ClaudeAgentOptions(
    system_prompt=SYSTEM_PROMPT,
    mcp_servers={"research": {"command": "uv", "args": ["run", "mcp_server.py"]}},
    allowed_tools=["mcp__research__*"],
)
async for message in query(prompt=user_prompt, options=options):
    ...
```

**Pattern: Remote HTTP MCP server with auth** (demo 04):
```python
# server side
mcp.run(transport="streamable-http")

# agent side
options = ClaudeAgentOptions(mcp_servers={
    "research": {
        "type": "http",
        "url": "http://localhost:8765/mcp",
        "headers": {"Authorization": f"Bearer {token}"},
    }
})
```

### Deployment Architecture (demo 06)

```
User → HTML/JS (SSE client)
         ↓ POST /chat
       FastAPI
         ↓
       Claude Agent SDK
         ↓
       In-process MCP server ("analysis")  →  pandas DataFrame
         ↓
       Text  → SSE text events  → rendered as markdown
       Plots → base64 PNG       → SSE image events → <img>
```

**Tools**: `describe_data`, `show_head`, `column_info`, `group_aggregate`, `correlation_matrix`, `plot_data`.

**Transport modes**:
- `stdio` — local development, subprocess communication
- `streamable-http` — production / remote MCP
- FastAPI + SSE — HTTP wrapper around an in-process SDK setup (demo 06)

## Development Guidelines

### When Creating MCP Servers
- Always use UV inline script metadata for dependencies
- Write descriptive tool/resource docstrings (the LLM sees them)
- Use Python type hints — schemas are auto-generated
- Test with MCP Inspector: `mcp dev <server_path>`
- Prefer **intent-grouped tools** (a few high-level tools that compose primitives) over many low-level tools — see demo 04

### When Creating Agents
- Validate file paths to prevent directory traversal
- Implement permission callbacks for security-sensitive operations
- Use streaming for long-running operations
- Log tool usage via `PostToolUse` hooks for debugging and auditing
- Block dangerous operations with `PreToolUse` hooks

### Security Considerations
- Never commit API keys (`.env` is in `.gitignore`)
- Validate all user inputs in tools
- Least-privilege principle for `allowed_tools`
- For HTTP transport, put auth on the wire (bearer token minimum)

## Key Files and Directories

- `requirements/requirements.txt` — pinned deps (generated from `requirements.in`)
- `requirements/requirements.in` — source requirements
- `Makefile` — environment automation
- `presentation/` — slides (`presentation.html`, `presentation-mcp-updated.key`, PNG assets)
- `demos/07-hacks-tips-tools-workflows/mcp-builder-skill/` — Claude skill for scaffolding MCP servers
- `demos/04-production-research-agent/presenter_notes.md` — 10-min live-demo script
- `demos/assets-resources/MCP_TECHNICAL_CHEATSHEET.md` — quick reference
- `.env` — API keys (not committed; create manually)

## Testing MCP Servers

### MCP Inspector (recommended)
```bash
mcp dev <path-to-server.py>
# Web UI at http://localhost:5173 — list tools, call them, view resources/prompts
```

### Claude Desktop
1. Edit config:
   - macOS/Linux: `~/.config/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
2. Add server entry:
   ```json
   {
     "mcpServers": {
       "server-name": {
         "command": "uv",
         "args": ["run", "/absolute/path/to/server.py"]
       }
     }
   }
   ```
3. Restart Claude Desktop.

## Common Patterns

### Error Handling in Tools
```python
@mcp.tool()
def safe_operation(path: str) -> str:
    try:
        if not is_safe_path(path):
            raise ValueError("Invalid path")
        return do_work(path)
    except Exception as e:
        return f"Error: {str(e)}"
```

### Resource with Dynamic Content
```python
@mcp.resource("data://{key}")
def get_data(key: str) -> str:
    """Dynamic resource based on URI parameter"""
    return load_data(key)
```

## Troubleshooting

### `mcp` module not found
```bash
uv pip install mcp model-context-protocol
# or: pip install mcp model-context-protocol
```

### Claude Desktop not recognizing servers
- Use absolute paths in config
- Verify `uv` is in PATH (`which uv`)
- Confirm the server runs standalone (`uv run mcp_server.py`)
- Check Claude Desktop logs; restart after config changes

### Demo 04 HTTP server issues
- `MCP_AUTH_TOKEN` must be set in **both** server and agent terminals
- Confirm nothing else is bound to port 8765

### API rate limiting
- Check API quotas
- Implement exponential backoff
- Swap to `claude-haiku` for iteration

## Additional Resources

- [MCP Specification](https://modelcontextprotocol.io/specification/)
- [MCP Python SDK (FastMCP)](https://github.com/modelcontextprotocol/python-sdk)
- [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview)
- [Building agents that reach production systems with MCP](https://claude.com/blog/building-agents-that-reach-production-systems-with-mcp) — basis for demo 04
- [Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
