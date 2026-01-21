# Deploying Claude Agent SDK to Vercel with Sandbox Integration

**Complete Guide to Production Deployment of Claude Agents**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture Deep Dive](#architecture-deep-dive)
3. [Prerequisites](#prerequisites)
4. [Understanding Vercel Sandbox](#understanding-vercel-sandbox)
5. [Local Development Setup](#local-development-setup)
6. [Production Deployment](#production-deployment)
7. [Alternative Sandbox Providers](#alternative-sandbox-providers)
8. [Security Considerations](#security-considerations)
9. [Troubleshooting](#troubleshooting)
10. [Next Steps](#next-steps)

---

## 🎯 Overview

This guide demonstrates how to deploy **Claude Agent SDK** applications to production using **Vercel Sandbox** for secure, isolated code execution.

### What You'll Learn

- How Claude Agent SDK differs from traditional LLM APIs
- Why sandboxing is essential for agent deployments
- How to integrate Vercel Sandbox with Claude agents
- Production deployment patterns and best practices
- Security hardening for untrusted code execution

### Key Technologies

- **Claude Agent SDK** - Agentic framework with tool use and sessions
- **Vercel Sandbox** - Ephemeral compute for isolated code execution
- **Model Context Protocol (MCP)** - Standardized tool integration
- **FastAPI** - Web framework for API endpoints
- **TypeScript/Python** - Hybrid architecture (Vercel Sandbox SDK is TypeScript-only)

---

## 🏗️ Architecture Deep Dive

### The Claude Agent SDK Difference

Unlike stateless API calls, Claude Agent SDK is a **long-running process** that:

1. **Maintains conversational state** across multiple turns
2. **Executes commands** in a persistent shell environment
3. **Manages file operations** within a working directory
4. **Handles tool execution** with context from previous interactions

**This means it CANNOT run as a traditional serverless function.**

### Why Sandbox Containers?

Agent capabilities require isolation:

```
✅ File System Access       → Sandbox provides isolated filesystem
✅ Command Execution         → Sandbox controls what commands can run
✅ Network Access            → Sandbox restricts outbound connections
✅ Resource Limits           → Sandbox enforces CPU/RAM/disk quotas
✅ Ephemeral State          → Sandbox destroys after use
```

### Three-Tier Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT                               │
│                  (Browser / Mobile App)                      │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTPS
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   VERCEL EDGE FUNCTION                       │
│                    (main_claude.py)                          │
│                                                              │
│  • Receives user requests                                   │
│  • Manages sandbox lifecycle                                │
│  • Routes to appropriate sandbox                            │
│  • Returns responses to client                              │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/WebSocket
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    VERCEL SANDBOX                            │
│                (claude_agent_sandbox.py)                     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Claude Agent SDK Process                    │    │
│  │  • Long-running agent loop                          │    │
│  │  • Tool execution                                   │    │
│  │  • File operations                                  │    │
│  │  • Command execution                                │    │
│  └──────────────┬──────────────────────────────────────┘    │
│                 │                                            │
│                 ↓                                            │
│  ┌────────────────────────────────────────────────────┐    │
│  │         MCP Servers (Tools)                         │    │
│  │  • fetch_url - Web content extraction               │    │
│  │  • fetch_html - Raw HTML retrieval                  │    │
│  │  • Custom tools as needed                           │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Deployment Patterns

Claude Agent SDK supports four patterns. This guide focuses on **Pattern 1: Ephemeral Sessions**.

| Pattern | Use Case | Sandbox Lifecycle |
|---------|----------|-------------------|
| **Ephemeral Sessions** | One-off tasks | Create → Execute → Destroy |
| **Long-Running Sessions** | Continuous agents | Create → Keep alive → Reuse |
| **Hybrid Sessions** | Intermittent use | Create → Resume from state |
| **Single Container** | Multi-agent collab | Global container for all |

**Pattern 1** is ideal for:
- Bug fixes
- Document processing
- Translation tasks
- Image/video processing
- **Web-based chat applications** (like this demo)

---

## ✅ Prerequisites

### Required Software

1. **Python 3.10+**
   ```bash
   python --version  # Should be 3.10 or higher
   ```

2. **Node.js 18+** (required for Vercel CLI and Sandbox SDK)
   ```bash
   node --version  # Should be 18 or higher
   npm --version
   ```

3. **Vercel CLI**
   ```bash
   npm install -g vercel
   ```

### Required Accounts & API Keys

1. **Anthropic API Key**
   - Sign up at https://console.anthropic.com
   - Create an API key
   - Set billing limits (recommended)

2. **Vercel Account**
   - Sign up at https://vercel.com
   - Free tier works for testing
   - Pro tier recommended for production (60s timeout vs 10s)

### System Requirements (per sandbox)

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM      | 512 MiB | 1 GiB       |
| Disk     | 2 GiB   | 5 GiB       |
| CPU      | 0.5     | 1 vCPU      |

**Cost Estimate:** ~$0.05/hour per running sandbox + Claude API costs

---

## 🔍 Understanding Vercel Sandbox

### What is Vercel Sandbox?

Vercel Sandbox is an **ephemeral compute primitive** for safely running untrusted code.

**Key Features:**
- ✅ Isolated container environment (Amazon Linux 2023)
- ✅ Multiple runtimes: `node24`, `node22`, `python3.13`
- ✅ Package managers: `npm`, `pnpm`, `pip`, `uv`
- ✅ Sudo access with secure defaults
- ✅ Automatic cleanup after timeout
- ✅ Port exposure for communication
- ✅ OIDC token authentication (automatic in production)

### Sandbox Specifications

**Python 3.13 Runtime:**
```
Runtime:          /vercel/runtimes/python
Working Dir:      /vercel/sandbox
User:             vercel-sandbox
Sudo:             Available
Package Manager:  pip, uv
```

**Pre-installed Packages:**
```
git, openssl, curl, wget, tar, gzip, bzip2, unzip, zstd
findutils, procps, iputils, bind-utils, ncurses-libs
```

**Installing Additional Packages:**
```bash
# Inside sandbox
sudo dnf install -y golang nodejs
```

### How Vercel Sandbox Works

1. **Creation**: SDK creates container with specified runtime
2. **Initialization**: Installs dependencies, copies files
3. **Execution**: Runs your code in isolation
4. **Communication**: Exposes ports for HTTP/WebSocket
5. **Cleanup**: Destroys container after timeout or completion

### Important Limitation: TypeScript SDK Only

**The Vercel Sandbox SDK is TypeScript-only.** This creates an architectural challenge for Python-based Claude agents.

**Solution Options:**

1. **Hybrid Architecture** (Recommended for Vercel)
   - TypeScript service manages Vercel Sandbox
   - Python agent runs inside sandbox
   - Communication via HTTP

2. **Alternative Sandbox Provider** (Easier for Python-only)
   - Modal (Python SDK available)
   - E2B (Python SDK available)
   - Fly Machines (API accessible from Python)
   - Cloudflare Sandboxes

---

## 🚀 Local Development Setup

### Option A: Simplified Demo (No Real Sandbox)

This approach simulates sandbox behavior for learning purposes.

#### Step 1: Clone and Navigate

```bash
cd demos/06-deploy-simple-agent-mcp-vercel
```

#### Step 2: Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

#### Step 3: Install Dependencies

```bash
pip install -r requirements_claude.txt
```

#### Step 4: Configure Environment

```bash
# Create .env file
cat > .env << EOF
ANTHROPIC_API_KEY=sk-ant-your-actual-api-key-here
DEBUG=True
EOF
```

#### Step 5: Run Locally

```bash
python main_claude.py
```

Visit http://localhost:8000

**What This Demo Does:**
- ✅ Shows API structure for sandbox management
- ✅ Demonstrates Claude API integration
- ✅ Provides working chat interface
- ⚠️ Does NOT actually create sandboxes (simulated)
- ⚠️ Does NOT provide true isolation

### Option B: Full Implementation with Real Sandboxes

For a production-ready implementation, you'll need:

#### 1. TypeScript Service for Sandbox Management

Create `sandbox-manager/index.ts`:

```typescript
import { Sandbox } from '@vercel/sandbox';
import express from 'express';

const app = express();
app.use(express.json());

// Create sandbox endpoint
app.post('/sandbox/create', async (req, res) => {
  const sandbox = await Sandbox.create({
    runtime: 'python3.13',
    source: {
      type: 'git',
      url: process.env.AGENT_REPO_URL!,
    },
    ports: [8000],
    timeout: 300000, // 5 minutes
    resources: {
      vcpus: 1,
    },
  });

  // Wait for sandbox to be ready
  await sandbox.connect();

  // Install dependencies
  await sandbox.runCommand({
    cmd: 'pip',
    args: ['install', '-r', 'requirements_claude.txt'],
  });

  // Start Claude agent
  const process = await sandbox.runCommand({
    cmd: 'python',
    args: ['claude_agent_sandbox.py'],
    background: true,
  });

  res.json({
    sandbox_id: sandbox.id,
    url: `http://${sandbox.hostname}:8000`,
    status: 'ready',
  });
});

// Cleanup sandbox endpoint
app.delete('/sandbox/:id', async (req, res) => {
  // Sandbox auto-terminates after timeout
  res.json({ status: 'cleanup_scheduled' });
});

app.listen(3000, () => {
  console.log('Sandbox manager running on port 3000');
});
```

#### 2. Python FastAPI Integration

Update `main_claude.py` to call TypeScript service:

```python
async def create_sandbox() -> Dict[str, Any]:
    """Create sandbox via TypeScript service"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:3000/sandbox/create",
            json={"requirements": "requirements_claude.txt"},
            timeout=60.0
        )
        return response.json()
```

#### 3. Deploy Both Services

```bash
# Deploy TypeScript sandbox manager
cd sandbox-manager
vercel --prod

# Deploy Python API
cd ..
vercel --prod
```

---

## ☁️ Production Deployment

### Deployment Architecture

```
User Request
    ↓
Vercel Edge (FastAPI)
    ↓
Sandbox Manager (TypeScript)
    ↓
Vercel Sandbox (Python + Claude Agent)
    ↓
Claude API + MCP Tools
    ↓
Response
```

### Step-by-Step Deployment

#### 1. Prepare Your Repository

```bash
# Project structure
your-repo/
├── main_claude.py                    # Main API
├── claude_agent_sandbox.py          # Agent code
├── requirements_claude.txt           # Python deps
├── vercel.json                      # Vercel config
├── static/
│   └── index.html                   # Chat UI
├── sandbox-manager/                 # TypeScript service
│   ├── package.json
│   ├── index.ts
│   └── tsconfig.json
└── .env.example                     # Example env vars
```

#### 2. Configure `vercel.json`

```json
{
  "version": 2,
  "builds": [
    {
      "src": "main_claude.py",
      "use": "@vercel/python"
    },
    {
      "src": "sandbox-manager/package.json",
      "use": "@vercel/node"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "main_claude.py"
    },
    {
      "src": "/sandbox/(.*)",
      "dest": "sandbox-manager/index.ts"
    },
    {
      "src": "/(.*)",
      "dest": "main_claude.py"
    }
  ],
  "env": {
    "ANTHROPIC_API_KEY": "@anthropic_api_key",
    "VERCEL_TEAM_ID": "@vercel_team_id",
    "VERCEL_PROJECT_ID": "@vercel_project_id"
  }
}
```

#### 3. Set Environment Variables

```bash
# Login to Vercel
vercel login

# Add secrets
vercel env add ANTHROPIC_API_KEY
# Paste your Anthropic API key

vercel env add VERCEL_TEAM_ID
# Find at: https://vercel.com/account/team

vercel env add VERCEL_PROJECT_ID
# Find in project settings
```

#### 4. Deploy to Production

```bash
# Deploy with production flag
vercel --prod

# You'll get a URL like:
# https://your-project.vercel.app
```

#### 5. Verify Deployment

```bash
# Health check
curl https://your-project.vercel.app/api/health

# Test chat
curl -X POST https://your-project.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "history": []}'
```

### Monitoring & Logging

**Vercel Dashboard:**
1. Go to your project
2. Click "Deployments" → Select latest
3. View:
   - Function logs
   - Request analytics
   - Error traces
   - Performance metrics

**Sandbox Monitoring:**
1. Navigate to "Observability" tab
2. Click "Sandboxes"
3. View:
   - Active sandboxes
   - Command history
   - Resource usage
   - Sandbox URLs

---

## 🔄 Alternative Sandbox Providers

Since Vercel Sandbox SDK is TypeScript-only, consider these Python-friendly alternatives:

### 1. Modal (Recommended for Python)

**Pros:**
- Native Python SDK
- Excellent for AI/ML workloads
- Simple deployment
- Great docs

**Example:**
```python
import modal

app = modal.App("claude-agent")

@app.function(
    image=modal.Image.debian_slim()
        .pip_install("anthropic", "mcp")
        .run_commands("npm install -g @anthropic-ai/claude-code"),
    memory=1024,
    timeout=300,
)
def run_agent(message: str):
    from anthropic import Anthropic
    client = Anthropic()
    # Agent logic here
    return response

# Deploy: modal deploy agent.py
```

**Deployment:**
```bash
pip install modal
modal token new
modal deploy main_claude.py
```

### 2. E2B (Code Execution Sandbox)

**Pros:**
- Python SDK available
- Built specifically for code execution
- Good documentation
- Fast startup times

**Example:**
```python
from e2b_code_interpreter import CodeInterpreter

with CodeInterpreter() as sandbox:
    # Run Claude agent inside
    execution = sandbox.notebook.exec_cell("""
        from anthropic import Anthropic
        # Agent code
    """)
```

### 3. Fly Machines

**Pros:**
- Full control over environment
- Persistent volumes available
- Good for long-running agents
- API accessible from Python

**Example:**
```python
import httpx

# Create Fly Machine via API
async with httpx.AsyncClient() as client:
    response = await client.post(
        "https://api.machines.dev/v1/apps/your-app/machines",
        headers={"Authorization": f"Bearer {fly_token}"},
        json={
            "config": {
                "image": "your-image:latest",
                "services": [{"ports": [{"port": 8000}]}]
            }
        }
    )
```

### 4. Docker + Cloud Run (DIY)

**Pros:**
- Maximum control
- Standard Docker workflow
- Works on any cloud

**Dockerfile:**
```dockerfile
FROM python:3.13-slim

# Install Node.js for Claude Code CLI
RUN apt-get update && apt-get install -y nodejs npm
RUN npm install -g @anthropic-ai/claude-code

# Install Python dependencies
COPY requirements_claude.txt .
RUN pip install -r requirements_claude.txt

# Copy agent code
COPY claude_agent_sandbox.py .

# Run agent
CMD ["python", "claude_agent_sandbox.py"]
```

**Deploy to Cloud Run:**
```bash
gcloud run deploy claude-agent \
  --source . \
  --memory 1Gi \
  --timeout 300
```

### Comparison Matrix

| Provider | Python SDK | Startup Time | Pricing | Best For |
|----------|------------|--------------|---------|----------|
| **Modal** | ✅ Yes | ~5s | $0.00025/GB-s | ML/AI workloads |
| **E2B** | ✅ Yes | ~2s | $0.002/min | Code execution |
| **Fly** | ⚠️ API | ~1s | $0.0000017/s | Long-running |
| **Vercel** | ❌ No | ~3s | Free tier | Vercel ecosystem |
| **Cloud Run** | ⚠️ Docker | ~5s | $0.00002/s | Full control |

---

## 🔒 Security Considerations

### Essential Security Measures

#### 1. Network Isolation

```python
# In sandbox configuration
{
    "network": {
        "allowed_domains": [
            "api.anthropic.com",  # Claude API
            "example-mcp-server.com"  # Your MCP servers
        ],
        "block_private_ips": True,  # Prevent SSRF
        "block_metadata_service": True  # Prevent cloud metadata access
    }
}
```

#### 2. File System Limits

```python
# Restrict file operations
{
    "filesystem": {
        "max_size": "1GB",  # Total disk usage
        "max_files": 1000,  # Number of files
        "allowed_paths": ["/vercel/sandbox"],  # Restrict to working dir
        "readonly_paths": ["/etc", "/usr"]  # Protect system files
    }
}
```

#### 3. Command Restrictions

```python
# Block dangerous commands
BLOCKED_COMMANDS = [
    "rm -rf /",
    "dd if=/dev/zero",
    ":(){ :|:& };:",  # Fork bomb
    "wget | bash",
    "curl | sh"
]

def validate_command(cmd: str) -> bool:
    return not any(blocked in cmd for blocked in BLOCKED_COMMANDS)
```

#### 4. Resource Limits

```python
{
    "resources": {
        "cpu": "1000m",  # 1 CPU core
        "memory": "1Gi",  # 1GB RAM
        "disk": "5Gi",  # 5GB disk
        "timeout": 300,  # 5 minutes max
    }
}
```

#### 5. API Key Protection

```python
# Never expose API keys to sandbox code
# Use environment injection at runtime
{
    "env": {
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        # Sandbox code cannot read this from filesystem
    }
}
```

#### 6. Input Validation

```python
from pydantic import BaseModel, validator

class AgentRequest(BaseModel):
    message: str

    @validator('message')
    def validate_message(cls, v):
        if len(v) > 10000:
            raise ValueError("Message too long")
        if any(char in v for char in ['\x00', '\x1b']):
            raise ValueError("Invalid characters")
        return v
```

### Security Checklist

Before deploying to production:

- [ ] Sandbox provider properly configured
- [ ] Network egress restricted
- [ ] File system permissions locked down
- [ ] Resource limits enforced
- [ ] Dangerous commands blocked
- [ ] API keys securely injected
- [ ] Input validation implemented
- [ ] Timeout limits set
- [ ] Logging and monitoring enabled
- [ ] Incident response plan documented

---

## 🔧 Troubleshooting

### Common Issues

#### Issue 1: "Sandbox creation timeout"

**Symptoms:**
```
TimeoutError: Sandbox failed to start within 60 seconds
```

**Solutions:**
1. Check Vercel account quotas
2. Verify team/project IDs are correct
3. Ensure OIDC token is valid
4. Try smaller Docker image
5. Reduce startup dependencies

**Debug:**
```bash
# Check Vercel sandbox logs
vercel logs --follow

# Test sandbox creation manually
curl -X POST https://your-app.vercel.app/sandbox/create
```

#### Issue 2: "ANTHROPIC_API_KEY not found"

**Symptoms:**
```
ValueError: ANTHROPIC_API_KEY not found in environment variables
```

**Solutions:**
1. Verify env var in Vercel dashboard
2. Check it's set for Production environment
3. Redeploy after setting env vars
4. Ensure no typos in variable name

**Debug:**
```bash
# List environment variables
vercel env ls

# Pull environment variables locally
vercel env pull .env.local
```

#### Issue 3: "Claude Code CLI not found"

**Symptoms:**
```
/bin/sh: claude-code: command not found
```

**Solutions:**
1. Ensure Node.js installed in sandbox
2. Install CLI during sandbox setup:
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```
3. Add to PATH: `export PATH=$PATH:/usr/local/bin`

#### Issue 4: "Function timeout"

**Symptoms:**
```
Error: Function execution timed out after 10s
```

**Solutions:**
1. Upgrade to Vercel Pro (60s timeout)
2. Optimize agent prompt for faster responses
3. Implement response streaming
4. Use background jobs for long tasks

**Example streaming:**
```python
from fastapi.responses import StreamingResponse

async def stream_response():
    # Stream agent responses as they arrive
    for chunk in agent.stream_response():
        yield f"data: {chunk}\n\n"

@app.post("/api/chat")
async def chat(request: QueryRequest):
    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream"
    )
```

#### Issue 5: "Rate limit exceeded"

**Symptoms:**
```
anthropic.RateLimitError: Rate limit exceeded
```

**Solutions:**
1. Implement request queuing
2. Add exponential backoff
3. Cache responses where possible
4. Upgrade Anthropic plan tier

**Example backoff:**
```python
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def call_claude_with_retry():
    client = anthropic.Anthropic()
    return client.messages.create(...)
```

#### Issue 6: "MCP server connection failed"

**Symptoms:**
```
ConnectionError: Failed to connect to MCP server
```

**Solutions:**
1. Ensure MCP server started before agent
2. Check port configuration matches
3. Verify network access allowed
4. Use health check before agent starts

**Debug MCP connection:**
```python
import httpx

async def wait_for_mcp_server(url: str, timeout: int = 30):
    """Wait for MCP server to be ready"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/health")
                if response.status_code == 200:
                    return True
        except:
            pass
        await asyncio.sleep(1)
    raise TimeoutError("MCP server failed to start")
```

---

## 🎓 Next Steps

### Beginner Track

1. ✅ **Deploy the simplified demo**
   - Understand the architecture
   - Test locally first
   - Deploy to Vercel

2. 📚 **Learn Claude Agent SDK basics**
   - Read official docs: https://platform.claude.com/docs/en/agent-sdk
   - Try example agents
   - Understand tool calling

3. 🔧 **Customize the agent**
   - Modify system prompt
   - Add custom tools
   - Change UI styling

### Intermediate Track

1. 🐳 **Implement real sandboxing**
   - Choose sandbox provider (Modal/E2B)
   - Set up TypeScript service for Vercel
   - Test sandbox creation/cleanup

2. 🔌 **Add MCP tools**
   - Create custom MCP server
   - Integrate with agent
   - Test tool execution

3. 🎨 **Enhance user experience**
   - Add streaming responses
   - Implement session persistence
   - Show typing indicators

### Advanced Track

1. 🏢 **Production hardening**
   - Implement all security measures
   - Set up monitoring/alerting
   - Load testing and optimization

2. 🔐 **Add authentication**
   - User accounts
   - API key management
   - Rate limiting per user

3. 📊 **Multi-agent orchestration**
   - Specialized agents for different tasks
   - Agent handoff and collaboration
   - Shared context management

4. 🌐 **Scale to multi-region**
   - Deploy to multiple regions
   - Implement caching layer
   - Database for session persistence

---

## 📚 Additional Resources

### Official Documentation

- **Claude Agent SDK:** https://platform.claude.com/docs/en/agent-sdk
- **Vercel Sandbox:** https://vercel.com/docs/vercel-sandbox
- **Model Context Protocol:** https://modelcontextprotocol.io
- **FastAPI:** https://fastapi.tiangolo.com

### Sandbox Providers

- **Modal:** https://modal.com/docs
- **E2B:** https://e2b.dev/docs
- **Fly Machines:** https://fly.io/docs/machines
- **Cloudflare Sandboxes:** https://github.com/cloudflare/sandbox-sdk

### Security Resources

- **OWASP Top 10:** https://owasp.org/www-project-top-ten/
- **Container Security:** https://cheatsheetseries.owasp.org/cheatsheets/Container_Security_Cheat_Sheet.html
- **Claude Security Best Practices:** https://docs.anthropic.com/security

### Community

- **Anthropic Discord:** Check platform.anthropic.com for invite
- **MCP Discord:** Visit modelcontextprotocol.io
- **Vercel Community:** https://vercel.com/community

---

## 💡 Key Takeaways

### Architecture Insights

1. **Claude Agent SDK ≠ Traditional API**
   - It's a long-running process, not stateless
   - Requires container isolation
   - Maintains conversational state

2. **Vercel Sandbox Limitation**
   - TypeScript SDK only
   - Requires hybrid architecture for Python
   - Consider alternatives for Python-first projects

3. **Security First**
   - Always sandbox untrusted code
   - Implement defense in depth
   - Monitor and log everything

### Best Practices

1. **Start Simple**
   - Deploy basic version first
   - Add features incrementally
   - Test thoroughly at each stage

2. **Choose Right Pattern**
   - Ephemeral for most use cases
   - Long-running only if needed
   - Hybrid for cost optimization

3. **Monitor Costs**
   - Sandbox costs add up
   - Implement auto-cleanup
   - Set billing alerts

4. **Plan for Scale**
   - Design for horizontal scaling
   - Use caching aggressively
   - Implement circuit breakers

---

## 🤝 Contributing

Found issues or have improvements?

1. Test your changes locally
2. Document new features
3. Follow existing code style
4. Submit PR with clear description

---

## 📄 License

This guide and associated code are provided for educational purposes.

---

## 🎉 Congratulations!

You now understand how to deploy Claude Agent SDK to production with proper sandboxing, security, and scalability. This architecture pattern is used by companies deploying AI agents at scale.

**Key Achievement:** You can now build production-ready agentic applications!

**Next Challenge:** Build your own custom agent with unique tools and deploy it!

---

**Happy building! 🚀**

*For questions or issues, open an issue in the repository.*
