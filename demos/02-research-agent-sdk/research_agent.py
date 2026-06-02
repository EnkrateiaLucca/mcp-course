#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["claude-agent-sdk", "python-dotenv"]
# ///
"""Demo 02 — Research assistant on the Claude Agent SDK.

Same use case as demos 00 and 01 (web search + filesystem research assistant),
but the agent loop is replaced by the **Claude Agent SDK**. The SDK is itself
an MCP host, so we point it at the *exact same* server we wrote in demo 01.

Compare:
- Demo 00: ~70 lines of agent-loop bookkeeping.
- Demo 01: same loop, tools now over MCP.
- Demo 02: no loop. Just configure the SDK and ask.

Run:
    export ANTHROPIC_API_KEY=sk-...
    uv run research_agent.py
    uv run research_agent.py "Research the latest LLM benchmarks and save a brief."

Docs: https://code.claude.com/docs/en/agent-sdk/overview
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    query,
)
from dotenv import load_dotenv

load_dotenv()

# Point the SDK at our demo 01 MCP server.
SERVER_PATH = (Path(__file__).parent.parent / "01-introduction-to-mcp" / "mcp_server.py").resolve()

SYSTEM_PROMPT = (
    "You are a personal research assistant. You can search the web and organize "
    "findings as files in the user's workspace. When asked to research a topic, "
    "search the web and save a short markdown brief with bullets and a sources "
    "section. Keep filenames lowercase-hyphenated."
)


def build_options() -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        mcp_servers={
            "research": {
                "command": "uv",
                "args": ["run", str(SERVER_PATH)],
            }
        },
        # MCP tools are namespaced as mcp__<server-name>__<tool-name>.
        # Allow all of ours; disallow Claude Code's built-in shell/edit tools
        # so the agent can only act through our MCP server.
        allowed_tools=["mcp__research__*"],
    )


async def run(user_prompt: str) -> None:
    options = build_options()
    print(f"\nUser: {user_prompt}\n")

    async for message in query(prompt=user_prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Agent: {block.text}")
                elif isinstance(block, ToolUseBlock):
                    print(f"  → {block.name}({block.input})")
        elif isinstance(message, ResultMessage) and message.subtype == "success":
            print(f"\n✅ Done. {message.result}")


if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]) or (
        "Research what the Model Context Protocol is and save a short markdown "
        "brief to research/mcp-brief.md with bullets and a sources section."
    )
    asyncio.run(run(prompt))
