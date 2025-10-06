#!/usr/bin/env python3
"""
OpenAI Agent with MCP Server Integration
This agent manages tasks using the MCP server capabilities
"""

import os
import asyncio
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

# Correct imports based on OpenAI Agents SDK documentation
from agents import Agent, Runner, run_demo_loop
from agents.mcp import MCPServerStdio

# Environment configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MCP_SERVER_PATH = os.path.join(os.path.dirname(__file__), "mcp_server.py")

async def create_task_agent() -> Agent:
    """Create an agent with MCP server integration for task management"""

    # Create MCP server connection using stdio
    mcp_server = MCPServerStdio(
        name="task-management-server",
        params={
            "command": "python",
            "args": [MCP_SERVER_PATH],
        },
        cache_tools_list=True,
    )

    # Connect to the MCP server
    await mcp_server.connect()

    # Create the agent with MCP server integration
    agent = Agent(
        name="Task Management Agent",
        instructions="""You are a helpful task management assistant. You can help users:

        - Create new tasks with priorities and descriptions
        - Update task statuses (pending, in_progress, completed)
        - List and search through tasks
        - Generate task summaries and reports
        - Provide daily standup reports
        - Delete unnecessary tasks

        When users ask for task operations, use the available MCP tools to help them.
        Be conversational and helpful, and always confirm actions you've taken.

        Priority levels: 5=Critical, 4=High, 3=Medium, 2=Low, 1=Nice to have
        Status values: pending, in_progress, completed
        """,
        mcp_servers=[mcp_server],
    )

    return agent

async def run_interactive_demo():
    """Run an interactive demo of the task management agent"""
    print("🚀 Initializing Task Management Agent with MCP Integration...")

    # Check for OpenAI API key
    if not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set it with: export OPENAI_API_KEY='your-key-here'")
        return

    try:
        # Create the agent
        agent = await create_task_agent()

        print("✅ Agent initialized successfully!")
        print("=" * 60)
        print("📋 Task Management Agent - Interactive Demo")
        print("=" * 60)
        print("Try these example commands:")
        print("• 'Create a high priority task to deploy the application'")
        print("• 'Show me all pending tasks'")
        print("• 'Generate a task summary'")
        print("• 'Create a daily standup report'")
        print("• Type 'quit' to exit")
        print("=" * 60)

        # Run the interactive demo loop
        await run_demo_loop(agent)

    except Exception as e:
        print(f"❌ Error initializing agent: {str(e)}")
        import traceback
        traceback.print_exc()


async def run_single_query(query: str):
    """Run a single query against the agent (useful for testing)"""
    if not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        return

    try:
        agent = await create_task_agent()
        result = await Runner.run(agent, query)
        print(f"Query: {query}")
        print(f"Result: {result.final_output}")
        return result.final_output

    except Exception as e:
        print(f"❌ Error running query: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """Main entry point for the agent"""
    import sys

    # Check if a specific query was provided as command line argument
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        await run_single_query(query)
    else:
        # Run interactive demo
        await run_interactive_demo()


if __name__ == "__main__":
    asyncio.run(main())