# Demo 09 — Multi-server Composition + Subagents

The first time in this course where the agent consumes an MCP server it
**did not write**, and delegates deep work to a **specialized subagent**
with a narrower toolset.

## What's in here

| File | What it does |
|------|--------------|
| `research_team.py` | A research agent wired to two MCP servers: the in-process `research` server from demo 04 *and* the public Playwright MCP server (`npx @playwright/mcp@latest`). It defines a `fact-checker` subagent that verifies each claim in a brief by opening the cited source in a real browser. |
| `git_research_agent.py` | A variant that composes the in-process research server with the **Git MCP server** — the canonical "real third-party server" example from Anthropic's `02_The_observability_agent` cookbook. |

## What this teaches

1. **Servers compose.** `mcp_servers={...}` is a dict; add a key, add a
   server. The Agent SDK is itself an MCP host.
2. **Built-in subagents.** `AgentDefinition` lets the parent delegate to
   a child agent with its own system prompt, model, and toolset.
   Subagents get a **fresh context** (no parent history), **cannot
   spawn subagents**, and inherit a permissive permission mode
   non-overridably — so keep the parent strict.
3. **Tool search is on by default.** When a server exposes 100+ tools
   (the GitHub MCP server does), the SDK withholds tool defs and loads
   only the ones Claude asks for per turn. Mentioned here because demo
   07's reading list links it but never shows it.

## Run it

```bash
export ANTHROPIC_API_KEY=sk-...

# Playwright MCP needs npx in PATH and will install on first use.
uv run research_team.py "Research MCP authentication, then verify your sources are still live."

# Git MCP composes with our in-process research server.
uv run git_research_agent.py
```

## References

- [MCP authentication docs](https://code.claude.com/docs/en/agent-sdk/mcp#authentication)
- [MCP tool search](https://code.claude.com/docs/en/agent-sdk/mcp#mcp-tool-search)
- Cookbook: `02_The_observability_agent` (Git + GitHub MCP composition)
- Cookbook: `01_The_chief_of_staff_agent` (subagent delegation)
