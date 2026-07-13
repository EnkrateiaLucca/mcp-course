#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["claude-agent-sdk>=0.1.0", "python-dotenv"]
# ///
"""Demo 04 (variant) — Research agent using the SDK's BUILT-IN tools.

Same use case as research_agent.py, but no custom MCP server. The agent
uses the SDK's built-in `WebSearch`, `WebFetch`, `Read`, and `Write`
tools — the path Anthropic itself takes in the cookbook example
`00_The_one_liner_research_agent`.

Side-by-side teaching contrast:
  - research_agent.py             → bring your own tool via MCP server
  - research_agent_builtin_tools  → use the platform's tools, no server

The built-in path removes the live-class ddgs rate-limit risk entirely
and is the *shorter* code, but you give up the auth seam, the hooks,
the eval harness — i.e. everything the custom server lets you put under
your own control. Both are valid; the choice is about what you want to
own.

Run:
    export ANTHROPIC_API_KEY=sk-...
    uv run research_agent_builtin_tools.py "How does MCP authentication work?"
"""

from __future__ import annotations

import asyncio
import sys
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

WORKSPACE = (Path(__file__).parent / "workspace" / "briefs").resolve()
WORKSPACE.mkdir(parents=True, exist_ok=True)

SYSTEM_PROMPT = (
    "You are a research assistant. To answer a research request:\n"
    "  1. Use WebSearch to find 3-5 relevant sources.\n"
    "  2. Use WebFetch to read the top sources in full.\n"
    "  3. Write a markdown brief to {workspace}/<slug>.md with sections:\n"
    "     # Topic\n     ## Findings (bulleted, with inline citations)\n"
    "     ## Sources (list of URLs)\n"
    "Keep filenames lowercase-hyphenated. Cite the brief path you produced."
).format(workspace=WORKSPACE)


def build_options() -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        model="claude-sonnet-5",
        system_prompt=SYSTEM_PROMPT,
        cwd=str(WORKSPACE.parent.parent),
        allowed_tools=["WebSearch", "WebFetch", "Read", "Write"],
        permission_mode="bypassPermissions",
    )


async def run(prompt: str) -> None:
    print(f"User: {prompt}\n")
    async with ClaudeSDKClient(options=build_options()) as client:
        await client.query(prompt)
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)
                    elif isinstance(block, ToolUseBlock):
                        print(f"  → {block.name}")
            elif isinstance(message, ResultMessage):
                print(f"\n[done — cost (est) ${message.total_cost_usd or 0:.4f}]")


if __name__ == "__main__":
    user_prompt = " ".join(sys.argv[1:]) or "How does MCP authentication work?"
    asyncio.run(run(user_prompt))
