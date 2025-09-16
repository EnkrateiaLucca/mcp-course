from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typing import Optional
from contextlib import AsyncExitStack
from mcp import types
import asyncio

class MCPClient:
    def __init__(self,command: str,args: list[str],
                 env: Optional[dict[str, str]]=None):
        self._command = command
        self._args = args
        self._session: Optional[ClientSession] = None
        self._exit_stack: AsyncExitStack = AsyncExitStack()
        self._env = env
    
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

    def session(self) -> ClientSession:
        if self._session is None:
            raise ConnectionError(
                "Client session not initialized or cache not populated. Call connect_to_server first."
            )
        return self._session


    async def list_tools(self) -> list[types.Tool]:
        result = await self.session().list_tools()
        return result.tools

    async def call_tool(
        self, tool_name: str, tool_input
    ) -> types.CallToolResult | None:
        return await self.session().call_tool(tool_name, tool_input)
    
    async def cleanup(self):
        await self._exit_stack.aclose()
        self._session = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()


# For testing
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

if __name__ == "__main__":
    asyncio.run(main())