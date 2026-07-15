#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mcp[cli]>=1.12,<2",
#     "anthropic",
#     "python-dotenv",
#     "ddgs",
# ]
# ///
"""Host application — same agent loop as demo 00, but tools come from an MCP server.

Architecture:
    Host (this file)  ->  MCP Client (mcp_client.py)  ->  MCP Server (mcp_server.py)

The agent loop is identical to demo 00. The only difference is *where the tools
live*: instead of being Python functions in the same file, they are advertised
by an MCP server and called over the protocol. That's the whole point of MCP —
one server, many hosts.

Run:
    uv run mcp_host.py ./mcp_server.py
    uv run mcp_host.py ./mcp_server.py "Research what MCP is and save a brief."
"""

from __future__ import annotations

import asyncio
import json
import os
import sys

from anthropic import Anthropic
from dotenv import load_dotenv

from mcp_client import SimpleMCPClient

load_dotenv()
MODEL = "claude-sonnet-5"
SYSTEM = (
    "You are a personal research assistant. You can search the web and organize "
    "findings as files in the user's workspace. When asked to research a topic, "
    "search the web and save a short markdown brief with sources. Keep filenames "
    "lowercase-hyphenated."
)


def mcp_tools_to_claude(mcp_tools) -> list[dict]:
    """MCP tool schemas are already JSON Schema — just rename for Claude's API."""
    return [
        {
            "name": t.name,
            "description": t.description or "",
            "input_schema": t.inputSchema,
        }
        for t in mcp_tools
    ]


async def run_agent(client: SimpleMCPClient, user_query: str, max_iterations: int = 10) -> str:
    anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    tools = mcp_tools_to_claude(await client.list_tools())
    messages = [{"role": "user", "content": user_query}]
    print(f"\nUser: {user_query}\n")

    for i in range(max_iterations):
        response = anthropic.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM,
            messages=messages,
            tools=tools,
        )

        if response.stop_reason != "tool_use":
            text = "".join(b.text for b in response.content if hasattr(b, "text"))
            print(f"\nAgent: {text}")
            return text

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                args_preview = json.dumps(block.input)[:120]
                print(f"  [{i + 1}] mcp:{block.name}({args_preview})")
                result = await client.call_tool(block.name, block.input)
                # CallToolResult.content is a list of content blocks; flatten the text.
                content_text = "".join(
                    getattr(c, "text", str(c)) for c in (result.content or [])
                )
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": content_text or "(no output)",
                    "is_error": bool(result.isError),
                })
        messages.append({"role": "user", "content": tool_results})

    return "(max iterations reached)"


async def interactive(client: SimpleMCPClient) -> None:
    print("\n🤖 Research assistant ready. Type a request, or 'quit' to exit.\n")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line or line.lower() in {"quit", "exit"}:
            break
        await run_agent(client, line)


async def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: uv run mcp_host.py <path_to_server.py> [\"one-shot prompt\"]")
        sys.exit(1)

    server_path = sys.argv[1]
    one_shot = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None

    client = SimpleMCPClient()
    try:
        await client.connect_to_server(server_path)
        if one_shot:
            await run_agent(client, one_shot)
        else:
            await interactive(client)
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
