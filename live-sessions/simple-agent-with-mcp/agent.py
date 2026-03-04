# /// script
# requires-python = ">=3.12"
# dependencies = ["claude-agent-sdk"]
# ///

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage
import os
import sys

async def main():
    options = ClaudeAgentOptions(
        model="claude-sonnet-4-6",
        mcp_servers={
            "get-time": {
                "command": "uv",
                "args": ["run", "mcp_server.py"]
            }
        },
        allowed_tools=["mcp__get-time__*"]
    )
    async for message in query(prompt="What is the current time?\
        Use the get-time mcp server to answer.", options=options):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(message.result)

asyncio.run(main())