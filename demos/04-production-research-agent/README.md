# Demo 04 — The production-shaped research agent

The research assistant from demos 00–02, evolved along the moves in
Anthropic's [*Building agents that reach production systems with MCP*](https://claude.com/blog/building-agents-that-reach-production-systems-with-mcp)
(updated Apr 2026):

1. **Intent-grouped tools, not API mirrors.** Demo 01's seven primitives
   collapse to three (`research_topic`, `list_briefs`, `read_brief`) —
   one round-trip per task instead of 4–6 turns of orchestration.
2. **Remote HTTP transport** (`streamable-http`) — cloud-reachable, not a
   laptop subprocess.
3. **An auth seam** — bearer token on every request, at the ASGI layer,
   exactly where real auth slots in (see the ladder below).
4. **Hooks + permissions** — `PreToolUse` validates inputs, `PostToolUse`
   logs outcomes, a `can_use_tool` callback enforces the allow-list.
5. **Telemetry vs evals** — `ExecutionTracker` (cost/duration/tool counts)
   tells you the agent *ran*; `evals.py` (assertions + LLM-as-judge) tells
   you it was *right*.

## Files

- `research_server.py` — the intent-grouped HTTP server (+ bearer middleware)
- `research_agent.py` — SDK agent: auth headers, hooks, permission callback, tracker
- `evals.py` — three-layer correctness harness (deterministic → LLM judge → CI gate)
- `structured_output_demo.py` — `output_format` + Pydantic: the final answer
  as validated JSON instead of prose. Structured verdicts are gradeable.
- `research_agent_builtin_tools.py` — contrast run with SDK built-ins

## Run

```bash
# Terminal 1 — server
export MCP_AUTH_TOKEN=demo-secret
uv run research_server.py                      # http://127.0.0.1:8765/mcp

# Terminal 2 — agent
export ANTHROPIC_API_KEY=sk-... MCP_AUTH_TOKEN=demo-secret
uv run research_agent.py "Research how MCP authentication works"
uv run evals.py                                 # correctness gate
uv run structured_output_demo.py                # typed final answers
```

## The auth ladder (know where you are on it)

1. **Nothing** — demos only.
2. **Static bearer token** ← *this demo.* The wiring is real (client sends
   the header, server middleware validates); the credential is not.
3. **OAuth 2.1** — the spec's answer: your server is an OAuth *resource
   server*; clients register via **Client ID Metadata Documents (CIMD)**
   and request scopes incrementally. This is what "Add custom connector"
   in Claude speaks. (Spec 2025-11-25 auth section + the enterprise-managed
   auth extension, stable June 2026.)

Teaching OAuth end-to-end is a course of its own; the point here is the
**seam** — swap layer 2 for layer 3 without touching a single tool.

## 2026 framing note: tool search changed the *why*, not the *what*

The token-bloat argument for fewer tools ("40 tool schemas burn 50k
context tokens") is now partially solved at the platform level — the Agent
SDK enables **tool search** by default, deferring tool definitions and
loading only what's relevant. So why still intent-group? Because the win
was never just tokens: one well-named tool per *job to be done* means
fewer wrong-tool choices, fewer round-trips, and less intermediate data
through context. Design lesson survives; the framing evolves.

For very large tool surfaces, the current guidance goes one step further:
expose a thin **code-execution** tool over your API instead of hundreds of
endpoints (see `presentation/code-execution-with-mcp.html`).
