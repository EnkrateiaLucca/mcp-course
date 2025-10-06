# Building AI Agents with MCP: Complete Course Materials

This repository contains all the demo code, examples, and hands-on materials for the O'Reilly Live Training course "Building AI Agents with MCP: The HTTP Moment of AI?"

## 🎯 Course Overview

The Model Context Protocol (MCP) is revolutionizing how AI applications connect to external tools and data sources. This course provides comprehensive, hands-on experience with MCP through practical demos and real-world examples.

### What You'll Learn

- **AI Agent Fundamentals**: Understanding agent architecture and decision-making patterns
- **MCP Core Concepts**: Architecture, capabilities, and protocol fundamentals
- **MCP Capabilities**: Tools, Resources, Prompts, and practical implementations
- **Agent Development**: Building agents with OpenAI SDK and MCP integration
- **Production Deployment**: Cloud hosting, API design, and security best practices
- **Real-world Applications**: Chat apps, image generation, and custom workflows

## 🚀 Quick Start with UV

### Using UV Package Manager (Recommended)

Most demo scripts in this course include UV inline metadata and can be run directly with [UV](https://github.com/astral-sh/uv), a fast Python package manager:

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run any demo script directly - UV handles dependencies automatically
uv run demos/01-introduction-to-mcp/mcp_server.py
uv run demos/03-tools-resources-prompts-sampling/comprehensive_mcp_server.py

# Or navigate to a demo directory and run
cd demos/02-first-mcp-server
uv run obsidian_vault_server.py
```

**Benefits of using UV:**
- No need to manage virtual environments manually
- Dependencies are installed automatically from inline script metadata
- Faster dependency resolution and installation
- Consistent environment across all demos

## 📁 Repository Structure

```
mcp-course/
├── README.md                           # This file - complete course guide
├── Makefile                            # Automation scripts
├── requirements/                       # Python dependencies
│   ├── requirements.txt                # All project dependencies
│   └── requirements.in                 # Source requirements file
├── presentation/                       # Course presentation materials
│   ├── presentation.html               # Main presentation
│   └── mcp-talk.pdf                    # PDF version
└── demos/                              # All demo materials organized by topic
    ├── 00-into-agents/                 # Introduction to AI agents
    ├── 01-introduction-to-mcp/         # MCP basics and first server
    ├── 02-study-case-anthropic-tools-resources-prompts-chat-app/  # Complete MCP chat app with tools
    ├── 03-personal-usecase-image-generation/  # Image generation MCP server
    ├── 04-openai-agents/               # OpenAI Agents SDK with MCP
    ├── 05-deployment-example/          # Production deployment example
    └── assets-resources/               # Images and supporting materials
```

## 🔧 Alternative Setup (Traditional Approach)

### Prerequisites

- **Python 3.10+** (Required for all demos)
- **Node.js 18+** (Required for some MCP servers)
- **Git** (For repository operations)

### API Keys Needed

Depending on which demos you want to run:

- [**OpenAI API Key**](https://platform.openai.com/docs/quickstart?api-mode=chat) (for OpenAI agent demos and chat app)
- [**Replicate API Key**](https://replicate.com/) (for image generation demo)

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/EnkrateiaLucca/mcp-course.git
cd mcp-course

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install base dependencies
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in the root directory:

```env
# API Keys (add the ones you have)
OPENAI_API_KEY=your-openai-api-key
REPLICATE_API_TOKEN=your-replicate-api-token

# Optional: Custom paths
MCP_DEMO_PATH=/path/to/your/demo/files
```

### 3. Quick Test

Test your setup with a basic MCP server:

```bash
cd demos/01-introduction-to-mcp
pip install -r requirements.txt
python mcp_server.py
```

## 🪟 Windows Setup Guide

Windows users need additional setup steps for MCP development. Follow this comprehensive guide for a smooth setup experience.

### Prerequisites for Windows

- **Windows 10/11** with Developer Mode enabled
- **Python 3.10+** from [python.org](https://www.python.org/downloads/) (ensure "Add to PATH" is checked)
- **Node.js 18+** from [nodejs.org](https://nodejs.org/)
- **Git for Windows** from [git-scm.com](https://git-scm.com/)
- **Windows Terminal** (recommended) from Microsoft Store

### 1. Enable Developer Mode

1. Open **Settings** → **Update & Security** → **For developers**
2. Select **Developer mode**
3. Restart your computer

### 2. Setup PowerShell Execution Policy

Open PowerShell as Administrator and run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Clone and Setup (Windows)

```cmd
# Clone the repository
git clone <repository-url>
cd mcp-course

# Create virtual environment
python -m venv venv

# Activate virtual environment (Command Prompt)
venv\Scripts\activate

# OR activate in PowerShell
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 4. Environment Variables (Windows)

Create a `.env` file in the project root:

```env
# API Keys
OPENAI_API_KEY=your-openai-api-key
REPLICATE_API_TOKEN=your-replicate-api-token

# Windows-specific paths (use forward slashes)
MCP_DEMO_PATH=C:/path/to/your/demo/files
```

Alternatively, set environment variables using Command Prompt:

```cmd
set OPENAI_API_KEY=your-openai-api-key
set REPLICATE_API_TOKEN=your-replicate-api-token
```

Or using PowerShell:

```powershell
$env:OPENAI_API_KEY="your-openai-api-key"
$env:REPLICATE_API_TOKEN="your-replicate-api-token"
```

### 5. Claude Desktop Configuration (Windows)

Claude Desktop config location on Windows:

```
%APPDATA%\Claude\claude_desktop_config.json
```

Example setup:

```cmd
# Navigate to Claude config directory
cd %APPDATA%\Claude

# Create or edit configuration
notepad claude_desktop_config.json
```

**Important**: Use absolute paths with forward slashes in the config file:

```json
{
  "mcpServers": {
    "mcp_demo": {
      "command": "C:/path/to/mcp-course/venv/Scripts/python.exe",
      "args": ["C:/path/to/mcp-course/demos/01-introduction-to-mcp/mcp_server.py"]
    }
  }
}
```

### 6. Windows-Specific Commands

When running demos, use these Windows-equivalent commands:

| Linux/macOS | Windows (CMD) | Windows (PowerShell) |
|-------------|---------------|----------------------|
| `source venv/bin/activate` | `venv\Scripts\activate` | `venv\Scripts\Activate.ps1` |
| `export VAR=value` | `set VAR=value` | `$env:VAR="value"` |
| `~/.config/Claude/` | `%APPDATA%\Claude\` | `$env:APPDATA\Claude\` |
| `python3` | `python` | `python` |

### 7. Testing on Windows

```cmd
# Activate virtual environment
venv\Scripts\activate

# Test basic server
cd demos\01-introduction-to-mcp
python mcp_server.py
```

### Windows Troubleshooting

**Common Windows Issues:**

1. **"python not found"**
   - Reinstall Python with "Add to PATH" checked
   - Or add Python manually to system PATH

2. **PowerShell execution policy errors**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
   ```

3. **Permission denied with npm/node**
   - Run terminal as Administrator
   - Or use `npm config set prefix "C:\Users\{username}\AppData\Roaming\npm"`

4. **Claude Desktop not finding MCP servers**
   - Use absolute paths in configuration
   - Ensure all backslashes are forward slashes in JSON
   - Check that Python executable path is correct: `C:\path\to\venv\Scripts\python.exe`

5. **Long path issues**
   - Enable long paths in Windows: `gpedit.msc` → Computer Configuration → Administrative Templates → System → Filesystem → Enable Win32 long paths

### Windows Development Tips

- Use **Windows Terminal** with PowerShell for better experience
- Consider **WSL2** for Linux-like environment if preferred
- Use **VS Code** with Python extension for development
- Set up **Windows Defender** exclusions for your development folder to improve performance

## 📚 Demo Sections Guide

### 00. Introduction to AI Agents

**What it covers**: Foundational concepts of AI agents - how they work, their components, and basic implementation patterns

**Files**:
- `intro-agents.ipynb` - Interactive Jupyter notebook with agent fundamentals

**Running**:
```bash
cd demos/00-into-agents

# Run with Jupyter
jupyter notebook intro-agents.ipynb

# Or use VS Code with Jupyter extension
code intro-agents.ipynb
```

**Key Learning**: Understanding agent architecture, reasoning patterns, and decision-making processes before diving into MCP.

---

### 01. Introduction to MCP

**What it covers**: MCP fundamentals, basic server implementation, and client interaction

**Files**:
- `mcp_server.py` - Basic MCP server with tools
- `mcp_client.py` - Test client for interaction
- `intro-mcp-walkthrough.md` - Step-by-step walkthrough
- `documents.txt` - Sample data file

**Running**:
```bash
cd demos/01-introduction-to-mcp

# With UV (recommended)
uv run mcp_server.py

# Or traditional method
pip install mcp
python mcp_server.py
```

**Key Learning**: Understanding MCP architecture and basic client-server communication.

---

### 02. MCP Chat Application Study Case

**What it covers**: Complete chat application integrating OpenAI function calling with MCP tools, resources, and prompts

**Files**:
- `chat_app.py` - Full-featured chat app with OpenAI integration
- `mcp_server.py` - MCP server with file tools
- `mcp_client.py` - MCP client wrapper
- `README.md` - Detailed documentation

**Running**:
```bash
cd demos/02-study-case-anthropic-tools-resources-prompts-chat-app

# Set up environment
export OPENAI_API_KEY="your-api-key"

# Run the chat app
uv run chat_app.py
```

**Key Learning**: Building production-ready applications that bridge OpenAI's function calling with MCP's capabilities.

---

### 03. Personal Use Case: Image Generation

**What it covers**: Real-world MCP server for generating thumbnails using Replicate AI

**Files**:
- `replicate_thumbnail_mcp.py` - MCP server for image generation
- `thumbnail_mcp.json` - Claude Desktop configuration

**Running**:
```bash
cd demos/03-personal-usecase-image-generation

# Configure Claude Desktop with the MCP server
cat thumbnail_mcp.json
# Add configuration to Claude Desktop settings

# Server runs automatically when Claude Desktop starts
```

**Key Learning**: Creating specialized MCP servers for specific workflows and integrating with AI image generation services.

---

### 04. OpenAI Agents

**What it covers**: OpenAI Agents SDK integration with MCP for enhanced tool capabilities

**Prerequisites**: OpenAI API key

**Files**:
- `intro-openai-agents-sdk.ipynb` - Interactive notebook tutorial
- `openai_agent_filesystem_mcp.py` - Agent with MCP filesystem access
- `openai_agent_custom_tools.py` - Custom tool integration examples
- `mcp_server_for_openai_agent.py` - Supporting MCP server

**Running**:
```bash
cd demos/04-openai-agents

# Set API key
export OPENAI_API_KEY="your-openai-api-key"

# Run Jupyter notebook
jupyter notebook intro-openai-agents-sdk.ipynb

# Or run standalone agent
uv run openai_agent_filesystem_mcp.py
```

**Key Learning**: Using OpenAI Agents SDK with MCP for structured data access and advanced tool usage.

---

### 05. Deployment Example

**What it covers**: Complete production deployment example with FastAPI, OpenAI agents, and MCP

**Prerequisites**: OpenAI API key, cloud platform account (Render.com recommended)

**Files**:
- `mcp_server.py` - Production MCP server with tools, resources, and prompts
- `agent.py` - OpenAI agent implementation
- `main.py` - FastAPI web wrapper
- `README.md` - Comprehensive deployment guide
- `setup.md` - Step-by-step setup instructions
- `security_auth_mcp.md` - Security best practices

**Running**:
```bash
cd demos/05-deployment-example

# Local development
export OPENAI_API_KEY="your-api-key"
python main.py  # Web API on http://localhost:8000
python agent.py # Interactive agent CLI

# See README.md for cloud deployment instructions
```

**Key Learning**: Production-ready MCP deployment with proper API design, security considerations, and cloud hosting.

## 🛠️ Automation with Makefile

The repository includes a Makefile for common tasks:

```bash
# Set up all environments
make setup-all

# Run all tests
make test-all

# Clean up all environments
make clean-all

# Start all demo servers
make start-servers

# Stop all demo servers
make stop-servers
```

## 🔧 Troubleshooting

### Common Issues

1. **"mcp module not found"**
   ```bash
   pip install mcp model-context-protocol
   ```

2. **"Permission denied" errors**
   ```bash
   chmod +x *.py
   ```

3. **Claude Desktop not recognizing MCP servers**
   - Check configuration file location: `~/.claude_desktop_config.json`
   - Verify server paths are absolute
   - Restart Claude Desktop after configuration changes

4. **API rate limiting**
   - Use API keys with sufficient quota
   - Implement rate limiting in custom servers
   - Add delays between requests in test scripts

### Getting Help

1. **Check the README** in each demo directory for specific instructions
2. **Review error logs** for detailed error messages
3. **Test MCP servers independently** before integrating with agents
4. **Use the MCP Inspector** tool for debugging:
   ```bash
   npx @modelcontextprotocol/inspector
   ```

## 📖 Additional Resources

### Official Documentation
- [MCP Specification](https://modelcontextprotocol.io/specification/)
- [MCP Documentation](https://modelcontextprotocol.io/introduction)
- [Official MCP Servers](https://github.com/modelcontextprotocol/servers)

### Agent Frameworks
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [Anthropic Claude](https://docs.anthropic.com/)

### Community Resources
- [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers)
- [MCP Community Examples](https://github.com/esxr/langgraph-mcp)
- [Glama MCP Directory](https://glama.ai/mcp)

## 🤝 Contributing

Found an issue or want to improve the demos? Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This course material is provided for educational purposes. Individual components may have their own licenses - please check specific directories for details.

## 🎓 Course Information

**Instructor**: Lucas Soares  
**Course**: Building AI Agents with MCP: The HTTP Moment of AI?  
**Platform**: O'Reilly Live Training  

### Connect with the Instructor
- 📚 [Blog](https://enkrateialucca.github.io/lucas-landing-page/)
- 🔗 [LinkedIn](https://www.linkedin.com/in/lucas-soares-969044167/)
- 🐦 [Twitter/X](https://x.com/LucasEnkrateia)
- 📺 [YouTube](https://www.youtube.com/@automatalearninglab)
- 📧 Email: lucasenkrateia@gmail.com

---

**Happy Learning! 🚀**

*The Model Context Protocol represents a significant step toward standardized AI-tool integration. Through these hands-on demos, you'll gain practical experience with this revolutionary technology that's shaping the future of AI applications.*
