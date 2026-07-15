#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["openai-agents", "python-dotenv"]
# ///
"""Demo 02 (alt) — Research assistant on the OpenAI Agents SDK.

Mirror of `research_agent.py` (Claude Agent SDK version), but the agent loop
is provided by the **OpenAI Agents SDK**. Same MCP server, same workspace,
same use case — just a different host.

Run:
    export OPENAI_API_KEY=sk-...
    uv run openai_research_agent_alternative.py
    uv run openai_research_agent_alternative.py "Research the latest LLM benchmarks and save a brief."

Docs: https://openai.github.io/openai-agents-python/mcp/
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from dotenv import load_dotenv

load_dotenv()

SERVER_PATH = (Path(__file__).parent / "mcp_server.py").resolve()
WORKSPACE = (Path(__file__).parent / "workspace").resolve()

SYSTEM_PROMPT = (
    "You are a personal research assistant. You have MCP tools for "
    "`web_search`, `write_file`, `read_file`, `edit_file`, `list_files`, "
    "`move_file`, `delete_file`. All file paths are resolved inside a "
    "sandboxed workspace — always pass *relative* paths (e.g. "
    "`skills-brief.md`, not absolute paths). When asked to research a "
    "topic: (1) call `web_search`, (2) write a markdown brief with bullets "
    "and a `## Sources` section via `write_file`. Keep filenames "
    "lowercase-hyphenated."
)


async def run(user_prompt: str) -> None:
    async with MCPServerStdio(
        name="research",
        params={"command": "uv", "args": ["run", str(SERVER_PATH)]},
    ) as server:
        agent = Agent(
            name="Research Assistant",
            model="gpt-5.4-mini",
            instructions=SYSTEM_PROMPT,
            mcp_servers=[server],
        )

        print(f"\nUser: {user_prompt}\n")
        result = await Runner.run(agent, user_prompt)
        print(f"Agent: {result.final_output}")


if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]) or (
        "Research what Agent Skills are and how they work in the Claude Agent "
        "SDK, then save a brief to `skills-brief.md` with bullets and a "
        "sources section."
    )
    print(f"Workspace: {WORKSPACE}")
    asyncio.run(run(prompt))
