# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Environment Setup
```bash
# Complete setup with Conda
make all                    # Creates conda env, installs deps, sets up notebooks

# Alternative: Python virtual environment
python -m venv venv
source venv/bin/activate    # Linux/macOS
pip install -r requirements.txt
```

### Running MCP Servers
```bash
# Basic server (Demo 1)
cd notebooks/01-introduction-to-mcp
python basic_server.py      # Terminal 1
python test_client.py       # Terminal 2

# Weather server (Demo 2)
cd notebooks/02-first-mcp-server
python weather_server.py

# Comprehensive server (Demo 3)
cd notebooks/03-tools-resources-prompts-sampling
python comprehensive_mcp_server.py    # Terminal 1
python test_client.py                 # Terminal 2

# MCP Inspector for debugging
mcp dev ./basic_server.py
```

### Agent Integration
```bash
# Google ADK Agent (Demo 4)
cd notebooks/04-google-adk-agents
export GOOGLE_CLOUD_PROJECT="your-project-id"
python simple_mcp_server.py           # Terminal 1
cd adk-agent && python agent.py       # Terminal 2

# OpenAI Agent (Demo 5)
cd notebooks/05-openai-agents
export OPENAI_API_KEY="your-key"
python basic_agent_file_access.py
```

## Architecture

This is an O'Reilly Live Training course demonstrating the Model Context Protocol (MCP) through progressive demos.

### MCP Architecture Pattern
- **MCP Servers**: Lightweight programs exposing capabilities through standardized protocol
- **MCP Clients**: Protocol clients maintaining 1:1 connections with servers
- **MCP Hosts**: Programs like Claude Desktop that access data through MCP
- **Transport**: HTTP (streamable-http) or stdio for direct connections

### Server Implementation Patterns

**FastMCP Server Pattern (HTTP Transport):**
```python
from fastmcp import FastMCP
mcp = FastMCP(server_name)

@mcp.tool()
async def tool_name(param: str) -> str:
    # Tool implementation
    
# Run with: mcp.run(port=8020, transport="stdio")
```

**Comprehensive Server (All 4 MCP Capabilities):**
- **Tools**: Model-controlled executable functions via `@server.call_tool()`
- **Resources**: Application-controlled data access via `@server.list_resources()`
- **Prompts**: User-controlled templates via `@server.list_prompts()`
- **Sampling**: Server-initiated LLM interactions via `@server.create_message()`

### Client Integration Patterns

**Direct MCP Client:**
```python
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async with streamablehttp_client(server_url) as (read, write, _):
    async with ClientSession(read, write) as session:
        await session.initialize()
        result = await session.call_tool("tool_name", {})
```

**Claude Desktop Configuration:**
Location: `~/.config/Claude/claude_desktop_config.json`
```json
{
  "mcpServers": {
    "server_name": {
      "command": "python",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```

## Course Structure

Progressive learning path through 7 demos:
1. `01-introduction-to-mcp/` - MCP fundamentals
2. `02-first-mcp-server/` - Practical weather/file server
3. `03-tools-resources-prompts-sampling/` - All 4 MCP capabilities
4. `04-google-adk-agents/` - Google ADK integration
5. `05-openai-agents/` - OpenAI Agents SDK
6. `06-claude-desktop-cursor-demos/` - Consumer app integration
7. `07-security-tips/` - Security best practices

## Key Dependencies

- **mcp[cli]==1.9.3** - Core MCP SDK
- **fastapi/uvicorn** - HTTP transport
- **google-adk** - Google Agent Development Kit
- **openai-agents** - OpenAI Agents SDK

## Development Notes

- Each demo has its own `requirements.txt`
- Test servers using accompanying `test_client.py` scripts
- MCP Inspector available for debugging: `mcp dev ./server.py`
- Environment variables needed: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_CLOUD_PROJECT`
- Windows users: PowerShell scripts and specific setup instructions in README