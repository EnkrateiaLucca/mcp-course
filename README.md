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

This hands-on course takes you from MCP fundamentals to production deployment through 7 comprehensive demos:

### What You'll Learn

- ✅ **MCP Fundamentals**: Architecture, protocol concepts, and tool/resource patterns
- ✅ **Building MCP Servers**: Using FastMCP to create custom tool providers
- ✅ **Claude Agents SDK**: Building production-grade agents with in-process MCP
- ✅ **OpenAI Integration**: Bridging MCP with OpenAI's function calling
- ✅ **Real-World Applications**: Chat apps, data queries, automation, and deployment
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
# Required for Claude Agents SDK demos
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Required for OpenAI demos
OPENAI_API_KEY=your-openai-api-key-here

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
- `mcp_server.py` - Basic MCP server with document tools
- `mcp_client.py` - Test client for server interaction
- `intro-mcp-walkthrough.md` - Step-by-step guide
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

**What it covers**: Complete chat application integrating **OpenAI function calling** with MCP capabilities.

**Key Files**:
- `chat_app.py` - Full-featured chat interface with tool usage
- `mcp_server.py` - MCP server with file operations
- `mcp_client.py` - MCP client wrapper for OpenAI integration
- `README.md` - Detailed documentation

**Learning Objectives**:
- Bridge OpenAI function calling with MCP tools
- Convert MCP schemas to OpenAI function definitions
- Build production-ready chat applications
- Handle tool execution and response streaming

**Run it**:
```bash
cd demos/02-study-case-anthropic-tools-resources-prompts-chat-app

export OPENAI_API_KEY="your-key"
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
- `examples/` - Individual topic examples
  - `example_mcp_server.py` - MCP server setup patterns
  - `example_tool_permissions.py` - Permission callbacks and security
  - `example_response_handling.py` - Processing agent responses
  - `example_error_handling.py` - Error handling strategies
- `scripts/file_reader_agent.py` - Complete file reader implementation
- `README.md` - Comprehensive learning guide
- `COURSE_SUMMARY.md` - Architecture deep dive

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

# Run individual examples
uv run examples/example_mcp_server.py
uv run examples/example_tool_permissions.py

# Run complete file reader agent
uv run scripts/file_reader_agent.py
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

**What it covers**: MCP server for CSV/tabular data queries with both **Claude and OpenAI** agent implementations.

**Key Files**:
- `csv_query_mcp_server.py` - MCP server with 7 CSV query tools
- `claude_agents_sdk_demo.py` - ⭐ **Recommended**: In-process tools with Claude SDK
- `openai_mcp_csv_demo.ipynb` - OpenAI Agents SDK approach (notebook)
- `replicate_thumbnail_mcp.py` - Image generation with Replicate
- `sample_data.csv` - Product database (15 products)
- `README_CLAUDE_AGENTS_SDK.md` - Claude SDK documentation
- `CLAUDE_SDK_EXPLANATION.md` - Architecture deep dive

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
jupyter notebook openai_mcp_csv_demo.ipynb

# Configure Claude Desktop for image generation
cat thumbnail_mcp.json  # Copy to Claude Desktop config
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

### Demo 05: Automation Agent
**Path**: `demos/05-automations-agent/`

**What it covers**: Intelligent automation script generator using **Claude Agents SDK** + MCP database integration.

**Key Files**:
- `automation_agent.py` - Claude Agent that generates scripts
- `automation_mcp_server.py` - MCP server with database query tools
- `automations_database.csv` - 7 pre-built automation templates
- `generated_scripts/` - Output directory (created at runtime)
- `README.md` - Complete architecture guide
- `QUICKSTART.md` - Quick reference
- `DEMO_OUTPUT.md` - Example session outputs

**Learning Objectives**:
- Combine MCP data tools with built-in filesystem tools
- Build multi-step agent workflows
- Query structured data (CSV) via MCP
- Generate executable scripts programmatically
- Implement permission-restricted file operations

**Architecture**:
```
User Request
    ↓
Automation Agent (Claude SDK)
    ↓
MCP Server (data queries) + Built-in Tools (Write, Bash, Glob)
    ↓
Automation Database (CSV)
    ↓
Generated Scripts (output)
```

**Run it**:
```bash
cd demos/05-automations-agent

export ANTHROPIC_API_KEY="your-key"
uv run automation_agent.py
```

**Example Workflow**:
```
You: What automations are available?
Agent: [Lists 7 automations: backup_files, clean_temp_files, etc.]

You: Generate the file backup automation
Agent: [Creates backup_files.sh with full template]
      ✅ Created: generated_scripts/backup_files.sh
      ✅ Made executable with chmod +x

Usage: ./backup_files.sh /source/path /backup/destination
```

**Available Automations**:
- **File Management**: backup_files, organize_downloads
- **System Maintenance**: clean_temp_files, monitor_disk_space
- **Database Operations**: backup_database
- **Version Control**: auto_commit_changes
- **Reporting**: generate_report

---

### Demo 06: Deploy to Vercel (Serverless)
**Path**: `demos/06-deploy-simple-agent-mcp-vercel/`

**What it covers**: Production deployment of AI agents with MCP to **Vercel serverless** platform. Includes **two complete implementations**:

1. **OpenAI Agents SDK** (Stateless) - `main.py`
2. **Claude Agents SDK** (Sandboxed) - `main_claude.py`

**Key Files**:
- `main.py` - OpenAI Agents SDK implementation
- `main_claude.py` - Claude Agents SDK with sandbox
- `claude_agent_sandbox.py` - Agent code for sandbox execution
- `mcp_fetch_server.py` - MCP server with HTTP transport (FastMCP)
- `static/index.html` - Beautiful chat interface
- `requirements.txt` / `requirements_claude.txt` - Dependencies
- `vercel.json` - Vercel configuration
- `deployment_agents_sdk_vercel.md` - OpenAI deployment guide
- `deployment_claude_agents_sdk_vercel.md` - Claude deployment guide
- `README.md` - Overview and comparison

**Learning Objectives**:
- Deploy MCP servers with HTTP transport (not just stdio)
- Use `MCPServerStreamableHttp` from OpenAI Agents SDK
- Build with official MCP Python SDK (`mcp[cli]`)
- Compare stateless vs sandboxed architectures
- Implement production security patterns
- Create FastAPI wrappers for agent endpoints
- Deploy to serverless platforms

**Architecture Comparison**:

| Feature | OpenAI (main.py) | Claude (main_claude.py) |
|---------|------------------|-------------------------|
| Model | Stateless serverless | Sandboxed containers |
| Complexity | Low ⭐ | Medium ⭐⭐⭐ |
| File Operations | Limited | Full (sandboxed) |
| Command Execution | No | Yes (in sandbox) |
| Best For | Chat apps | Complex agents |
| Cost | API only | API + sandbox compute |

**Run Locally (OpenAI)**:
```bash
cd demos/06-deploy-simple-agent-mcp-vercel

cp .env.example .env
# Add OPENAI_API_KEY to .env

# Terminal 1: MCP Server
python mcp_fetch_server.py

# Terminal 2: Main App
python main.py

# Open http://localhost:8000
```

**Run Locally (Claude)**:
```bash
export ANTHROPIC_API_KEY="your-key"
python main_claude.py
```

**Deploy to Vercel**:
```bash
# Install Vercel CLI
npm install -g vercel

# Login and configure
vercel login
vercel env add OPENAI_API_KEY  # or ANTHROPIC_API_KEY

# Deploy
vercel --prod
```

**Example Queries**:
```
"Fetch content from https://modelcontextprotocol.io"
"What's the latest on the OpenAI blog?"
"Read https://github.com/anthropics/claude-agent-sdk-python and summarize"
```

**★ Insight ─────────────────────────────────────**
**MCP HTTP Transport** (New in this demo):
- MCP traditionally uses stdio (standard input/output)
- HTTP transport enables serverless deployment
- FastMCP supports both stdio and HTTP via `transport="sse"`
- OpenAI SDK uses `MCPServerStreamableHttp` to connect
**─────────────────────────────────────────────────**

---

## 🎨 Architecture Patterns

### Pattern 1: In-Process MCP Tools (Claude Agents SDK)

**Used in**: Demos 03, 04, 05

```python
from agents import tool
from agents.extensions.mcp import create_sdk_mcp_server

@tool("query_data", "Query the database", {"query": str})
async def query_data(args: dict) -> dict:
    result = execute_query(args["query"])
    return {"content": [{"type": "text", "text": result}]}

# Create in-process MCP server
server = create_sdk_mcp_server(
    name="data-tools",
    version="1.0.0",
    tools=[query_data]
)

# Agent has direct access
agent = Agent(
    name="assistant",
    instructions="You help query data",
    mcp_servers={"data": server},
    model="claude-sonnet-4-5-20250929"
)
```

**Pros**: Fast, simple deployment, easy debugging
**Cons**: All in one process, Python-only

---

### Pattern 2: External MCP Server (Traditional)

**Used in**: Demos 01, 02, 04 (OpenAI version)

```python
# Server (FastMCP)
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("tool-server")

@mcp.tool()
def process_data(input: str) -> str:
    return f"Processed: {input}"

if __name__ == "__main__":
    mcp.run(transport="stdio")

# Client connects via subprocess
from agents.mcp import MCPServerConfig

config = MCPServerConfig(
    command="uv",
    args=["run", "server.py"]
)

agent = Agent(mcp_servers=[config])
```

**Pros**: Language-agnostic, isolated, restartable
**Cons**: Subprocess overhead, more complex deployment

---

### Pattern 3: HTTP Transport (Serverless)

**Used in**: Demo 06

```python
# Server with HTTP transport
mcp = FastMCP("web-tools")

@mcp.tool()
def fetch_url(url: str) -> str:
    return httpx.get(url).text

if __name__ == "__main__":
    mcp.run(transport="sse")  # Server-Sent Events transport

# Client via HTTP
from agents_mcp import MCPServerStreamableHttp

agent = Agent(
    mcp_servers=[
        MCPServerStreamableHttp(
            name="web",
            url="http://localhost:8001/sse"
        )
    ]
)
```

**Pros**: Serverless-friendly, scalable, network-accessible
**Cons**: Network latency, requires HTTP infrastructure

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
OPENAI_API_KEY=your-key
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

**Claude SDK**:
```bash
export ANTHROPIC_API_KEY="your-key"
# Or add to .env file
```

**OpenAI**:
```bash
export OPENAI_API_KEY="your-key"
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
- Use cheaper models for testing (gpt-4o-mini, claude-haiku)

---

## 📖 Learning Resources

### Official Documentation

- **MCP Specification**: https://modelcontextprotocol.io/specification/
- **MCP Introduction**: https://modelcontextprotocol.io/introduction
- **FastMCP SDK**: https://github.com/modelcontextprotocol/python-sdk
- **Claude Agents SDK**: https://github.com/anthropics/claude-agent-sdk-python
- **OpenAI Agents SDK**: https://openai.github.io/openai-agents-python/

### Community Resources

- **Awesome MCP Servers**: https://github.com/punkpeye/awesome-mcp-servers
- **Glama MCP Directory**: https://glama.ai/mcp
- **MCP Community Examples**: https://github.com/esxr/langgraph-mcp

### Course Materials

- `presentation/presentation.html` - Full course slides
- `presentation/mcp-talk.pdf` - PDF version
- `how-mcp-works-with-claude.md` - Integration guide
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
3. ✅ **Choose your SDK**:
   - **Claude Agents SDK** (Demos 03, 04, 05) - In-process, fast, Python-native
   - **OpenAI Agents SDK** (Demos 02, 06) - Stateless, simple, widely compatible
4. ✅ **Deploy to production** (Demo 06) - Vercel serverless deployment
5. ✅ **Build your own** - Create custom MCP servers for your use cases

---

**The Model Context Protocol is revolutionizing how AI agents connect to the world. This course gives you the practical skills to build with it today.**

**Happy building! 🎉**
