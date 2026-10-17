#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["claude-agent-sdk>=0.1.0", "python-dotenv"]
# ///
"""Demo 07 — Make the SDK actually load `mcp-builder-skill`.

Use case: 'The agent reaches for your repo's mcp-builder skill
automatically when asked to scaffold an MCP server.'

The gotchas that bite learners (called out in the SDK docs):

  - Skills are discovered only from the setting sources the SDK loads.
    Leave `setting_sources` unset and it loads 'user' + 'project' (your
    personal ~/.claude skills come along too); pass `[]` and the
    `skills=...` option finds none of them, only the CLI's built-ins.
    Pass ['project'] to load only the repo's skills.
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
        model="claude-sonnet-5-5",
        cwd=str(HERE),
        # Skills are discovered only through the 'user' / 'project' setting
        # sources. Unset loads both; [] loads none. ['project'] keeps
        # discovery to this repo's .claude/skills/.
        setting_sources=["project"],
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
                    print(s)
                    # print(f"  • {s.get('name', s)}")
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
