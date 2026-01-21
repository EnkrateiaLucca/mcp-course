# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is an O'Reilly Live Training course repository: "Building AI Agents with MCP: The HTTP Moment of AI?" It contains hands-on demos and examples for learning the Model Context Protocol (MCP) and AI agent development.

## Development Setup

### Package Manager
- **Primary method**: Use UV package manager (recommended)
- Most Python scripts include inline UV metadata headers with dependencies
- Run scripts directly with: `uv run <script_name>.py`
- No need to manage virtual environments when using UV

### Traditional Setup (Alternative)
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install base dependencies
pip install -r requirements/requirements.txt
```

### Environment Variables
Required API keys (depending on which demos you run):
- `OPENAI_API_KEY` - For OpenAI agent demos and chat applications
- `REPLICATE_API_TOKEN` - For image generation demos

Create `.env` file in root directory with these keys.

## Common Commands

### Running Demos
```bash
# Run any demo with UV (handles dependencies automatically)
uv run demos/01-introduction-to-mcp/mcp_server.py
uv run demos/04-query-tabular-data/csv_query_mcp_server.py

# Run MCP Inspector for debugging
mcp dev <path-to-mcp-server.py>
```

### Makefile Commands
```bash
make conda-create          # Create conda environment
make env-setup            # Setup environment with pip-tools and uv
make notebook-setup       # Install Jupyter kernel
make env-update          # Update dependencies from requirements.in
make freeze              # Freeze current dependencies
make clean               # Remove conda environment
```

### Testing
```bash
# Run tests in deployment example
cd demos/05-deployment-example
python test_deployment.py
python test_task_creation.py
```

## Project Architecture

### Demo Organization
Demos are organized sequentially by learning progression:

1. **00-intro-agents/** - AI agent fundamentals and architecture
2. **01-introduction-to-mcp/** - Basic MCP server/client implementation using FastMCP
3. **02-study-case-anthropic-tools-resources-prompts-chat-app/** - Complete chat app integrating OpenAI function calling with MCP
4. **03-claude-agents-sdk-filesystem-agent/** - Claude Agent SDK with filesystem operations via MCP servers
5. **04-query-tabular-data/** - CSV/tabular data querying with MCP tools, plus image generation
6. **05-deployment-example/** - Production deployment with FastAPI, OpenAI agents, and MCP
7. **06-deploy-simple-agent-mcp-vercel/** - Serverless deployment to Vercel using MCP HTTP transport

### MCP Server Patterns

**FastMCP (Recommended for most demos)**:
- Import: `from mcp.server.fastmcp import FastMCP`
- Declarative tool/resource definition with decorators
- Automatic schema generation from Python types
- Built-in transport support (stdio, SSE)

**Typical MCP Server Structure**:
```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["mcp[cli]>=1.0.0"]
# ///

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("server-name")

@mcp.tool()
def tool_function(param: type) -> return_type:
    """Tool description for LLM"""
    # Implementation
    return result

@mcp.resource("uri://resource-path")
def get_resource() -> str:
    """Resource description"""
    return data

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### Agent Integration Patterns

**Claude Agent SDK** (demos/03-*):
- In-process MCP servers for better performance
- Tool permissions and callbacks for security
- Response handling with streaming support
- Error handling with PreToolUse/PostToolUse hooks

**OpenAI Agents SDK** (demos/02-*, 05-*, 06-*):
- MCP client wraps MCP server communication
- Converts MCP tools to OpenAI function calling format
- Agent loops handle tool execution and response processing

### Deployment Architecture (demos/05-*, 06-*)

**Key Components**:
- **MCP Server**: Provides tools/resources via stdio or HTTP
- **Agent**: OpenAI/Claude Agent SDK with tool execution
- **FastAPI Wrapper**: Web API layer for HTTP requests
- **Client Interface**: HTML/JavaScript frontend

**Transport Modes**:
- `stdio`: Local development, subprocess communication
- `sse`: Server-Sent Events for streaming
- HTTP: Production deployment (requires MCP HTTP transport)

## Development Guidelines

### When Creating MCP Servers
- Always use UV inline script metadata for dependencies
- Include descriptive tool/resource descriptions (visible to LLM)
- Use type hints for automatic schema generation
- Test with MCP Inspector: `mcp dev <server_path>`

### When Creating Agents
- Validate file paths to prevent directory traversal
- Implement permission callbacks for security-sensitive operations
- Use streaming for long-running operations
- Log tool usage for debugging and auditing

### Security Considerations
- Never commit API keys (already in .gitignore as `.env`)
- Validate all user inputs in tools
- Use least-privilege principle for tool permissions
- Implement PreToolUse hooks to block dangerous operations

## Key Files and Directories

- `requirements/requirements.txt` - All Python dependencies (auto-generated from requirements.in)
- `requirements/requirements.in` - Source requirements file
- `Makefile` - Environment setup and management automation
- `presentation/` - Course presentation materials
- `mcp-builder-skill/` - Claude skill for building MCP servers
- `.env` - API keys (not committed, create manually)

## Testing MCP Servers

### With MCP Inspector (Recommended)
```bash
mcp dev <path-to-server.py>
# Opens web interface to test tools and resources interactively
```

### With Claude Desktop
1. Edit `~/.config/Claude/claude_desktop_config.json` (macOS/Linux)
   or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
2. Add server configuration:
```json
{
  "mcpServers": {
    "server-name": {
      "command": "uv",
      "args": ["run", "/absolute/path/to/server.py"]
    }
  }
}
```
3. Restart Claude Desktop

## Common Patterns

### Error Handling in Tools
```python
@mcp.tool()
def safe_operation(path: str) -> str:
    try:
        # Validate inputs
        if not is_safe_path(path):
            raise ValueError("Invalid path")
        # Perform operation
        return result
    except Exception as e:
        return f"Error: {str(e)}"
```

### Resource with Dynamic Content
```python
@mcp.resource("data://{key}")
def get_data(key: str) -> str:
    """Dynamic resource based on URI parameter"""
    return load_data(key)
```

### Agent with Tool Execution
```python
# OpenAI Agents SDK pattern
from agents import Agent, tool

@tool
def custom_tool(input: str) -> str:
    """Tool available to agent"""
    return process(input)

agent = Agent(
    name="helper",
    instructions="System instructions",
    tools=[custom_tool],
    model="gpt-4o"
)

response = agent.run_sync("Task for agent")
```

## Troubleshooting

### "mcp module not found"
```bash
pip install mcp model-context-protocol
# Or with UV: uv add mcp
```

### "Permission denied" on script execution
```bash
chmod +x script.py
```

### Claude Desktop not recognizing servers
- Use absolute paths in configuration
- Verify UV is in PATH
- Check server logs for errors
- Restart Claude Desktop after config changes

### API rate limiting
- Check API key quotas
- Implement exponential backoff
- Add request delays in loops

## Additional Resources

- [MCP Specification](https://modelcontextprotocol.io/specification/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
