# Automation Agent Demo

Claude Agent SDK + MCP server for creating, testing, and running Python automation scripts.

## Quick Start

```bash
export ANTHROPIC_API_KEY='your-key'
uv run automation_agent.py
```

## Files

- `automation_agent.py` — Claude agent (interactive CLI)
- `automation_mcp_server.py` — MCP server with sandboxed script tools
- `generated_scripts/` — Where scripts are saved and executed
- `WALKTHROUGH.md` — Full explanation of how this works

## Test the MCP Server Independently

```bash
mcp dev automation_mcp_server.py
```
