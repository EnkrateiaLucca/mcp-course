# Deploying an AI Agent with OpenAI Agents SDK to Vercel

This guide walks you through deploying a simple AI agent with web search and MCP fetch capabilities to Vercel.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Local Development Setup](#local-development-setup)
4. [Understanding the Architecture](#understanding-the-architecture)
5. [Deploying to Vercel](#deploying-to-vercel)
6. [Testing Your Deployment](#testing-your-deployment)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This project demonstrates how to build and deploy an AI agent that can:

- **Search the web** for current information
- **Fetch content from URLs** using MCP tools
- **Provide intelligent responses** using OpenAI's GPT models
- **Run as a web application** with a simple chat interface

**Tech Stack:**
- OpenAI GPT-4o-mini
- FastAPI (Python web framework)
- MCP (Model Context Protocol) for tool integration
- Vercel (serverless deployment platform)
- Vanilla JavaScript (no build tools needed!)

---

## ✅ Prerequisites

Before you begin, make sure you have:

1. **Python 3.9+** installed
   ```bash
   python --version  # Should be 3.9 or higher
   ```

2. **Node.js and npm** (for Vercel CLI)
   ```bash
   node --version  # Should be 14 or higher
   npm --version
   ```

3. **An OpenAI API key**
   - Sign up at https://platform.openai.com
   - Create an API key at https://platform.openai.com/api-keys
   - Keep this key secure!

4. **A Vercel account** (free tier works great!)
   - Sign up at https://vercel.com
   - Connect your GitHub account (optional but recommended)

---

## 🚀 Local Development Setup

### Step 1: Clone and Navigate to the Project

```bash
cd 06-deploy-simple-agent-mcp-vercel
```

### Step 2: Create a Virtual Environment

This keeps your dependencies isolated and organized.

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

You should see `(.venv)` in your terminal prompt now.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI (web framework)
- OpenAI Agents SDK
- MCP support libraries
- HTTP clients and utilities

### Step 4: Set Up Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your favorite text editor
# Add your OpenAI API key
```

Your `.env` file should look like:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
MCP_FETCH_SERVER_URL=http://localhost:8001
DEBUG=False
```

### Step 5: Start the MCP Fetch Server (Terminal 1)

The MCP fetch server provides web scraping capabilities.

```bash
python mcp_fetch_server.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8001
```

Leave this running!

### Step 6: Start the Main Application (Terminal 2)

Open a new terminal, activate your virtual environment again, then:

```bash
python main.py
```

You should see:
```
🚀 Starting AI Agent API on http://localhost:8000
📝 Chat interface: http://localhost:8000
📚 API docs: http://localhost:8000/docs
```

### Step 7: Test Locally

1. Open your browser to http://localhost:8000
2. You should see the chat interface!
3. Try asking: "What are the latest AI developments?"

**Example Queries to Test:**

- "Search the web for Python tutorials"
- "What's the weather like today?" (demonstrates web search)
- "Fetch content from https://example.com" (demonstrates URL fetching)
- "Tell me about the Model Context Protocol"

---

## 🏗️ Understanding the Architecture

### Project Structure

```
06-deploy-simple-agent-mcp-vercel/
├── main.py                      # Main FastAPI app with agent logic
├── mcp_fetch_server.py         # MCP server for web fetching
├── static/
│   └── index.html              # Chat interface
├── requirements.txt            # Python dependencies
├── vercel.json                 # Vercel configuration
├── .env                        # Environment variables (local only)
└── .env.example               # Template for environment variables
```

### How It Works

1. **User sends a message** via the chat interface
2. **FastAPI receives the request** at `/api/chat`
3. **Agent processes the query** and decides which tools to use:
   - `web_search` for general queries
   - `fetch_url` for reading specific web pages
4. **Tools execute** and return results
5. **Agent synthesizes a response** based on tool outputs
6. **Response is sent back** to the user in the chat

### Key Components

#### `main.py` - The Brain

Contains:
- FastAPI application setup
- Agent configuration with tools
- API endpoints for chat and health checks
- Custom tool implementations

#### `mcp_fetch_server.py` - The Web Fetcher

Provides:
- URL fetching with text extraction
- HTML content retrieval
- BeautifulSoup parsing for clean text

#### `static/index.html` - The Interface

Features:
- Beautiful gradient design
- Real-time chat experience
- Typing indicators
- Example prompts

---

## ☁️ Deploying to Vercel

### Option 1: Deploy via Vercel CLI (Recommended for Beginners)

#### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

#### Step 2: Login to Vercel

```bash
vercel login
```

Follow the prompts to authenticate.

#### Step 3: Configure Environment Variables

Before deploying, set your OpenAI API key in Vercel:

```bash
# Set the OpenAI API key
vercel env add OPENAI_API_KEY

# When prompted:
# - Environment: Production
# - Value: sk-your-actual-api-key-here
```

**Note about MCP Server:** For simplicity, the main app includes built-in fetch functionality. You don't need to deploy the MCP server separately for basic functionality.

#### Step 4: Deploy!

```bash
# From the project directory
vercel --prod
```

The CLI will:
1. Ask a few questions (accept defaults)
2. Build your project
3. Deploy to Vercel
4. Give you a URL (like `https://your-project.vercel.app`)

#### Step 5: Test Your Deployment

Visit the URL provided by Vercel. You should see your chat interface!

### Option 2: Deploy via GitHub Integration

#### Step 1: Push to GitHub

```bash
# Initialize git (if not already done)
git init

# Add files
git add .

# Commit
git commit -m "Initial commit: AI Agent with MCP"

# Create a repo on GitHub, then:
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

#### Step 2: Import to Vercel

1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Vercel auto-detects Python and FastAPI
4. Add environment variable:
   - Key: `OPENAI_API_KEY`
   - Value: `sk-your-actual-api-key-here`
5. Click "Deploy"

#### Step 3: Auto-Deploy on Push

Now every time you push to `main`, Vercel automatically redeploys!

---

## 🧪 Testing Your Deployment

### Basic Functionality Tests

Once deployed, test these scenarios:

#### 1. Health Check

```bash
curl https://your-project.vercel.app/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "ai-agent-api",
  "version": "1.0.0"
}
```

#### 2. Agent Info

```bash
curl https://your-project.vercel.app/api/info
```

Shows available capabilities and tools.

#### 3. Chat via API

```bash
curl -X POST https://your-project.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is FastAPI?",
    "history": []
  }'
```

#### 4. Chat via Web Interface

Visit `https://your-project.vercel.app` and try:
- "Search for the latest AI news"
- "What can you do?"
- "Fetch content from https://python.org"

### Performance Monitoring

Vercel provides built-in monitoring:

1. Go to your project dashboard
2. Click "Analytics" to see:
   - Request counts
   - Response times
   - Error rates
3. Click "Logs" to see:
   - Function execution logs
   - Error messages
   - Debug information

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Issue: "ModuleNotFoundError: No module named 'X'"

**Solution:**
```bash
# Make sure you're in your virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### Issue: "OpenAI API key not found"

**Solution:**
- **Local:** Check your `.env` file has `OPENAI_API_KEY=sk-...`
- **Vercel:** Go to project settings → Environment Variables → Add `OPENAI_API_KEY`

#### Issue: "Connection refused on localhost:8001"

**Solution:**
The MCP fetch server isn't running. Start it in a separate terminal:
```bash
python mcp_fetch_server.py
```

#### Issue: "Vercel deployment fails"

**Solution:**
1. Check `vercel.json` is properly formatted (JSON syntax)
2. Ensure all dependencies are in `requirements.txt`
3. Check deployment logs: `vercel logs` or via dashboard
4. Verify Python version compatibility (3.9+)

#### Issue: "Rate limit exceeded" from OpenAI

**Solution:**
- You're making too many requests
- Check your OpenAI usage dashboard
- Consider adding request caching
- Use `gpt-4o-mini` instead of `gpt-4` (10x cheaper)

#### Issue: "Function timeout" on Vercel

**Solution:**
- Free tier has 10s timeout limit
- Upgrade to Pro for 60s timeout
- Or optimize your agent to respond faster
- Add streaming for better UX

#### Issue: Chat interface loads but doesn't respond

**Solution:**
1. Open browser DevTools (F12) → Console
2. Check for JavaScript errors
3. Check Network tab for failed API calls
4. Verify environment variables are set in Vercel

---

## 🎨 Customization Ideas

### Make It Your Own!

#### 1. Change the UI Theme

Edit `static/index.html`:
```css
/* Change the gradient colors */
background: linear-gradient(135deg, #your-color-1 0%, #your-color-2 100%);
```

#### 2. Add More Tools

Edit `main.py` to add custom tools:
```python
{
    "type": "function",
    "function": {
        "name": "your_custom_tool",
        "description": "What your tool does",
        "parameters": {
            # Define parameters here
        }
    }
}
```

#### 3. Use a Different Model

In `main.py`, change:
```python
"model": "gpt-4o-mini",  # Change to "gpt-4" or "gpt-4-turbo"
```

#### 4. Add Authentication

Consider adding:
- API key authentication
- User login system
- Rate limiting per user

#### 5. Integrate Real Web Search

Replace the simulated search with:
- Brave Search API
- Tavily Search API
- Bing Web Search API
- Perplexity API

---

## 📚 Additional Resources

### Documentation

- **OpenAI Agents SDK:** https://openai.github.io/openai-agents-python/
- **MCP Specification:** https://modelcontextprotocol.io
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Vercel Python Docs:** https://vercel.com/docs/functions/runtimes/python

### Learning More

- **OpenAI Cookbook:** https://cookbook.openai.com
- **FastAPI Tutorial:** https://fastapi.tiangolo.com/tutorial/
- **Async Python:** https://realpython.com/async-io-python/

### Community

- **OpenAI Forum:** https://community.openai.com
- **MCP Discord:** Check modelcontextprotocol.io for invite
- **FastAPI Discord:** https://discord.com/invite/fastapi

---

## 🎓 Next Steps

### Beginner Path

1. ✅ Deploy this demo successfully
2. Try modifying the UI colors and text
3. Add a new example prompt
4. Experiment with different models
5. Add error handling improvements

### Intermediate Path

1. Integrate a real web search API
2. Add conversation memory/history storage
3. Implement user authentication
4. Add rate limiting
5. Create custom MCP tools

### Advanced Path

1. Build a multi-agent system
2. Add vector database for RAG
3. Implement streaming responses
4. Create a mobile app frontend
5. Deploy at scale with monitoring

---

## 💡 Pro Tips

1. **Start Simple:** Get the basic version working before adding features
2. **Monitor Costs:** OpenAI API calls add up! Use `gpt-4o-mini` for development
3. **Use Environment Variables:** Never commit API keys to git
4. **Test Locally First:** Always test changes locally before deploying
5. **Read the Logs:** Vercel logs are your friend for debugging
6. **Version Control:** Commit often with clear messages
7. **Documentation:** Update this file as you make changes!

---

## 🤝 Contributing

Found a bug or have an improvement?

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📄 License

This demo is provided as-is for educational purposes.

---

## 🙋 Need Help?

- **Issues with Vercel:** Check https://vercel.com/docs
- **OpenAI API Issues:** Visit https://help.openai.com
- **General Questions:** Open an issue in the repository

---

## 🎉 Congratulations!

You've successfully deployed an AI agent to the cloud! This is a significant achievement. From here, the possibilities are endless. Keep building, keep learning, and most importantly - have fun!

**Happy coding! 🚀**
