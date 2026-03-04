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
from claude_agent_sdk import (
    ClaudeAgentOptions,
    query,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock,
)

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_scripts")

# ANSI color helpers
DIM = "\033[2m"
BOLD = "\033[1m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
RED = "\033[31m"
RESET = "\033[0m"

# Friendly labels for MCP tool calls
TOOL_LABELS = {
    "save_script": ("Saving script", GREEN),
    "list_scripts": ("Listing scripts", CYAN),
    "read_script": ("Reading script", CYAN),
    "run_script": ("Running script", YELLOW),
    "delete_script": ("Deleting script", RED),
}


def format_tool_call(block):
    """Format a ToolUseBlock into a readable one-liner."""
    short_name = block.name.split("__")[-1] if "__" in block.name else block.name
    label, color = TOOL_LABELS.get(short_name, (short_name, DIM))

    detail = ""
    if isinstance(block.input, dict):
        if "filename" in block.input:
            detail = f" -> {block.input['filename']}"

    return f"{color}  [{label}{detail}]{RESET}"


def format_tool_result(block):
    """Format a ToolResultBlock into readable output."""
    content = block.content if isinstance(block.content, str) else str(block.content)

    if not content or not content.strip():
        return None

    # Truncate very long results for readability
    lines = content.strip().splitlines()
    if len(lines) > 15:
        lines = lines[:12] + [f"{DIM}  ... ({len(lines) - 12} more lines){RESET}"]

    formatted = "\n".join(f"  {DIM}| {line}{RESET}" for line in lines)

    if block.is_error:
        return f"  {RED}Error:{RESET}\n{formatted}"
    return formatted


options = ClaudeAgentOptions(
    model="claude-sonnet-4-6",
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
            "args": [
                "run",
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "automation_mcp_server.py",
                ),
            ],
        }
    },
    allowed_tools=["mcp__scripts__*"],
    permission_mode="bypassPermissions",
)


async def main():
    print(f"{BOLD}┌─────────────────────────────────────────────────┐{RESET}")
    print(f"{BOLD}│   Automation Agent — Create & Run Python Scripts │{RESET}")
    print(f"{BOLD}│   Powered by Claude Agent SDK + MCP             │{RESET}")
    print(f"{BOLD}└─────────────────────────────────────────────────┘{RESET}")
    print()
    print(f"  {DIM}Scripts directory: {SCRIPTS_DIR}{RESET}")
    print()
    print("  Try:")
    print(f'    {CYAN}"Create a script that finds duplicate files in a folder"{RESET}')
    print(f'    {CYAN}"Make a password generator"{RESET}')
    print(f'    {CYAN}"Write a CSV to JSON converter"{RESET}')
    print(f'    {CYAN}"List my scripts" / "Run hello.py"{RESET}')
    print()
    print(f"  Type {BOLD}quit{RESET} to exit\n")

    while True:
        try:
            user_input = input(f"{BOLD}You:{RESET} ").strip()
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
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text, end="", flush=True)
                    elif isinstance(block, ToolUseBlock):
                        print(f"\n{format_tool_call(block)}", flush=True)
                    elif isinstance(block, ToolResultBlock):
                        result = format_tool_result(block)
                        if result:
                            print(result, flush=True)

            elif isinstance(message, ResultMessage):
                cost = message.total_cost_usd
                turns = message.num_turns
                print(f"\n{DIM}  ({turns} turns, ${cost:.4f}){RESET}")

        print(f"\n{DIM}{'─' * 50}{RESET}\n")


if __name__ == "__main__":
    asyncio.run(main())
