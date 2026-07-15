# Building AI Agents with MCP

### From Agent Loop to Production Servers

A hands-on O'Reilly Live Training on the **Model Context Protocol (MCP)** —
the open standard (now under the Linux Foundation's Agentic AI Foundation)
for connecting AI agents to tools, data, and external systems.

> The course used to ask *"The HTTP Moment of AI?"* — the question has been
> answered. MCP was donated to the Linux Foundation in Dec 2025 with every
> major vendor (Anthropic, OpenAI, Google, Microsoft, AWS…) on board. This
> course teaches you to build with the settled standard: from the agent
> loop up to deployed, secured, production servers.

## 🎯 What is MCP?

- **One protocol, many hosts** — the server you write in module 01 is
  consumed unmodified by Claude Desktop, Claude Code, the Claude Agent SDK,
  Cursor, and (deployed) Claude web.
- **Tools, resources, prompts** — first-class primitives, discoverable at
  runtime. **MCP Apps** (interactive UIs) shipped as the first official
  extension in Jan 2026.
- **Local or remote** — `stdio` for development, `streamable-http`
  (stateless) for production.

## 📚 The arc — 7 modules, one use case

One coherent artifact — a **personal research assistant** — grows a layer
at a time. Every module ends on "why this is the current way."

| Module | The move | Day |
|--------|----------|-----|
| `00` | **Agents are loops.** Hand-rolled loop, tools = plain Python functions | 1 |
| `01` | **Tools move out of the process.** Same tools behind an MCP server; thin client; connect Claude Code & Claude Desktop | 1 |
| `02` | **The Agent SDK is an MCP host.** Loop collapses to ~15 lines; in-process servers | 1 |
| `03` | **Skills vs MCP.** Access vs know-how — then an agent *builds* an MCP server via the mcp-builder skill | 1 |
| `04` | **Production shape.** Remote HTTP, auth seam, intent-grouped tools, hooks, evals, structured outputs | 2 |
| `05` | **Deploy it.** Remote server on Vercel, connected from multiple hosts — plus your first **MCP App** | 2 |
| `06` | **Defend & scale.** Tool-poisoning attack/defense lab; multi-server composition, subagents, sessions | 2 |

Take-home: `demos/exercises/link-checker/`. Retired material: `demos/archive/`.

## 🚀 Quick start

Every script carries uv inline metadata — no environment juggling:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/EnkrateiaLucca/mcp-course.git
cd mcp-course

# run anything directly
uv run demos/01-introduction-to-mcp/mcp_server.py

# inspect any MCP server
mcp dev demos/01-introduction-to-mcp/mcp_server.py
```

Traditional setup: `python -m venv venv && source venv/bin/activate && pip install -r requirements/requirements.txt`

### Environment

```env
# .env at the repo root
ANTHROPIC_API_KEY=sk-...       # all agent demos (console: platform.claude.com)
MCP_AUTH_TOKEN=demo-secret     # module 04 (and optionally 05)
```

**Version pins that matter (July 2026):**
- `mcp>=1.12,<2` — the official Python SDK, pinned to v1. **v2 (tracking
  the 2026-07-28 spec) renames `FastMCP` → `MCPServer`**; the standalone
  "FastMCP 3" is a separate Prefect-backed project. Concepts identical.
- `claude-agent-sdk` 0.2.x — bundles the Claude Code CLI; Python ≥3.10.

---

## 📁 Modules

### 00 — Agents are loops
**`demos/00-intro-agents/`** · Build the research assistant with the bare
Claude API: `web_search` (DuckDuckGo) + sandboxed filesystem tools in a
hand-rolled loop. You'll never write this loop again — but you'll know
what every framework is doing.

```bash
jupyter lab demos/00-intro-agents/intro-agents-cld.ipynb
uv run demos/00-intro-agents/basic_personal_agent.py "Research MCP and save a brief."
```

### 01 — Introduction to MCP
**`demos/01-introduction-to-mcp/`** · Same tools behind a FastMCP server.
Inspect with MCP Inspector, watch the raw protocol via the thin client,
then connect **Claude Code** and **Claude Desktop** to it — two hosts, one
server, zero changes.

```bash
cd demos/01-introduction-to-mcp
mcp dev ./mcp_server.py                 # inspector
uv run mcp_client.py ./mcp_server.py    # the protocol, demystified
claude mcp add research -- uv run $PWD/mcp_server.py
```

### 02 — The Agent SDK is an MCP host
**`demos/02-research-agent-sdk/`** · The loop disappears:

```python
options = ClaudeAgentOptions(
    system_prompt=SYSTEM_PROMPT,
    mcp_servers={"research": {"command": "uv", "args": ["run", "mcp_server.py"]}},
    allowed_tools=["mcp__research__*"],
)
async for message in query(prompt=user_prompt, options=options): ...
```

Plus the in-process pattern (`create_sdk_mcp_server`) — tools as plain
async functions, no subprocess, ideal for serverless.

### 03 — Skills vs MCP
**`demos/03-skills-and-mcp/`** · The 2026 question, answered: **MCP =
access, skills = know-how, plugins bundle both.** Then the wow moment:
the `mcp-builder` skill scaffolds a working MCP server from one prompt —
the workflow the official MCP docs now recommend.

### 04 — Production-shaped research agent
**`demos/04-production-research-agent/`** · Intent-grouped tools (7→3),
`streamable-http`, a real auth seam (bearer → OAuth 2.1/CIMD ladder),
`PreToolUse`/`PostToolUse` hooks, telemetry vs evals, structured outputs.

```bash
export MCP_AUTH_TOKEN=demo-secret
uv run demos/04-production-research-agent/research_server.py   # terminal 1
uv run demos/04-production-research-agent/research_agent.py "Research MCP auth"
```

### 05 — Deploy a remote MCP server (+ MCP Apps)
**`demos/05-deploy-remote-mcp/`** · The 2026 deployment story: don't wrap
your agent in a web framework — deploy the **server** (stateless
streamable HTTP) and connect every host to it. Ships an **MCP App**: an
interactive research explorer rendered inside the Claude conversation.

```bash
cd demos/05-deploy-remote-mcp
uv run server.py                                      # terminal 1
uv run test_client.py                                 # pre-flight
npx cloudflared tunnel --url http://localhost:8000    # → Claude custom connector
vercel deploy --prod                                  # → permanent
```

### 06 — Security & composition
**`demos/06-security-and-composition/`** · `security-lab/`: a runnable
tool-poisoning attack and its `PreToolUse` defense. `composition/`:
third-party servers (Playwright, Git), a fact-checker **subagent**, and
session **resume/fork**.

---

## 🎨 The five architecture patterns

1. **External stdio server** (01) — `mcp.run(transport="stdio")`; subprocess, language-agnostic.
2. **Agent SDK as host** (02) — `mcp_servers={...}`, `allowed_tools=["mcp__x__*"]`.
3. **In-process server** (02b) — `create_sdk_mcp_server(tools=[...])`; no transport.
4. **Remote HTTP + auth** (04) — `mcp.run(transport="streamable-http")` + bearer/OAuth on the wire.
5. **Stateless remote + MCP Apps** (05) — `stateless_http=True`; tool `_meta.ui.resourceUri` → `ui://` HTML.

## 🛠️ Development tools

```bash
mcp dev path/to/server.py        # MCP Inspector — call tools in a web UI
claude mcp add <name> -- uv run /abs/path/server.py   # Claude Code (stdio)
claude mcp add <name> --transport http <url>          # Claude Code (remote)
```

Claude Desktop config: `~/Library/Application Support/Claude/claude_desktop_config.json`
(macOS) / `%APPDATA%\Claude\claude_desktop_config.json` (Windows) — absolute
paths, restart after editing.

## 🐛 Troubleshooting

- **`mcp` module not found** → `uv` reads each script's inline metadata;
  for manual envs `pip install "mcp[cli]>=1.12,<2"`.
- **Claude Desktop doesn't see the server** → absolute paths, `which uv`,
  run the server standalone first, restart the app.
- **Module 04 401s** → `MCP_AUTH_TOKEN` must be set in *both* terminals.
- **DDGS returns nothing** → DuckDuckGo throttles; the tools degrade
  gracefully — retry, or swap in your favorite search API.
- **Rate limits** → iterate on `claude-haiku`.

## 📖 Resources

**Official:** [MCP docs](https://modelcontextprotocol.io/docs/getting-started/intro) ·
[Spec (2025-11-25)](https://modelcontextprotocol.io/specification/2025-11-25) ·
[2026-07-28 release candidate](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/) ·
[Python SDK](https://github.com/modelcontextprotocol/python-sdk) ·
[Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) ·
[MCP Apps](https://modelcontextprotocol.io/extensions/apps) ·
[Agent Skills standard](https://agentskills.io)

**The production canon (read in this order):**
[Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) →
[Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents) →
[Equipping agents with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) →
[Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) →
[Advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use) →
[Building agents that reach production systems with MCP](https://claude.com/blog/building-agents-that-reach-production-systems-with-mcp)

**Community:** [Official MCP Registry](https://registry.modelcontextprotocol.io) ·
[Awesome MCP servers](https://github.com/punkpeye/awesome-mcp-servers) ·
[PulseMCP](https://www.pulsemcp.com/servers)

**Course materials:** `presentation/presentation.html` ·
`presentation/code-execution-with-mcp.html` ·
`demos/assets-resources/MCP_TECHNICAL_CHEATSHEET.md`

## 🎓 Instructor

**Lucas Soares** —
[Blog](https://enkrateialucca.github.io/lucas-landing-page/) ·
[LinkedIn](https://www.linkedin.com/in/lucas-soares-969044167/) ·
[X](https://x.com/LucasEnkrateia) ·
[YouTube — Automata Learning Lab](https://www.youtube.com/@automatalearninglab) ·
lucasenkrateia@gmail.com

---

**Happy building. 🎉**
