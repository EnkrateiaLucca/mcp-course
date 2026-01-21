#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "agents>=0.3.0",
#     "anthropic>=0.40.0"
# ]
# ///

"""
Automation Agent - Claude Agent SDK + MCP Integration

This agent demonstrates how to combine Claude Agent SDK with MCP servers
to create a practical automation script generator.

Architecture:
1. MCP Server (automation_mcp_server.py) - Provides tools to query automation database
2. Claude Agent - Uses MCP tools to find and generate automation scripts
3. File System - Agent writes generated scripts to disk

Key Concepts:
- Attaching in-process MCP servers to Claude Agent SDK
- Using MCP tools within agent workflows
- File writing with proper permissions
- Interactive agent responses with streaming
"""

import asyncio
import os
from pathlib import Path

# Claude Agent SDK imports
from agents import Agent, MCPServerConfig
from agents.tools import builtin_tools


# ============================================================================
# Configuration
# ============================================================================

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent

# Path to the MCP server script
MCP_SERVER_PATH = SCRIPT_DIR / "automation_mcp_server.py"

# Output directory for generated automation scripts
OUTPUT_DIR = SCRIPT_DIR / "generated_scripts"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================================
# Agent Configuration
# ============================================================================

# System instructions guide the agent's behavior
SYSTEM_INSTRUCTIONS = """
You are an Automation Script Generator Agent. Your job is to help users
discover and generate automation scripts from a database of templates.

Your workflow:
1. When a user asks about available automations, use the list_all_automations
   or search tools to show what's available
2. When a user requests a specific automation, use get_automation_by_id to
   retrieve the template
3. Write the automation script to a file using the Write tool
4. Make the script executable (chmod +x for bash scripts)
5. Provide clear instructions on how to use the generated script

Important guidelines:
- Always use descriptive filenames (e.g., backup_files.sh, organize_downloads.py)
- Include file extensions (.sh for bash, .py for python)
- Explain what the script does and how to run it
- For bash scripts, mention they need execute permissions
- Be helpful and educational - explain the automation's purpose

Available MCP tools from automation database server:
- list_all_automations: Browse all automations
- search_automations_by_category: Filter by category
- search_by_script_type: Filter by language (bash/python)
- get_automation_by_id: Get full script template
- get_database_stats: See database overview
""".strip()


# ============================================================================
# Main Agent Function
# ============================================================================

async def run_automation_agent():
    """
    Initialize and run the automation agent with MCP integration.

    This function demonstrates:
    1. Creating an MCPServerConfig for in-process server
    2. Attaching built-in tools (Write, Glob, Bash) for file operations
    3. Creating the agent with instructions and tools
    4. Running an interactive loop for user queries
    """

    print("🤖 Automation Agent Starting...")
    print("=" * 60)

    # ========================================================================
    # STEP 1: Configure the MCP Server
    # ========================================================================
    # MCPServerConfig tells the agent how to connect to our automation database server
    # Using 'command' with 'uv' ensures dependencies are handled automatically

    mcp_config = MCPServerConfig(
        command="uv",
        args=[
            "run",
            "--script",
            str(MCP_SERVER_PATH)
        ],
        env=None  # No additional environment variables needed
    )

    print(f"📊 MCP Server configured: {MCP_SERVER_PATH}")
    print(f"💾 Output directory: {OUTPUT_DIR}")
    print()

    # ========================================================================
    # STEP 2: Configure Built-in Tools
    # ========================================================================
    # The agent needs file system access to write generated scripts
    # We provide: Write (create files), Glob (find files), Bash (make executable)

    tools = [
        builtin_tools.Write(
            # Restrict writes to our output directory for safety
            allowed_directories=[str(OUTPUT_DIR)]
        ),
        builtin_tools.Glob(
            # Allow searching in output directory
            allowed_directories=[str(OUTPUT_DIR)]
        ),
        builtin_tools.Bash(
            # Enable bash for chmod commands to make scripts executable
            # In production, you'd want more restrictions here
            enabled=True
        )
    ]

    print("🔧 Built-in tools configured:")
    print("  - Write (restricted to generated_scripts/)")
    print("  - Glob (for finding generated files)")
    print("  - Bash (for chmod +x permissions)")
    print()

    # ========================================================================
    # STEP 3: Create the Agent
    # ========================================================================
    # Combine everything: instructions, MCP server, and built-in tools

    agent = Agent(
        name="automation-generator",
        instructions=SYSTEM_INSTRUCTIONS,
        mcp_servers=[mcp_config],  # Attach our automation database MCP server
        tools=tools,  # Attach built-in tools for file operations
        model="claude-sonnet-4-5-20250929",  # Latest Claude model
    )

    print("✨ Agent initialized with:")
    print("  - Name: automation-generator")
    print("  - Model: Claude Sonnet 4.5")
    print("  - MCP Server: automation-database-server")
    print("  - Built-in Tools: Write, Glob, Bash")
    print()
    print("=" * 60)
    print()

    # ========================================================================
    # STEP 4: Interactive Loop
    # ========================================================================
    # Run the agent in an interactive mode where users can make requests

    print("💬 Automation Agent Ready!")
    print()
    print("Example queries:")
    print("  - 'What automations are available?'")
    print("  - 'Show me file management automations'")
    print("  - 'Generate the backup files automation'")
    print("  - 'Create the download organizer script'")
    print()
    print("Type 'quit' to exit")
    print("-" * 60)
    print()

    # Simple interactive loop
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()

            # Check for exit command
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break

            # Skip empty inputs
            if not user_input:
                continue

            print()  # Blank line for readability

            # ================================================================
            # STEP 5: Run the Agent
            # ================================================================
            # run_async_sync() executes the agent and returns the response
            # The agent will:
            # 1. Understand the user's request
            # 2. Call appropriate MCP tools (from automation database)
            # 3. Use built-in tools (Write, Bash) to generate files
            # 4. Return a helpful response

            response = await agent.run_async(
                task=user_input,
                stream=False  # Set to True for streaming responses
            )

            # ================================================================
            # STEP 6: Display Response
            # ================================================================
            # Extract the agent's final response text

            print("🤖 Agent:", response.final_messages[-1].content)
            print()

            # Show metadata (optional, useful for debugging)
            if response.cost:
                print(f"💰 Cost: ${response.cost:.4f}")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'quit' to exit.")


# ============================================================================
# Advanced Example: Programmatic Agent Usage
# ============================================================================

async def generate_automation_programmatically(automation_id: int, output_filename: str):
    """
    Example of using the agent programmatically (non-interactive).

    This shows how you could integrate the agent into your own scripts
    or applications.

    Args:
        automation_id: The ID of the automation to generate
        output_filename: The desired filename for the script

    Returns:
        The agent's response
    """

    # Configure MCP server
    mcp_config = MCPServerConfig(
        command="uv",
        args=["run", "--script", str(MCP_SERVER_PATH)],
    )

    # Configure tools
    tools = [
        builtin_tools.Write(allowed_directories=[str(OUTPUT_DIR)]),
        builtin_tools.Bash(enabled=True)
    ]

    # Create agent
    agent = Agent(
        name="automation-generator",
        instructions=SYSTEM_INSTRUCTIONS,
        mcp_servers=[mcp_config],
        tools=tools,
        model="claude-sonnet-4-5-20250929",
    )

    # Run with specific task
    task = f"Generate automation ID {automation_id} and save it as {output_filename}"

    response = await agent.run_async(task=task, stream=False)

    return response


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                    Automation Agent - MCP Demo                           ║
║                  Claude Agent SDK + MCP Integration                      ║
╚══════════════════════════════════════════════════════════════════════════╝
    """)

    # Check if MCP server exists
    if not MCP_SERVER_PATH.exists():
        print(f"❌ Error: MCP server not found at {MCP_SERVER_PATH}")
        print("Please ensure automation_mcp_server.py is in the same directory.")
        exit(1)

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set your API key:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        exit(1)

    # Run the interactive agent
    try:
        asyncio.run(run_automation_agent())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

    # Example of programmatic usage (commented out):
    # asyncio.run(generate_automation_programmatically(
    #     automation_id=3,
    #     output_filename="organize_downloads.py"
    # ))
