#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["claude-agent-sdk>=0.1.0", "python-dotenv"]
# ///
"""Agent with ClaudeSDKClient and MCP servers.

Run:
    export ANTHROPIC_API_KEY=sk-...
    uv run agent_mcp.py
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
)
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = (
    "You are a personal assistant with browser and file system tools."
)

def build_options() -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        mcp_servers={
            "playwright": {
                "command": "npx", 
                "args": ["@playwright/mcp@latest"]},
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem"]},
        },
        allowed_tools=["mcp__playwright", "mcp__filesystem"],
    )

async def stream_until_result(client: ClaudeSDKClient) -> None:
    async for message in client.receive_response():
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Agent: {block.text}")
                elif isinstance(block, ToolUseBlock):
                    print(f"  → {block.name}({block.input})")
        elif isinstance(message, ResultMessage):
            return


async def main() -> None:
    async with ClaudeSDKClient(options=build_options()) as client:
        await client.query("""
                           Open the this website: 
                           https://www.oreilly.com/live-events/mcp-bootcamp-building-ai-agents-with-model-context-protocol/0642572264840/ 
                           and take a screenshot.
                           Save the screenshot to a new folder named screenshot-test.
                           """)
        await stream_until_result(client)


if __name__ == "__main__":
    asyncio.run(main())