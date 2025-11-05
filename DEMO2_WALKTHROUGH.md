# Demo 2: MCP Server and Client Code Walkthrough

## Overview

Demo 2 showcases a complete Model Context Protocol (MCP) implementation with a chat application interface. This demo demonstrates how to create an MCP server that exposes tools and resources, and an MCP client that connects to and interacts with the server.

**Location**: `/demos/02-study-case-anthropic-tools-resources-prompts-chat-app/`

**Key Components**:
- `mcp_server.py` - MCP server that exposes file operations as tools and resources
- `mcp_client.py` - MCP client wrapper for connecting to and using the server
- `chat_app.py` - Chat interface that bridges OpenAI function calling with MCP tools

---

## MCP Server Walkthrough (`mcp_server.py`)

### Initialization

```python
from mcp.server.fastmcp import FastMCP
from glob import glob

mcp = FastMCP("lucas-never-quits-mcp")
DOCS_PATH = "./docs"
```

**Line 1-4**: The server uses `FastMCP`, a simplified framework for building MCP servers. The server is named `"lucas-never-quits-mcp"` and defines a constant path for document storage.

### Tool 1: Reading Documents

```python
@mcp.tool(
    name="read_doc",
    description="Function to read documents"
)
def read_doc(filepath: str) -> str:
    """Read the contents of a file at the specified filepath."""
    with open(filepath, "r") as f:
        return f.read()
```

**Lines 8-15**: The `@mcp.tool()` decorator registers a function as an MCP tool. This makes it:
- **Discoverable**: Clients can list and find this tool
- **Callable**: Clients can execute it remotely
- **Documented**: The name and description are exposed to clients

The `read_doc` function simply reads and returns file contents. MCP handles the serialization and transport automatically.

### Tool 2: Writing Files

```python
@mcp.tool(
    name='write_file',
    description='Function that writes to file'
)
def write_file(filepath: str, contents: str) -> str:
    """Write contents to a file at the specified filepath."""
    with open(filepath, "w") as f:
        f.write(contents)
    return f"File written successfully to: {filepath}"
```

**Lines 17-26**: Similar to `read_doc`, this tool is registered with the `@mcp.tool()` decorator. It accepts two parameters (filepath and contents) and returns a success message. The function signature automatically becomes the tool's schema.

### Resource 1: List Documents

```python
@mcp.resource(f"docs://documents/{DOCS_PATH}", mime_type="text/plain")
def list_docs() -> list[str]:
    return glob(f"{DOCS_PATH}/*.md")
```

**Lines 28-30**: The `@mcp.resource()` decorator exposes data as MCP resources. Resources differ from tools:
- **Tools** are actions (functions that do something)
- **Resources** are data endpoints (expose information)

This resource provides a list of all markdown files in the docs folder. The URI scheme `docs://documents/...` creates a unique identifier for this resource.

### Resource 2: Fetch Specific Document

```python
@mcp.resource("docs://documents/{doc_name}", mime_type="text/plain")
def fetch_doc(doc_name: str) -> str:
    """Fetch a document from the docs folder by name."""
    filepath = f"{DOCS_PATH}/{doc_name}"
    try:
        with open(filepath, "r") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: Document '{doc_name}' not found in docs folder"
```

**Lines 32-40**: This resource demonstrates dynamic URIs with the `{doc_name}` parameter. It:
- Takes a document name as a parameter
- Returns the document contents
- Handles errors gracefully with try/except

### Server Execution

```python
if __name__ == "__main__":
    mcp.run(transport='stdio')
```

**Lines 42-43**: When run directly, the server starts with `stdio` transport (communication via standard input/output). This is perfect for local development and process-based communication.

---

## MCP Client Walkthrough (`mcp_client.py`)

### Class Structure and Initialization

```python
class MCPClient:
    def __init__(self, command: str, args: list[str],
                 env: Optional[dict[str, str]]=None):
        self._command = command
        self._args = args
        self._session: Optional[ClientSession] = None
        self._exit_stack: AsyncExitStack = AsyncExitStack()
        self._env = env
```

**Lines 8-15**: The `MCPClient` class wraps the MCP client SDK to provide a cleaner interface. Key components:
- `command` and `args`: Used to spawn the MCP server process (e.g., `python mcp_server.py`)
- `_session`: The active MCP connection (initially None)
- `_exit_stack`: Manages async context cleanup (ensures proper resource disposal)
- `_env`: Optional environment variables for the server process

### Connecting to the Server

```python
async def connect(self):
    server_params = StdioServerParameters(
        command=self._command,
        args=self._args,
        env=self._env,
    )
    stdio_transport = await self._exit_stack.enter_async_context(
        stdio_client(server_params)
    )
    _stdio, _write = stdio_transport
    self._session = await self._exit_stack.enter_async_context(
        ClientSession(_stdio, _write)
    )
    await self._session.initialize()
```

**Lines 17-30**: The connection process involves several steps:

1. **Create Server Parameters** (lines 18-22): Configure how to launch the server process
2. **Establish Transport** (lines 23-25): Create stdio communication channels
   - `stdio_client()` spawns the server process and connects via stdin/stdout
   - `enter_async_context()` ensures cleanup on exit
3. **Create Session** (lines 26-29): Wrap the transport in a ClientSession
   - The session handles MCP protocol details (requests, responses, serialization)
4. **Initialize** (line 30): Perform MCP handshake and capability negotiation

### Session Access

```python
def session(self) -> ClientSession:
    if self._session is None:
        raise ConnectionError(
            "Client session not initialized or cache not populated. "
            "Call connect_to_server first."
        )
    return self._session
```

**Lines 32-37**: This getter method provides safe access to the session with error handling. It ensures you don't try to use the client before connecting.

### Listing Available Tools

```python
async def list_tools(self) -> list[types.Tool]:
    result = await self.session().list_tools()
    return result.tools
```

**Lines 40-42**: This method queries the server for available tools. The server responds with tool definitions including:
- Tool names
- Descriptions
- Parameter schemas (automatically derived from function signatures)

### Calling Tools

```python
async def call_tool(
    self, tool_name: str, tool_input
) -> types.CallToolResult | None:
    return await self.session().call_tool(tool_name, tool_input)
```

**Lines 44-47**: This method executes a tool on the server:
- `tool_name`: The name of the tool to call (e.g., "read_doc")
- `tool_input`: A dictionary of parameters (e.g., `{"filepath": "test.txt"}`)
- Returns the tool's result wrapped in a `CallToolResult` object

### Cleanup

```python
async def cleanup(self):
    await self._exit_stack.aclose()
    self._session = None
```

**Lines 49-51**: Proper cleanup:
- Closes all async contexts (session and transport)
- Terminates the server process
- Resets the session to None

### Context Manager Support

```python
async def __aenter__(self):
    await self.connect()
    return self

async def __aexit__(self, exc_type, exc_val, exc_tb):
    await self.cleanup()
```

**Lines 53-58**: Implements async context manager protocol (Python's `async with` statement). This ensures:
- Automatic connection when entering the context
- Automatic cleanup when exiting (even if errors occur)
- Clean, pythonic usage pattern

### Test Example

```python
async def main():
    async with MCPClient(
        command="python",
        args=["./mcp_server.py"],
    ) as client:
        # List available tools
        tools = await client.list_tools()
        print("Available tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")

        # Test reading a file
        result = await client.call_tool("read_doc", {"filepath": "./file.txt"})
        if result:
            print(f"\nFile contents: {result.content}")

        # Test writing a file
        result = await client.call_tool("write_file", {
            "filepath": "./test_output.txt",
            "contents": "Hello from MCP client!"
        })
        if result:
            print(f"\nWrite result: {result.content}")
```

**Lines 62-84**: A complete example demonstrating:
1. Creating a client that spawns `python mcp_server.py`
2. Using the context manager for automatic setup/cleanup
3. Discovering available tools
4. Calling the `read_doc` tool
5. Calling the `write_file` tool

---

## How They Work Together

### 1. Server Startup

When `mcp_server.py` runs:
```
python mcp_server.py
```
It starts listening on stdin/stdout for MCP protocol messages.

### 2. Client Connection

When the client connects:
```python
async with MCPClient(command="python", args=["./mcp_server.py"]) as client:
```

The following happens:
1. Client spawns server as subprocess
2. Client sends initialization message
3. Server responds with capabilities
4. Handshake completes

### 3. Tool Discovery

```python
tools = await client.list_tools()
```

**Message Flow**:
```
Client → Server: "list_tools" request
Server → Client: Tool definitions (read_doc, write_file)
```

### 4. Tool Execution

```python
result = await client.call_tool("read_doc", {"filepath": "file.txt"})
```

**Message Flow**:
```
Client → Server: "call_tool" request with name="read_doc" and params
Server: Executes read_doc("file.txt")
Server → Client: Returns file contents
```

### 5. Integration with Chat App

The `chat_app.py` uses this client to bridge OpenAI and MCP:

```
User Input → OpenAI API (with MCP tools as functions)
                ↓
         OpenAI decides to call a function
                ↓
         Chat App intercepts function call
                ↓
         MCP Client executes tool on server
                ↓
         Result sent back to OpenAI
                ↓
         OpenAI generates final response
                ↓
         Response shown to user
```

---

## Key Concepts

### Tools vs Resources

**Tools** (`@mcp.tool()`):
- Actions or operations
- Can have side effects (write files, make API calls)
- Like function calls
- Examples: `read_doc`, `write_file`

**Resources** (`@mcp.resource()`):
- Data endpoints
- Read-only by convention
- Like REST API endpoints
- Examples: `list_docs`, `fetch_doc`

### Transport: Stdio

The stdio transport uses:
- **stdin**: Client sends requests
- **stdout**: Server sends responses
- **Process-based**: Client spawns server as subprocess

This is simple and works well for local development but requires one server process per client.

### Async/Await Pattern

MCP is built on async Python:
- All I/O operations are non-blocking
- Multiple operations can run concurrently
- The `AsyncExitStack` ensures proper cleanup

### Type Safety

Both files use Python type hints:
- Function parameters are typed (`filepath: str`)
- Return types are specified (`-> str`)
- MCP uses these to generate schemas automatically

---

## Testing the Code

To test the server and client independently:

```bash
# Terminal 1: Start the server manually
cd demos/02-study-case-anthropic-tools-resources-prompts-chat-app
python mcp_server.py

# Terminal 2: Run the client test
python mcp_client.py
```

Or use the integrated chat app:

```bash
python chat_app.py
```

---

## Summary

**MCP Server** (`mcp_server.py`):
- Uses FastMCP framework
- Exposes 2 tools: `read_doc`, `write_file`
- Exposes 2 resources: `list_docs`, `fetch_doc`
- Runs on stdio transport
- Simple, declarative API with decorators

**MCP Client** (`mcp_client.py`):
- Wraps MCP SDK in a clean interface
- Manages server process lifecycle
- Provides methods for listing and calling tools
- Implements context manager for easy usage
- Handles all protocol details internally

Together, they demonstrate a complete MCP implementation that can be extended with additional tools and resources for various use cases.
