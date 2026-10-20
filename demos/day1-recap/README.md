# Day 1 recap: reusable MCP server

`reusable_mcp_server.py` is a stdio `MCPServer` (MCP SDK v2) with one tool, `query_movie_data(movie)`.
Any MCP host can launch it: Claude Desktop, Claude Code, the Inspector, or the Agent SDK.

## 1. Sanity check

```bash
cd demos/day1-recap
mcp dev reusable_mcp_server.py      # Inspector UI, call query_movie_data with "Barbie"
```

## 2. Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (absolute paths, then restart Claude Desktop):

```json
{
  "mcpServers": {
    "lucas_movies": {
      "command": "uv",
      "args": [
        "run",
        "/Users/greatmaster/Desktop/projects/oreilly-live-trainings/mcp-course/demos/day1-recap/reusable_mcp_server.py"
      ]
    }
  }
}
```

If Desktop can't find `uv`, use its full path: `which uv`.

## 3. Claude Code

```bash
claude mcp add lucas_movies -- uv run $PWD/demos/day1-recap/reusable_mcp_server.py
claude mcp list
```

## 4. Agent SDK (external process)

```python
options = ClaudeAgentOptions(
    mcp_servers={"lucas_movies": {"command": "uv", "args": ["run", "/abs/path/reusable_mcp_server.py"]}},
    allowed_tools=["mcp__lucas_movies__*"],
)
```

## Troubleshooting

- Inspector shows "Connection closed": keep the `dependencies=[...]` on `MCPServer(...)`; `mcp dev` installs from it.
- Desktop shows no tools: check the log at `~/Library/Logs/Claude/mcp-server-lucas_movies.log`.
