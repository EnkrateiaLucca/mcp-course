# Building AI Agents with MCP: Complete Course Materials

This repository contains all the demo code, examples, and hands-on materials for the O'Reilly Live Training course "Building AI Agents with MCP: The HTTP Moment of AI?"

## 🎯 Course Overview

The Model Context Protocol (MCP) is revolutionizing how AI applications connect to external tools and data sources. This course provides comprehensive, hands-on experience with MCP through practical demos and real-world examples.

### What You'll Learn

- **MCP Fundamentals**: Core concepts, architecture, and capabilities
- **MCP Capabilities**: Tools, Resources, Prompts, and Sampling
- **Agent Development**: Building agents with Google ADK, and OpenAI SDK
- **Consumer Applications**: Using MCP with Claude Desktop and Cursor IDE
- **Security Best Practices**: Securing MCP implementations and preventing attacks

## 🚀 Quick Start with UV

### Using UV Package Manager (Recommended)

Most demo scripts in this course include UV inline metadata and can be run directly with [UV](https://github.com/astral-sh/uv), a fast Python package manager:

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run any demo script directly - UV handles dependencies automatically
uv run notebooks/01-introduction-to-mcp/mcp_server.py
uv run notebooks/03-tools-resources-prompts-sampling/comprehensive_mcp_server.py

# Or navigate to a demo directory and run
cd notebooks/02-first-mcp-server
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
├── Makefile                           # Automation scripts
├── presentation/                      # Course presentation materials
│   ├── presentation.html              # Main presentation
│   ├── mcp-talk.pdf                  # PDF version
│   └── anki-mcp.txt                  # Study materials
└── notebooks/                        # All demo materials organized by topic
    ├── 01-introduction-to-mcp/       # MCP basics and first server
    ├── 02-first-mcp-server/          # Building your first MCP server
    ├── 03-tools-resources-prompts-sampling/  # Core MCP capabilities
    ├── 04-google-adk-agents/         # Google Agent Development Kit demos
    ├── 05-openai-agents/             # OpenAI Agents SDK with MCP
    ├── 06-claude-desktop-cursor-demos/  # Consumer app integration
    ├── 07-security-tips/             # Security best practices
    └── assets-resources/             # Images and supporting materials
```

## 🔧 Alternative Setup (Traditional Approach)

### Prerequisites

- **Python 3.10+** (Required for all demos)
- **Node.js 18+** (Required for some MCP servers)
- **Git** (For repository operations)

### API Keys Needed

Depending on which demos you want to run:

- [**OpenAI API Key**](https://platform.openai.com/docs/quickstart?api-mode=chat) (for OpenAI demos)
- [**Anthropic API Key**](https://docs.anthropic.com/en/docs/get-started) (for Claude-based demos)
- [**Google Cloud Project**](https://arc.net/l/quote/pyqkrzxd) (for ADK demos)

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
ANTHROPIC_API_KEY=your-anthropic-api-key
GOOGLE_CLOUD_PROJECT=your-google-cloud-project-id

# Optional: Custom paths
MCP_DEMO_PATH=/path/to/your/demo/files
```

### 3. Quick Test

Test your setup with a basic MCP server:

```bash
cd notebooks/01-introduction-to-mcp
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
ANTHROPIC_API_KEY=your-anthropic-api-key
GOOGLE_CLOUD_PROJECT=your-google-cloud-project-id

# Windows-specific paths (use forward slashes)
MCP_DEMO_PATH=C:/path/to/your/demo/files
```

Alternatively, set environment variables using Command Prompt:

```cmd
set OPENAI_API_KEY=your-openai-api-key
set ANTHROPIC_API_KEY=your-anthropic-api-key
```

Or using PowerShell:

```powershell
$env:OPENAI_API_KEY="your-openai-api-key"
$env:ANTHROPIC_API_KEY="your-anthropic-api-key"
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

# Copy and edit configuration
copy "C:\path\to\mcp-course\notebooks\02-first-mcp-server\claude_desktop_config.json" claude_desktop_config.json
```

**Important**: Use absolute paths with forward slashes in the config file:

```json
{
  "mcpServers": {
    "weather": {
      "command": "C:/path/to/mcp-course/venv/Scripts/python.exe",
      "args": ["C:/path/to/mcp-course/notebooks/02-first-mcp-server/weather_server.py"]
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
cd notebooks\01-introduction-to-mcp
pip install -r requirements.txt
python basic_server.py
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

### 01. Introduction to MCP

**What it covers**: MCP fundamentals, basic server implementation, client interaction

**Files**:
- `basic_server.py` - Minimal MCP server
- `test_client.py` - Test client for interaction
- `README.md` - Detailed explanation

**Running**:
```bash
cd notebooks/01-introduction-to-mcp
pip install -r requirements.txt

# Terminal 1: Start the server
python basic_server.py

# Terminal 2: Test with client
python test_client.py
```

**Key Learning**: Understanding MCP architecture and basic client-server communication.

---

### 02. First MCP Server

**What it covers**: Building a practical MCP server with Claude Desktop integration for real-world workflows

**Files**:
- `weather_server.py` - MCP server with weather and file management tools
- `claude_desktop_config.json` - Configuration for Claude Desktop
- `README.md` - Detailed setup and usage instructions

**Running**:
```bash
cd notebooks/02-first-mcp-server

# Start the weather server
python weather_server.py

# Configure Claude Desktop (copy and edit the config)
cp claude_desktop_config.json ~/.config/Claude/claude_desktop_config.json
# Restart Claude Desktop to load the new configuration
```

**Key Learning**: Creating practical MCP servers for end-user workflows with Claude Desktop.

---

### 03. Tools, Resources, Prompts & Sampling

**What it covers**: All four core MCP capabilities with comprehensive examples

**Files**:
- `comprehensive_mcp_server.py` - Server implementing all capabilities
- `test_client.py` - Client testing all capabilities
- `README.md` - Detailed capability explanations

**Running**:
```bash
cd notebooks/03-tools-resources-prompts-sampling
pip install -r requirements.txt

# Terminal 1: Start comprehensive server
python comprehensive_mcp_server.py

# Terminal 2: Test all capabilities
python test_client.py
```

**Key Learning**: Deep dive into MCP's four core capabilities and their use cases.

---

### 04. Google ADK Agents

**What it covers**: Integrating MCP servers with Google's Agent Development Kit (ADK) using MCPToolset

**Prerequisites**: Google Cloud account and project

**Files**:
- `simple_mcp_server.py` - Sample MCP server for testing
- `adk-agent/agent.py` - ADK agent implementation with MCP integration
- `README.md` - Detailed setup instructions

**Running**:
```bash
cd notebooks/04-google-adk-agents

# Set up Google Cloud credentials
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Start the MCP server
python simple_mcp_server.py

# In another terminal, run the ADK agent
cd adk-agent
python agent.py
```

**Key Learning**: Using MCPToolset to connect Google ADK agents with MCP servers for interoperability.

---

### 05. OpenAI Agents

**What it covers**: OpenAI agent integration with MCP for file access capabilities

**Prerequisites**: OpenAI API key

**Files**:
- `basic_agent_file_access.py` - OpenAI agent with file access via MCP
- `sample_files/` - Sample markdown files for testing
  - `books.md` - Book recommendations
  - `music.md` - Music playlists

**Running**:
```bash
cd notebooks/05-openai-agents

# Set API key
export OPENAI_API_KEY="your-openai-api-key"

# Run the agent with file access
python basic_agent_file_access.py
```

**Key Learning**: Using OpenAI agents with MCP for structured file access and data retrieval.

---

### 06. Claude Desktop & Cursor Demos

**What it covers**: Advanced consumer application integration with Claude Desktop and Cursor IDE

**Prerequisites**: Claude Desktop app installed

**Files**:
- `development_mcp_server.py` - Development-focused MCP server
- `mcp_demo_workflow.py` - Workflow automation examples
- `claude_desktop_configs/` - Multiple configuration examples
  - `basic.json` - Basic configuration
  - `development.json` - Development environment setup
  - `production.json` - Production-ready configuration
- `README.md` - Detailed setup and usage guide

**Running**:
```bash
cd notebooks/06-claude-desktop-cursor-demos

# Start development server
python development_mcp_server.py

# Configure Claude Desktop (choose a config)
cp claude_desktop_configs/development.json ~/.config/Claude/claude_desktop_config.json

# Restart Claude Desktop to load new configuration
```

**Key Learning**: Real-world "end-user" experience with MCP in consumer applications, including tips and best practices.

---

### 07. Security Tips

**What it covers**: Comprehensive security guide for MCP implementations

**Files**:
- `README.md` - Complete security guide covering:
  - Tool poisoning attacks and mitigations
  - Prompt injection vulnerabilities
  - Privilege escalation risks
  - Directory traversal and command injection
  - Information disclosure vulnerabilities
  - Security best practices for servers and clients
  - Pre/during/post-deployment security checklists

**Key Learning**: Understanding critical security considerations for production MCP deployments, including common attack vectors and mitigation strategies.

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
- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)

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
