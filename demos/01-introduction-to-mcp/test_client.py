#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "mcp[cli]==1.9.3",
#     "httpx"
# ]
# ///

"""
Test Client for Basic MCP Server Demo

This script demonstrates how to connect to an MCP server and use its capabilities.

Based on MCP Python SDK documentation:
https://github.com/modelcontextprotocol/python-sdk
"""

import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def test_mcp_server():
    """Test the basic MCP server functionality."""
    
    server_url = "http://localhost:8000/mcp"
    
    print("🔌 Connecting to MCP server...")
    print(f"📡 Server URL: {server_url}")
    
    try:
        # Connect to the MCP server using Streamable HTTP transport
        async with streamablehttp_client(server_url) as (read, write, _):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                print("✅ Connected successfully!")
                
                # Test 1: List available tools
                print("\n🛠️  Available Tools:")
                tools = await session.list_tools()
                for tool in tools.tools:
                    print(f"   - {tool.name}: {tool.description}")
                
                # Test 4: Call a tool
                print("\n🧪 Testing Tools:")
                
                # Test get_current_time tool
                time_result = await session.call_tool("get_current_time", {})
                print(f"   Current time: {time_result.content[0].text}")
                
                # Test add_numbers tool
                add_result = await session.call_tool("add_numbers", {"a": 15, "b": 27})
                print(f"   15 + 27 = {add_result.content[0].text}")
                
                # Test write_file_lucas_teaches tool
                write_result = await session.call_tool("write_file_lucas_teaches", {"file_name": "test_file.txt", "file_content": "This is a test file."})
                print(f"   File written: {write_result.content[0].text}")
                
                # Test silly_joke resource
                joke_result = await session.read_resource("joke://silly_joke.txt")
                print(f"   Joke: {joke_result.contents[0].text}")
                
                print("\n🎉 All tests completed successfully!")
                
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        print("\n💡 Make sure the server is running:")
        print("   uv run ./basic_server.py")

if __name__ == "__main__":
    print("🧪 MCP Server Test Client")
    print("=" * 40)
    asyncio.run(test_mcp_server())
