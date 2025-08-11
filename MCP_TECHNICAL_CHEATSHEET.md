# MCP Technical Cheat Sheet for Instructors

## Core Concepts Overview

### What is MCP?
The Model Context Protocol (MCP) is an open protocol that standardizes how AI assistants connect with external data sources and tools. Think of it as a universal adapter that lets AI models talk to any system in a consistent way.

### Key Architecture Components

1. **MCP Hosts** (e.g., Claude Desktop, IDEs)
   - Applications that want to access data through MCP
   - Maintain connections to multiple MCP servers
   - Examples: Claude Desktop, VS Code, Cursor

2. **MCP Clients** 
   - Protocol clients that maintain 1:1 connections with servers
   - Handle the actual protocol communication
   - Built into or alongside the host application

3. **MCP Servers**
   - Lightweight programs exposing specific capabilities
   - Can provide tools, resources, prompts, and sampling
   - Run as separate processes from the host

4. **Transport Layer**
   - **stdio**: Direct parent-child process communication
   - **HTTP (streamable-http)**: Network communication for remote servers

## JSON-RPC Message Format

MCP uses JSON-RPC 2.0 for all communication. Every message follows this structure:

### Request Message
```json
{
  "jsonrpc": "2.0",
  "id": "unique-request-id",
  "method": "tools/call",
  "params": {
    "name": "get_weather",
    "arguments": {"city": "New York"}
  }
}
```

### Response Message
```json
{
  "jsonrpc": "2.0",
  "id": "unique-request-id",
  "result": {
    "content": [
      {"type": "text", "text": "Weather: 72°F, Sunny"}
    ]
  }
}
```

### Error Message
```json
{
  "jsonrpc": "2.0",
  "id": "unique-request-id",
  "error": {
    "code": -32601,
    "message": "Method not found"
  }
}
```

## MCP Lifecycle

### 1. Initialization Phase
```
Client → Server: initialize request
{
  "method": "initialize",
  "params": {
    "protocolVersion": "1.0.0",
    "capabilities": {
      "tools": {},
      "resources": {"subscribe": true}
    },
    "clientInfo": {
      "name": "Claude Desktop",
      "version": "1.0"
    }
  }
}

Server → Client: initialize response
{
  "result": {
    "protocolVersion": "1.0.0",
    "capabilities": {
      "tools": {},
      "resources": {},
      "prompts": {},
      "sampling": {}
    },
    "serverInfo": {
      "name": "weather-server",
      "version": "1.0"
    }
  }
}

Client → Server: initialized notification
{
  "method": "notifications/initialized"
}
```

### 2. Operation Phase
The server is now ready to handle:
- Tool calls
- Resource requests
- Prompt requests
- Sampling requests
- Subscriptions

### 3. Shutdown Phase
```
Client → Server: close notification
{
  "method": "notifications/closed"
}
```

## The Four MCP Capabilities

### 1. Tools (Model-Controlled)
Functions the AI can execute:
```python
@mcp.tool()
async def calculate(expression: str) -> str:
    """Evaluate a mathematical expression"""
    return str(eval(expression))
```

### 2. Resources (Application-Controlled)
Data the host application can access:
```python
@server.list_resources()
async def list_resources():
    return [
        Resource(uri="file:///data.json", name="Data File")
    ]
```

### 3. Prompts (User-Controlled)
Templates users can invoke:
```python
@server.list_prompts()
async def list_prompts():
    return [
        Prompt(name="debug_code", description="Help debug code")
    ]
```

### 4. Sampling (Server-Initiated)
Server requests LLM completions:
```python
result = await session.create_message(
    messages=[{"role": "user", "content": "Analyze this"}],
    max_tokens=100
)
```

## Elicitation (New Feature)

Elicitation allows servers to request additional information from users during execution. This is crucial for:
- Confirming dangerous operations
- Getting missing parameters
- Clarifying ambiguous requests

### How Elicitation Works

1. **Server sends elicitation request during operation:**
```json
{
  "method": "elicitation/request",
  "params": {
    "prompt": "This will delete 5 files. Continue?",
    "options": ["yes", "no"]
  }
}
```

2. **Client presents to user and responds:**
```json
{
  "result": {
    "choice": "yes"
  }
}
```

### Implementation Example
```python
async def delete_files(self, context, file_pattern: str):
    files = glob.glob(file_pattern)
    
    # Request confirmation via elicitation
    response = await context.request_elicitation(
        f"Delete {len(files)} files matching {file_pattern}?",
        options=["yes", "no"]
    )
    
    if response.choice == "yes":
        for file in files:
            os.remove(file)
        return f"Deleted {len(files)} files"
    else:
        return "Operation cancelled"
```

## Authorization

### OAuth 2.0 Support
MCP supports OAuth for secure authentication:

```python
# Server declares OAuth requirement
@server.get_auth_requirements()
async def get_auth_requirements():
    return {
        "type": "oauth2",
        "authorization_url": "https://api.example.com/oauth/authorize",
        "token_url": "https://api.example.com/oauth/token",
        "scopes": ["read", "write"]
    }
```

### Token Management
- Clients handle token acquisition and refresh
- Servers validate tokens on each request
- Tokens passed in request headers or params

## Security Best Practices

### 1. Input Validation
**Always validate and sanitize inputs:**
```python
@mcp.tool()
async def read_file(filename: str) -> str:
    # Prevent directory traversal
    if ".." in filename or filename.startswith("/"):
        raise ValueError("Invalid filename")
    
    # Whitelist allowed directories
    safe_path = os.path.join(ALLOWED_DIR, filename)
    if not safe_path.startswith(ALLOWED_DIR):
        raise ValueError("Access denied")
    
    return open(safe_path).read()
```

### 2. Rate Limiting
```python
from functools import wraps
import time

rate_limit = {}

def limit_calls(max_calls=10, window=60):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            now = time.time()
            key = func.__name__
            
            if key not in rate_limit:
                rate_limit[key] = []
            
            # Clean old entries
            rate_limit[key] = [t for t in rate_limit[key] if now - t < window]
            
            if len(rate_limit[key]) >= max_calls:
                raise Exception("Rate limit exceeded")
            
            rate_limit[key].append(now)
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### 3. Principle of Least Privilege
- Only expose necessary capabilities
- Use read-only access when possible
- Implement granular permissions

### 4. Secure Transport
- Use HTTPS for network transport
- Validate SSL certificates
- Encrypt sensitive data in transit

### 5. Audit Logging
```python
import logging

logging.basicConfig(
    filename='mcp_audit.log',
    format='%(asctime)s - %(name)s - %(message)s'
)

@mcp.tool()
async def sensitive_operation(param: str) -> str:
    logging.info(f"User requested sensitive_operation with param: {param}")
    # Perform operation
    result = do_operation(param)
    logging.info(f"Operation completed successfully")
    return result
```

## Under the Hood: How @mcp.tool() Works

When you decorate a function with `@mcp.tool()`, FastMCP:

1. **Registers the function** in an internal tool registry
2. **Extracts metadata** from the function signature and docstring
3. **Creates a JSON Schema** for the parameters
4. **Handles the JSON-RPC routing** when `tools/call` is received
5. **Marshals arguments** from JSON to Python types
6. **Executes the function** and formats the response

### Simplified Internal Implementation
```python
class FastMCP:
    def __init__(self, name):
        self.tools = {}
        
    def tool(self):
        def decorator(func):
            # Extract function metadata
            sig = inspect.signature(func)
            schema = generate_json_schema(sig)
            
            # Register tool
            self.tools[func.__name__] = {
                "function": func,
                "schema": schema,
                "description": func.__doc__
            }
            
            return func
        return decorator
    
    async def handle_tool_call(self, name, arguments):
        if name not in self.tools:
            raise ToolNotFound(name)
        
        tool = self.tools[name]
        # Validate arguments against schema
        validated_args = validate(arguments, tool["schema"])
        
        # Execute function
        result = await tool["function"](**validated_args)
        
        # Format response
        return {"content": [{"type": "text", "text": str(result)}]}
```

## Common Gotchas for Beginners

### 1. Async/Await
- All MCP operations are asynchronous
- Don't forget `await` when calling tools/resources
- Use `asyncio.run()` for testing

### 2. Path Issues
```python
# BAD: Relative paths break when server runs from different directory
config = open("config.json")

# GOOD: Use absolute paths
import os
config_path = os.path.join(os.path.dirname(__file__), "config.json")
config = open(config_path)
```

### 3. Error Handling
```python
@mcp.tool()
async def risky_operation(param: str) -> str:
    try:
        result = do_something_risky(param)
        return result
    except SpecificError as e:
        # Return user-friendly error message
        return f"Operation failed: {str(e)}"
    except Exception as e:
        # Log unexpected errors for debugging
        logging.error(f"Unexpected error: {e}")
        return "An unexpected error occurred"
```

### 4. Resource URIs
- Must be valid URIs: `file:///path/to/file` or `https://example.com/resource`
- Not just paths: `/path/to/file` ❌

## Testing MCP Servers

### Using MCP Inspector
```bash
# Interactive debugging tool
mcp dev ./my_server.py

# Opens browser with:
# - Tool testing interface
# - Resource browser
# - Message inspector
# - Real-time logs
```

### Manual Testing with Client
```python
# test_client.py
import asyncio
from mcp import ClientSession
from mcp.client.stdio import stdio_client

async def test():
    async with stdio_client() as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {tools}")
            
            # Call a tool
            result = await session.call_tool(
                "get_weather",
                {"city": "New York"}
            )
            print(f"Result: {result}")

asyncio.run(test())
```

## Debugging Tips

1. **Enable verbose logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **Use MCP Inspector** for visual debugging

3. **Check Claude Desktop logs:**
   - macOS/Linux: `~/.config/Claude/logs/`
   - Windows: `%APPDATA%\Claude\logs\`

4. **Common errors:**
   - "Method not found" → Server doesn't implement that capability
   - "Invalid params" → Check your JSON schema
   - "Transport error" → Server crashed or network issue

## Quick Reference: Course Demo Progression

1. **Demo 1**: Basic server with single tool
2. **Demo 2**: Weather server with external API
3. **Demo 3**: All 4 capabilities (tools, resources, prompts, sampling)
4. **Demo 4**: Google ADK integration
5. **Demo 5**: OpenAI Agents integration
6. **Demo 6**: Claude Desktop configuration
7. **Demo 7**: Security best practices

## Teaching Tips

### For Complete Beginners
1. Start with the "universal adapter" analogy
2. Show before/after: AI without MCP vs with MCP
3. Use real-world examples (weather, files, databases)
4. Build incrementally - one capability at a time

### Common Student Questions

**Q: Why not just use function calling?**
A: MCP is standardized across all AI providers, provides resource management, supports prompts, and handles auth/security consistently.

**Q: Can MCP servers talk to each other?**
A: No, MCP servers are independent. The host/client orchestrates between them.

**Q: Is MCP only for Claude?**
A: No! It's an open protocol. Any AI system can implement MCP client capabilities.

**Q: How is this different from LangChain/Agent frameworks?**
A: MCP is a protocol, not a framework. It defines how communication happens, not what you build. You can use MCP with any agent framework.

## Resources for Further Learning

- [MCP Specification](https://modelcontextprotocol.io/specification)
- [MCP Architecture Guide](https://modelcontextprotocol.io/docs/learn/architecture)
- [Security Best Practices](https://modelcontextprotocol.io/specification/2025-06-18/basic/security_best_practices)
- [MCP GitHub](https://github.com/modelcontextprotocol/mcp)
- [Community Servers](https://github.com/modelcontextprotocol/servers)