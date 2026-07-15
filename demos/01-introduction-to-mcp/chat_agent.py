#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["claude-agent-sdk>=0.1.0"]
# ///
"""A minimal chat CLI where the agent can ONLY act through our MCP server.

The big idea of this demo:

    You (terminal) ──> Claude Agent SDK (the HOST) ──> mcp_server.py (the SERVER)

The SDK runs the whole agent loop for us (model calls, tool execution,
retries). Our only jobs are: (1) point it at an MCP server, (2) say which
tools it may use, (3) stream the conversation to the terminal.

Run it:  uv run chat_agent.py
"""

from __future__ import annotations

import asyncio
from pathlib import Path
import os

from claude_agent_sdk import (
    AssistantMessage,      # a turn from the model: text and/or tool calls
    ClaudeAgentOptions,    # all agent configuration lives in this one object
    ClaudeSDKClient,       # multi-turn client: ONE session, memory across turns
    TextBlock,             # plain text the model wrote
    ToolUseBlock,          # the model deciding to call a tool
)

# The MCP server is just a script on disk. The SDK will spawn it as a
# subprocess and speak the protocol over stdio — we never import it.
SERVER_PATH = (Path(__file__).parent / "mcp_server.py").resolve()
WORKSPACE = (Path(__file__).parent / "workspace").resolve()

SYSTEM_PROMPT = """\
You are a personal research assistant. Your tools live under two namespaces:
- `mcp__research__`: web_search, write_file, read_file, edit_file,
  list_files, move_file, delete_file. File paths are resolved inside a
  sandboxed workspace — always pass relative paths (e.g. `notes.md`).
- `mcp__notion__`: Notion API tools (search, read, and write pages/databases).
When asked to research a topic: (1) web_search, (2) write a markdown brief
with bullets and a `## Sources` section. Keep filenames lowercase-hyphenated.
When asked to save or publish to Notion, use the notion tools.
"""

OPTIONS = ClaudeAgentOptions(
    system_prompt=SYSTEM_PROMPT,
    # "Here is a server; launch it with this command." That's the whole
    # integration — the SDK discovers the tools by asking the server.
    mcp_servers={
        "research": {"command": "uv", "args": ["run", str(SERVER_PATH)]},
        # Notion's remote server (https://mcp.notion.com/mcp) needs an
        # interactive OAuth flow the headless SDK can't run. The official
        # stdio server reuses the OAuth credentials already cached by a
        # previous login (same config as `claude mcp get notion`).
        "notion": {"command": "npx", "args": ["-y", "@notionhq/notion-mcp-server"]},
        "env": {"NOTION_TOKEN": os.environ["NOTION_TOKEN"]},
    },
    # MCP tools are namespaced mcp__<server>__<tool>. Allowing ONLY this
    # pattern means the agent can't touch Claude Code's built-in tools
    # (Bash, Edit, ...) — every action must go through our server.
    allowed_tools=["mcp__research__*", "mcp__notion__*"],
)


async def chat() -> None:
    # To create a chat experience within claude-agents-sdk 
    # we use the ClaudeSDKClient
    # One client = one session. Ask a follow-up ("now summarize that file")
    print("START of Session")
    async with ClaudeSDKClient(options=OPTIONS) as client:
        print(f"Chatting with the research agent (workspace: {WORKSPACE})")
        print("Type 'exit' or 'quit' to quit.\n")
        
        # this is the chat loop! The Agent loop is being handled
        # by the claude agents sdk behind the hood!
        while True:
            try:
                user_input = input("you > ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if user_input.lower() in {"exit", "quit"} or not user_input:
                break
            
            # sending message to the agent
            await client.query(user_input)
            
            # ...then stream everything back until the turn is done.
            # We surface tool calls so students can SEE the agent loop.
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, ToolUseBlock):
                            print(f"  [tool] {block.name} {block.input}")
                        elif isinstance(block, TextBlock):
                            print(f"\nagent > {block.text}")
            print() # prints a new line

    print("End of Session!")
    print("bye!")
            
if __name__ == "__main__":
    # this chat() functions plays the role of the host application
    asyncio.run(chat())    
        