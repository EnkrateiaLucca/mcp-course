# /// script
# requires-python = ">=3.12"
# dependencies = ["claude-agent-sdk>=0.1.21"]
# ///


import asyncio
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    model="claude-sonnet-4-5",
    permission_mode="bypassPermissions",
    max_turns=10,
)

async def main():
    query_user_input = input("Enter your query:")
    async for message in query(prompt=query_user_input, options=options):
        print(message)

if __name__ == "__main__":
    asyncio.run(main())