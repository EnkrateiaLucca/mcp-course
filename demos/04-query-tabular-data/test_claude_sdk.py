#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "claude-agent-sdk>=0.1.0",
#     "anthropic>=0.40.0",
# ]
# ///

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock

async def main():
    print("Testing basic Claude Agent SDK query...")

    options = ClaudeAgentOptions(
        model="claude-sonnet-4-5",
        tools=[],  # No tools
        max_turns=1,
    )

    async for message in query(prompt="What is 2 + 2?", options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Response: {block.text}")

if __name__ == "__main__":
    asyncio.run(main())
