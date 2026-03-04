# /// script
# requires-python = ">=3.12"
# dependencies = ["claude-agent-sdk"]
# ///

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    async for message in query(
        prompt="Transcribe all the .mp4 files in the current directory.",
        options=ClaudeAgentOptions(
            system_prompt="You are a helpful assistant that can run bash commands,\
                if the user asks for a transcription , use the transcribe cli tool.",
            allowed_tools=["Bash"]
        ),
    ):
        print(message)

asyncio.run(main())