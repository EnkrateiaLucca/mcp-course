#!/usr/bin/env python3
"""
MCP Demo Script
Shows how to use the MCP client to interact with the server
"""

import asyncio
from mcp_client import MCPClient


async def demo():
    """Demonstrate MCP client-server interaction."""
    print("MCP Demo - Connecting to server...")
    print("=" * 50)

    # Create client and connect to server
    async with MCPClient(
        command="python",
        args=["./mcp_server.py"],
    ) as client:
        # List available tools
        tools = await client.list_tools()
        print("\nAvailable tools from server:")
        for tool in tools:
            print(f"  • {tool.name}: {tool.description}")

        print("\n" + "=" * 50)

        # Demo 1: Read a file
        print("\n1. Reading file.txt using 'read_doc' tool:")
        result = await client.call_tool("read_doc", {"filepath": "./file.txt"})
        if result:
            print(f"   Content: {result.content}")

        # Demo 2: Write a new file
        print("\n2. Writing to demo_output.txt using 'write_file' tool:")
        result = await client.call_tool("write_file", {
            "filepath": "./demo_output.txt",
            "contents": "This file was created by the MCP client!\nTimestamp: " +
                       str(asyncio.get_event_loop().time())
        })
        if result:
            print(f"   Result: {result.content}")

        # Demo 3: Read the file we just wrote
        print("\n3. Reading back demo_output.txt:")
        result = await client.call_tool("read_doc", {"filepath": "./demo_output.txt"})
        if result:
            print(f"   Content: {result.content}")

        print("\n" + "=" * 50)
        print("Demo complete! The MCP server provided tools that the client used.")


if __name__ == "__main__":
    asyncio.run(demo())