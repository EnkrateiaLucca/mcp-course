#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "mcp[cli]==1.9.3",
#     "openai",
#     "python-dotenv",
#     "prompt-toolkit"
# ]
# ///

#!/usr/bin/env python3
"""
MCP Chat Application with OpenAI Function Calling
Demonstrates Model Context Protocol by connecting OpenAI's function calling
capabilities with MCP server tools.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from mcp_client import MCPClient
from mcp import types
from openai import OpenAI
from dotenv import load_dotenv
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style

# Load environment variables
load_dotenv()


class FileCompleter(Completer):
    """Completer for @mentions of files in the ./docs folder."""

    def __init__(self, docs_dir: str = "./docs"):
        self.docs_dir = Path(docs_dir)
        self.files = []
        self._refresh_files()

    def _refresh_files(self):
        """Refresh the list of available files."""
        if self.docs_dir.exists():
            self.files = [f.name for f in self.docs_dir.iterdir() if f.is_file()]

    def get_completions(self, document, complete_event):
        text_before_cursor = document.text_before_cursor

        # Check if we're completing an @mention
        if "@" in text_before_cursor:
            last_at_pos = text_before_cursor.rfind("@")
            prefix = text_before_cursor[last_at_pos + 1:]

            for filename in self.files:
                if filename.lower().startswith(prefix.lower()):
                    yield Completion(
                        filename,
                        start_position=-len(prefix),
                        display=filename,
                        display_meta="File",
                    )


class MCPChatApp:
    def __init__(self, server_command: str, server_args: list[str], docs_dir: str = "./docs"):
        self.client = MCPClient(command=server_command, args=server_args)
        self.tools = []
        self.openai_client = None
        self.messages = []
        self.docs_dir = Path(docs_dir)

        # Setup prompt toolkit
        self.completer = FileCompleter(docs_dir)
        self.history = InMemoryHistory()
        self.session = PromptSession(
            completer=self.completer,
            history=self.history,
            style=Style.from_dict({
                "prompt": "#aaaaaa",
                "completion-menu.completion": "bg:#222222 #ffffff",
                "completion-menu.completion.current": "bg:#444444 #ffffff",
            }),
            complete_while_typing=True,
        )

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

    def _extract_mentioned_files(self, text: str) -> str:
        """Extract @mentions from text and load file contents."""
        mentions = [word[1:] for word in text.split() if word.startswith("@")]

        if not mentions:
            return ""

        context_parts = []
        for filename in mentions:
            file_path = self.docs_dir / filename
            if file_path.exists() and file_path.is_file():
                try:
                    content = file_path.read_text(encoding="utf-8")
                    context_parts.append(f'<document id="{filename}">\n{content}\n</document>')
                except Exception as e:
                    print(f"Warning: Could not read {filename}: {e}")

        return "\n".join(context_parts) if context_parts else ""

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
            print("\nFeatures:")
            print("  @filename       - Mention files from ./docs (auto-complete with @)")
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
                user_input = await self.session.prompt_async("You> ")
                user_input = user_input.strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith("/"):
                    if await self.handle_command(user_input):
                        continue
                    else:
                        break

                # Extract any @mentioned files and add as context
                file_context = self._extract_mentioned_files(user_input)

                # Build the message with context if files were mentioned
                if file_context:
                    message_content = f"""The user has a question:
<query>
{user_input}
</query>

The following context may be useful in answering their question:
<context>
{file_context}
</context>

Note: The user's query contains references to documents like "@filename". The "@" is only
included as a way of mentioning the document. If the document content is included in this prompt,
you don't need to use an additional tool to read it.
Answer the user's question directly and concisely. Don't refer to or mention the provided context
in any way - just use it to inform your answer."""
                else:
                    message_content = user_input

                # Add user message to conversation
                self.messages.append({"role": "user", "content": message_content})

                # Get response from OpenAI with function calling
                response = await self.get_openai_response(openai_tools)

                if response:
                    print(f"\nAssistant> {response}\n")

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
            print("  /exit or /quit  - Exit the application")
            print("\nFeatures:")
            print("  @filename       - Mention files from ./docs (auto-complete with @)\n")

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