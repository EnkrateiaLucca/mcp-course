# Building AI Agents with MCP

A hands-on bootcamp on the **Model Context Protocol (MCP)** — the standardized way to connect AI agents to external tools, data sources, and systems.

> 🎓 **O'Reilly Live Training**: *"Building AI Agents with MCP: The HTTP Moment of AI?"*

## 🎯 What is MCP?

The **Model Context Protocol** is an open standard that gives AI applications a single, uniform way to talk to tools, data, and external systems — a "USB-C port for AI."

- **One protocol, many hosts** — Claude Desktop, the Claude Agent SDK, custom apps all consume the same MCP servers.
- **Tools, resources, prompts** — first-class primitives, discoverable at runtime.
- **Local or remote** — `stdio` for development, `streamable-http` for production.
- **Cross-platform** — works with any AI model that speaks MCP client.

## 📚 Course arc

The first four demos build a **single coherent use case** — a personal research assistant with web search + filesystem — and grow it one layer at a time:

| Demo | What changes | Lines of agent code |
|------|--------------|---------------------|
| `00` | Hand-rolled agent loop, tools = plain Python functions | ~70 |
| `01` | Tools moved behind an **MCP server**, same loop becomes a "host" | ~60 |
| `02` | Agent loop replaced by the **Claude Agent SDK**, same MCP server | ~15 |
| `04` | **Production shape**: HTTP transport, auth, hooks, evals, intent-grouped tools | ~80 (with all the hardening) |

Demo `03` then branches into a real use case (tabular data), demo `04` returns to harden the SDK pattern for production, and `05`–`07` cover automations, deployment, and tips & workflows.

### Prerequisites

- **Python 3.10+** (3.12+ for demos that use the Claude Agent SDK)
- **Basic async/await** understanding
- **API keys**:
  - `ANTHROPIC_API_KEY` — [console.anthropic.com](https://console.anthropic.com/)
  - `REPLICATE_API_TOKEN` — optional, only for demo 04's image-generation extra

## 🚀 Quick start

### UV (recommended)

Every script has uv inline metadata, so no virtualenv juggling:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

cd demos/01-introduction-to-mcp
uv run mcp_server.py            # run a demo directly
mcp dev mcp_server.py           # or inspect with MCP Inspector
```

### Traditional setup

```bash
git clone https://github.com/EnkrateiaLucca/mcp-course.git
cd mcp-course
python -m venv venv && source venv/bin/activate
pip install -r requirements/requirements.txt
```

### Environment

```env
# .env at the repo root
ANTHROPIC_API_KEY=sk-...
REPLICATE_API_TOKEN=...        # optional, demo 04
MCP_AUTH_TOKEN=demo-secret     # demo 03
```

---

## 📁 Demos

### Demo 00 — Intro to agents (build from scratch)
**Path**: `demos/00-intro-agents/`

Build a research assistant with the bare Claude API: `web_search` (DuckDuckGo, no API key) + sandboxed filesystem tools (`read`, `write`, `edit`, `move`, `delete`, `list`), wired into a hand-rolled agent loop.

```bash
jupyter lab demos/00-intro-agents/intro-agents-cld.ipynb
# or
uv run demos/00-intro-agents/research_agent.py "Research MCP and save a brief."
```

**Files**: `intro-agents-cld.ipynb` (teaching), `research_agent.py` (standalone runnable companion).

---

### Demo 01 — Introduction to MCP
**Path**: `demos/01-introduction-to-mcp/`

Same tools, now behind an MCP server. The agent loop from demo 00 becomes a thin "host" that calls tools through an MCP client.

```
Host (mcp_host.py + Claude)  →  MCP Client (mcp_client.py)  →  MCP Server (mcp_server.py)
```

```bash
cd demos/01-introduction-to-mcp
uv run mcp_host.py ./mcp_server.py                              # interactive
uv run mcp_host.py ./mcp_server.py "Research MCP and save it."  # one-shot
```

**Files**: `mcp_server.py` (FastMCP, 7 tools + `workspace://files` resource), `mcp_client.py` (protocol layer), `mcp_host.py` (agent loop, identical to demo 00 but tools live remotely).

---

### Demo 02 — Research assistant on the Claude Agent SDK
**Path**: `demos/02-research-agent-sdk/`

Throw away the host and the client. The **Claude Agent SDK** is itself an MCP host — point it at the same `mcp_server.py` and the agent loop collapses to ~15 lines.

```bash
cd demos/02-research-agent-sdk
uv run research_agent.py "Research what Agent Skills are and save a brief."
```

```python
options = ClaudeAgentOptions(
    system_prompt=SYSTEM_PROMPT,
    mcp_servers={"research": {"command": "uv", "args": ["run", "mcp_server.py"]}},
    allowed_tools=["mcp__research__*"],
)
async for message in query(prompt=user_prompt, options=options):
    ...
```

---

### Demo 03 — Query tabular data
**Path**: `demos/03-query-tabular-data/`

MCP server for CSV/tabular queries, driven by the Claude Agent SDK.

```bash
cd demos/03-query-tabular-data
uv run claude_agents_sdk_demo.py
# or
jupyter notebook claude_agents_csv_demo.ipynb
```

**Tools**: `get_all_products`, `search_products_by_category`, `search_products_by_price_range`, `get_product_by_name`, `get_top_rated_products`, `get_products_in_stock`, `get_category_statistics`.

**Example queries**:
```
"What electronics do we have?"
"Show me products between $50 and $150"
"What are the top 3 highest-rated products?"
```

---

### Demo 04 — Production-shaped research agent
**Path**: `demos/04-production-research-agent/`

The research assistant from demos `00–02`, evolved along the four moves from Anthropic's [*Building agents that reach production systems with MCP*](https://claude.com/blog/building-agents-that-reach-production-systems-with-mcp):

1. **Intent-grouped tools** — 7 primitives collapse to 3 (`research_topic`, `list_briefs`, `read_brief`).
2. **Remote HTTP transport** — `mcp.run(transport="streamable-http")`.
3. **Auth seam** — bearer token on every MCP request (real OAuth swap-in marked).
4. **Hooks + evals** — `PreToolUse` validator, `PostToolUse` logger, `ExecutionTracker` (duration, cost, tool counts).

```bash
# Terminal 1 — the server
export MCP_AUTH_TOKEN=demo-secret
uv run demos/04-production-research-agent/research_server.py

# Terminal 2 — the agent
uv run demos/04-production-research-agent/research_agent.py "Research how MCP auth works"
```

**Files**: `research_server.py`, `research_agent.py`, `README.md`, **`presenter_notes.md`** (10-min live-demo script).

---

### Demo 05 — Link health checker agent
**Path**: `demos/05-link-checker-agent/`

An agent that audits markdown files for broken links — Claude Agent SDK + a dedicated MCP server for link-checking.

```
User request → Link Checker Agent (SDK)
                  ↓ discovers files, dedupes URLs, checks each
              MCP server (link-checker)
                  - list_markdown_files(directory)
                  - extract_links(filepath)
                  - check_url(url)          ← HEAD request + latency
                  - write_report(filename, content)
                  ↓
              reports/  (audit output)
```

```bash
cd demos/05-link-checker-agent
uv run link_checker_agent.py
```

---

### Demo 06 — Data analysis agent (FastAPI + Vercel)
**Path**: `demos/06-deploy-simple-agent-mcp-vercel/`

Chat UI backed by the Claude Agent SDK with an **in-process** MCP server for data analysis, deployed to **Vercel serverless**. Ask plain-English questions about a synthetic Portuguese company dataset.

```
User → HTML/JS (SSE client)
         ↓ POST /chat
       FastAPI
         ↓
       Claude Agent SDK
         ↓
       In-process MCP server ("analysis")
         ↓  tools operate on pandas DataFrame
       Text  → SSE text events  → rendered as markdown
       Plots → base64 PNG       → SSE image events → <img>
```

**Tools**: `describe_data`, `show_head`, `column_info`, `group_aggregate`, `correlation_matrix`, `plot_data`.

```bash
cd demos/06-deploy-simple-agent-mcp-vercel
cp .env.example .env             # add ANTHROPIC_API_KEY
uv run main.py                    # → http://localhost:8000

# Deploy
vercel link && vercel env add ANTHROPIC_API_KEY production && vercel --prod
```

---

### Demo 07 — Hacks, tips, tools & workflows
**Path**: `demos/07-hacks-tips-tools-workflows/`

Curated practical material shown live: ecosystem tools, workflow shortcuts, and a Claude **skill** for scaffolding MCP servers.

**Files**: `hacks_tips.md`, `mcp-builder-skill/`.

---

### Archive
**Path**: `demos/archive/`

- `02-study-case-anthropic-tools-resources-prompts-chat-app/` — the original full-featured chat app with native Claude tool use + MCP. Kept for reference; not part of the current course flow.

---

### Assets & resources
**Path**: `demos/assets-resources/`

- `MCP_TECHNICAL_CHEATSHEET.md` — quick reference
- `mcp_server_prompt_templates.md` — prompt templates for scaffolding MCP servers
- `mcp_security_report.pdf` — security analysis
- `diagram.excalidraw` — editable architecture diagrams
- Architecture/agent-loop/market-map PNGs

---

## 🎨 Architecture patterns

### Pattern 1 — External MCP server over stdio
*Used in*: demo 01.

```python
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("server")

@mcp.tool()
def do_thing(x: str) -> str: ...

mcp.run(transport="stdio")
```

A separate subprocess, language-agnostic, isolated. Great for development and the Claude Desktop config flow.

### Pattern 2 — Same server, consumed by the Claude Agent SDK
*Used in*: demo 02.

```python
options = ClaudeAgentOptions(
    mcp_servers={"research": {"command": "uv", "args": ["run", "mcp_server.py"]}},
    allowed_tools=["mcp__research__*"],
)
async for message in query(prompt, options=options): ...
```

The SDK *is* the MCP host. No client/loop code on your side.

### Pattern 3 — Remote MCP server over HTTP (production)
*Used in*: demo 04.

```python
# server
mcp.run(transport="streamable-http")

# agent
options = ClaudeAgentOptions(mcp_servers={
    "research": {"type": "http", "url": "...", "headers": {"Authorization": f"Bearer {tok}"}}
})
```

Cloud-deployable; auth lives on the wire; same SDK API.

### Pattern 4 — In-process MCP server
*Used in*: demos 03, 05, 06.

```python
from claude_agent_sdk import create_sdk_mcp_server, tool

@tool
async def query_data(args): ...

server = create_sdk_mcp_server(name="data-tools", tools=[query_data])
options = ClaudeAgentOptions(mcp_servers={"data": server})
```

Tools run in the same Python process — fastest, single deployment artifact, ideal for serverless.

### Pattern 5 — FastAPI + SSE streaming
*Used in*: demo 06.

```python
@app.post("/chat")
async def chat(req: ChatRequest):
    async def stream():
        async for event in client.receive_response():
            yield f"data: {event.json()}\n\n"
    return StreamingResponse(stream(), media_type="text/event-stream")
```

Wraps an in-process Agent SDK setup behind an HTTP endpoint with real-time streaming.

---

## 🛠️ Development tools

### MCP Inspector

```bash
mcp dev path/to/your_server.py
# Opens http://localhost:5173 — list tools, call them, view resources/prompts
```

### Claude Desktop integration

Config:
- macOS/Linux: `~/.config/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "research": {
      "command": "uv",
      "args": ["run", "/absolute/path/to/demos/01-introduction-to-mcp/mcp_server.py"]
    }
  }
}
```

Restart Claude Desktop after editing.

### Makefile

```bash
make conda-create     # create conda env
make env-setup        # pip-tools + UV
make notebook-setup   # install Jupyter kernel
make env-update       # rebuild requirements from requirements.in
make freeze           # freeze current deps
make clean            # nuke env
```

---

## 🪟 Windows setup

Prereqs: Python 3.10+, Node.js 18+, Git for Windows, Developer Mode on.

```cmd
git clone https://github.com/EnkrateiaLucca/mcp-course.git
cd mcp-course
python -m venv venv
venv\Scripts\activate
pip install -r requirements/requirements.txt
```

PowerShell execution policy (once):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Env vars:
```powershell
$env:ANTHROPIC_API_KEY="sk-..."
```

Claude Desktop config: `%APPDATA%\Claude\claude_desktop_config.json` — **use absolute paths with forward slashes**.

| Linux/macOS                  | Windows (PowerShell)             |
|------------------------------|----------------------------------|
| `source venv/bin/activate`   | `venv\Scripts\Activate.ps1`      |
| `export VAR=value`           | `$env:VAR="value"`               |
| `~/.config/Claude/`          | `$env:APPDATA\Claude\`           |

---

## 🐛 Troubleshooting

**`Module not found`**
```bash
uv pip install mcp model-context-protocol     # or pip install ...
```

**Claude Desktop not finding servers** — absolute paths, `which uv` in PATH, server runs standalone (`uv run mcp_server.py`), check Claude Desktop logs, restart after config edit.

**MCP server won't connect** — test with `mcp dev path/to/server.py`. Check the process is alive: `ps aux | grep mcp_server` (or `tasklist | findstr python` on Windows).

**Demo 03 HTTP server** — confirm `MCP_AUTH_TOKEN` is set in **both** terminals, and that nothing else is using port 8765.

**Rate limiting** — check API quota, exponential backoff, swap to a cheaper model (e.g. `claude-haiku`) for iteration.

---

## 📖 Resources

### Official docs
- [MCP introduction](https://modelcontextprotocol.io/introduction)
- [MCP specification](https://modelcontextprotocol.io/specification/)
- [Python SDK (FastMCP)](https://github.com/modelcontextprotocol/python-sdk)
- [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview)

### Production reading
- [Building agents that reach production systems with MCP](https://claude.com/blog/building-agents-that-reach-production-systems-with-mcp) — basis for demo 03
- [Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [Tool search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)

### Community
- [Awesome MCP servers](https://github.com/punkpeye/awesome-mcp-servers)
- [Glama MCP directory](https://glama.ai/mcp)
- [PulseMCP — clients](https://www.pulsemcp.com/clients) / [servers](https://www.pulsemcp.com/servers)

### Course materials
- `presentation/presentation.html` — interactive slides
- `presentation/presentation-mcp-updated.pdf` — slide deck PDF
- `demos/assets-resources/MCP_TECHNICAL_CHEATSHEET.md` — quick reference
- `demos/04-production-research-agent/presenter_notes.md` — live-demo script for demo 04
- `CLAUDE.md` — repo conventions for Claude Code

---

## 🎓 Instructor

**Lucas Soares**

- 📚 [Blog](https://enkrateialucca.github.io/lucas-landing-page/)
- 🔗 [LinkedIn](https://www.linkedin.com/in/lucas-soares-969044167/)
- 🐦 [Twitter/X](https://x.com/LucasEnkrateia)
- 📺 [YouTube — Automata Learning Lab](https://www.youtube.com/@automatalearninglab)
- 📧 lucasenkrateia@gmail.com

---

## 🚀 Suggested path

1. **Demo 00** — agents from scratch, build the loop yourself.
2. **Demo 01** — wrap the same tools as an MCP server, become an MCP host.
3. **Demo 02** — hand the loop to the Claude Agent SDK.
4. **Demo 03** — apply the SDK pattern to real data (CSV/tabular queries).
5. **Demo 04** — ship it: HTTP transport, auth, hooks, evals, intent-grouped tools.
6. **Demo 05** — branch to automations (link health auditor).
7. **Demo 06** — deploy to Vercel serverless (FastAPI + SSE).
8. **Demo 07** — tips, workflows, and the MCP-builder Claude skill.

Build your own MCP server for *your* workflow next.

---

**Happy building. 🎉**
