# MCP Course Walkthrough for Beginners

Welcome! This guide will walk you through everything you need to know to follow and understand this O'Reilly Live Training course on building AI agents with the Model Context Protocol (MCP).

## Table of Contents

1. [Quick Reference - Essential Links](#quick-reference---essential-links)
2. [Core Concepts](#core-concepts)
3. [Prerequisites](#prerequisites)
4. [Technical Setup](#technical-setup)
5. [Understanding the Repository Structure](#understanding-the-repository-structure)
6. [Running Your First Demo](#running-your-first-demo)
7. [Learning Path](#learning-path)
8. [Troubleshooting](#troubleshooting)

---

## Quick Reference - Essential Links

🚀 **Get Started Fast:**

| Resource            | URL                                                                  | Purpose                    |
| ------------------- | -------------------------------------------------------------------- | -------------------------- |
| **Python**          | [python.org/downloads](https://www.python.org/downloads/)            | Install Python 3.9+        |
| **UV Package Manager** | [docs.astral.sh/uv](https://docs.astral.sh/uv/)                   | Modern Python package manager |
| **Git**             | [git-scm.com](https://git-scm.com/)                                  | Version control            |
| **VS Code**         | [code.visualstudio.com](https://code.visualstudio.com/)              | Recommended editor         |
| **Claude Desktop**  | [claude.ai/download](https://claude.ai/download)                     | Test MCP servers           |
| **OpenAI API Keys** | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) | Get API access             |
| **Replicate API**   | [replicate.com](https://replicate.com)                               | Image generation API       |

📚 **Core Documentation:**

| Resource              | URL                                                                                             | Purpose               |
| --------------------- | ----------------------------------------------------------------------------------------------- | --------------------- |
| **MCP Specification** | [spec.modelcontextprotocol.io](https://spec.modelcontextprotocol.io/)                           | Protocol details      |
| **MCP Docs**          | [modelcontextprotocol.io](https://modelcontextprotocol.io/)                                     | Getting started       |
| **MCP Python SDK**    | [github.com/modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk) | Python implementation |
| **MCP Inspector**     | [github.com/modelcontextprotocol/inspector](https://github.com/modelcontextprotocol/inspector)   | Testing tool          |
| **Claude Agent SDK**  | [github.com/anthropics/claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python) | Build Claude agents   |
| **OpenAI Agents SDK** | [openai.github.io/openai-agents-python](https://openai.github.io/openai-agents-python/)         | Build OpenAI agents   |
| **FastMCP**           | [github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp)                                  | Quick MCP servers     |

🎓 **Advanced Learning:**

| Resource                      | URL                                                                                                                                                                   | Purpose                  |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------ |
| **Code Execution with MCP**   | [anthropic.com/engineering/code-execution-with-mcp](https://www.anthropic.com/engineering/code-execution-with-mcp)                                                    | Engineering deep dive    |
| **MCP + Claude Integration**  | [platform.claude.com/docs/.../mcp-integration](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool#mcp-integration)                       | Claude API integration   |
| **Context Rot Research**      | [research.trychroma.com/context-rot](https://research.trychroma.com/context-rot)                                                                                     | AI context best practices |
| **OpenAI Function Calling**   | [platform.openai.com/docs/guides/function-calling](https://platform.openai.com/docs/guides/function-calling)                                                         | Tool use patterns        |
| **FastAPI Docs**              | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)                                                                                                                | API framework            |
| **Vercel Docs**               | [vercel.com/docs](https://vercel.com/docs)                                                                                                                            | Deployment platform      |

---

## Core Concepts

### What is an AI Agent?
An **AI agent** is a program that uses a Large Language Model (LLM) like GPT-4 or Claude to:
- Understand natural language requests
- Make decisions about what actions to take
- Use tools to accomplish tasks
- Return results to the user

Think of it as giving an AI the ability to "do things" rather than just "say things."

**Example**: Instead of just telling you how to check the weather, an AI agent can actually call a weather API and give you the current temperature.

### What is MCP (Model Context Protocol)?
**MCP** is like a universal adapter for AI agents. It's a standardized way to:
- **Expose tools** that AI agents can use (like file operations, API calls, database queries)
- **Provide resources** that agents can access (like documents, data sources)
- **Connect different systems** without writing custom integration code each time

**Analogy**: If AI agents are smartphones, MCP is like the USB-C standard - one protocol that works with many different devices and accessories.

📚 **Official MCP Resources:**

- [MCP Specification](https://spec.modelcontextprotocol.io/) - Complete protocol documentation
- [MCP Documentation](https://modelcontextprotocol.io/) - Getting started guides
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - Official Python implementation
- [MCP Integration with Claude](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool#mcp-integration) - Using MCP with Claude API
- [Code Execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) - Anthropic's engineering blog on MCP code execution

### Key MCP Components

#### 1. MCP Server
A program that **provides** tools and resources. For example:
- A filesystem MCP server provides tools to read/write files
- A database MCP server provides tools to query data
- A weather MCP server provides tools to fetch weather data

#### 2. MCP Client
A program that **uses** the tools and resources from MCP servers. Usually integrated with an AI agent.

#### 3. Tools
Functions that the AI agent can call. Each tool has:
- **Name**: What it's called
- **Description**: What it does (the AI reads this!)
- **Parameters**: What inputs it needs
- **Return value**: What it gives back

#### 4. Resources
Data sources the AI can read from (like files, URLs, database tables).

#### 5. Transport
How the client and server communicate:
- **stdio**: Standard input/output (for local, same-machine communication)
- **SSE**: Server-Sent Events (for streaming data)
- **HTTP**: Web-based communication (for production deployments)

---

## Prerequisites

### Required Knowledge
- **Basic Python**: variables, functions, classes
- **Command line basics**: running commands, navigating directories
- **JSON**: understanding basic data structures
- **APIs**: basic understanding of how APIs work (optional but helpful)

### Required Software
1. **Python 3.9 or higher**
   ```bash
   python --version  # Should show 3.9+
   ```

   📥 Download: [python.org/downloads](https://www.python.org/downloads/)

2. **UV Package Manager** (recommended)
   ```bash
   # Install UV (macOS/Linux)
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install UV (Windows)
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

   # Verify installation
   uv --version
   ```

   📚 Documentation: [docs.astral.sh/uv](https://docs.astral.sh/uv/)

3. **Git**
   ```bash
   git --version  # Should show git version
   ```

   📥 Download: [git-scm.com](https://git-scm.com/)

4. **Text Editor or IDE**
   - [VS Code](https://code.visualstudio.com/) (recommended)
   - [PyCharm](https://www.jetbrains.com/pycharm/)
   - Any text editor you're comfortable with

### Optional Software

- **Claude Desktop**: For testing MCP servers interactively
  - 📥 Download: [claude.ai/download](https://claude.ai/download)
  - 📚 MCP Integration Guide: [modelcontextprotocol.io/quickstart](https://modelcontextprotocol.io/quickstart)
- **Node.js**: For some frontend demos and MCP Inspector
  - 📥 Download: [nodejs.org](https://nodejs.org/)

---

## Technical Setup

### Step 1: Clone the Repository
```bash
# Navigate to where you want to store the course
cd ~/Desktop/projects

# Clone the repository
git clone <repository-url>
cd mcp-course
```

### Step 2: Set Up Environment Variables

Create a file called `.env` in the root directory of the project:

```bash
# Create .env file
touch .env
```

Open `.env` in your text editor and add your API keys:

```env
# OpenAI API Key (required for most demos)
OPENAI_API_KEY=sk-your-key-here

# Replicate API Token (required for image generation demos)
REPLICATE_API_TOKEN=r8_your-token-here
```

**How to get API keys:**

- **OpenAI**:
  - 🔑 Sign up: [platform.openai.com/signup](https://platform.openai.com/signup)
  - 📚 API Keys Guide: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
  - 💰 Pricing: [openai.com/api/pricing](https://openai.com/api/pricing/)
- **Replicate**:
  - 🔑 Sign up: [replicate.com](https://replicate.com)
  - 📚 Get API Token: Account settings → API tokens
  - 💰 Pricing: [replicate.com/pricing](https://replicate.com/pricing)

⚠️ **Important**: Never commit `.env` to git. It's already in `.gitignore` to prevent this.

### Step 3: Understand UV (Recommended Approach)

This course uses **UV** for dependency management. Here's why it's great:

**Traditional approach** (the old way):
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate
# Install dependencies
pip install -r requirements.txt
# Run script
python script.py
```

**UV approach** (the new way):
```bash
# Just run the script - UV handles everything!
uv run script.py
```

UV automatically:
- Creates isolated environments
- Installs dependencies listed in the script
- Runs the script
- Cleans up when done

**How UV works with our scripts:**

Every script in this course has a special header:
```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["mcp[cli]>=1.0.0", "fastmcp"]
# ///
```

This tells UV what Python version and packages the script needs.

### Step 4: Alternative Setup (Without UV)

If you prefer the traditional approach:

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements/requirements.txt
```

Now you can run scripts with regular `python`:
```bash
python demos/01-introduction-to-mcp/mcp_server.py
```

---

## Understanding the Repository Structure

```
mcp-course/
├── demos/                          # All hands-on demos (numbered sequentially)
│   ├── 00-intro-agents/           # Agent fundamentals
│   ├── 01-introduction-to-mcp/    # Your first MCP server
│   ├── 02-study-case-*/           # Full chat application
│   ├── 03-claude-agents-sdk-*/    # Claude SDK examples
│   ├── 04-query-tabular-data/     # Working with CSV data
│   ├── 05-deployment-example/     # Production deployment
│   └── 06-deploy-simple-*/        # Serverless deployment
├── requirements/                   # Python dependencies
│   ├── requirements.in            # Source requirements
│   └── requirements.txt           # Generated dependencies
├── presentation/                   # Course slides and materials
├── .env                           # Your API keys (create this!)
├── CLAUDE.md                      # Project guidelines
├── Makefile                       # Setup automation
└── README.md                      # Project overview
```

### Key Files to Know

- **`demos/`**: All the example code you'll run and learn from
- **`.env`**: Your API keys (you create this)
- **`requirements/requirements.txt`**: All the Python packages needed
- **`CLAUDE.md`**: Technical documentation (useful reference)

---

## Running Your First Demo

Let's run the simplest MCP server to verify everything works!

### Demo 1: Basic MCP Server

Navigate to the first demo:
```bash
cd demos/01-introduction-to-mcp
```

#### Option A: Using UV (Recommended)
```bash
uv run mcp_server.py
```

#### Option B: Using Python
```bash
# Make sure your virtual environment is activated
python mcp_server.py
```

**What you should see:**
The server will start and wait for input. It's now running as an MCP server!

**Press `Ctrl+C`** to stop the server.

### Understanding What Just Happened

When you ran `mcp_server.py`:
1. The server started listening on **stdio** (standard input/output)
2. It registered **tools** (functions an AI can call)
3. It registered **resources** (data the AI can access)
4. It's now waiting for MCP client connections

**But wait - how do we actually use it?**

Good question! An MCP server by itself just sits there. You need a **client** (like an AI agent) to connect to it and use its tools.

### Testing with MCP Inspector

The **MCP Inspector** is a web-based tool for testing MCP servers:

```bash
# Install MCP Inspector (one-time)
npm install -g @modelcontextprotocol/inspector

# Or use with npx (no install needed)
npx @modelcontextprotocol/inspector demos/01-introduction-to-mcp/mcp_server.py
```

📚 **MCP Inspector Documentation**: [github.com/modelcontextprotocol/inspector](https://github.com/modelcontextprotocol/inspector)

This will:
1. Open a web browser
2. Show all the tools your server provides
3. Let you test them interactively

**Try it!** Click on a tool, fill in parameters, and click "Run" to see what happens.

---

## Learning Path

Follow the demos in order - each builds on concepts from the previous one:

### Week 1: Foundations

#### Demo 0: Agent Fundamentals (`00-intro-agents/`)
**What you'll learn:**
- What makes a program an "agent"
- How agents make decisions
- The agent loop: think → act → observe → repeat

**Time**: 30-60 minutes

**Action**: Read the code and documentation in this folder.

#### Demo 1: Your First MCP Server (`01-introduction-to-mcp/`)
**What you'll learn:**
- How to create an MCP server with FastMCP
- How to define tools with `@mcp.tool()` decorator
- How to define resources with `@mcp.resource()` decorator
- Testing with MCP Inspector

**Time**: 1-2 hours

**Action**:
1. Run the server
2. Test it with MCP Inspector
3. Try modifying a tool's description
4. Add a new simple tool (like "add two numbers")

### Week 2: Integration

#### Demo 2: Chat Application (`02-study-case-*/`)
**What you'll learn:**
- Connecting MCP servers to AI agents (OpenAI)
- Building a complete chat application
- Function calling / tool use in practice
- Frontend integration

**Time**: 2-3 hours

📚 **Related Documentation:**

- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)

**Action**:
1. Run the chat application
2. Interact with it through the web interface
3. Watch how the AI decides when to use tools
4. Examine how MCP tools are converted to OpenAI function schemas

#### Demo 3: Claude Agent SDK (`03-claude-agents-sdk-*/`)
**What you'll learn:**
- Using Claude's official Agent SDK
- Filesystem operations via MCP
- Permission callbacks and security
- Streaming responses

**Time**: 2-3 hours

📚 **Related Documentation:**

- [Claude Agent SDK Documentation](https://github.com/anthropics/claude-agent-sdk-python)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Claude API Guide](https://docs.anthropic.com/en/api/getting-started)

**Action**:
1. Run the filesystem agent
2. Ask it to read/write files
3. See how permission callbacks work
4. Compare with OpenAI approach from Demo 2

### Week 3: Real-World Applications

#### Demo 4: Data Querying (`04-query-tabular-data/`)
**What you'll learn:**
- Working with CSV/tabular data
- Building domain-specific tools
- Integrating multiple services (data + image generation)
- Error handling in tools

**Time**: 2-3 hours

**Action**:
1. Load the sample CSV data
2. Query it using natural language
3. Generate images based on data
4. Try with your own CSV files

#### Demo 5: Production Deployment (`05-deployment-example/`)
**What you'll learn:**
- FastAPI wrapper for agents
- Production architecture patterns
- API design for agent systems
- Testing and validation

**Time**: 3-4 hours

**Action**:
1. Run the FastAPI server
2. Test with the provided test scripts
3. Examine the API endpoints
4. Understand the deployment architecture

#### Demo 6: Serverless Deployment (`06-deploy-simple-*/`)
**What you'll learn:**
- Deploying to Vercel
- HTTP transport for MCP
- Serverless architecture considerations
- Production MCP patterns

**Time**: 2-3 hours

📚 **Related Documentation:**

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/functions/runtimes/python)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)

**Action**:
1. Set up Vercel account
2. Deploy the demo
3. Test the live deployment
4. Understand serverless trade-offs

---

## Common Patterns You'll See

### Pattern 1: Defining an MCP Tool

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together.

    This description is shown to the AI, so make it clear!
    """
    return a + b
```

**Key points:**
- Use `@mcp.tool()` decorator
- Type hints are important (they create the schema)
- Docstring describes what the tool does (the AI reads this!)
- Return the result

### Pattern 2: Defining a Resource

```python
@mcp.resource("file://data/config.json")
def get_config() -> str:
    """Get the application configuration."""
    with open("config.json", "r") as f:
        return f.read()
```

**Key points:**
- Use `@mcp.resource()` decorator
- URI identifies the resource
- Usually returns a string

### Pattern 3: Running the Server

```python
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

**Key points:**
- `transport="stdio"` for local development
- `transport="sse"` for streaming
- Server runs as a process

### Pattern 4: Connecting an Agent

```python
# OpenAI pattern
from openai import OpenAI

client = OpenAI()

# Agent uses tools from MCP server
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Add 5 and 3"}],
    tools=tools_from_mcp_server
)
```

---

## Troubleshooting

### Issue: "Command not found: uv"

**Solution**: Install UV package manager
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Then restart your terminal
```

### Issue: "Module not found: mcp"

**Solution 1** (with UV): Just run `uv run script.py` - it auto-installs

**Solution 2** (without UV): Install manually
```bash
pip install mcp model-context-protocol
```

### Issue: "API key not found"

**Solution**:
1. Create `.env` file in the root directory
2. Add your API keys:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```
3. Make sure `.env` is in the same directory where you run the script

### Issue: Server starts but nothing happens

**This is normal!** MCP servers run in the background waiting for connections. You need:
- MCP Inspector to test interactively, OR
- An agent/client to connect to the server

### Issue: "Permission denied" when running scripts

**Solution**: Make the script executable
```bash
chmod +x script.py
```

### Issue: Port already in use (for web demos)

**Solution**: Kill the process using the port
```bash
# Find process using port 8000
lsof -ti:8000

# Kill it
kill -9 $(lsof -ti:8000)
```

Or just change the port in the code:
```python
app.run(port=8001)  # Use a different port
```

---

## Best Practices for Learning

### 1. Read Before You Run
Don't just copy-paste commands. Read the code, understand what it does, THEN run it.

### 2. Experiment
- Modify tool descriptions and see how the AI behaves differently
- Add new tools
- Break things on purpose to see what errors look like

### 3. Use MCP Inspector
It's your best friend for understanding how MCP servers work. Always test your servers with it.

### 4. Read Error Messages
Error messages tell you exactly what's wrong. Take time to read and understand them.

### 5. Start Simple
Don't jump straight to Demo 6. Master each demo before moving to the next.

### 6. Take Notes
Keep a learning journal. Write down:
- What you learned
- What confused you
- Questions you still have

---

## Next Steps

1. ✅ Complete the technical setup above
2. ✅ Run Demo 1 successfully
3. ✅ Test with MCP Inspector
4. 📖 Read through Demo 0 materials
5. 🚀 Continue with Demo 2

## Getting Help

📚 **Official Resources:**

- **MCP Specification**: [spec.modelcontextprotocol.io](https://spec.modelcontextprotocol.io/)
- **MCP Documentation**: [modelcontextprotocol.io](https://modelcontextprotocol.io/)
- **MCP Python SDK**: [github.com/modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)
- **FastMCP Framework**: [github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp)
- **Claude Agent SDK**: [github.com/anthropics/claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python)
- **OpenAI Agents SDK**: [openai.github.io/openai-agents-python](https://openai.github.io/openai-agents-python/)

**Advanced Reading & Engineering Insights:**

- **Code Execution with MCP**: [anthropic.com/engineering/code-execution-with-mcp](https://www.anthropic.com/engineering/code-execution-with-mcp) - Deep dive into MCP architecture
- **MCP Integration with Claude**: [platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool#mcp-integration](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool#mcp-integration)
- **Context Rot Research**: [research.trychroma.com/context-rot](https://research.trychroma.com/context-rot) - Understanding AI context limitations and best practices

**Project Documentation:**

- Check [CLAUDE.md](CLAUDE.md) for technical details
- Browse the `demos/` folders for README files and examples

**Community & Support:**

- **MCP GitHub**: Report issues or browse discussions
- **Stack Overflow**: Search for `model-context-protocol` tag

---

## Glossary

- **Agent**: AI system that can take actions (not just generate text)
- **LLM**: Large Language Model (like GPT-4, Claude)
- **MCP**: Model Context Protocol - standard for AI tool integration
- **Tool**: Function an AI agent can call
- **Resource**: Data source an AI agent can read
- **Transport**: Communication method (stdio, SSE, HTTP)
- **stdio**: Standard Input/Output - local process communication
- **FastMCP**: Python library for building MCP servers easily
- **Client**: Program that uses MCP tools (usually contains an agent)
- **Server**: Program that provides MCP tools

---

## Visual Learning Aid

```
┌─────────────────────────────────────────────────┐
│                    USER                         │
│              "Add 5 and 3"                      │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│                AI AGENT                         │
│  (OpenAI/Claude decides to use add_numbers)     │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│              MCP CLIENT                         │
│     (Sends tool request via transport)          │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│              MCP SERVER                         │
│    @mcp.tool()                                  │
│    def add_numbers(a, b):                       │
│        return a + b                             │
│                                                 │
│    Result: 8                                    │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
           (Result flows back up)
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│                    USER                         │
│              "The answer is 8"                  │
└─────────────────────────────────────────────────┘
```

---

Good luck with your learning journey! Remember: every expert was once a beginner. Take it one demo at a time, experiment freely, and don't be afraid to break things - that's how you learn!
