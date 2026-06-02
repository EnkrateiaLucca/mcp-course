# Demo 02 — Research Assistant on the Claude Agent SDK

The same research assistant from demos `00` and `01`, rebuilt on the
[**Claude Agent SDK**](https://code.claude.com/docs/en/agent-sdk/overview).

The agent loop disappears. The SDK is itself an MCP host, so we point it at the
**exact same `mcp_server.py` we built in demo 01** and let it drive.

## The progression

| Demo | What's new                                  | Lines of agent code |
|------|---------------------------------------------|---------------------|
| 00   | Hand-rolled agent loop, tools = Python      | ~70                 |
| 01   | Tools moved behind an MCP server            | ~60 (host + client) |
| 02   | Agent loop replaced by Claude Agent SDK     | ~15                 |

## How it wires up

```python
options = ClaudeAgentOptions(
    system_prompt=SYSTEM_PROMPT,
    mcp_servers={
        "research": {"command": "uv", "args": ["run", "<path>/mcp_server.py"]},
    },
    allowed_tools=["mcp__research__*"],     # only our tools, no shell etc.
)

async for message in query(prompt=user_prompt, options=options):
    ...
```

That's it. No tool-result bookkeeping, no `messages` list, no `stop_reason`
branching. The SDK:

- spawns the MCP server as a subprocess,
- lists its tools and exposes them to Claude,
- runs the loop,
- streams `AssistantMessage` / `ResultMessage` events back.

MCP tool names get namespaced: `web_search` on the `research` server becomes
`mcp__research__web_search`, which is why `allowed_tools=["mcp__research__*"]`
restricts the agent to *only* our tools.

## Run

```bash
export ANTHROPIC_API_KEY=sk-...

# Default prompt (researches MCP, saves a brief)
uv run research_agent.py

# Custom prompt
uv run research_agent.py "Find three recent papers on agentic RAG and summarize them."
```

Files land under `demos/01-introduction-to-mcp/workspace/` (the server's
workspace), so demos 00 → 02 all reuse the same MCP server and the same
filesystem sandbox.

## Where to go next

- Demo 03 — Agent SDK + a third-party MCP server (filesystem reference server).
- Demo 04 — Agent SDK over tabular/CSV data via MCP.
- Demo 06 — Deploying an Agent SDK + MCP agent to Vercel.
