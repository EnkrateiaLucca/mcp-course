# Simple MCP Tutorial: 3-File Chat Application

A simplified tutorial demonstrating the Model Context Protocol (MCP) with OpenAI integration and a clean CLI chat interface.

## Files Overview

This tutorial consists of just 3 main files:

1. **`mcp_server_simple.py`** - MCP server with document management tools
2. **`mcp_client_simple.py`** - MCP client that integrates with OpenAI
3. **`chat_cli.py`** - Interactive chat interface using prompt_toolkit

## Features

### MCP Server (`mcp_server_simple.py`)
- **Tools**: Read, write, list, and search documents
- **Resources**: Access document list and content via URIs
- **Sample Data**: Pre-loaded with example documents

### MCP Client (`mcp_client_simple.py`)
- Connects to MCP server via stdio
- Integrates MCP tools with OpenAI function calling
- Handles tool execution and conversation flow

### Chat CLI (`chat_cli.py`)
- Beautiful terminal interface with prompt_toolkit
- Command support (`/help`, `/tools`, `/clear`, `/quit`)
- Persistent chat history
- Real-time tool execution display

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Run the chat interface**:
   ```bash
   python chat_cli.py
   ```

## Usage Examples

Once the chat is running, try these commands:

```
You: List all available documents

You: Read the content of notes.txt

You: Write a new document called "shopping.txt" with a grocery list

You: Search all documents for the word "project"
```

## Chat Commands

- `/help` - Show available commands
- `/tools` - Display MCP tools
- `/clear` - Clear conversation history
- `/quit` - Exit the application

## How It Works

1. **Server Start**: `mcp_server_simple.py` runs as a subprocess
2. **Client Connection**: `mcp_client_simple.py` connects via stdio transport
3. **Tool Integration**: OpenAI receives MCP tools as function definitions
4. **Conversation Flow**:
   - User sends message
   - OpenAI decides whether to use tools
   - If tools needed, client executes them on MCP server
   - Results are sent back to OpenAI for final response

## Educational Value

This simplified version teaches:
- Basic MCP server/client architecture
- Tool and resource definitions
- OpenAI function calling integration
- Async programming patterns
- CLI development with prompt_toolkit

Perfect for understanding MCP fundamentals without complex abstractions!