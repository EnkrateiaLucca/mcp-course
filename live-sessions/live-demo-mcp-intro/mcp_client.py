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
        # we won't use this one for now but usually its there
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
        result = await self.session.read_resource(AnyUrl(uri))
        if not result.contents:
            return ""

        resource = result.contents[0]
        
        # In MCP, text resources can come back as TextResourceContents or plain strings.
        if isinstance(resource, types.TextResourceContents):
            return resource.text
        if isinstance(resource, str):
            return resource

        return str(resource)
    
    async def cleanup(self):
        """
        Clean up resources handling 
        with AsyncExitStack automatically
        """
        await self.exist_stack.aclose()

