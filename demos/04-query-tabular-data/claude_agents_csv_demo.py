#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "claude-agent-sdk>=0.1.0",
#     "anthropic>=0.40.0",
# ]
# ///

"""
Claude Agents SDK with CSV Query MCP Server Demo

This script demonstrates how to use Claude Agents SDK to query CSV data
through a custom MCP server. The MCP server provides tools for filtering,
searching, and analyzing product data.

Based on Claude Agent SDK documentation:
https://platform.claude.com/docs/en/agent-sdk/overview
"""

import asyncio
import os
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock, ResultMessage

# Ensure API key is set
if not os.getenv('ANTHROPIC_API_KEY'):
    print("⚠️  Warning: ANTHROPIC_API_KEY not set!")
    print("Please set it with: export ANTHROPIC_API_KEY='your-key'")
    exit(1)

# Get the path to the MCP server script
SCRIPT_DIR = Path(__file__).parent
MCP_SERVER_PATH = SCRIPT_DIR / "csv_query_mcp_server.py"


async def run_query(prompt: str, system_prompt: str = None, verbose: bool = False):
    """
    Run a query using Claude with the CSV MCP server.

    Args:
        prompt: The user's question
        system_prompt: Optional system prompt to guide Claude's behavior
        verbose: If True, show tool usage details
    """
    # Configure Claude to use the external MCP server via stdio
    options = ClaudeAgentOptions(
        model="claude-sonnet-4-5",
        system_prompt=system_prompt or "You are a helpful product assistant with access to a product catalog.",
        mcp_servers={
            "csv-query": {
                "type": "stdio",
                "command": "python",
                "args": [str(MCP_SERVER_PATH)]
            }
        },
        permission_mode="bypassPermissions",  # Auto-approve tool usage for demo
        max_turns=10,
    )

    print(f"\n{'='*70}")
    print(f"Query: {prompt}")
    print(f"{'='*70}\n")

    # Stream the response
    assistant_text = []

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    assistant_text.append(block.text)
                    if verbose:
                        print(f"Claude: {block.text}")
                # Show tool usage if verbose
                elif hasattr(block, 'name') and verbose:
                    print(f"🔧 Using tool: {block.name}")

        elif isinstance(message, ResultMessage) and verbose:
            print(f"\n💰 Cost: ${message.total_cost_usd:.4f}")
            if message.usage:
                print(f"📊 Input tokens: {message.usage.get('input_tokens', 0)}")
                print(f"📊 Output tokens: {message.usage.get('output_tokens', 0)}")

    # Print final response
    if not verbose and assistant_text:
        print("Response:")
        print('\n'.join(assistant_text))

    print(f"\n{'='*70}\n")


async def main():
    """Run several example queries demonstrating different capabilities."""

    print("\n" + "="*70)
    print("Claude Agents SDK - CSV Query Demo")
    print("="*70)

    # Example 1: Simple category search
    await run_query(
        "What electronics products do we have? List them with their prices.",
        verbose=False
    )

    # Example 2: Price range query
    await run_query(
        "Show me products that cost between $50 and $150",
        verbose=False
    )

    # Example 3: Top rated products
    await run_query(
        "What are the top 3 highest-rated products?",
        verbose=False
    )

    # Example 4: Category statistics
    await run_query(
        "Give me a summary of our product categories with average prices and ratings",
        verbose=False
    )

    # Example 5: Complex multi-step query (with verbose output)
    await run_query(
        """I need to buy some office equipment. Can you help me find:
        1. A good keyboard (check ratings)
        2. Any furniture items under $200
        3. Tell me if they're in stock
        """,
        verbose=True
    )


if __name__ == "__main__":
    asyncio.run(main())
