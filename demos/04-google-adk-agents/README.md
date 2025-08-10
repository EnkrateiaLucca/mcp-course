# Google ADK + MCP Integration Demo

This example demonstrates how to integrate MCP (Model Context Protocol) servers with Google's Agent Development Kit (ADK).

## Overview

The demo includes:
- A simple MCP server (`simple_mcp_server.py`) that provides basic tools
- An ADK agent (`adk_mcp_demo.py`) that connects to and uses the MCP server
- The original agent.py file showing the pattern for connecting to external MCP servers

## Files

1. **simple_mcp_server.py** - A basic MCP server providing three tools:
   - `get_current_time` - Returns current time in various formats
   - `calculate` - Performs mathematical calculations
   - `get_weather_info` - Returns simulated weather data

2. **adk_mcp_demo.py** - ADK agent that uses the MCP server tools
   - Shows the simplest integration pattern
   - Includes both demo and interactive modes

3. **adk-agent/agent.py** - Original example showing HTTP/SSE connection pattern

## Installation

```bash
# Install Google ADK
pip install google-adk

# Install MCP SDK
pip install mcp

# Install other dependencies
pip install python-dotenv rich
```

## Running the Demo

### Option 1: Run the automated demo
```bash
python adk_mcp_demo.py
```

### Option 2: Run interactive mode
```bash
python adk_mcp_demo.py --interactive
```

## Key Concepts

### MCPToolset Integration

The key to integrating MCP with ADK is the `MCPToolset` class:

```python
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

agent = LlmAgent(
    model="gemini-2.0-flash",
    tools=[
        MCPToolset(
            connection_params=StdioServerParameters(
                command="python",
                args=["simple_mcp_server.py"],
            )
        )
    ]
)
```

### Connection Types

1. **StdioServerParameters** - For local MCP servers (stdio communication)
2. **SseServerParams** - For HTTP/SSE based MCP servers

## How It Works

1. The ADK agent starts and initializes the MCPToolset
2. MCPToolset spawns the MCP server process and connects to it
3. The agent discovers available tools from the MCP server
4. When the agent needs to use a tool, MCPToolset proxies the call to the MCP server
5. Results are returned to the agent for processing

## Benefits

- **Separation of Concerns**: Tools can be developed independently as MCP servers
- **Reusability**: MCP servers can be used with any MCP-compatible client
- **Flexibility**: Easy to add/remove tools without modifying agent code
- **Standardization**: Uses the open MCP protocol for tool communication