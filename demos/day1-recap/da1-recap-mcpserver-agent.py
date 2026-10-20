#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["claude-agent-sdk>=0.1.0", "ddgs", "python-dotenv"]
# ///

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    create_sdk_mcp_server,
    query,
    tool,
)
from ddgs import DDGS
from dotenv import load_dotenv

load_dotenv()

WORKSPACE = (Path(__file__).parent / "workspace").resolve()
WORKSPACE.mkdir(exist_ok=True)


# --- Tools: plain async functions + @tool ------------------------------------


@tool("web_search", "Search the web. Returns JSON [{title, url, snippet}].", {"query": str})
async def web_search(args: dict[str, Any]) -> dict[str, Any]:
    hits = DDGS().text(args["query"], max_results=5)
    results = [
        {"title": h.get("title"), "url": h.get("href"), "snippet": h.get("body")}
        for h in hits
    ]
    return {"content": [{"type": "text", "text": json.dumps(results, indent=2)}]}


@tool("save_brief", "Save a markdown brief to the workspace.", {"filename": str, "content": str})
async def save_brief(args: dict[str, Any]) -> dict[str, Any]:
    p = (WORKSPACE / args["filename"]).resolve()
    if WORKSPACE not in p.parents:
        return {"content": [{"type": "text", "text": "Error: path escapes workspace"}], "is_error": True}
    p.write_text(args["content"])
    return {"content": [{"type": "text", "text": f"Saved {args['filename']}"}]}

research_server = create_sdk_mcp_server(
    name="research",
    version="1.0.0",
    tools=[web_search, save_brief]
)

async def run(user_prompt: str) -> None:
    options=ClaudeAgentOptions(
        system_prompt="""You are a research assistant that searches the web and writes concise briefs.""",
        mcp_servers={"research": research_server},
        allowed_tools=["mcp__research__*"],
    )
    
    print(f"\nUser: {user_prompt}\n")
    
    async for message in query(prompt=user_prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Agent: {block.text}")
                elif isinstance(block, ToolUseBlock):
                    print(f"  → {block.name}")
        elif isinstance(message, ResultMessage) and message.subtype == "success":
            print(f"\n✅ Done. {message.result}")
    
if __name__== "__main__":
    prompt = " ".join(sys.argv[1:]) or "Research what MCP Apps are and save a brief to mcp-apps.md."
    asyncio.run(run(prompt))
        
    




