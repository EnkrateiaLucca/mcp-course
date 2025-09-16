#!/usr/bin/env python3
"""
Obsidian Notes Agent using Google ADK with MCP Tools

This agent provides the same functionality as chat_notes.py but uses
Google's ADK (Agent Development Kit) instead of the agents library.

It connects to the obsidian_vault_server.py MCP server and allows you to:
- Read notes from your Obsidian vault
- Create new notes with structured metadata
- List available notes in your vault
"""

import asyncio
from typing import Optional
from google.adk.agents import Agent, LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.genai import types


def create_notes_agent() -> Agent:
    """
    Create a Google ADK agent with access to Obsidian vault MCP tools.

    Returns:
        Agent configured with MCP tools for Obsidian vault management
    """
    # Configure the MCP server connection parameters
    # This connects to the local obsidian_vault_server.py via stdio
    mcp_connection = StdioConnectionParams(
        server_params=StdioServerParameters(
            command="uv",
            args=["run", "./obsidian_vault_server.py"]
        )
    )

    # Create the MCPToolset with our connection
    obsidian_toolset = MCPToolset(
        connection_params=mcp_connection,
        # Optionally filter tools if you only want specific ones
        # tool_filter=['read_note', 'create_note', 'list_notes']
    )

    # Create the agent with instructions and MCP tools
    agent = Agent(
        model='gemini-2.0-flash',  # You can also use 'gemini-1.5-pro' or other models
        name='obsidian_notes_assistant',
        instruction="""
        You are a helpful assistant that can answer questions and help manage
        an Obsidian vault of notes. You have access to tools that allow you to:

        1. Read existing notes from the Obsidian vault
        2. Create new notes with proper metadata and structure
        3. List available notes in the vault

        When users ask about their notes, help them effectively manage their
        personal knowledge base. Be proactive in suggesting relevant notes
        and helping organize information.

        Always provide clear and concise responses. When creating notes,
        suggest appropriate folders and tags based on the content.
        """,
        tools=[obsidian_toolset]
    )

    return agent


async def run_interactive_session():
    """
    Run an interactive chat session with the Obsidian notes agent.

    This function creates the agent and handles the chat loop,
    similar to the original chat_notes.py implementation.
    """
    print("🚀 Starting Obsidian Notes Agent (Google ADK)")
    print("=" * 50)
    print("Type 'exit' or 'quit' to end the session")
    print("=" * 50)
    print()

    # Create the agent and setup session
    agent = create_notes_agent()
    session_service = InMemorySessionService()

    # Create a session
    session = await session_service.create_session(
        app_name="obsidian_notes_app",
        user_id="user_123",
        session_id="session_123"
    )

    # Create runner
    runner = Runner(
        agent=agent,
        app_name="obsidian_notes_app",
        session_service=session_service
    )

    # Main chat loop
    while True:
        try:
            # Get user input
            user_message = input("\n📝 You: ").strip()

            # Check for exit commands
            if user_message.lower() in ['exit', 'quit', 'bye']:
                print("\n👋 Goodbye! Your notes are safely stored in your vault.")
                break

            # Skip empty messages
            if not user_message:
                continue

            print("\n🤖 Assistant: ", end="", flush=True)

            # Create user message content
            user_content = types.Content(
                role='user',
                parts=[types.Part(text=user_message)]
            )

            # Execute the agent with the user's message using run_async
            events = runner.run_async(
                user_id="user_123",
                session_id="session_123",
                new_message=user_content
            )

            # Process events and display response
            response_text = ""
            async for event in events:
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts') and event.content.parts:
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                response_text += part.text
                                print(part.text, end="", flush=True)

            if not response_text:
                print("I'm ready to help with your notes. Try asking me to list notes or create a new one!")
            else:
                print()  # New line after response

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted! Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try again or type 'exit' to quit.")


def main():
    """
    Main entry point for the application.

    Sets up the async environment and runs the interactive session.
    """
    print("""
    ╔══════════════════════════════════════════════╗
    ║   Obsidian Notes Assistant (Google ADK)      ║
    ║   Connected to your personal vault via MCP   ║
    ╚══════════════════════════════════════════════╝
    """)

    try:
        # Run the async interactive session
        asyncio.run(run_interactive_session())
    except Exception as e:
        print(f"Failed to start the agent: {e}")
        print("\nMake sure:")
        print("  1. The obsidian_vault_server.py is accessible")
        print("  2. You have installed the required dependencies:")
        print("     - pip install google-adk mcp")
        print("  3. Your OBSIDIAN_VAULT_PATH is configured (optional)")


if __name__ == "__main__":
    main()