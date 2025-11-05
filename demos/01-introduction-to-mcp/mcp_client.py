#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "mcp[cli]==1.9.3",
#     "anthropic",
#     "python-dotenv",
#     "rich"
# ]
# ///

# Main source from the mcp docs: https://modelcontextprotocol.io/docs/develop/build-client
import asyncio
from typing import Optional, Any
from pydantic import AnyUrl
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp import types

class SimpleMCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
    
    async def connect_to_server(self, server_path: str):
        """Connect to your basic MCP server"""
        print(f"Connecting to server: {server_path}")
        
        # Set up server parameters for Python script
        server_params = StdioServerParameters(
            command="python",
            args=[server_path],
            env=None
        )
        
        # Use AsyncExitStack to manage the connection lifecycle
        # This ensures the connection is properly closed when done
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        
        # Get the read/write streams
        self.stdio, self.write = stdio_transport
        
        # Create and initialize the session
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )
        
        await self.session.initialize()
        
        # List available tools
        tools = await self.list_tools()
        
        print(f"✅ Connected! Available tools: {[tool.name for tool in tools]}")
        
        # List available resources
        resources_response = await self.session.list_resources()
        resources = resources_response.resources
        print(f"📚 Available resources: {[r.uri for r in resources]}")
    
    async def list_tools(self) -> list[types.Tool]:
        result = await self.session.list_tools()
        return result.tools
    
    async def list_prompts(self) -> list[types.Prompt]:
        result = await self.session.list_prompts()
        return result.prompts
    
    async def get_prompt(self, prompt_name: str, args: dict[str, str]):
        result = await self.session.get_prompt(prompt_name, args)
        return result
    
    # The LLM is going to decide the tool and arguments to call
    async def call_tool(self, tool_name: str, arguments: dict) -> types.CallToolResult | None:
        """Call a tool on the server"""
        if not self.session:
            raise RuntimeError("Not connected to server")
        
        print(f"Calling tool: {tool_name} with args: {arguments}")
        result = await self.session.call_tool(tool_name, arguments) # very similar to function calling in LLMs!
        return result
    
    async def read_resource(self, uri: str) -> Any:
        result = await self.session().read_resource(AnyUrl(uri))
        resource = result.contents[0]
        
        if isinstance(resource, types.TextResourceContents):
            if resource.mimeType == "text/plain":
                return resource.text
    
    # SImulation of the Server/Host application!
    async def interactive_mode(self):
        """Simple interactive loop to test the tools"""
        print("\n🤖 Interactive Mode - Type 'help' for commands or 'quit' to exit")
        
        while True:
            try:
                command = input("\n> ").strip().lower()
                
                if command == 'quit':
                    break
                elif command == 'help':
                    print("""
Available commands:
  time          - Get current time
  add X Y       - Add two numbers
  write F C     - Write to file C content F
  read          - Read the documents resource
  help          - Show this help
  quit          - Exit
                    """)
                elif command == 'time':
                    result = await self.call_tool('get_current_time', {})
                    print(f"Current time: {result.content}")
                elif command.startswith('add '):
                    parts = command.split()
                    if len(parts) == 3:
                        a, b = float(parts[1]), float(parts[2])
                        result = await self.call_tool('add_numbers', {'a': a, 'b': b})
                        print(f"Result: {result.content}")
                    else:
                        print("Usage: add <number1> <number2>")
                elif command.startswith('write '):
                    parts = command.split(maxsplit=2)
                    if len(parts) == 3:
                        filename = parts[1]
                        content = parts[2]
                        result = await self.call_tool('write_file', {
                            'file_name': filename,
                            'file_content': content
                        })
                        print(f"File written: {result.content}")
                    else:
                        print("Usage: write <filename> <content>")
                elif command == 'read':
                    result = await self.read_resource('docs://documents.txt')
                    print(f"Document content:\n{result.contents[0].text if result.contents else 'No content'}")
                else:
                    print("Unknown command. Type 'help' for available commands.")
                    
            except Exception as e:
                print(f"Error: {e}")
    
    async def cleanup(self):
        """Clean up resources - AsyncExitStack handles this automatically"""
        await self.exit_stack.aclose()

async def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python mcp_client.py <path_to_server.py>")
        print("Example: python mcp_client.py ./mcp_server.py")
        sys.exit(1)
    
    server_path = sys.argv[1]
    client = SimpleMCPClient()
    
    try:
        # Connect to server
        await client.connect_to_server(server_path)
        
        # Run interactive mode
        await client.interactive_mode()
        
    finally:
        # Clean up - AsyncExitStack ensures all resources are properly closed
        await client.cleanup()
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    asyncio.run(main())