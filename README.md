# Building AI Agents with MCP: Complete Course Materials

A comprehensive 2-day bootcamp on the **Model Context Protocol (MCP)** - the standardized way to connect AI agents to external tools, data sources, and systems.

> 🎓 **O'Reilly Live Training**: "MCP Bootcamp: Building AI Agents with Model Context Protocol"

## 🎯 What is MCP?

The **Model Context Protocol (MCP)** is an open standard that provides a universal way to connect AI applications to data sources and tools - like a "USB-C port for AI." Instead of building custom integrations for each tool, MCP provides:

- **Standardized Communication**: A single protocol for all AI-tool interactions
- **Tool Discovery**: Agents can discover and understand available capabilities dynamically
- **Resource Access**: Structured access to data sources (files, databases, APIs)
- **Prompt Templates**: Reusable, versioned prompts that agents can leverage
- **Cross-Platform**: Works with any AI model (Claude, GPT, local models, etc.)

**Why It Matters**: MCP enables a future where AI agents can seamlessly integrate with any tool or data source, just as USB-C standardized hardware connectivity.

## 📚 Course Overview

This hands-on course takes you from MCP fundamentals to production deployment through 8 comprehensive demos:

### What You'll Learn

- ✅ **MCP Fundamentals**: Architecture, protocol concepts, and tool/resource patterns
- ✅ **Building MCP Servers**: Using FastMCP to create custom tool providers
- ✅ **Claude Agents SDK**: Building production-grade agents with in-process MCP
- ✅ **Chat Applications**: Building full-featured chat apps with Claude tool use and MCP
- ✅ **Real-World Applications**: Data queries, automation, and deployment
- ✅ **Security & Permissions**: Tool authorization, input validation, and best practices
- ✅ **Production Deployment**: Serverless deployment to Vercel with both SDKs

### Prerequisites

- **Python 3.10+** (Python 3.12+ recommended for latest features)
- **Basic async/await** understanding
- **API keys**:
  - Anthropic API key (for Claude demos) - [Get one here](https://console.anthropic.com/)
  - Replicate API key (OPTIONAL - for image generation demo) - [Get one here](https://replicate.com/)

## 🚀 Quick Start

### Using UV Package Manager (Recommended)

[UV](https://github.com/astral-sh/uv) is a fast Python package manager that handles dependencies automatically:

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run any demo directly (UV handles dependencies automatically)
cd demos/01-introduction-to-mcp
uv run mcp_server.py

# Or test with MCP Inspector
mcp dev mcp_server.py
```

**Benefits of UV:**
- ✅ No virtual environment management
- ✅ Automatic dependency resolution from script metadata
- ✅ Faster than pip
- ✅ Consistent across all demos

### Traditional Setup (Alternative)

```bash
# Clone and navigate to the repository
git clone https://github.com/EnkrateiaLucca/mcp-course.git
cd mcp-course

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install base dependencies
pip install -r requirements/requirements.txt
```

### Environment Setup

Create a `.env` file in the root directory:

```env
# Required for Claude Agent SDK demos
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Optional: for image generation demo
REPLICATE_API_TOKEN=your-replicate-token-here
```

## 📁 Course Structure

### Demo 00: Introduction to AI Agents
**Path**: `demos/00-intro-agents/`

**What it covers**: Foundational concepts of AI agents before diving into MCP.

**Key Files**:
- `intro-agents-cld.ipynb` - Jupyter notebook with agent architecture and patterns

**Learning Objectives**:
- Understand agent components (perception, reasoning, action)
- Learn agent decision-making patterns
- Grasp the difference between simple LLM calls and agentic systems

**Run it**:
```bash
cd demos/00-intro-agents
jupyter notebook intro-agents-cld.ipynb
```

---

### Demo 01: Introduction to MCP
**Path**: `demos/01-introduction-to-mcp/`

**What it covers**: MCP fundamentals, server implementation with FastMCP, and client interaction.

**Key Files**:
- `mcp_server.py` - Basic MCP server with time, math, and file tools
- `mcp_client.py` - Test client for server interaction
- `mcp_host.py` - Host/client integration example
- `walkthrough.md` - Step-by-step guide
- `documents.txt` - Sample data

**Learning Objectives**:
- Understand MCP architecture (client/server/host)
- Create tools with `@mcp.tool()` decorator
- Handle stdio transport communication
- Test servers with MCP Inspector

**Run it**:
```bash
cd demos/01-introduction-to-mcp

# Run the server
uv run mcp_server.py

# Or test interactively
mcp dev mcp_server.py
```

**★ Insight ─────────────────────────────────────**
MCP uses a client-server architecture where:
- **MCP Host**: Your AI application (coordinates everything)
- **MCP Client**: Maintains connection to a single server
- **MCP Server**: Provides tools, resources, and prompts

Think of it like a restaurant: the Host seats you, Clients take orders from specific tables, and Servers (kitchen stations) provide specific capabilities.
**─────────────────────────────────────────────────**

---

### Demo 02: MCP Chat Application Study Case
**Path**: `demos/02-study-case-anthropic-tools-resources-prompts-chat-app/`

**What it covers**: Complete chat application integrating **Claude tool use** with MCP capabilities.

**Key Files**:
- `chat_app.py` - Full-featured chat interface with Claude tool use
- `mcp_server.py` - MCP server with file operations
- `mcp_client.py` - MCP client wrapper for Anthropic integration
- `README.md` - Detailed documentation

**Learning Objectives**:
- Bridge Claude tool use with MCP tools
- Convert MCP schemas to Claude tool definitions
- Build production-ready chat applications with `@file` mentions
- Handle tool execution and multi-turn conversations

**Run it**:
```bash
cd demos/02-study-case-anthropic-tools-resources-prompts-chat-app

export ANTHROPIC_API_KEY="your-key"
uv run chat_app.py
```

**Example Interaction**:
```
You> Create a file called notes.md with "Hello MCP"
[Calling tool: write_doc...]
✅ File created successfully

You> What's in notes.md?
[Calling tool: read_doc...]
Content: Hello MCP
```

---

### Demo 03: Claude Agents SDK - Filesystem Agent
**Path**: `demos/03-claude-agents-sdk-filesystem-agent/`

**What it covers**: Building agents with the **Claude Agents SDK** using in-process MCP servers for filesystem operations.

**Key Files**:
- `file_reader_agent.py` - Complete file reader agent implementation
- `simple_claude_agent_files.py` - Simplified starter example
- `examples/` - Individual topic examples
  - `example_mcp_server.py` - MCP server setup patterns
  - `example_tool_permissions.py` - Permission callbacks and security
  - `example_response_handling.py` - Processing agent responses
  - `example_error_handling.py` - Error handling strategies
- `README.md` - Comprehensive learning guide

**Learning Objectives**:
- Create in-process MCP servers (no subprocess overhead)
- Implement tool permissions and security callbacks
- Handle streaming responses with async/await
- Use PreToolUse/PostToolUse hooks for validation
- Mix in-process and external MCP servers

**Run it**:
```bash
cd demos/03-claude-agents-sdk-filesystem-agent

export ANTHROPIC_API_KEY="your-key"

# Run the simplified example
uv run simple_claude_agent_files.py

# Run individual topic examples
uv run examples/example_mcp_server.py
uv run examples/example_tool_permissions.py

# Run complete file reader agent
uv run file_reader_agent.py
```

**★ Insight ─────────────────────────────────────**
**In-Process MCP** (Claude Agents SDK approach):
- Tools run directly in your Python process
- No subprocess management needed
- Better performance, simpler debugging
- Single deployment artifact

**External MCP** (Traditional approach):
- Separate server process via stdio/HTTP
- Language-agnostic server implementation
- Better isolation, can restart independently
**─────────────────────────────────────────────────**

---

### Demo 04: Query Tabular Data
**Path**: `demos/04-query-tabular-data/`

**What it covers**: MCP server for CSV/tabular data queries with the **Claude Agent SDK**.

**Key Files**:
- `csv_query_mcp_server.py` - MCP server with 7 CSV query tools
- `claude_agents_sdk_demo.py` - ⭐ **Recommended**: In-process tools with Claude SDK
- `claude_agents_csv_demo.ipynb` - Claude Agents SDK notebook demo
- `sample_data.csv` - Product database (15 products)

**Learning Objectives**:
- Create specialized MCP tools for data analysis
- Compare in-process vs external MCP patterns
- Use Claude SDK's `@tool` decorator
- Integrate AI with image generation APIs
- Handle complex multi-step queries

**Run it**:
```bash
cd demos/04-query-tabular-data

export ANTHROPIC_API_KEY="your-key"

# Claude Agents SDK approach (recommended)
uv run claude_agents_sdk_demo.py

# Or explore with Jupyter
jupyter notebook claude_agents_csv_demo.ipynb
```

**Available Tools**:
1. `get_all_products` - Browse entire catalog
2. `search_products_by_category` - Filter by category (Electronics, Furniture)
3. `search_products_by_price_range` - Find products in price range
4. `get_product_by_name` - Get specific product details
5. `get_top_rated_products` - Find highest-rated items
6. `get_products_in_stock` - Check inventory
7. `get_category_statistics` - Analytics and summaries

**Example Queries**:
```
"What electronics do we have?"
"Show me products between $50 and $150"
"What are the top 3 highest-rated products?"
"I need office equipment: keyboard (check ratings), furniture under $200"
```

---

### Demo 05: Link Health Checker Agent
**Path**: `demos/05-automations-agent/`

**What it covers**: An AI agent that audits markdown files for broken links using the **Claude Agent SDK** + a dedicated MCP server for link-checking operations.

**Key Files**:
- `link_checker_agent.py` - Claude Agent (CLI) that orchestrates the audit
- `link_checker_mcp_server.py` - MCP server with 4 link-checking tools
- `reports/` - Where audit reports are written

**Learning Objectives**:
- Connect Claude Agent SDK to an external MCP server via stdio
- Use MCP as a **capability boundary** (constrained, auditable tools)
- Build agents that compose multiple tools intelligently
- Generate structured reports from agentic workflows

**Architecture**:
```
User Request ("Audit all course links")
    ↓
Link Checker Agent (Claude Agent SDK)
    ↓ discovers files, deduplicates URLs, checks each
MCP Server (link-checker)
    - list_markdown_files(directory)
    - extract_links(filepath)
    - check_url(url)  ← HEAD request, returns status + latency
    - write_report(filename, content)
    ↓
reports/  (audit output)
```

**Run it**:
```bash
cd demos/05-automations-agent

export ANTHROPIC_API_KEY="your-key"
uv run link_checker_agent.py
```

**Example Queries**:
```
"Audit all course links"
"Check only the demos folder"
"Find broken links in the presentation"
```

---

### Demo 06: Data Analysis Agent — FastAPI + Claude Agent SDK + Vercel
**Path**: `demos/06-deploy-simple-agent-mcp-vercel/`

**What it covers**: A chat UI backed by the **Claude Agent SDK** with an **in-process MCP server** for data analysis, deployed to **Vercel serverless**. Ask questions about a synthetic Portuguese company dataset in plain English.

**Key Files**:
- `main.py` - FastAPI app + in-process MCP tools + Claude Agent SDK + SSE streaming
- `requirements.txt` - Python dependencies
- `vercel.json` - Vercel routing config
- `.env.example` - Environment variable template

**Learning Objectives**:
- Use **in-process MCP** (`create_sdk_mcp_server`) — no subprocess, tools run in same process
- Stream agent responses token-by-token via **Server-Sent Events**
- Deploy a Claude Agent SDK app to **Vercel serverless**
- Implement FastAPI as the HTTP layer for an agent endpoint

**Architecture**:
```
User → HTML/JS (SSE client)
           ↓  POST /chat
       FastAPI
           ↓
       Claude Agent SDK
           ↓
       In-process MCP server ("analysis")
           ↓  tools operate on pandas DataFrame
       Text  → SSE text events → rendered as markdown
       Plots → base64 PNG      → SSE image events → <img>
```

**Available Tools**:

| Tool | What it does |
|---|---|
| `describe_data` | pandas `.describe()` summary stats |
| `show_head` | First N rows as a markdown table |
| `column_info` | Dtypes, non-null counts, unique values |
| `group_aggregate` | GroupBy + aggregate (mean/sum/count/etc.) |
| `correlation_matrix` | Heatmap + numeric correlation table |
| `plot_data` | bar, line, scatter, hist, or box plot |

**Run it**:
```bash
cd demos/06-deploy-simple-agent-mcp-vercel

cp .env.example .env
# Add ANTHROPIC_API_KEY to .env

uv run main.py
# Open http://localhost:8000
```

**Deploy to Vercel**:
```bash
npm install -g vercel
vercel login
vercel link
vercel env add ANTHROPIC_API_KEY production --value YOUR_KEY_HERE --yes
vercel --prod
```

**Example Queries**:
```
"Describe the dataset"
"What is the average EBITDA by sector?"
"Plot a histogram of revenue"
"Which region has the highest average revenue?"
"Show the correlation matrix"
```

**★ Insight ─────────────────────────────────────**
**In-Process MCP** (the pattern used here):
- MCP tools run directly in your Python process — no subprocess
- `create_sdk_mcp_server` wires Claude Agent SDK tools as an MCP server
- Vercel's hobby plan has a 10s timeout — cold starts may hit it; Pro plan gives 60s
**─────────────────────────────────────────────────**

---

### Demo 07: Hacks, Tips, Tools & Workflows
**Path**: `demos/07-hacks-tips-tools-workflows/`

**What it covers**: Curated collection of **practical tips, tools, and workflow patterns** demonstrated live during the training session.

**Key Files**:
- `mcp-builder-skill/` - Claude skill for building MCP servers
  - `SKILL.md` - Skill definition and usage guide
  - `reference/` - Reference implementations
  - `scripts/` - Helper scripts

**Learning Objectives**:
- Discover useful MCP ecosystem tools and integrations
- Learn workflow shortcuts for MCP development
- Use Claude skills to accelerate MCP server creation
- Explore tips and tricks shared during live sessions

---

### Assets & Resources
**Path**: `demos/assets-resources/`

**What it contains**: Reference materials, diagrams, and cheatsheets used throughout the course.

**Key Files**:
- `MCP_TECHNICAL_CHEATSHEET.md` - Quick reference for MCP concepts and patterns
- `mcp_server_prompt_templates.md` - Prompt templates for building MCP servers
- `mcp_security_report.pdf` - Security analysis and best practices
- `diagram.excalidraw` - Editable architecture diagrams
- `mcp-course.md` - Comprehensive course reference document
- Various `.png` files - Architecture diagrams, agent loops, market maps

---

## 🎨 Architecture Patterns

### Pattern 1: In-Process MCP Tools (Claude Agent SDK)

**Used in**: Demos 03, 04, 05, 06

```python
import asyncio
from claude_agent_sdk import Agent, create_sdk_mcp_server, tool

@tool
async def query_data(query: str) -> str:
    """Query the database"""
    return execute_query(query)

server = create_sdk_mcp_server(
    name="data-tools",
    tools=[query_data]
)

agent = Agent(
    name="assistant",
    instructions="You help query data",
    mcp_servers=[server],
    model="claude-sonnet-4-5"
)

asyncio.run(agent.run("Find top products"))
```

**Pros**: Fast, no subprocess, easy debugging, single deployment artifact
**Cons**: All in one process, Python-only

---

### Pattern 2: External MCP Server (Traditional)

**Used in**: Demos 01, 02, 05

```python
# Server (FastMCP) — runs as a separate process
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("tool-server")

@mcp.tool()
def process_data(input: str) -> str:
    return f"Processed: {input}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

```python
# Agent connects to server via subprocess
import asyncio
from claude_agent_sdk import Agent, MCPServerStdio

server = MCPServerStdio(command="uv", args=["run", "server.py"])

agent = Agent(
    name="assistant",
    instructions="You have data tools",
    mcp_servers=[server]
)

asyncio.run(agent.run("Process this input"))
```

**Pros**: Language-agnostic, isolated, restartable independently
**Cons**: Subprocess overhead, more complex deployment

---

### Pattern 3: FastAPI + SSE Streaming (Serverless)

**Used in**: Demo 06

```python
# FastAPI wraps the agent and streams responses via SSE
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from claude_agent_sdk import Agent, create_sdk_mcp_server

app = FastAPI()
agent = Agent(name="assistant", mcp_servers=[...])

@app.post("/chat")
async def chat(request: ChatRequest):
    async def stream():
        async for event in agent.stream(request.message):
            yield f"data: {event.json()}\n\n"
    return StreamingResponse(stream(), media_type="text/event-stream")
```

**Pros**: Serverless-friendly, real-time streaming, scalable
**Cons**: Vercel hobby plan 10s timeout can hit cold starts

---

## 🛠️ Development Tools

### MCP Inspector

Interactively test any MCP server:

```bash
# Run inspector on your server
mcp dev path/to/your_server.py

# Opens web UI at http://localhost:5173
# - List available tools
# - Test tool calls with parameters
# - View resources and prompts
# - See full request/response logs
```

### Claude Desktop Integration

Configure MCP servers in Claude Desktop:

**macOS/Linux**: `~/.config/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "csv-query": {
      "command": "uv",
      "args": ["run", "/absolute/path/to/csv_query_mcp_server.py"]
    },
    "automation-tools": {
      "command": "uv",
      "args": ["run", "/absolute/path/to/automation_mcp_server.py"]
    }
  }
}
```

**After adding**, restart Claude Desktop. Tools appear in the tool selector.

### Makefile Commands

Automate common tasks:

```bash
make conda-create     # Create conda environment
make env-setup        # Setup with pip-tools and UV
make notebook-setup   # Install Jupyter kernel
make env-update       # Update dependencies
make freeze           # Freeze current dependencies
make clean            # Remove environments
```

---

## 🪟 Windows Setup Guide

### Prerequisites

- **Windows 10/11** with Developer Mode enabled
- **Python 3.10+** from [python.org](https://www.python.org/downloads/)
- **Node.js 18+** from [nodejs.org](https://nodejs.org/)
- **Git for Windows** from [git-scm.com](https://git-scm.com/)

### Enable Developer Mode

1. **Settings** → **Update & Security** → **For developers**
2. Select **Developer mode**
3. Restart computer

### PowerShell Execution Policy

Open PowerShell as Administrator:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Setup

```cmd
# Clone repository
git clone https://github.com/EnkrateiaLucca/mcp-course.git
cd mcp-course

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements/requirements.txt
```

### Environment Variables

Create `.env` file:

```env
ANTHROPIC_API_KEY=your-key
# Use forward slashes in paths
MCP_DEMO_PATH=C:/path/to/files
```

Or set in Command Prompt:
```cmd
set ANTHROPIC_API_KEY=your-key
```

Or PowerShell:
```powershell
$env:ANTHROPIC_API_KEY="your-key"
```

### Claude Desktop Config (Windows)

Location: `%APPDATA%\Claude\claude_desktop_config.json`

```cmd
cd %APPDATA%\Claude
notepad claude_desktop_config.json
```

**Use absolute paths with forward slashes**:

```json
{
  "mcpServers": {
    "demo": {
      "command": "C:/path/to/venv/Scripts/python.exe",
      "args": ["C:/path/to/mcp_server.py"]
    }
  }
}
```

### Windows Command Reference

| Linux/macOS | Windows (CMD) | Windows (PowerShell) |
|-------------|---------------|----------------------|
| `source venv/bin/activate` | `venv\Scripts\activate` | `venv\Scripts\Activate.ps1` |
| `export VAR=value` | `set VAR=value` | `$env:VAR="value"` |
| `~/.config/Claude/` | `%APPDATA%\Claude\` | `$env:APPDATA\Claude\` |
| `python3` | `python` | `python` |

### Common Windows Issues

**"python not found"**
- Reinstall Python with "Add to PATH" checked

**PowerShell script errors**
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

**Long path issues**
- Enable in Group Policy: `gpedit.msc` → Computer Configuration → Administrative Templates → System → Filesystem → Enable Win32 long paths

---

## 🐛 Troubleshooting

### "Module not found" errors

```bash
# With UV
uv pip install mcp model-context-protocol

# With pip
pip install mcp model-context-protocol
```

### API Key Issues

```bash
export ANTHROPIC_API_KEY="your-key"
# Or add to .env file
```

### Claude Desktop Not Recognizing Servers

1. ✅ Use **absolute paths** in config
2. ✅ Verify UV is in PATH: `which uv`
3. ✅ Test server independently: `uv run mcp_server.py`
4. ✅ Check server logs for errors
5. ✅ **Restart Claude Desktop** after config changes

### Permission Denied

```bash
chmod +x script.py
```

### MCP Server Connection Issues

**Test independently**:
```bash
mcp dev path/to/server.py
```

**Check if running**:
```bash
ps aux | grep mcp_server  # Linux/macOS
tasklist | findstr python  # Windows
```

### Rate Limiting

- Check API quota in your provider dashboard
- Implement exponential backoff
- Add request delays in loops
- Use cheaper models for testing (claude-haiku)

---

## 📖 Learning Resources

### Official Documentation

- **MCP Specification**: https://modelcontextprotocol.io/specification/
- **MCP Introduction**: https://modelcontextprotocol.io/introduction
- **FastMCP SDK**: https://github.com/modelcontextprotocol/python-sdk
- **Claude Agent SDK**: https://github.com/anthropics/claude-agent-sdk-python

### Community Resources

- **Awesome MCP Servers**: https://github.com/punkpeye/awesome-mcp-servers
- **Glama MCP Directory**: https://glama.ai/mcp
- **MCP Community Examples**: https://github.com/esxr/langgraph-mcp

### Course Materials

- `presentation/presentation.html` - Interactive HTML course slides
- `presentation/presentation-mcp-updated.pdf` - PDF version of slides
- `demos/assets-resources/MCP_TECHNICAL_CHEATSHEET.md` - Quick reference cheatsheet
- `CLAUDE.md` - Project development guidelines

---

## 🎓 Course Instructor

**Lucas Soares**

📚 [Blog](https://enkrateialucca.github.io/lucas-landing-page/)
🔗 [LinkedIn](https://www.linkedin.com/in/lucas-soares-969044167/)
🐦 [Twitter/X](https://x.com/LucasEnkrateia)
📺 [YouTube - Automata Learning Lab](https://www.youtube.com/@automatalearninglab)
📧 lucasenkrateia@gmail.com

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes with clear commits
4. Test thoroughly across demos
5. Submit a pull request

---

## 📝 License

This course material is provided for educational purposes as part of the O'Reilly Live Training series.

---

## 🚀 Next Steps

1. ✅ **Start with Demo 00** - Understand AI agent fundamentals
2. ✅ **Build MCP basics** (Demo 01) - Create your first server
3. ✅ **Build a chat app** (Demo 02) - Connect Claude tool use with MCP
4. ✅ **Master the Claude Agents SDK** (Demos 03, 04, 05) - In-process tools, data queries, automation
5. ✅ **Deploy to production** (Demo 06) - Data analysis agent on Vercel serverless
6. ✅ **Level up** (Demo 07) - Explore hacks, tips, and workflow tools
7. ✅ **Build your own** - Create custom MCP servers for your use cases

---

**The Model Context Protocol is revolutionizing how AI agents connect to the world. This course gives you the practical skills to build with it today.**

**Happy building! 🎉**
