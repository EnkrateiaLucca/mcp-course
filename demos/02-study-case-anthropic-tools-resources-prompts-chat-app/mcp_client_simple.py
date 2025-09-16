#!/usr/bin/env python3

import asyncio
import json
from typing import Optional, List, Dict, Any
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI


class SimpleMCPClient:
    """Simplified MCP client that connects to an MCP server and integrates with OpenAI."""

    def __init__(self, server_script_path: str, openai_api_key: str):
        self.server_script_path = server_script_path
        self.openai_client = OpenAI(api_key=openai_api_key)
        self._session: Optional[ClientSession] = None
        self._exit_stack: AsyncExitStack = AsyncExitStack()

    async def connect(self):
        """Connect to the MCP server."""
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_script_path]
        )

        # Create stdio transport
        stdio_transport = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        stdio_read, stdio_write = stdio_transport

        # Create session
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(stdio_read, stdio_write)
        )

        # Initialize the session
        await self._session.initialize()
        print("✓ Connected to MCP server")

    async def disconnect(self):
        """Disconnect from the MCP server."""
        await self._exit_stack.aclose()
        self._session = None

    async def list_tools(self):
        """List all available tools from the MCP server."""
        if not self._session:
            raise RuntimeError("Not connected to MCP server")

        result = await self._session.list_tools()
        return result.tools

    async def call_tool(self, name: str, arguments: Dict[str, Any]):
        """Call a specific tool on the MCP server."""
        if not self._session:
            raise RuntimeError("Not connected to MCP server")

        result = await self._session.call_tool(name, arguments)
        if result.isError:
            return f"Error: {result.content}"

        # Extract text content from the result
        if result.content:
            if isinstance(result.content, list):
                # Handle list of content blocks
                text_parts = []
                for item in result.content:
                    if hasattr(item, 'text'):
                        text_parts.append(item.text)
                    elif isinstance(item, dict) and 'text' in item:
                        text_parts.append(item['text'])
                    else:
                        text_parts.append(str(item))
                return "\n".join(text_parts)
            else:
                return str(result.content)

        return "Tool executed successfully"

    async def get_available_tools_for_openai(self):
        """Get tools formatted for OpenAI function calling."""
        tools = await self.list_tools()
        openai_tools = []

        for tool in tools:
            # Convert MCP tool schema to OpenAI format
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }

            # Convert input schema to OpenAI format
            if hasattr(tool, 'inputSchema') and tool.inputSchema:
                if hasattr(tool.inputSchema, 'properties'):
                    openai_tool["function"]["parameters"]["properties"] = tool.inputSchema.properties
                if hasattr(tool.inputSchema, 'required'):
                    openai_tool["function"]["parameters"]["required"] = tool.inputSchema.required

            openai_tools.append(openai_tool)

        return openai_tools

    async def chat_with_tools(self, messages: List[Dict[str, str]], model: str = "gpt-4"):
        """Chat with OpenAI using MCP tools."""
        # Get available tools
        tools = await self.get_available_tools_for_openai()

        # Make initial request to OpenAI
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools if tools else None,
            tool_choice="auto" if tools else None
        )

        message = response.choices[0].message

        # Handle tool calls
        if message.tool_calls:
            # Add assistant message with tool calls to conversation
            messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in message.tool_calls
                ]
            })

            # Execute each tool call
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                print(f"🔧 Calling tool: {function_name} with args: {function_args}")

                # Call the MCP tool
                tool_result = await self.call_tool(function_name, function_args)

                # Add tool result to conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(tool_result)
                })

            # Make another request with tool results
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages
            )

            return response.choices[0].message.content
        else:
            return message.content


async def main():
    """Example usage of the SimpleMCPClient."""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("Please set OPENAI_API_KEY in your environment")
        return

    client = SimpleMCPClient("mcp_server_simple.py", openai_api_key)

    try:
        await client.connect()

        # Test conversation
        messages = [
            {"role": "user", "content": "List all available documents and then read the content of notes.txt"}
        ]

        response = await client.chat_with_tools(messages)
        print(f"\n🤖 Response: {response}")

    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())