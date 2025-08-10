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
                
                # Test 2: List available resources
                print("\n📊 Available Resources:")
                resources = await session.list_resources()
                for resource in resources.resources:
                    print(f"   - {resource.uri}: {resource.name}")
                
                # Test 3: List available prompts
                print("\n📝 Available Prompts:")
                prompts = await session.list_prompts()
                for prompt in prompts.prompts:
                    print(f"   - {prompt.name}: {prompt.description}")
                
                # Test 4: Call a tool
                print("\n🧪 Testing Tools:")
                
                # Test get_current_time tool
                time_result = await session.call_tool("get_current_time", {})
                print(f"   Current time: {time_result.content[0].text}")
                
                # Test add_numbers tool
                add_result = await session.call_tool("add_numbers", {"a": 15, "b": 27})
                print(f"   15 + 27 = {add_result.content[0].text}")
                
                # Test 5: Read a resource
                print("\n📖 Testing Resources:")
                try:
                    greeting_result = await session.read_resource("demo://greeting/Alice")
                    print(f"   Greeting: {greeting_result.contents[0].text}")
                except Exception as e:
                    print(f"   Resource error: {e}")
                
                # Test 6: Get a prompt
                print("\n📋 Testing Prompts:")
                try:
                    intro_prompt = await session.get_prompt("introduction_prompt")
                    print(f"   Introduction prompt length: {len(intro_prompt.messages[0].content.text)} characters")
                    print(f"   First 100 chars: {intro_prompt.messages[0].content.text[:100]}...")
                except Exception as e:
                    print(f"   Prompt error: {e}")
                
                print("\n🎉 All tests completed successfully!")
                
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        print("\n💡 Make sure the server is running:")
        print("   uv run ./basic_server.py")

if __name__ == "__main__":
    print("🧪 MCP Server Test Client")
    print("=" * 40)
    asyncio.run(test_mcp_server())
