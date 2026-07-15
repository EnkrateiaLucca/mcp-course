# Demo 02 — The Claude Agent SDK *is* an MCP host

Delete the loop. The Claude Agent SDK — the same engine that powers Claude
Code — is itself an MCP host. Point it at the **exact same server file from
demo 01** and the ~70-line agent loop from demo 00 collapses to a
configuration object and one `query()` call.

```python
options = ClaudeAgentOptions(
    system_prompt=SYSTEM_PROMPT,
    mcp_servers={"research": {"command": "uv", "args": ["run", "mcp_server.py"]}},
    allowed_tools=["mcp__research__*"],   # tools are namespaced mcp__<server>__<tool>
)
async for message in query(prompt=user_prompt, options=options):
    ...
```

## Files

- `research_agent.py` — the ~15-line version of demos 00/01. External MCP
  server over stdio (same `mcp_server.py`).
- `research_agent_multiturn.py` — `ClaudeSDKClient` for a multi-turn
  session (follow-up questions share context).
- `in_process_agent.py` — **the fourth pattern**: `create_sdk_mcp_server`
  registers plain async functions as an MCP server running inside the
  agent's process. No subprocess, no transport. Use it when the tools only
  exist for this one agent (and for serverless).
- `mcp_server.py` — copy of demo 01's server, so this folder runs standalone.

## Run

```bash
export ANTHROPIC_API_KEY=sk-...
cd demos/02-research-agent-sdk

uv run research_agent.py "Research what Agent Skills are and save a brief."
uv run in_process_agent.py "Research MCP Apps and save a brief."
```

## What the SDK gives you that the hand-rolled loop didn't

Context management, streaming, permissions, hooks, subagents, sessions,
skills — all the production machinery demos 04–06 build on. And since
late 2025, **tool search is on by default**: with many MCP servers
connected, the SDK defers tool definitions and loads only the relevant
ones into context (we come back to this in demo 04).

## External vs in-process — the decision in one line

Reusable by other hosts / separately deployable → **external** (stdio or
HTTP). Only this agent needs it / single artifact / serverless →
**in-process**.
