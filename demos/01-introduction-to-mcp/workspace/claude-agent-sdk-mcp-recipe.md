# Claude Agent SDK + MCP Setup Recipe

> **Research brief** — Sources: github.com/anthropics/claude-agent-sdk-python, code.claude.com/docs, github.com/modelcontextprotocol/python-sdk, pypi.org/project/claude-agent-sdk, deepwiki.com/anthropics/claude-agent-sdk-python

---

## What These Are

- **Claude Agent SDK** (`claude-agent-sdk`) — Anthropic's Python library that wraps Claude Code CLI into a programmable agent loop. Handles tool use, subagent orchestration, permission hooks, and session management. Requires Python 3.10+.
- **MCP (Model Context Protocol)** — Open standard (JSON-RPC based) that lets agents talk to external tool servers (local processes, SSE endpoints, HTTP endpoints) in a uniform way. Claude Agent SDK treats MCP servers as the primary tool delivery mechanism.

---

## Three MCP Server Flavors (pick one or mix)

| Type | When to use | Config key |
|---|---|---|
| **Stdio** | Local subprocess (Python/Node script) | `McpStdioServerConfig` |
| **SSE** | Remote server over HTTP event stream | `McpSSEServerConfig` |
| **SDK (in-process)** | Custom tools defined in same Python process, no subprocess | `McpSdkServerConfig` via `create_sdk_mcp_server` |

---

## Mini Recipe: Build a Claude Agent with MCP Tools

### 1. Install Dependencies
```bash
pip install claude-agent-sdk          # bundles Claude Code CLI automatically
pip install mcp                       # MCP Python SDK (for building your own server)
```

### 2. Write an External MCP Tool Server (stdio)
```python
# my_tools_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MyTools")

@mcp.tool()
def get_weather(city: str) -> str:
    """Return current weather for a city."""
    return f"Weather in {city}: 72°F, sunny"   # stub — swap real API

@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

if __name__ == "__main__":
    mcp.run()   # starts stdio transport by default
```

### 3. Wire the Agent to That MCP Server
```python
# agent.py
import asyncio
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient

options = ClaudeAgentOptions(
    model="claude-opus-4-5",          # or claude-sonnet-4-5
    mcp_servers={
        "my_tools": {                  # arbitrary name — becomes the server label
            "type": "stdio",
            "command": "python",
            "args": ["my_tools_server.py"],
        }
    },
    system_prompt="You are a helpful assistant with access to weather and math tools.",
    max_turns=10,
)

async def main():
    client = ClaudeSDKClient(options)
    async for event in client.run("What's the weather in Tokyo and what is 42 + 58?"):
        if event.type == "assistant":
            print(event.content)

asyncio.run(main())
```

### 4. (Optional) Add In-Process SDK Tools (no subprocess needed)
```python
# agent_with_sdk_tools.py
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions, ClaudeSDKClient
import asyncio

@tool
def reverse_string(text: str) -> str:
    """Reverse any string."""
    return text[::-1]

sdk_server = create_sdk_mcp_server([reverse_string])

options = ClaudeAgentOptions(
    mcp_servers={
        "internal": sdk_server,            # in-process — zero latency
        "my_tools": {                      # external subprocess alongside it
            "type": "stdio",
            "command": "python",
            "args": ["my_tools_server.py"],
        },
    },
)

async def main():
    client = ClaudeSDKClient(options)
    async for event in client.run("Reverse 'hello world', then add 10 + 5"):
        if event.type == "assistant":
            print(event.content)

asyncio.run(main())
```

### 5. (Optional) Connect to a Remote SSE MCP Server
```python
mcp_servers={
    "remote_tools": {
        "type": "sse",
        "url": "https://my-mcp-server.example.com/sse",
        "headers": {"Authorization": "Bearer <TOKEN>"},
    }
}
```

---

## Key Gotchas & Tips

- **`ANTHROPIC_API_KEY`** env var must be set — Claude Code CLI picks it up automatically.
- **Tool docstrings matter** — FastMCP and the `@tool` decorator use them verbatim as the tool description sent to the model. Write them clearly; the model decides when to call tools based on them.
- **`alwaysLoad: true`** — Set this on an MCP server config if it must be available from the very first agent turn (default: lazy-loaded after turn 1).
- **`MCP_CONNECTION_NONBLOCKING=0`** — Env var that makes the SDK wait up to 5 s for server startup before the first query (useful for slow subprocess starts).
- **`max_turns`** — Always cap it. Agents can loop indefinitely without this. A safe default is 10–20 for most tasks.
- **Permissions/hooks** — Use `permission_prompt_tool_name` or pre-approve tool patterns via `ClaudeAgentOptions` hooks to avoid interactive prompts blocking automation.
- **Mix server types freely** — You can pass both `"internal"` (SDK) and `"external"` (stdio/SSE) keys in the same `mcp_servers` dict.

---

## Minimal File Layout

```
my_agent/
├── my_tools_server.py   # FastMCP tool server (stdio)
├── agent.py             # ClaudeSDKClient runner
├── .env                 # ANTHROPIC_API_KEY=sk-...
└── requirements.txt     # claude-agent-sdk, mcp
```

---

## Sources

| Resource | URL |
|---|---|
| Claude Agent SDK (PyPI) | https://pypi.org/project/claude-agent-sdk/ |
| claude-agent-sdk-python (GitHub) | https://github.com/anthropics/claude-agent-sdk-python |
| Agent SDK Python Reference | https://code.claude.com/docs/en/agent-sdk/python |
| MCP Python SDK (GitHub) | https://github.com/modelcontextprotocol/python-sdk |
| MCP Official Docs — Build a Server | https://modelcontextprotocol.io/docs/develop/build-server |
| DeepWiki — ClaudeAgentOptions Reference | https://deepwiki.com/anthropics/claude-agent-sdk-python/2.3-claudeagentoptions-configuration-reference |
| MCP Calculator Example | https://github.com/anthropics/claude-agent-sdk-python/blob/main/examples/mcp_calculator.py |
