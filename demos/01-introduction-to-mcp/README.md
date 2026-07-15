# Demo 01 — Introduction to MCP

Same research assistant as demo `00` — but the tools move out of your
process and behind a **Model Context Protocol server**. That one change is
the whole point: the server you write here is consumed, unmodified, by
*four different hosts* over the course of the day.

```
                 JSON-RPC over stdio
  ┌─────────────┐                    ┌───────────────────────────┐
  │  Any host    │ ─────────────────▶│  MCP Server                │
  │  (see below) │ ◀───────────────── │  mcp_server.py             │
  └─────────────┘                    │  web_search + filesystem   │
                                     └───────────────────────────┘
```

## What changed vs demo 00

| demo 00                                  | demo 01                                                 |
|------------------------------------------|---------------------------------------------------------|
| Tools = Python functions in the notebook | Tools = `@mcp.tool()` in `mcp_server.py`                |
| Agent calls functions directly           | Any MCP host calls them over the protocol               |
| One file, one consumer                   | One server, N hosts — the M×N problem solved            |

## Files

- `mcp_server.py` — FastMCP server: `web_search`, `read_file`, `write_file`,
  `edit_file`, `move_file`, `delete_file`, `list_files`, plus a
  `workspace://files` resource.
- `mcp_client.py` — a thin protocol client, runnable standalone. ~60 lines
  that demystify what every host does under the hood: `initialize`,
  `tools/list`, `tools/call`, `resources/read`.

*(The hand-rolled agent loop that wired this client to Claude lives in
`demos/archive/01-full-host-client/` — we don't run it live anymore because
demo 02's Agent SDK replaces it, but it's worth reading once.)*

## Run

```bash
cd demos/01-introduction-to-mcp

# 1. Inspect the server interactively (tools, resources, try a call)
mcp dev ./mcp_server.py

# 2. Watch the raw protocol happen — one round-trip per primitive
uv run mcp_client.py ./mcp_server.py
```

## Connect real hosts — same server, zero changes

**Claude Code** (the host most of you use daily):

```bash
claude mcp add research -- uv run /absolute/path/to/mcp_server.py
# then inside claude:  "search the web for MCP and save a brief to notes.md"
```

**Claude Desktop** — add to the config and restart:

```json
// macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "research": {
      "command": "uv",
      "args": ["run", "/absolute/path/to/mcp_server.py"]
    }
  }
}
```

Everything the tools create lands under `./workspace/`.

## Why this matters

You just solved the **M×N integration problem**: M hosts × N tool
integrations collapses to M+N. In demo 02, a third host — the **Claude
Agent SDK** — consumes this same file, and the "agent loop" you built in
demo 00 disappears into one SDK call.

> 🗓️ **2026 note.** This server uses the official Python SDK's v1 `FastMCP`
> class (pinned `mcp>=1.12,<2`). SDK v2 — which tracks the July 28, 2026
> spec revision — renames it to `MCPServer`; the standalone "FastMCP 3"
> project (Prefect) is a separate, higher-level framework. Same concepts
> everywhere; only names move.
