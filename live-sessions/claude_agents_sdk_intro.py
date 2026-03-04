# /// script
# requires-python = ">=3.12"
# dependencies = ["claude-agent-sdk"]
# ///

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage
import os
import sys

async def main():
    project_dir = os.path.abspath(os.path.dirname(__file__))
    options = ClaudeAgentOptions(
        mcp_servers={
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", f"{project_dir}"]
            }
        },
        allowed_tools=["mcp__filesystem__*"]
    )

    async for message in query(prompt="List files in my project", options=options):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(message.result)

asyncio.run(main())