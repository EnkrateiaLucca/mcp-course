# /// script
# requires-python = ">=3.12"
# dependencies = ["claude-agent-sdk"]
# ///

import asyncio
import json
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import (
    AssistantMessage,
    ResultMessage,
    UserMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock,
)


async def main():
    options = ClaudeAgentOptions(
        model="claude-sonnet-4-6",
        mcp_servers={
            "csv-query": {
                "command": "uv",
                "args": ["run", "mcp_database_server.py"],
            }
        },
        allowed_tools=["mcp__csv-query__*"],
    )

    async for message in query(
        prompt="Use the csv-query mcp server to answer: What is the total sales amount from the sales database in ./sample_data.csv?",
        options=options,
    ):
        # --- Assistant turn: text or tool calls ---
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"\n💬 Assistant: {block.text}")
                elif isinstance(block, ToolUseBlock):
                    print(f"\n🔧 Tool Call: {block.name}")
                    print(f"   Input: {json.dumps(block.input, indent=2)}")

        # --- User turn: tool results fed back ---
        elif isinstance(message, UserMessage):
            if isinstance(message.content, list):
                for block in message.content:
                    if isinstance(block, ToolResultBlock):
                        status = "❌ Error" if block.is_error else "✅ Result"
                        print(f"\n{status} from tool:")
                        print(f"   {block.content[:300] if isinstance(block.content, str) else block.content}")

        # --- Final result ---
        elif isinstance(message, ResultMessage):
            print("\n" + "=" * 50)
            print(f"🏁 Done | Turns: {message.num_turns} | Cost: ${message.total_cost_usd:.4f} | Duration: {message.duration_ms}ms")
            if message.result:
                print(f"\n📊 Final Answer:\n{message.result}")


asyncio.run(main())
