#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["claude-agent-sdk>=0.1.0", "python-dotenv"]
# ///
"""Demo 07 — Make the SDK actually load `mcp-builder-skill`.

Use case: 'The agent reaches for your repo's mcp-builder skill
automatically when asked to scaffold an MCP server.'

The gotchas that bite learners (called out in the SDK docs):

  - `setting_sources` must include 'project' (and/or 'user') for skills
    to be discovered. With the default `setting_sources=[]`, the
    `skills=...` option loads NOTHING.
  - The `allowed-tools` frontmatter inside SKILL.md is IGNORED by the
    SDK — only Claude Code (the CLI) reads it. Gate tools through the
    SDK's `allowed_tools` option instead.
  - `cwd` controls which project folder counts as 'project' for skills
    discovery.

Run:
    export ANTHROPIC_API_KEY=sk-...
    uv run skill_loader_demo.py
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

HERE = Path(__file__).parent.resolve()


def build_options() -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        model="claude-sonnet-4-6",
        cwd=str(HERE),
        # REQUIRED: skills are discovered only through 'user' / 'project'
        # setting sources. Default is []; without this, skills="all" loads
        # nothing.
        setting_sources=["user", "project"],
        skills="all",
        allowed_tools=["Read", "Write", "Bash", "Skill"],
        permission_mode="bypassPermissions",
    )


PROMPT = (
    "Scaffold a new MCP server called 'pg-inspector' that exposes one "
    "tool, `list_tables(database_url: str)`, returning a list of table "
    "names from a Postgres connection string. Use the mcp-builder skill "
    "in this project. Write the server to ./scratch/pg_inspector.py."
)


async def main() -> None:
    async with ClaudeSDKClient(options=build_options()) as client:
        await client.query(PROMPT)
        async for message in client.receive_response():
            if isinstance(message, SystemMessage) and message.subtype == "init":
                skills = message.data.get("skills", []) or []
                print(f"[skills discovered: {len(skills)}]")
                for s in skills:
                    print(f"  • {s.get('name', s)}")
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
