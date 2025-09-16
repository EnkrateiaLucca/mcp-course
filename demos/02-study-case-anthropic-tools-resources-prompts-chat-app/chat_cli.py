#!/usr/bin/env python3

import asyncio
import os
import sys
from typing import List, Dict
from dotenv import load_dotenv

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.shortcuts import confirm
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML

from mcp_client_simple import SimpleMCPClient


class ChatCLI:
    """Simple chat CLI interface using prompt_toolkit and MCP with OpenAI."""

    def __init__(self, openai_api_key: str):
        self.client = SimpleMCPClient("mcp_server_simple.py", openai_api_key)
        self.messages: List[Dict[str, str]] = []
        self.session = PromptSession(
            history=FileHistory('.chat_history'),
            auto_suggest=AutoSuggestFromHistory(),
        )

        # Custom style for the chat interface
        self.style = Style.from_dict({
            'user': '#00aa00',
            'assistant': '#0088ff',
            'system': '#888888',
            'tool': '#ff8800',
        })

    async def start(self):
        """Start the chat CLI."""
        print("🚀 Starting MCP Chat CLI...")

        try:
            # Connect to MCP server
            await self.client.connect()

            # Show available tools
            await self.show_available_tools()

            # Add system message
            self.messages = [{
                "role": "system",
                "content": "You are a helpful assistant with access to document management tools. "
                          "You can read, write, list, and search documents. Be concise and helpful."
            }]

            print("\n" + "="*60)
            print("💬 MCP Chat Interface Ready!")
            print("Type your message and press Enter to chat.")
            print("Commands:")
            print("  /help    - Show this help")
            print("  /tools   - Show available tools")
            print("  /clear   - Clear conversation history")
            print("  /quit    - Exit the chat")
            print("="*60 + "\n")

            # Main chat loop
            await self.chat_loop()

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await self.client.disconnect()

    async def show_available_tools(self):
        """Display available MCP tools."""
        tools = await self.client.list_tools()
        if tools:
            print("\n🔧 Available MCP Tools:")
            for tool in tools:
                print(f"  • {tool.name}: {tool.description}")

    async def chat_loop(self):
        """Main chat interaction loop."""
        while True:
            try:
                # Get user input
                user_input = await self.session.prompt_async(
                    HTML('<user>You:</user> '),
                    style=self.style
                )

                if not user_input.strip():
                    continue

                # Handle commands
                if user_input.startswith('/'):
                    if await self.handle_command(user_input):
                        continue
                    else:
                        break

                # Add user message
                self.messages.append({"role": "user", "content": user_input})

                # Show thinking indicator
                print("🤔 Thinking...")

                # Get AI response with tool usage
                response = await self.client.chat_with_tools(
                    self.messages.copy(),
                    model="gpt-4"
                )

                # Add assistant response to conversation
                self.messages.append({"role": "assistant", "content": response})

                # Display response
                self.print_message("assistant", response)

            except (EOFError, KeyboardInterrupt):
                if confirm("\n❓ Are you sure you want to quit?"):
                    break
                else:
                    print()
                    continue

    async def handle_command(self, command: str) -> bool:
        """Handle special commands. Returns True to continue, False to quit."""
        command = command.lower().strip()

        if command == '/quit' or command == '/exit':
            return False

        elif command == '/help':
            print("\n📖 Help:")
            print("  /help    - Show this help")
            print("  /tools   - Show available tools")
            print("  /clear   - Clear conversation history")
            print("  /quit    - Exit the chat")
            print()

        elif command == '/tools':
            await self.show_available_tools()
            print()

        elif command == '/clear':
            self.messages = [{
                "role": "system",
                "content": "You are a helpful assistant with access to document management tools. "
                          "You can read, write, list, and search documents. Be concise and helpful."
            }]
            print("🧹 Conversation history cleared!\n")

        else:
            print(f"❓ Unknown command: {command}")
            print("Type /help for available commands.\n")

        return True

    def print_message(self, role: str, content: str):
        """Print a formatted message."""
        if role == "user":
            icon = "👤"
            color = "user"
        elif role == "assistant":
            icon = "🤖"
            color = "assistant"
        elif role == "tool":
            icon = "🔧"
            color = "tool"
        else:
            icon = "ℹ️"
            color = "system"

        # Print with formatting
        print()
        session = PromptSession()
        session.print_formatted_text(
            HTML(f'<{color}>{icon} {role.title()}:</color>'),
            style=self.style
        )
        print(content)
        print()


async def main():
    """Main entry point."""
    load_dotenv()

    # Check for OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment variables.")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_key_here")
        sys.exit(1)

    # Create and start the chat CLI
    chat = ChatCLI(openai_api_key)
    await chat.start()


if __name__ == "__main__":
    # Ensure proper event loop policy on Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    asyncio.run(main())