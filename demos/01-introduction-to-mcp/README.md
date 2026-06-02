# Demo 01 — Introduction to MCP

Same research assistant as demo `00` — but now the tools live behind a
**Model Context Protocol** server, and the agent loop becomes a thin "host"
that talks to the server through a client.

```
┌──────────────┐    JSON-RPC over stdio    ┌──────────────────────────┐
│  Host        │ ────────────────────────▶ │  MCP Server               │
│  mcp_host.py │                           │  mcp_server.py            │
│  + Claude    │ ◀──────────────────────── │  web_search + filesystem │
└──────┬───────┘                           └──────────────────────────┘
       │ uses
       ▼
┌──────────────┐
│ MCP Client    │
│ mcp_client.py │
└──────────────┘
```

## What changed vs demo 00

| demo 00                                  | demo 01                                                 |
|------------------------------------------|---------------------------------------------------------|
| Tools = Python functions in the notebook | Tools = `@mcp.tool()` in `mcp_server.py`                |
| Agent calls functions directly           | Agent calls them through the MCP client (`call_tool`)   |
| One file, one client                     | One server reusable by any MCP host (Claude Desktop, the Agent SDK, our own host…) |

The **agent loop is identical**. Only the tool transport changed.

## Files

- `mcp_server.py` — FastMCP server exposing `web_search`, `read_file`, `write_file`, `edit_file`, `move_file`, `delete_file`, `list_files`, and a `workspace://files` resource.
- `mcp_client.py` — minimal protocol client (no UI). Pure `list_tools` / `call_tool` / `read_resource`.
- `mcp_host.py` — the user-facing app. Connects via the client, converts MCP tool schemas to Claude's `tools=` format, runs the agent loop.

## Run

```bash
export ANTHROPIC_API_KEY=sk-...

# Inspect the server interactively
mcp dev ./mcp_server.py

# Or run the full host (interactive)
uv run mcp_host.py ./mcp_server.py

# One-shot
uv run mcp_host.py ./mcp_server.py "Research the Model Context Protocol and save a brief."
```

Everything the agent creates lands under `./workspace/`.

## Why this matters

In demo 02 we throw away `mcp_host.py` and `mcp_client.py` entirely — the
**Claude Agent SDK** is *itself* an MCP host. We will point it at this exact
same `mcp_server.py` and the agent loop disappears into one SDK call.
