#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["claude-agent-sdk>=0.1.0", "python-dotenv"]
# ///
"""Demo 02 (variant) — Multi-turn research agent with ClaudeSDKClient.

Same MCP server as `research_agent.py`, but uses `ClaudeSDKClient` instead of
the one-shot `query()` helper. The client keeps the session alive across
turns so the agent can refine, follow up, and act on prior results without
the caller re-sending context.

Most real-world agent use cases are multi-turn (ask → refine → act); this is
the surface you'll reach for in production.

Run:
    export ANTHROPIC_API_KEY=sk-...
    uv run research_agent_multiturn.py
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

SERVER_PATH = (Path(__file__).parent / "mcp_server.py").resolve()

SYSTEM_PROMPT = (
    "You are a personal research assistant. Use the `mcp__research__*` tools "
    "to search the web and write markdown briefs into the sandboxed workspace. "
    "Keep filenames lowercase-hyphenated. Cite the brief path you produce."
)


def build_options() -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        mcp_servers={
            "research": {"command": "uv", "args": ["run", str(SERVER_PATH)]},
        },
        allowed_tools=["mcp__research__*"],
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
        await client.query("Research Agent Skills in the Claude Agent SDK and save a brief.")
        await stream_until_result(client)

        # Same session — full context carries over. The agent knows what
        # brief it just wrote and where it lives.
        await client.query("Now add a section comparing Skills to plain tools.")
        await stream_until_result(client)


if __name__ == "__main__":
    asyncio.run(main())
