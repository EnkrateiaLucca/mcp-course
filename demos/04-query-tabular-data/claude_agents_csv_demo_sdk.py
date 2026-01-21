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
    query,
    AssistantMessage,
    TextBlock,
    ResultMessage,
    ToolUseBlock
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
@tool("get_all_products", "Get all products from the CSV file", {})
async def get_all_products(args: dict[str, Any]) -> dict[str, Any]:
    """Get all products from the CSV file."""
    df = pd.read_csv(CSV_FILE_PATH)
    return {
        "content": [{"type": "text", "text": df.to_string(index=False)}]
    }


@tool("search_products_by_category", "Search for products by category", {"category": str})
async def search_products_by_category(args: dict[str, Any]) -> dict[str, Any]:
    """Search for products by category."""
    category = args["category"]
    df = pd.read_csv(CSV_FILE_PATH)
    filtered_df = df[df['category'].str.lower() == category.lower()]

    if filtered_df.empty:
        return {
            "content": [{"type": "text", "text": f"No products found in category: {category}"}]
        }

    return {
        "content": [{"type": "text", "text": filtered_df.to_string(index=False)}]
    }


@tool("search_products_by_price_range", "Search for products by price range", {"min_price": float, "max_price": float})
async def search_products_by_price_range(args: dict[str, Any]) -> dict[str, Any]:
    """Search for products within a price range."""
    min_price = args["min_price"]
    max_price = args["max_price"]
    df = pd.read_csv(CSV_FILE_PATH)
    filtered_df = df[(df['price'] >= min_price) & (df['price'] <= max_price)]

    if filtered_df.empty:
        return {
            "content": [{"type": "text", "text": f"No products found between ${min_price} and ${max_price}"}]
        }

    return {
        "content": [{"type": "text", "text": filtered_df.to_string(index=False)}]
    }


@tool("get_product_by_name", "Get details of a specific product by name", {"product_name": str})
async def get_product_by_name(args: dict[str, Any]) -> dict[str, Any]:
    """Get details of a specific product by name."""
    product_name = args["product_name"]
    df = pd.read_csv(CSV_FILE_PATH)
    filtered_df = df[df['product_name'].str.contains(product_name, case=False, na=False)]

    if filtered_df.empty:
        return {
            "content": [{"type": "text", "text": f"No product found with name containing: {product_name}"}]
        }

    return {
        "content": [{"type": "text", "text": filtered_df.to_string(index=False)}]
    }


@tool("get_top_rated_products", "Get the top-rated products", {"limit": int})
async def get_top_rated_products(args: dict[str, Any]) -> dict[str, Any]:
    """Get the top-rated products."""
    limit = args.get("limit", 5)
    df = pd.read_csv(CSV_FILE_PATH)
    top_products = df.nlargest(limit, 'rating')
    return {
        "content": [{"type": "text", "text": top_products.to_string(index=False)}]
    }


@tool("get_products_in_stock", "Get products that have at least the specified stock level", {"min_stock": int})
async def get_products_in_stock(args: dict[str, Any]) -> dict[str, Any]:
    """Get products that have at least the specified stock level."""
    min_stock = args.get("min_stock", 1)
    df = pd.read_csv(CSV_FILE_PATH)
    in_stock_df = df[df['stock'] >= min_stock]
    return {
        "content": [{"type": "text", "text": in_stock_df.to_string(index=False)}]
    }


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
    return {
        "content": [{"type": "text", "text": stats.to_string()}]
    }


async def run_query_with_tools(prompt: str, verbose: bool = False):
    """
    Run a query using Claude with in-process CSV query tools.

    Args:
        prompt: The user's question
        verbose: If True, show tool usage details
    """
    # Create SDK MCP server with our tools
    csv_server = create_sdk_mcp_server(
        name="csv-query",
        version="1.0.0",
        tools=[
            get_all_products,
            search_products_by_category,
            search_products_by_price_range,
            get_product_by_name,
            get_top_rated_products,
            get_products_in_stock,
            get_category_statistics,
        ]
    )

    # Configure Claude to use the in-process MCP server
    options = ClaudeAgentOptions(
        model="claude-sonnet-4-5",
        system_prompt="""
        You are a helpful product assistant with access to a product catalog.
        Use the available tools to answer questions about products, including:
        - Searching by category, price, or name
        - Finding top-rated products
        - Checking inventory levels
        - Providing category statistics

        Always provide clear, helpful responses based on the data.
        """,
        mcp_servers={"csv-query": csv_server},
        permission_mode="bypassPermissions",  # Auto-approve tool usage for demo
        max_turns=10,
    )

    print(f"\n{'='*70}")
    print(f"Query: {prompt}")
    print(f"{'='*70}\n")

    # Stream the response
    assistant_text = []
    tools_used = []

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    assistant_text.append(block.text)
                    if verbose:
                        print(f"Claude: {block.text}")
                # Track tool usage
                elif isinstance(block, ToolUseBlock):
                    tools_used.append(block.name)
                    if verbose:
                        print(f"🔧 Using tool: {block.name} with input: {block.input}")

        elif isinstance(message, ResultMessage):
            if verbose:
                print(f"\n💰 Cost: ${message.total_cost_usd:.4f}")
                if message.usage:
                    print(f"📊 Input tokens: {message.usage.get('input_tokens', 0)}")
                    print(f"📊 Output tokens: {message.usage.get('output_tokens', 0)}")
                if tools_used:
                    print(f"🔧 Tools used: {', '.join(tools_used)}")

    # Print final response
    if not verbose and assistant_text:
        print("Response:")
        print('\n'.join(assistant_text))

    print(f"\n{'='*70}\n")


async def main():
    """Run several example queries demonstrating different capabilities."""

    print("\n" + "="*70)
    print("Claude Agents SDK - In-Process CSV Query Tools Demo")
    print("="*70)

    # Example 1: Simple category search
    await run_query_with_tools(
        "What electronics products do we have? List them with their prices.",
        verbose=False
    )

    # Example 2: Price range query
    await run_query_with_tools(
        "Show me products that cost between $50 and $150",
        verbose=False
    )

    # Example 3: Top rated products
    await run_query_with_tools(
        "What are the top 3 highest-rated products?",
        verbose=False
    )

    # Example 4: Category statistics
    await run_query_with_tools(
        "Give me a summary of our product categories with average prices and ratings",
        verbose=False
    )

    # Example 5: Complex multi-step query (with verbose output)
    await run_query_with_tools(
        """I need to buy some office equipment. Can you help me find:
        1. A good keyboard (check ratings)
        2. Any furniture items under $200
        3. Tell me if they're in stock
        """,
        verbose=True
    )


if __name__ == "__main__":
    asyncio.run(main())
