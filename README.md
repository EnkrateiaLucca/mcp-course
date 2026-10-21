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

## 📚 The arc — 6 modules

Modules 00–03 grow one artifact — a **personal research assistant** — a layer
at a time. Module 04 then ships a real product end to end: a **shop analytics
agent** with its own MCP server, deployed as two containers. Module 05 attacks
and defends it. Every module ends on "why this is the current way."

| Module | The move | Day |
|--------|----------|-----|
| `00` | **Agents are loops.** Hand-rolled loop, tools = plain Python functions | 1 |
| `01` | **Tools move out of the process.** Same tools behind an MCP server; thin client; connect Claude Code & Claude Desktop | 1 |
| `02` | **The Agent SDK is an MCP host.** Loop collapses to ~15 lines; in-process servers | 1 |
| `03` | **Skills vs MCP.** Access vs know-how — then an agent *builds* an MCP server via the mcp-builder skill | 1 |
| `04` | **Ship it.** Shop analytics agent (FastAPI + Agent SDK) + governed MCP server (SQLite), Docker Compose, Render deploy, cost/token telemetry | 2 |
| `05` | **Defend & scale.** Data-exposure lab on module 04; tool-poisoning attack/defense; multi-server composition, subagents, sessions | 2 |

Take-home: `demos/exercises/link-checker/`. Retired material: `demos/archive/`.

## 🚀 Quick start

Every script carries uv inline metadata — no environment juggling:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/EnkrateiaLucca/mcp-course.git
cd mcp-course

# run anything directly
uv run --with mcp==2.3.0 --with mcp[cli]>=2.3,<3 --with ddgs mcp run ./demos/01-introduction-to-mcp/mcp_server.py

# inspect any MCP server (install the `mcp` CLI once; uv alone doesn't put it on PATH)
uv tool install "mcp[cli]>=2.3,<3"
uv run --with mcp==2.3.0 --with mcp[cli]>=2.3,<3 --with ddgs mcp dev demos/01-introduction-to-mcp/mcp_server.py
```

### Notebook setup (Jupyter kernel)

The scripts need nothing beyond `uv`. The notebook
(`demos/00-intro-agents/intro-agents-cld.ipynb`) additionally needs a kernel
named **`mcp-course`** on **Python 3.12+** — `requirements.txt` pins
`contourpy==1.4.0`, which refuses to install below 3.12. Build it once:

```bash
uv venv --python 3.12 && source .venv/bin/activate
uv pip install -r requirements/requirements.txt

# register the kernel the notebook declares — skip this and Jupyter
# opens the notebook with "kernel not found"
python -m ipykernel install --user --name mcp-course --display-name "mcp-course"
```

Plain `pip` works too — `python -m venv venv && pip install -r requirements/requirements.txt` —
as long as the active Python is 3.12+ and you still run the `ipykernel install` line.

### Environment

```env
# .env at the repo root
ANTHROPIC_API_KEY=sk-...       # all agent demos (console: platform.claude.com)
```

Module 04 runs from its own folder: copy `demos/04-shop-analytics-agent/.env.example`
to `.env` there and set only `ANTHROPIC_API_KEY`.

**Version pins that matter:**
- `mcp>=2.3,<3` — the official Python SDK v2 (`from mcp.server.mcpserver
  import MCPServer`). It speaks the 2026-07-28 spec and still accepts
  2025-11-25 clients. v1 called the class `FastMCP`; the standalone
  "FastMCP 3" is a separate Prefect-backed project.
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
**`demos/01-introduction-to-mcp/`** · Same tools behind an `MCPServer`.
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
the workflow the official MCP docs now recommend. Finally,
`skills-over-mcp/` serves that same skill over MCP through the official
Skills extension (SEP-2640).

### 04 — Ship it: a shop analytics agent with its own MCP server
**`demos/04-shop-analytics-agent/`** · A chat agent answers business questions
("How did Black Friday go?") with numbers and charts. Two deployables: the
**agent** (FastAPI + Claude Agent SDK, `tools=[]`, budget and turn caps) and a
**governed MCP server** (read-only SQLite, one definition of revenue, bearer
auth, stateless HTTP). Every reply shows tokens, estimated cost and steps; the
agent logs one JSON line per message. Deploys to Render with `render.yaml`.

```bash
cd demos/04-shop-analytics-agent
cp .env.example .env              # set ANTHROPIC_API_KEY only
docker compose up --build         # http://localhost:8000 · password: demo
```

### 05 — Security & composition
**`demos/05-security-and-composition/`** · `data-exposure-lab/`: module 04's
read-only server still leaks customer emails through `run_sql`; a SQLite
authorizer (`PII_GUARD=1`) fixes it at the data layer. `security-lab/`: a
runnable tool-poisoning attack and its `PreToolUse` defense. `composition/`:
third-party servers (Playwright, Git), a fact-checker **subagent**, and
session **resume/fork**.

The previous modules 04 (production research agent) and 05 (Vercel deploy +
MCP App) live in `demos/archive/`.

---

## 🎨 The five architecture patterns

1. **External stdio server** (01) — `mcp.run(transport="stdio")`; subprocess, language-agnostic.
2. **Agent SDK as host** (02) — `mcp_servers={...}`, `allowed_tools=["mcp__x__*"]`.
3. **In-process server** (02b) — `create_sdk_mcp_server(tools=[...])`; no transport.
4. **Remote HTTP + auth** (04) — `mcp.streamable_http_app(stateless_http=True)` + bearer middleware; agent and server as separate containers.
5. **MCP Apps** (`archive/05-deploy-remote-mcp`, `mcp-apps-productivity-timer`) — tool `_meta.ui.resourceUri` → `ui://` HTML.

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
  for manual envs `pip install "mcp[cli]>=2.3,<3"`.
- **Claude Desktop doesn't see the server** → absolute paths, `which uv`,
  run the server standalone first, restart the app.
- **Module 04 says the data service is unavailable** → the agent's `MCP_TOKEN` doesn't match the server's, or the server is down. With Docker Compose both use the same default; outside Docker, set the same `MCP_TOKEN` in both terminals.
- **DDGS returns nothing** → DuckDuckGo throttles; the tools degrade
  gracefully — retry, or swap in your favorite search API.
- **Rate limits** → iterate on `claude-haiku-5-5`.

## 📖 Resources

**Official:** [MCP docs](https://modelcontextprotocol.io/docs/getting-started/intro) ·
[Spec (2026-07-28 — current)](https://modelcontextprotocol.io/specification/2026-07-28) ·
[Spec (2025-11-25 — previous revision)](https://modelcontextprotocol.io/specification/2025-11-25) ·
[2026-07-28 release post](https://blog.modelcontextprotocol.io/posts/2026-07-28/) ·
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
`demos/assets-resources/MCP_TECHNICAL_CHEATSHEET.md`

**Two handouts, different audiences:**
- **Students** — [`assets/mcp-course-cheatsheet.html`](assets/mcp-course-cheatsheet.html)
  (printable: [`assets/mcp-course-cheatsheet.pdf`](assets/mcp-course-cheatsheet.pdf)).
  The quick-reference card to keep after the session.
- **Instructor** — [`assets/mcp-instructor-cheatsheet.html`](assets/mcp-instructor-cheatsheet.html)
  ([PDF](assets/mcp-instructor-cheatsheet.pdf)), generated from
  `demos/assets-resources/MCP_TECHNICAL_CHEATSHEET.md`. Deeper reference for
  answering questions live.

## 🎓 Instructor

**Lucas Soares** —
[Blog](https://enkrateialucca.github.io/lucas-landing-page/) ·
[LinkedIn](https://www.linkedin.com/in/lucas-soares-969044167/) ·
[X](https://x.com/LucasEnkrateia) ·
[YouTube — Automata Learning Lab](https://www.youtube.com/@automatalearninglab) ·
lucasenkrateia@gmail.com

---

**Happy building. 🎉**
