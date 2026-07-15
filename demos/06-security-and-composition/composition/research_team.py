#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["claude-agent-sdk>=0.1.0", "python-dotenv"]
# ///
"""Demo 09 — A research agent that COMPOSES servers and DELEGATES.

Two new things vs demo 04:

  1. Multi-server. We add Playwright's official MCP server
     (`npx @playwright/mcp@latest`) alongside our own. The agent can now
     research a topic AND open a live page to verify a claim — no custom
     code on our side.

  2. Subagent. We define a 'fact-checker' agent that the parent can
     delegate to via the SDK's built-in `Agent` tool. The subagent has
     a narrower toolset (Read + Playwright only) and a focused prompt.

Subagent gotchas (from the docs):
  - Fresh context: the subagent does not see parent conversation history.
  - Cannot spawn its own subagents.
  - Inherits permissive parent permission_modes ('bypassPermissions',
    'acceptEdits') non-overridably. Keep the parent strict.

Run:
    export ANTHROPIC_API_KEY=sk-...
    # Playwright MCP needs npx in PATH (installs on first run).
    uv run research_team.py "Research MCP authentication and verify each source URL is still live."
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from claude_agent_sdk import (
    AgentDefinition,
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ToolUseBlock,
)
from dotenv import load_dotenv

load_dotenv()

# Reuse the demo 04 research server (in-process via stdio). We expect demo 04
# to be present as a sibling directory.
DEMO_04 = Path(__file__).resolve().parent.parent / "04-production-research-agent"
RESEARCH_SERVER = DEMO_04 / "research_server.py"

SYSTEM_PROMPT = (
    "You are a research lead. Use mcp__research__research_topic to produce "
    "a brief on the user's topic. THEN delegate to the 'fact-checker' agent "
    "to verify the brief against its cited sources. Report what the "
    "fact-checker found."
)


def build_options() -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        model="claude-sonnet-5",
        system_prompt=SYSTEM_PROMPT,
        mcp_servers={
            # Our own server, run as a subprocess (stdio transport).
            "research": {"command": "uv", "args": ["run", str(RESEARCH_SERVER)]},
            # Playwright's published MCP server. Zero custom code.
            "playwright": {"command": "npx", "args": ["@playwright/mcp@latest"]},
        },
        allowed_tools=[
            "mcp__research__*",
            "mcp__playwright__*",
            "Read",
            "Agent",  # required for the parent to delegate to subagents
        ],
        agents={
            "fact-checker": AgentDefinition(
                description=(
                    "Verifies that claims in a research brief are supported by "
                    "the brief's cited sources. Use AFTER the brief is saved."
                ),
                prompt=(
                    "You are a meticulous fact-checker. Read the brief at the "
                    "path the parent gives you. For each cited source URL, open "
                    "it with the Playwright MCP tools and confirm the page is "
                    "live and the brief's claims are supported by visible text. "
                    "Report a per-claim verdict: VERIFIED, UNSUPPORTED, or "
                    "PAGE_UNAVAILABLE."
                ),
                tools=["Read", "mcp__playwright__*"],  # narrower than parent
                model="sonnet",
            ),
        },
    )


async def run(prompt: str) -> None:
    print(f"User: {prompt}\n")
    async with ClaudeSDKClient(options=build_options()) as client:
        await client.query(prompt)
        async for message in client.receive_response():
            if isinstance(message, SystemMessage) and message.subtype == "init":
                for srv in message.data.get("mcp_servers", []) or []:
                    print(f"[mcp] {srv.get('name')}: {srv.get('status')}")
            elif isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)
                    elif isinstance(block, ToolUseBlock):
                        print(f"  → {block.name}")
            elif isinstance(message, ResultMessage):
                print(f"\n[done — cost (est) ${message.total_cost_usd or 0:.4f}]")


if __name__ == "__main__":
    user_prompt = " ".join(sys.argv[1:]) or (
        "Research MCP authentication, save a brief, then delegate to the "
        "fact-checker to verify each source URL is still live."
    )
    asyncio.run(run(user_prompt))
