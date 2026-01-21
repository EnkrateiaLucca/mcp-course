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
    ClaudeSDKClient,
    AssistantMessage,
    TextBlock,
    ToolUseBlock
)

CSV_FILE_PATH = Path(__file__).parent / "sample_data.csv"

@tool("get_electronics", "Get all electronics products", {})
async def get_electronics(args: dict[str, Any]) -> dict[str, Any]:
    """Get all electronics products."""
    df = pd.read_csv(CSV_FILE_PATH)
    electronics = df[df['category'] == 'Electronics']
    return {
        "content": [{"type": "text", "text": electronics.to_string(index=False)}]
    }

async def main():
    print("Testing MCP tools with Claude SDK...")

    # Create SDK MCP server
    csv_server = create_sdk_mcp_server(
        name="csv-tools",
        version="1.0.0",
        tools=[get_electronics]
    )

    # Configure options
    options = ClaudeAgentOptions(
        model="claude-sonnet-4-5",
        mcp_servers={"csv": csv_server},
        permission_mode="bypassPermissions",  # Auto-approve tool usage
        max_turns=5,
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("Show me electronics products")

        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")
                    elif isinstance(block, ToolUseBlock):
                        print(f"[Using tool: {block.name}]")

if __name__ == "__main__":
    asyncio.run(main())
