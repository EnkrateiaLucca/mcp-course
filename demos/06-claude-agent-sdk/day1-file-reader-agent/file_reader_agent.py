#!/usr/bin/env python3
"""
File Reader Agent - Day 1 Demo
===============================

A minimal file reader agent that uses Claude Agents SDK with MCP filesystem server.

This demo shows:
- Setting up Claude Agents SDK
- Connecting to an external MCP filesystem server
- Listing available tools
- Reading and analyzing files
- Providing intelligent summaries

Usage:
    python file_reader_agent.py

    # Or with UV
    uv run file_reader_agent.py

Requirements:
- Python 3.10+
- Node.js (for MCP filesystem server)
- ANTHROPIC_API_KEY environment variable

# /// script
# dependencies = [
#   "claude-agent-sdk>=0.1.0",
#   "anthropic>=0.40.0",
#   "python-dotenv>=1.0.0",
# ]
# ///
"""

import asyncio
import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions


def setup_demo_directory() -> str:
    """Create a temporary directory with sample files for the demo"""
    demo_dir = tempfile.mkdtemp(prefix="claude_file_reader_")

    # Sample files to create
    files = {
        "project_notes.txt": """Project Notes - AI Agent Development
==========================================

Key Objectives:
- Build intelligent file analysis system
- Integrate Claude Agents SDK with MCP
- Create reusable automation tools
- Ensure proper error handling

Status: In Progress
Priority: High
""",
        "meeting_notes.txt": """Meeting Notes - 2025-01-15
============================

Attendees: Dev Team, Product Manager
Topic: Claude Agents SDK Integration

Discussion Points:
1. MCP filesystem integration completed ✓
2. Need to implement error handling
3. Consider adding file filtering capabilities
4. Plan for production deployment

Action Items:
- Review SDK documentation
- Test with different file types
- Create comprehensive examples
""",
        "data_summary.txt": """Data Analysis Summary
====================

Dataset: User Interactions Q4 2024
Total Records: 1,247,893
Analysis Period: Oct 1 - Dec 31, 2024

Key Metrics:
- Average session duration: 8.5 minutes
- Peak usage hours: 2pm - 5pm EST
- Top features used: Search (45%), Analysis (32%), Export (23%)
- User satisfaction: 4.7/5.0

Insights:
- Strong adoption of new AI features
- Need to optimize search performance
- Consider adding batch export functionality
""",
        "tasks.md": """# TODO List

## High Priority
- [ ] Implement file reader agent with MCP
- [ ] Add comprehensive error handling
- [ ] Write unit tests for tool functions
- [ ] Create documentation

## Medium Priority
- [ ] Add support for multiple file formats
- [ ] Implement file search capabilities
- [ ] Create CLI interface
- [ ] Add progress indicators

## Low Priority
- [ ] Add file watching capabilities
- [ ] Implement caching layer
- [ ] Create web interface
- [ ] Add analytics dashboard
"""
    }

    # Create the files
    for filename, content in files.items():
        filepath = os.path.join(demo_dir, filename)
        with open(filepath, "w") as f:
            f.write(content)

    print(f"✅ Created demo directory: {demo_dir}")
    print("\n📁 Files created:")
    for filename in files.keys():
        print(f"   • {filename}")
    print()

    return demo_dir


async def list_available_tools(client: ClaudeSDKClient):
    """List all available MCP tools"""
    print("=" * 70)
    print("🔍 STEP 1: Listing Available Tools")
    print("=" * 70)

    await client.query("List all the tools you have access to and briefly describe what each one does.")

    async for msg in client.receive_response():
        print(msg, end="", flush=True)

    print("\n")


async def read_and_summarize(client: ClaudeSDKClient):
    """Read files and provide a summary"""
    print("=" * 70)
    print("📖 STEP 2: Reading and Summarizing Files")
    print("=" * 70)

    query = """Please do the following:
1. List all files in the directory
2. Read each .txt and .md file
3. Provide a comprehensive summary including:
   - What types of files are present
   - Key information from each file
   - Any action items or todos found
   - Overall insights about the project
"""

    await client.query(query)

    async for msg in client.receive_response():
        print(msg, end="", flush=True)

    print("\n")


async def extract_action_items(client: ClaudeSDKClient):
    """Extract and prioritize action items"""
    print("=" * 70)
    print("🎯 STEP 3: Extracting Action Items")
    print("=" * 70)

    query = """Based on all the files you've read, extract and organize all action items.
Group them by priority (High, Medium, Low) and provide a consolidated list.
Also note which file each action item came from."""

    await client.query(query)

    async for msg in client.receive_response():
        print(msg, end="", flush=True)

    print("\n")


async def run_file_reader_agent(directory: str):
    """
    Run the complete file reader agent workflow

    Args:
        directory: Path to the directory to analyze
    """
    print("\n" + "=" * 70)
    print("🤖 CLAUDE FILE READER AGENT - DAY 1 DEMO")
    print("=" * 70)
    print(f"📂 Analyzing directory: {directory}\n")

    # Configure the agent with filesystem MCP server
    options = ClaudeAgentOptions(
        system_prompt="""You are an intelligent file analysis assistant. Your role is to:
- Analyze files in the provided directory
- Extract key information and insights
- Identify action items and priorities
- Provide clear, well-organized summaries

Always be thorough but concise in your analysis.""",

        mcp_servers={
            "filesystem": {
                "type": "stdio",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", directory]
            }
        },

        max_turns=10  # Allow multiple tool invocations
    )

    try:
        async with ClaudeSDKClient(options=options) as client:
            # Step 1: List available tools
            await list_available_tools(client)

            # Step 2: Read and summarize files
            await read_and_summarize(client)

            # Step 3: Extract action items
            await extract_action_items(client)

    except Exception as e:
        print(f"❌ Error: {e}")
        raise

    print("=" * 70)
    print("✅ File Reader Agent Demo Complete!")
    print("=" * 70)


async def main():
    """Main entry point for the demo"""

    # Load environment variables
    load_dotenv()

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY not found!")
        print("\nPlease set your API key:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        print("\nOr create a .env file with:")
        print("  ANTHROPIC_API_KEY=your-api-key-here")
        return

    # Setup demo directory
    demo_dir = setup_demo_directory()

    try:
        # Run the agent
        await run_file_reader_agent(demo_dir)

    finally:
        # Cleanup
        print(f"\n🧹 Cleaning up demo directory: {demo_dir}")
        import shutil
        if os.path.exists(demo_dir):
            shutil.rmtree(demo_dir)
            print("✅ Cleanup complete!")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                   CLAUDE FILE READER AGENT - DAY 1                   ║
║                                                                      ║
║  This demo shows how to build a file reader agent using:            ║
║  • Claude Agents SDK                                                ║
║  • External MCP filesystem server                                   ║
║  • Streaming sessions with Claude                                   ║
║                                                                      ║
║  The agent will:                                                    ║
║  1. List available MCP tools                                        ║
║  2. Read and analyze files in a directory                           ║
║  3. Extract and organize action items                               ║
╚══════════════════════════════════════════════════════════════════════╝
    """)

    asyncio.run(main())
