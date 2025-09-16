# MCP Chat Application with OpenAI Function Calling

This application demonstrates how to integrate OpenAI's function calling capabilities with Model Context Protocol (MCP) servers.

## Features

- **OpenAI Function Calling**: The AI assistant automatically determines when to use available tools
- **MCP Tool Integration**: Seamlessly bridges OpenAI function calls to MCP server tools
- **Interactive Chat**: Natural conversation interface with automatic tool usage
- **Tool Discovery**: Automatically discovers and converts MCP tools to OpenAI functions

## Setup

1. **Install Dependencies**:
   ```bash
   pip install openai python-dotenv mcp
   ```

2. **Configure API Keys**:
   Edit the `.env` file and add your OpenAI API key:
   ```
   OPENAI_API_KEY="your-api-key-here"
   OPENAI_MODEL="gpt-4-turbo-preview"  # or any other model that supports function calling
   USE_UV=0  # Set to 1 if using uv package manager
   ```

3. **Run the Application**:
   ```bash
   python chat_app.py
   ```

## How It Works

1. **MCP Tool Discovery**: On startup, the app connects to the MCP server and discovers available tools
2. **Tool Conversion**: MCP tool definitions are automatically converted to OpenAI function schemas
3. **Intelligent Tool Usage**: When you chat with the assistant, it automatically decides when to use tools
4. **Seamless Execution**: Function calls from OpenAI are executed through the MCP client and results are returned to the conversation

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
User <-> Chat App <-> OpenAI API
             |
             v
        MCP Client
             |
             v
        MCP Server (with tools)
```

The chat app acts as a bridge:
- Receives user input
- Sends it to OpenAI with available tool definitions
- OpenAI decides if/which tools to call
- App executes tools via MCP client
- Results are sent back to OpenAI for final response

## MCP Server

The included `mcp_server.py` provides two example tools:
- `read_doc`: Read contents of a file
- `write_file`: Write contents to a file

You can extend the MCP server with additional tools using the `@mcp.tool()` decorator.