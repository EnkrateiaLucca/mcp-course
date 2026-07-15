# Demo 06 — Security, composition & sessions

Two sub-modules that close the course: first *defend* the stack you built,
then *scale* it — multiple servers, delegation to subagents, resumable
sessions.

## `security-lab/` — tool poisoning: attack & defense

A runnable attack-and-defense pair. A poisoned MCP tool hides a directive
telling the model to exfiltrate a (fake) secret; the defended version
blocks it with a `PreToolUse` path firewall + tool-description inspection.
Everything is local; nothing real leaks.

```bash
cd security-lab
export ANTHROPIC_API_KEY=sk-...
uv run attack_demo.py       # the attack succeeds
uv run defended_demo.py     # the defense stops it
```

Why this matters in 2026: MCP security is now a first-class module in
every serious curriculum (OWASP-style *MCP Top 10*, the spec's hardened
OAuth story, mandatory Origin validation in 2025-11-25). Tool poisoning is
the attack class students can actually *see* in an hour.

## `composition/` — multi-server agents, subagents, sessions

The first time the agent consumes servers it **didn't write** (Playwright,
Git) and delegates to a **subagent** with a narrower toolset.

```bash
cd composition
export ANTHROPIC_API_KEY=sk-...
uv run research_team.py       # research + Playwright fact-checker subagent
uv run git_research_agent.py  # research + Git MCP server
uv run resume_and_fork.py     # sessions: resume a run, fork an alternative
```

Current-API notes (2026):
- The subagent-invoking tool is named **`Agent`** (renamed from `Task`) —
  include `"Agent"` in `allowed_tools`.
- Subagents run **in the background by default** now; control with
  `run_in_background`.
- Sessions are **cwd-sensitive**: `resume=session_id` silently starts fresh
  if the working directory changed.

Where to find servers worth composing: the official **MCP Registry**
(registry.modelcontextprotocol.io) and the host-specific catalogs built on
top of it.
