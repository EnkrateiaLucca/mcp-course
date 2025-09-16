#!/usr/bin/env python3
"""
MCP Chat Application with OpenAI Function Calling
Demonstrates Model Context Protocol by connecting OpenAI's function calling
capabilities with MCP server tools.
"""

import asyncio
import json
import os
from typing import Optional, Dict, Any, List
from mcp_client import MCPClient
from mcp import types
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class MCPChatApp:
    def __init__(self, server_command: str, server_args: list[str]):
        self.client = MCPClient(command=server_command, args=server_args)
        self.tools = []
        self.openai_client = None
        self.messages = []

    def _convert_mcp_to_openai_tool(self, mcp_tool: types.Tool) -> Dict[str, Any]:
        """Convert MCP tool definition to OpenAI function format."""
        openai_tool = {
            "type": "function",
            "function": {
                "name": mcp_tool.name,
                "description": mcp_tool.description or f"Execute {mcp_tool.name}",
            }
        }

        # Convert input schema if present
        if mcp_tool.inputSchema:
            # OpenAI expects parameters in a specific format
            parameters = {
                "type": "object",
                "properties": mcp_tool.inputSchema.get("properties", {}),
                "required": mcp_tool.inputSchema.get("required", [])
            }
            openai_tool["function"]["parameters"] = parameters
        else:
            openai_tool["function"]["parameters"] = {
                "type": "object",
                "properties": {}
            }

        return openai_tool

    async def start(self):
        """Initialize the MCP connection and OpenAI client, then start the chat loop."""
        print("MCP Chat Application with OpenAI")
        print("=" * 50)

        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Error: OPENAI_API_KEY not found in environment variables")
            print("Please add OPENAI_API_KEY to your .env file")
            return

        self.openai_client = OpenAI(api_key=api_key)

        print("Connecting to MCP server...")

        async with self.client as client:
            # Get available tools from MCP server
            self.tools = await client.list_tools()

            # Convert MCP tools to OpenAI function format
            openai_tools = [self._convert_mcp_to_openai_tool(tool) for tool in self.tools]

            print(f"\nConnected! Available tools:")
            for tool in self.tools:
                print(f"  • {tool.name}: {tool.description}")
                if tool.inputSchema:
                    params = tool.inputSchema.get("properties", {})
                    if params:
                        print(f"    Parameters: {', '.join(params.keys())}")

            print("\n" + "=" * 50)
            print("Chat with the assistant. The AI will automatically use available tools.")
            print("Commands:")
            print("  /clear          - Clear conversation history")
            print("  /tools          - List available tools")
            print("  /help           - Show this help message")
            print("  /exit or /quit  - Exit the application")
            print("=" * 50 + "\n")

            await self.chat_loop(openai_tools)

    async def chat_loop(self, openai_tools: List[Dict[str, Any]]):
        """Main chat interaction loop with OpenAI function calling."""
        # Initialize with a system message
        self.messages = [
            {"role": "system", "content": "You are a helpful assistant with access to tools. Use them when appropriate to help the user."}
        ]

        while True:
            try:
                user_input = input("You> ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith("/"):
                    if await self.handle_command(user_input):
                        continue
                    else:
                        break

                # Add user message to conversation
                self.messages.append({"role": "user", "content": user_input})

                # Get response from OpenAI with function calling
                response = await self.get_openai_response(openai_tools)

                if response:
                    print(f"Assistant> {response}")

            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")

    async def get_openai_response(self, openai_tools: List[Dict[str, Any]]) -> Optional[str]:
        """Get response from OpenAI, handling function calls."""
        try:
            # Call OpenAI API with tools
            response = self.openai_client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
                messages=self.messages,
                tools=openai_tools if openai_tools else None,
                tool_choice="auto" if openai_tools else None
            )

            response_message = response.choices[0].message

            # Add assistant's response to conversation
            self.messages.append(response_message.model_dump())

            # Check if the model wants to call functions
            if response_message.tool_calls:
                # Execute all function calls
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    print(f"[Calling tool: {function_name} with args: {function_args}]")

                    # Execute the tool through MCP
                    result = await self.execute_mcp_tool(function_name, function_args)

                    # Add the function result to messages
                    self.messages.append({
                        "role": "tool",
                        "content": str(result),
                        "tool_call_id": tool_call.id
                    })

                # Get the final response from OpenAI after tool execution
                final_response = self.openai_client.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
                    messages=self.messages
                )

                final_message = final_response.choices[0].message
                self.messages.append(final_message.model_dump())
                return final_message.content
            else:
                # No function calls, return the response
                return response_message.content

        except Exception as e:
            return f"Error getting response: {e}"

    async def execute_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute an MCP tool and return the result."""
        try:
            result = await self.client.call_tool(tool_name, arguments)

            if result:
                if isinstance(result.content, list):
                    # Extract text from content items
                    text_results = []
                    for item in result.content:
                        if hasattr(item, 'text'):
                            text_results.append(item.text)
                        else:
                            text_results.append(str(item))
                    return "\n".join(text_results)
                else:
                    return str(result.content)
            else:
                return "Tool executed successfully with no output"

        except Exception as e:
            return f"Error executing tool: {e}"

    async def handle_command(self, command: str) -> bool:
        """Handle chat commands. Returns True to continue, False to exit."""
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()

        if cmd in ["/exit", "/quit"]:
            print("Goodbye!")
            return False

        elif cmd == "/help":
            print("\nCommands:")
            print("  /clear          - Clear conversation history")
            print("  /tools          - List available tools")
            print("  /help           - Show this help message")
            print("  /exit or /quit  - Exit the application\n")

        elif cmd == "/clear":
            self.messages = [
                {"role": "system", "content": "You are a helpful assistant with access to tools. Use them when appropriate to help the user."}
            ]
            print("Conversation history cleared.\n")

        elif cmd == "/tools":
            print("\nAvailable tools:")
            for tool in self.tools:
                print(f"  • {tool.name}: {tool.description}")
                if tool.inputSchema:
                    params = tool.inputSchema.get("properties", {})
                    if params:
                        print(f"    Parameters: {', '.join(params.keys())}")
            print()

        else:
            print(f"Unknown command: {cmd}")
            print("Type /help for available commands")

        return True


async def main():
    """Main entry point."""
    # Configure the MCP server command
    use_uv = os.getenv("USE_UV", "0") == "1"

    if use_uv:
        server_command = "uv"
        server_args = ["run", "./mcp_server.py"]
    else:
        server_command = "python"
        server_args = ["./mcp_server.py"]

    app = MCPChatApp(server_command, server_args)

    try:
        await app.start()
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)