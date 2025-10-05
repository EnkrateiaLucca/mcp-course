#!/usr/bin/env python3
"""
Advanced Obsidian Notes Agent using Google ADK with MCP Tools

This version demonstrates more advanced Google ADK features including:
- Proper async agent execution
- Error handling and retry logic
- Session management
- Tool result processing
"""

import asyncio
import sys
from typing import Optional, Dict, Any
from datetime import datetime

from google.adk.agents import Agent, LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StdioConnectionParams,
    SseConnectionParams
)
from mcp import StdioServerParameters


class ObsidianNotesAgent:
    """
    A sophisticated Obsidian notes management agent using Google ADK.

    This class encapsulates the agent creation, execution, and session
    management for interacting with an Obsidian vault via MCP.
    """

    def __init__(self, model: str = 'gemini-2.0-flash', vault_server_path: str = "./obsidian_vault_server.py"):
        """
        Initialize the Obsidian Notes Agent.

        Args:
            model: The Gemini model to use (e.g., 'gemini-2.0-flash', 'gemini-1.5-pro')
            vault_server_path: Path to the obsidian_vault_server.py script
        """
        self.model = model
        self.vault_server_path = vault_server_path
        self.agent = self._create_agent()
        self.session_history = []
        self.session_service = None
        self.runner = None

    def _create_agent(self) -> Agent:
        """
        Create and configure the LLM agent with MCP tools.

        Returns:
            Configured Agent with Obsidian vault tools
        """
        # Set up MCP server connection
        mcp_connection = StdioConnectionParams(
            server_params=StdioServerParameters(
                command="uv",
                args=["run", self.vault_server_path]
            )
        )

        # Create MCPToolset
        obsidian_toolset = MCPToolset(
            connection_params=mcp_connection,
            # You can add tool filters for production environments
            # tool_filter=['read_note', 'create_note', 'list_notes']
        )

        # Define the agent with comprehensive instructions
        agent = Agent(
            model=self.model,
            name='obsidian_vault_expert',
            instruction="""
            You are an expert Obsidian vault assistant with deep knowledge of
            personal knowledge management systems. Your capabilities include:

            **Core Functions:**
            - Reading notes from the user's Obsidian vault
            - Creating well-structured notes with appropriate metadata
            - Listing and browsing available notes
            - Suggesting organization strategies

            **Best Practices:**
            - Always suggest relevant tags based on content
            - Recommend appropriate folders for new notes
            - Help users link related notes together
            - Provide summaries when listing multiple notes
            - Use appropriate note types (project, idea, daily, reference, meeting)

            **Communication Style:**
            - Be concise but thorough
            - Use markdown formatting for clarity
            - Provide actionable suggestions
            - Ask clarifying questions when needed

            Remember: You're helping users build their second brain. Make their
            knowledge management effortless and effective.
            """,
            tools=[obsidian_toolset]
        )

        return agent

    async def setup_session(self):
        """Setup session service and runner if not already done."""
        if self.session_service is None:
            self.session_service = InMemorySessionService()
            self.session = await self.session_service.create_session(
                app_name="obsidian_notes_app",
                user_id="user_123",
                session_id="session_123"
            )
            self.runner = Runner(
                agent=self.agent,
                app_name="obsidian_notes_app",
                session_service=self.session_service
            )

    async def execute(self, user_input: str) -> str:
        """
        Execute the agent with user input and return the response.

        Args:
            user_input: The user's message or command

        Returns:
            The agent's response as a string
        """
        try:
            # Setup session if needed
            await self.setup_session()

            # Add to session history
            self.session_history.append({
                'timestamp': datetime.now().isoformat(),
                'role': 'user',
                'content': user_input
            })

            # Create user message content
            user_content = types.Content(
                role='user',
                parts=[types.Part(text=user_input)]
            )

            # Execute the agent using runner.run_async
            events = self.runner.run_async(
                user_id="user_123",
                session_id="session_123",
                new_message=user_content
            )

            # Process events and collect response
            response_text = ""
            async for event in events:
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts') and event.content.parts:
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                response_text += part.text

            # Add response to history
            self.session_history.append({
                'timestamp': datetime.now().isoformat(),
                'role': 'assistant',
                'content': response_text
            })

            return response_text or "No response generated."

        except Exception as e:
            error_msg = f"Error executing agent: {str(e)}"
            self.session_history.append({
                'timestamp': datetime.now().isoformat(),
                'role': 'error',
                'content': error_msg
            })
            return error_msg

    def get_session_summary(self) -> str:
        """
        Get a summary of the current session.

        Returns:
            A formatted summary of the session history
        """
        if not self.session_history:
            return "No session history available."

        summary = "📊 Session Summary:\n"
        summary += f"Total interactions: {len([h for h in self.session_history if h['role'] == 'user'])}\n"
        summary += f"Session started: {self.session_history[0]['timestamp']}\n"

        return summary


class InteractiveCLI:
    """
    Interactive command-line interface for the Obsidian Notes Agent.
    """

    def __init__(self, agent: ObsidianNotesAgent):
        """
        Initialize the CLI with an agent instance.

        Args:
            agent: The ObsidianNotesAgent to use for interactions
        """
        self.agent = agent
        self.commands = {
            '/help': self.show_help,
            '/summary': self.show_summary,
            '/model': self.show_model_info,
            '/clear': self.clear_screen,
        }

    def show_help(self) -> str:
        """Display available commands."""
        return """
📚 Available Commands:
  /help     - Show this help message
  /summary  - Show session summary
  /model    - Show current model info
  /clear    - Clear the screen
  exit/quit - End the session

💡 Tips:
  - Ask me to list your notes
  - Create new notes with specific types
  - Read any existing note
  - Get vault statistics
        """

    def show_summary(self) -> str:
        """Display session summary."""
        return self.agent.get_session_summary()

    def show_model_info(self) -> str:
        """Display model information."""
        return f"🤖 Current Model: {self.agent.model}"

    def clear_screen(self) -> str:
        """Clear the terminal screen."""
        import os
        os.system('clear' if os.name == 'posix' else 'cls')
        return "Screen cleared."

    async def run(self):
        """
        Run the interactive CLI session.
        """
        print("""
╔════════════════════════════════════════════════════╗
║     Obsidian Vault Assistant (Google ADK)         ║
║     Powered by Gemini & MCP                       ║
╚════════════════════════════════════════════════════╝

Type '/help' for available commands
Type 'exit' or 'quit' to end the session
        """)

        while True:
            try:
                # Get user input
                user_input = input("\n💬 You: ").strip()

                # Check for exit
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("\n👋 Thank you for using Obsidian Vault Assistant!")
                    print(self.agent.get_session_summary())
                    break

                # Check for commands
                if user_input.startswith('/'):
                    if user_input in self.commands:
                        result = self.commands[user_input]()
                        print(result)
                    else:
                        print("❌ Unknown command. Type '/help' for available commands.")
                    continue

                # Skip empty input
                if not user_input:
                    continue

                # Process with agent
                print("\n🤔 Thinking...", end='\r')
                response = await self.agent.execute(user_input)
                print("                    ", end='\r')  # Clear the thinking message
                print(f"🤖 Assistant:\n{response}")

            except KeyboardInterrupt:
                print("\n\n⚠️  Session interrupted!")
                print(self.agent.get_session_summary())
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("Please try again or type 'exit' to quit.")


async def main():
    """
    Main entry point for the application.
    """
    # Parse command line arguments if needed
    model = 'gemini-2.0-flash'  # Default model
    if len(sys.argv) > 1:
        if sys.argv[1] in ['gemini-1.5-pro', 'gemini-2.0-flash']:
            model = sys.argv[1]
            print(f"Using model: {model}")

    try:
        # Create agent and CLI
        agent = ObsidianNotesAgent(model=model)
        cli = InteractiveCLI(agent)

        # Run the interactive session
        await cli.run()

    except Exception as e:
        print(f"❌ Failed to start the agent: {e}")
        print("\n📋 Troubleshooting:")
        print("  1. Ensure obsidian_vault_server.py is in the current directory")
        print("  2. Install required dependencies:")
        print("     pip install google-adk mcp")
        print("  3. Set OBSIDIAN_VAULT_PATH environment variable (optional)")
        print("  4. Ensure you have API credentials configured for Gemini")


if __name__ == "__main__":
    asyncio.run(main())