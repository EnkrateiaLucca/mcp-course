# AI Agent Deployment Examples - Vercel with MCP Integration

Two comprehensive examples showing how to build and deploy AI agents with MCP capabilities to Vercel:

1. **OpenAI Agents SDK** (Stateless) - `main.py`
2. **Claude Agents SDK** (Sandboxed) - `main_claude.py`

Both use the **official MCP Python SDK** for proper protocol integration.

## ✨ What's New (v2.0)

This demo has been **upgraded to use the official MCP Python SDK** (`mcp[cli]`) instead of a custom FastAPI implementation:

**Before (v1.0):**
- Custom FastAPI endpoints mimicking MCP protocol
- Manual tool definitions and HTTP routing
- Direct HTTP POST to `/tools/fetch_url` endpoint

**Now (v2.0):**
- ✅ Built with **FastMCP** (official MCP Python SDK)
- ✅ Proper MCP protocol compliance with **HTTP/Streamable transport**
- ✅ Seamless integration with **OpenAI Agents SDK** via `MCPServerStreamableHttp`
- ✅ Standard MCP tool decorators (`@mcp.tool()`)
- ✅ Better error handling and protocol adherence

This provides better compatibility, follows MCP best practices, and makes the code more maintainable and extensible.

## 🔀 Choose Your Implementation

### Option 1: OpenAI Agents SDK (Recommended for Beginners)

**Best for:** Simple chat applications, stateless interactions, quick deployments

**Architecture:**
- ✅ Stateless request/response model
- ✅ Simple serverless deployment
- ✅ No sandbox management needed
- ✅ Lower operational complexity

**Files:**
- `main.py` - OpenAI Agents SDK implementation
- `requirements.txt` - Dependencies
- `deployment_agents_sdk_vercel.md` - Full deployment guide

**Quick Start:**
```bash
pip install -r requirements.txt
python main.py
```

📖 **[Complete OpenAI Deployment Guide →](./deployment_agents_sdk_vercel.md)**

---

### Option 2: Claude Agents SDK (Recommended for Production)

**Best for:** Complex agents, long-running tasks, advanced tool use, production deployments

**Architecture:**
- ✅ Long-running agent processes
- ✅ Sandboxed execution environment
- ✅ File system and command execution
- ✅ Production-grade security

**Files:**
- `main_claude.py` - Claude Agents SDK with sandbox management
- `claude_agent_sandbox.py` - Agent code that runs in sandbox
- `requirements_claude.txt` - Dependencies
- `deployment_claude_agents_sdk_vercel.md` - Comprehensive deployment guide

**Quick Start:**
```bash
pip install -r requirements_claude.txt
python main_claude.py
```

📖 **[Complete Claude Agents SDK Deployment Guide →](./deployment_claude_agents_sdk_vercel.md)**

---

### 🆚 Quick Comparison

| Feature | OpenAI Agents SDK | Claude Agents SDK |
|---------|-------------------|-------------------|
| **Deployment Model** | Stateless serverless | Sandboxed containers |
| **Setup Complexity** | Low ⭐ | Medium ⭐⭐⭐ |
| **Security** | API-level | Container isolation |
| **File Operations** | Limited | Full access (sandboxed) |
| **Command Execution** | No | Yes (in sandbox) |
| **Session State** | Stateless | Persistent (per container) |
| **Cost** | API calls only | API + sandbox compute |
| **Best For** | Chat apps | Complex agents |
| **Production Ready** | Yes | Yes (with sandboxing) |

---

## 🚀 Quick Start (OpenAI)

### 1. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Up Environment

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Run Locally

**Terminal 1 - Start MCP Fetch Server:**
```bash
python mcp_fetch_server.py
```

**Terminal 2 - Start Main App:**
```bash
python main.py
```

Open http://localhost:8000 in your browser!

## 📚 Full Documentation

For complete setup, deployment, and troubleshooting instructions, see:

**[deployment_agents_sdk_vercel.md](./deployment_agents_sdk_vercel.md)**

## 🎯 What This Demo Includes

- ✅ **OpenAI Agents SDK** integration with GPT-4o-mini
- ✅ **Official MCP Python SDK** (FastMCP) for building the MCP server
- ✅ **MCP Fetch Server** with HTTP transport for web scraping and content extraction
- ✅ **Proper MCP Integration** using `MCPServerStreamableHttp` from OpenAI Agents SDK
- ✅ **Beautiful Chat Interface** with gradient design and typing indicators
- ✅ **FastAPI Backend** optimized for Vercel serverless deployment
- ✅ **Complete Deployment Guide** with step-by-step instructions

## 🏗️ Architecture

```
User → Chat Interface (HTML/JS)
  ↓
FastAPI Backend (main.py)
  ↓
OpenAI Agents SDK
  ↓
MCPServerStreamableHttp (MCP Client)
  ↓ HTTP/Streamable Transport
  ↓
MCP Fetch Server (mcp_fetch_server.py)
  Built with FastMCP (Official MCP Python SDK)
  ↓
Tools:
  ├── fetch_url (extract clean text)
  └── fetch_html (raw HTML)
```

**Key Architectural Components:**

1. **MCP Server** (`mcp_fetch_server.py`): Built with the official `FastMCP` SDK, exposing tools via HTTP transport
2. **MCP Client Integration**: Uses `MCPServerStreamableHttp` from OpenAI Agents SDK to connect to the MCP server
3. **OpenAI Agent**: Orchestrates tool calling and conversation flow
4. **FastAPI Backend**: Handles HTTP requests and manages the agent lifecycle

## 🌟 Features

### For Users
- Ask questions and get AI-powered responses
- Search the web for current information
- Fetch and analyze content from URLs
- Clean, modern chat interface

### For Developers
- Simple, well-commented code
- No complex build tools required
- Easy to customize and extend
- Production-ready Vercel deployment
- Beginner-friendly architecture

## 🛠️ Tech Stack

- **Backend:** Python 3.9+, FastAPI, Uvicorn
- **AI:** OpenAI GPT-4o-mini, OpenAI Agents SDK
- **MCP:** Official MCP Python SDK (`mcp[cli]>=1.9.0`) with FastMCP
- **MCP Transport:** HTTP/Streamable (modern approach, replaces SSE)
- **Frontend:** Vanilla HTML/CSS/JavaScript
- **Deployment:** Vercel Serverless Functions
- **HTTP Client:** httpx
- **Parsing:** BeautifulSoup4

## 📁 Project Structure

```
06-deploy-simple-agent-mcp-vercel/
├── main.py                          # FastAPI app with agent logic
├── mcp_fetch_server.py             # MCP server for web fetching
├── static/
│   └── index.html                  # Chat interface
├── requirements.txt                # Python dependencies
├── vercel.json                     # Vercel configuration
├── .env.example                    # Environment template
├── README.md                       # This file
└── deployment_agents_sdk_vercel.md # Complete deployment guide
```

## 🧪 Example Queries

Try these once your agent is running:

- "Fetch content from https://example.com"
- "Read the documentation at https://modelcontextprotocol.io"
- "What's on the OpenAI website?"
- "Get the HTML from https://github.com"
- "Tell me about the Model Context Protocol by reading https://modelcontextprotocol.io"
- "What can you do?"

## 🚢 Deploy to Vercel

### Quick Deploy

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Set environment variable
vercel env add OPENAI_API_KEY

# Deploy
vercel --prod
```

See the [full deployment guide](./deployment_agents_sdk_vercel.md) for detailed instructions.

## 🔑 Environment Variables

Required:
- `OPENAI_API_KEY` - Your OpenAI API key from https://platform.openai.com/api-keys

Optional:
- `MCP_FETCH_SERVER_URL` - URL of the MCP fetch server (defaults to localhost:8001)
- `DEBUG` - Enable debug logging (default: False)

## 📋 API Endpoints

- `GET /` - Chat interface
- `POST /api/chat` - Send message to agent
- `GET /api/health` - Health check
- `GET /api/info` - Agent capabilities info
- `GET /docs` - Interactive API documentation

## 🎨 Customization

### Change the Model

In `main.py`, find:
```python
"model": "gpt-4o-mini",  # Change to "gpt-4" or "gpt-4-turbo"
```

### Modify the UI

Edit `static/index.html` to change:
- Colors and gradients
- Example prompts
- Layout and styling

### Add New Tools

Extend the agent's capabilities by adding custom tools in `main.py`.

## 🐛 Troubleshooting

### Issue: "Module not found"
```bash
pip install -r requirements.txt
```

### Issue: "OpenAI API key not found"
Check your `.env` file or Vercel environment variables.

### Issue: "Connection refused on localhost:8001"
Make sure the MCP fetch server is running:
```bash
python mcp_fetch_server.py
```

For more help, see the [troubleshooting section](./deployment_agents_sdk_vercel.md#troubleshooting) in the deployment guide.

## 📚 Learn More

- **OpenAI Agents SDK:** https://openai.github.io/openai-agents-python/
- **MCP Specification:** https://modelcontextprotocol.io
- **FastAPI:** https://fastapi.tiangolo.com
- **Vercel Python:** https://vercel.com/docs/functions/runtimes/python

## 💡 Next Steps

1. ✅ Get the demo running locally
2. 🚀 Deploy to Vercel
3. 🎨 Customize the UI and prompts
4. 🔧 Add real web search API integration
5. 🌟 Build your own custom tools

## 🤝 Contributing

Improvements welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Share your customizations

## 📄 License

This demo is provided for educational purposes.

## 🎉 Credits

Built with:
- OpenAI Agents SDK
- FastAPI
- Model Context Protocol (MCP)
- Vercel

---

**Happy building! 🚀**

For the complete guide with detailed explanations, see [deployment_agents_sdk_vercel.md](./deployment_agents_sdk_vercel.md)
