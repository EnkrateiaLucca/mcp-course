# AI Agent with OpenAI Agents SDK & MCP - Vercel Deployment Demo

A beginner-friendly demo showing how to build and deploy an AI agent with web search and MCP fetch capabilities to Vercel.

## 🚀 Quick Start

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
- ✅ **Web Search** capabilities (simulated, ready for real API integration)
- ✅ **MCP Fetch Server** for web scraping and content extraction
- ✅ **Beautiful Chat Interface** with gradient design and typing indicators
- ✅ **FastAPI Backend** optimized for Vercel serverless deployment
- ✅ **Complete Deployment Guide** with step-by-step instructions

## 🏗️ Architecture

```
User → Chat Interface (HTML/JS)
  ↓
FastAPI Backend (main.py)
  ↓
OpenAI Agent with Tools:
  ├── Web Search Tool
  └── Fetch URL Tool
      ↓
      MCP Fetch Server (mcp_fetch_server.py)
```

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
- **Tools:** MCP (Model Context Protocol)
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

- "What are the latest AI developments?"
- "Search for Python tutorials for beginners"
- "Fetch content from https://example.com"
- "Tell me about the Model Context Protocol"
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
