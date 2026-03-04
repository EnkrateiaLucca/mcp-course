# /// script
# requires-python = ">=3.12"
# dependencies = ["claude-agent-sdk>=0.1.21"]
# ///

"""
Automation Agent — Claude Agent SDK + MCP

An interactive agent that writes, tests, and runs Python automation scripts.
The agent uses Claude for intelligence and an MCP server for sandboxed execution.

Usage: uv run automation_agent.py
"""

import asyncio
import os
from claude_agent_sdk import ClaudeAgentOptions, query

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_scripts")

options = ClaudeAgentOptions(
    model="claude-sonnet-4-5",
    system_prompt="""You are a Python automation assistant. You help users create
simple, practical Python scripts for everyday tasks.

Your workflow:
1. Understand what the user wants to automate
2. Write a clean Python script using save_script
3. Run the script with run_script to verify it works
4. If there are errors, read the script, fix it, and re-run

Rules for scripts you write:
- Use only the Python standard library (no pip installs needed)
- Keep scripts simple and self-contained (under 80 lines)
- Always include a if __name__ == '__main__' block
- Add a brief docstring explaining what the script does
- Print clear output so the user can see what happened

Available tools from MCP server:
- save_script(filename, code) — save a .py file
- list_scripts() — see all saved scripts
- read_script(filename) — read a script's contents
- run_script(filename, args) — execute a script (30s timeout)
- delete_script(filename) — remove a script

When the user asks you to create something, write the script, save it,
then immediately test it by running it. Fix any errors before reporting back.
""",
    mcp_servers={
        "scripts": {
            "type": "stdio",
            "command": "uv",
            "args": ["run", os.path.join(os.path.dirname(os.path.abspath(__file__)), "automation_mcp_server.py")],
        }
    },
    permission_mode="bypassPermissions",
)


async def main():
    print("┌─────────────────────────────────────────────────┐")
    print("│   Automation Agent — Create & Run Python Scripts │")
    print("│   Powered by Claude Agent SDK + MCP             │")
    print("└─────────────────────────────────────────────────┘")
    print()
    print(f"Scripts are saved to: {SCRIPTS_DIR}")
    print()
    print("Examples:")
    print('  "Create a script that finds duplicate files in a folder"')
    print('  "Make a script to rename files with today\'s date"')
    print('  "Write a CSV to JSON converter"')
    print('  "List my scripts" / "Run hello.py"')
    print()
    print("Type 'quit' to exit\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if user_input.lower() in ["quit", "exit", "q"]:
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        print()
        async for message in query(prompt=user_input, options=options):
            print(message, end="", flush=True)
        print("\n")


if __name__ == "__main__":
    asyncio.run(main())
