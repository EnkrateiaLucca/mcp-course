#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "claude-agent-sdk>=0.1.0",
#     "anthropic>=0.40.0",
#     "pandas>=2.0.0",
# ]
# ///

"""
Claude Agents SDK with In-Process CSV Query Tools Demo

This script demonstrates how to use Claude Agents SDK with in-process MCP tools
for querying CSV data. Tools are defined using the @tool decorator and run
directly in the application (no subprocess needed).

Based on Claude Agent SDK documentation:
https://platform.claude.com/docs/en/agent-sdk/overview
"""

import asyncio
import os
from pathlib import Path
from typing import Any
import pandas as pd
from claude_agent_sdk import (
    tool,
    create_sdk_mcp_server,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ResultMessage
)

# Ensure API key is set
if not os.getenv('ANTHROPIC_API_KEY'):
    print("⚠️  Warning: ANTHROPIC_API_KEY not set!")
    print("Please set it with: export ANTHROPIC_API_KEY='your-key'")
    exit(1)

# Get the path to the CSV file
SCRIPT_DIR = Path(__file__).parent
CSV_FILE_PATH = SCRIPT_DIR / "sample_data.csv"


# Define tools using @tool decorator
@tool("search_products_by_category", "Search for products by category", {"category": str})
async def search_products_by_category(args: dict[str, Any]) -> dict[str, Any]:
    """Search for products by category."""
    category = args["category"]
    df = pd.read_csv(CSV_FILE_PATH)
    filtered_df = df[df['category'].str.lower() == category.lower()]

    if filtered_df.empty:
        return {"content": [{"type": "text", "text": f"No products found in category: {category}"}]}

    return {"content": [{"type": "text", "text": filtered_df.to_string(index=False)}]}


@tool("search_products_by_price_range", "Search for products by price range", {"min_price": float, "max_price": float})
async def search_products_by_price_range(args: dict[str, Any]) -> dict[str, Any]:
    """Search for products within a price range."""
    min_price = args["min_price"]
    max_price = args["max_price"]
    df = pd.read_csv(CSV_FILE_PATH)
    filtered_df = df[(df['price'] >= min_price) & (df['price'] <= max_price)]

    if filtered_df.empty:
        return {"content": [{"type": "text", "text": f"No products found between ${min_price} and ${max_price}"}]}

    return {"content": [{"type": "text", "text": filtered_df.to_string(index=False)}]}


@tool("get_top_rated_products", "Get the top-rated products", {"limit": int})
async def get_top_rated_products(args: dict[str, Any]) -> dict[str, Any]:
    """Get the top-rated products."""
    limit = args.get("limit", 5)
    df = pd.read_csv(CSV_FILE_PATH)
    top_products = df.nlargest(limit, 'rating')
    return {"content": [{"type": "text", "text": top_products.to_string(index=False)}]}


@tool("get_category_statistics", "Get statistics about products grouped by category", {})
async def get_category_statistics(args: dict[str, Any]) -> dict[str, Any]:
    """Get statistics about products grouped by category."""
    df = pd.read_csv(CSV_FILE_PATH)
    stats = df.groupby('category').agg({
        'product_id': 'count',
        'price': 'mean',
        'rating': 'mean',
        'stock': 'sum'
    }).round(2)

    stats.columns = ['count', 'avg_price', 'avg_rating', 'total_stock']
    return {"content": [{"type": "text", "text": stats.to_string()}]}


async def run_example(client: ClaudeSDKClient, query_text: str, title: str, verbose: bool = False):
    """Run a single example query."""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    print(f"Query: {query_text}\n")

    await client.query(query_text)

    tools_used = []
    async for message in client.receive_response():
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Response: {block.text}")
                elif isinstance(block, ToolUseBlock):
                    tools_used.append(block.name)
                    if verbose:
                        print(f"[Using tool: {block.name}]")

        elif isinstance(message, ResultMessage):
            if verbose:
                print(f"\n💰 Cost: ${message.total_cost_usd:.4f}")
                if message.usage:
                    print(f"📊 Tokens: {message.usage.get('input_tokens', 0)} in, {message.usage.get('output_tokens', 0)} out")
                if tools_used:
                    print(f"🔧 Tools used: {', '.join(tools_used)}")

    print(f"{'='*70}\n")


async def main():
    """Run several example queries demonstrating different capabilities."""

    print("\n" + "="*70)
    print("Claude Agents SDK - CSV Query Tools Demo")
    print("="*70)

    # Create SDK MCP server with our tools
    csv_server = create_sdk_mcp_server(
        name="csv-query",
        version="1.0.0",
        tools=[
            search_products_by_category,
            search_products_by_price_range,
            get_top_rated_products,
            get_category_statistics,
        ]
    )

    # Configure Claude to use the in-process MCP server
    options = ClaudeAgentOptions(
        model="claude-sonnet-4-5",
        system_prompt="""You are a helpful product assistant with access to a product catalog.
        Use the available tools to answer questions about products. Always provide clear, helpful responses.""",
        mcp_servers={"csv": csv_server},
        permission_mode="bypassPermissions",  # Auto-approve tool usage for demo
        max_turns=10,
    )

    # Run examples using ClaudeSDKClient for stateful conversation
    async with ClaudeSDKClient(options=options) as client:
        # Example 1: Simple category search
        await run_example(
            client,
            "What electronics products do we have? List them with their prices.",
            "Example 1: Category Search"
        )

        # Example 2: Price range query
        await run_example(
            client,
            "Show me products that cost between $50 and $150",
            "Example 2: Price Range Query"
        )

        # Example 3: Top rated products
        await run_example(
            client,
            "What are the top 3 highest-rated products?",
            "Example 3: Top Rated Products"
        )

        # Example 4: Category statistics
        await run_example(
            client,
            "Give me a summary of our product categories with average prices and ratings",
            "Example 4: Category Statistics"
        )

        # Example 5: Complex multi-step query (with verbose output)
        await run_example(
            client,
            """I need to buy some office equipment. Can you help me find:
            1. A good keyboard (check ratings)
            2. Any furniture items under $200
            3. Tell me if they're in stock""",
            "Example 5: Complex Multi-Step Query",
            verbose=True
        )

    print("\n" + "="*70)
    print("Demo completed successfully!")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
