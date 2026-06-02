# Demo 00 — Intro to Agents

Build a personal **research assistant** from scratch with the Claude API: web search + filesystem tools, wired into a small agent loop.

This is the use case we carry through demos `01` (MCP server) and `02` (Claude Agent SDK).

## Files

- `intro-agents-cld.ipynb` — the teaching notebook (start here).
- `research_agent.py` — standalone version of the final agent, runnable from the CLI.

## Run

```bash
export ANTHROPIC_API_KEY=sk-...

# Notebook
jupyter lab intro-agents-cld.ipynb

# Or the .py companion
uv run research_agent.py "Research the Model Context Protocol and save a brief."
```

Tools the agent has: `web_search` (DuckDuckGo, no key), `read_file`, `write_file`, `edit_file`, `move_file`, `delete_file`, `list_files`. Every file the agent touches lives under `./workspace/`.
