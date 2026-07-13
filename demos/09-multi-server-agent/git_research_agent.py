#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["claude-agent-sdk>=0.1.0", "python-dotenv"]
# ///
"""Demo 09 (variant) — Compose our research server with the GIT MCP server.

The Git MCP server is the canonical 'real third-party server' example
from Anthropic's `02_The_observability_agent` cookbook. It exposes 13+
tools (status, log, diff, branch, commit, ...). Our agent gets git
literacy without us writing any git code.

Tool search note: the SDK has MCP tool search on by default — when a
server exposes many tools (the GitHub MCP server has 100+), tool defs
are withheld and loaded per turn. So adding a big server doesn't burn
the context window up front.

Run:
    export ANTHROPIC_API_KEY=sk-...
    # uvx installs/runs the Git MCP server on first use.
    uv run git_research_agent.py
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from claude_agent_sdk import (
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

DEMO_04 = Path(__file__).resolve().parent.parent / "04-production-research-agent"
RESEARCH_SERVER = DEMO_04 / "research_server.py"
REPO_ROOT = Path(__file__).resolve().parents[2]

SYSTEM_PROMPT = (
    "You are a research lead with access to two MCP servers: 'research' "
    "(web search + brief writing) and 'git' (read-only inspection of this "
    "repo). When asked about the project, prefer git tools for current "
    "state and research tools for outside context."
)


def build_options() -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        model="claude-sonnet-5",
        system_prompt=SYSTEM_PROMPT,
        mcp_servers={
            "research": {"command": "uv", "args": ["run", str(RESEARCH_SERVER)]},
            # The Git MCP server, run via uvx (Python ecosystem equivalent of
            # npx). Reference: github.com/modelcontextprotocol/servers
            "git": {
                "command": "uvx",
                "args": ["mcp-server-git", "--repository", str(REPO_ROOT)],
            },
        },
        allowed_tools=["mcp__research__*", "mcp__git__*"],
    )


async def main() -> None:
    prompt = (
        "Look at the last 3 commits on this repo with the git server, then "
        "research one technical term used in those commit messages and save "
        "a brief."
    )
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
    asyncio.run(main())
