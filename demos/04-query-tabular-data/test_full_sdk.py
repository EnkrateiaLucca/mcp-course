#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "claude-agent-sdk>=0.1.0",
#     "anthropic>=0.40.0",
#     "pandas>=2.0.0",
# ]
# ///

import asyncio
from typing import Any
import pandas as pd
from pathlib import Path
from claude_agent_sdk import (
    tool,
    create_sdk_mcp_server,
    ClaudeAgentOptions,
    query,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ResultMessage
)

CSV_FILE_PATH = Path(__file__).parent / "sample_data.csv"

@tool("search_by_category", "Search products by category", {"category": str})
async def search_by_category(args: dict[str, Any]) -> dict[str, Any]:
    df = pd.read_csv(CSV_FILE_PATH)
    filtered = df[df['category'].str.lower() == args["category"].lower()]
    if filtered.empty:
        return {"content": [{"type": "text", "text": f"No products in {args['category']}"}]}
    return {"content": [{"type": "text", "text": filtered.to_string(index=False)}]}

@tool("search_by_price", "Search by price range", {"min_price": float, "max_price": float})
async def search_by_price(args: dict[str, Any]) -> dict[str, Any]:
    df = pd.read_csv(CSV_FILE_PATH)
    filtered = df[(df['price'] >= args["min_price"]) & (df['price'] <= args["max_price"])]
    if filtered.empty:
        return {"content": [{"type": "text", "text": "No products in range"}]}
    return {"content": [{"type": "text", "text": filtered.to_string(index=False)}]}

async def main():
    # Create MCP server
    csv_server = create_sdk_mcp_server(
        name="csv-query",
        version="1.0.0",
        tools=[search_by_category, search_by_price]
    )

    # Configure
    options = ClaudeAgentOptions(
        model="claude-sonnet-4-5",
        mcp_servers={"csv": csv_server},
        permission_mode="bypassPermissions",
        max_turns=5,
    )

    # Test
    print("Test 1: Category search")
    async for msg in query("Show me all electronics", options=options):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"Response: {block.text[:200]}...")

    print("\n\nTest 2: Price range")
    async for msg in query("Products between $50 and $150", options=options):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"Response: {block.text[:200]}...")

if __name__ == "__main__":
    asyncio.run(main())
