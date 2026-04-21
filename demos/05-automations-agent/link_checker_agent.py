# /// script
# requires-python = ">=3.12"
# dependencies = ["claude-agent-sdk>=0.1.21"]
# ///

"""
Link Health Checker Agent — Claude Agent SDK + MCP

An interactive agent that discovers markdown files, extracts hyperlinks,
checks each URL for broken/working status, and writes a structured audit report.

Usage: uv run link_checker_agent.py
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

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEMOS_DIR = os.path.dirname(SCRIPT_DIR)
PRESENTATION_DIR = os.path.join(os.path.dirname(DEMOS_DIR), "presentation")
REPORTS_DIR = os.path.join(SCRIPT_DIR, "reports")

# ANSI color helpers
DIM = "\033[2m"
BOLD = "\033[1m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
RED = "\033[31m"
RESET = "\033[0m"

TOOL_LABELS = {
    "list_markdown_files": ("Scanning for markdown", CYAN),
    "extract_links":       ("Extracting links",      CYAN),
    "check_url":           ("Checking URL",           YELLOW),
    "write_report":        ("Writing report",         GREEN),
}


def format_tool_call(block):
    short_name = block.name.split("__")[-1] if "__" in block.name else block.name
    label, color = TOOL_LABELS.get(short_name, (short_name, DIM))

    detail = ""
    if isinstance(block.input, dict):
        if "filepath" in block.input:
            detail = f" [{os.path.basename(block.input['filepath'])}]"
        elif "url" in block.input:
            u = block.input["url"]
            detail = f" [{u[:60]}{'...' if len(u) > 60 else ''}]"
        elif "filename" in block.input:
            detail = f" [{block.input['filename']}]"
        elif "directory" in block.input:
            detail = f" [{block.input['directory']}]"

    return f"{color}  [{label}{detail}]{RESET}"


def format_tool_result(block):
    content = block.content if isinstance(block.content, str) else str(block.content)

    if not content or not content.strip():
        return None

    lines = content.strip().splitlines()
    if len(lines) > 15:
        lines = lines[:12] + [f"{DIM}  ... ({len(lines) - 12} more lines){RESET}"]

    formatted = "\n".join(f"  {DIM}| {line}{RESET}" for line in lines)

    if block.is_error:
        return f"  {RED}Error:{RESET}\n{formatted}"
    return formatted


options = ClaudeAgentOptions(
    model="claude-sonnet-4-6",
    system_prompt=f"""You are a link health checker assistant. You help developers find broken links
in their markdown documentation by checking each URL and producing an audit report.

The course directories to scan are:
- Demos:        {DEMOS_DIR}
- Presentation: {PRESENTATION_DIR}

When the user asks to audit the course or check all links, scan both directories above.

Your workflow:
1. list_markdown_files — discover all .md files in the given directory (call once per directory)
2. extract_links — get all URLs from each file
3. check_url — check each unique URL (deduplicate before checking)
4. write_report — always write a structured report at the end

Your report should include:
- Total files scanned and links checked
- Broken links (4xx, 5xx, connection errors) with the file they came from
- Redirects worth noting (3xx)
- Working links count
- Recommendation if many links are broken

Name report files descriptively, e.g.: link_audit_2026-04-20.txt
You MUST always write a report file — do not just describe findings in chat.
Deduplicate URLs before checking — the same URL may appear in multiple files.
""",
    mcp_servers={
        "links": {
            "type": "stdio",
            "command": "uv",
            "args": [
                "run",
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "link_checker_mcp_server.py",
                ),
            ],
        }
    },
    allowed_tools=["mcp__links__*"],
    permission_mode="bypassPermissions",
)


async def main():
    print(f"{BOLD}┌────────────────────────────────────────────────┐{RESET}")
    print(f"{BOLD}│   Link Health Checker — Audit Markdown Links   │{RESET}")
    print(f"{BOLD}│   Powered by Claude Agent SDK + MCP            │{RESET}")
    print(f"{BOLD}└────────────────────────────────────────────────┘{RESET}")
    print()
    print(f"  {DIM}Scanning: {DEMOS_DIR}{RESET}")
    print(f"  {DIM}          {PRESENTATION_DIR}{RESET}")
    print(f"  {DIM}Reports:  {REPORTS_DIR}{RESET}")
    print()
    print("  Try:")
    print(f'    {CYAN}"Audit all course links"{RESET}')
    print(f'    {CYAN}"Check only the demos folder"{RESET}')
    print(f'    {CYAN}"Find broken links in the presentation"{RESET}')
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
