# MCP Chat Application with Claude Tool Use

This application demonstrates how to integrate Claude's tool use capabilities with Model Context Protocol (MCP) servers.

## Features

- **Claude Tool Use**: The AI assistant automatically determines when to use available tools
- **MCP Tool Integration**: Seamlessly bridges Claude tool use to MCP server tools
- **Interactive Chat**: Natural conversation interface with automatic tool usage
- **Tool Discovery**: Automatically discovers and converts MCP tools to Claude tool format

## Setup

1. **Install Dependencies**:
   ```bash
   pip install anthropic python-dotenv mcp
   ```

2. **Configure API Keys**:
   Edit the `.env` file and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY="your-api-key-here"
   ANTHROPIC_MODEL="claude-3-5-sonnet-20241022"  # or any other Claude model
   USE_UV=0  # Set to 1 if using uv package manager
   ```

3. **Run the Application**:
   ```bash
   python chat_app.py
   ```

## How It Works

1. **MCP Tool Discovery**: On startup, the app connects to the MCP server and discovers available tools
2. **Tool Conversion**: MCP tool definitions are automatically converted to Claude tool schemas
3. **Intelligent Tool Usage**: When you chat with the assistant, it automatically decides when to use tools
4. **Seamless Execution**: Tool use requests from Claude are executed through the MCP client and results are returned to the conversation

## Available Commands

- `/tools` - List all available MCP tools
- `/clear` - Clear the conversation history
- `/help` - Show available commands
- `/exit` or `/quit` - Exit the application

## Example Usage

```
You> What's in the file.txt?
[Calling tool: read_doc with args: {'filepath': 'file.txt'}]
Assistant> The file contains: "Lucas will never leave anyone behind!"

You> Write "Hello World" to a new file called greeting.txt
[Calling tool: write_file with args: {'filepath': 'greeting.txt', 'contents': 'Hello World'}]
Assistant> I've successfully written "Hello World" to greeting.txt.
```

## Architecture

```
User <-> Chat App <-> Claude API
             |
             v
        MCP Client
             |
             v
        MCP Server (with tools)
```

The chat app acts as a bridge:
- Receives user input
- Sends it to Claude with available tool definitions
- Claude decides if/which tools to call
- App executes tools via MCP client
- Results are sent back to Claude for final response

## MCP Server

The included `mcp_server.py` provides two example tools:
- `read_doc`: Read contents of a file
- `write_file`: Write contents to a file

You can extend the MCP server with additional tools using the `@mcp.tool()` decorator.
