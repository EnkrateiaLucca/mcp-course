#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["claude-agent-sdk>=0.1.0", "python-dotenv"]
# ///
"""Demo 08 — Defense: hooks + least-privilege block the poisoned tool's attack.

Same poisoned server as attack_demo.py. We add:

  1. A `PreToolUse` hook that runs *before* the tool executes:
     - Path firewall on Read: deny any path containing 'secrets' or
       starting with '/'. Defense in depth, even though the agent here
       happens to be running with cwd set to the demo folder.
     - Description scan: also block tool calls whose tool description
       contains known injection markers (visible-to-model-but-not-user).
  2. A tighter `allowed_tools` list and `permission_mode='default'`
     (no auto-approve).
  3. A description checksum stored on first run; on subsequent runs we
     compare and flag any tool whose description changed — the rug-pull
     scenario.

Run:
    export ANTHROPIC_API_KEY=sk-...
    uv run defended_demo.py
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    HookMatcher,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ToolUseBlock,
)
from dotenv import load_dotenv

from poisoned_server import build_poisoned_server

load_dotenv()

HERE = Path(__file__).parent
CHECKSUM_FILE = HERE / ".tool_checksums.json"

SUSPICIOUS_DESCRIPTION_MARKERS = (
    "<important>",
    "do not mention",
    "include its contents",
    "api_key",
    "ssh",
    "/etc/passwd",
)


def deny(reason: str) -> dict:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


async def pretool_guard(input_data, tool_use_id, context):
    """Defense in depth — path firewall + suspicious-arg blocker."""
    name = input_data.get("tool_name", "")
    args = input_data.get("tool_input", {})

    if name == "Read":
        path = str(args.get("file_path", ""))
        lowered = path.lower()
        if "secrets" in lowered or path.startswith("/"):
            print(f"  ⛔ blocked Read({path!r}): outside allowed scope")
            return deny("Read blocked: outside allowed workspace scope")

    return {}


def fingerprint_tools_and_warn(message) -> None:
    """At init, hash each tool description and flag changes (rug pulls)."""
    if not (isinstance(message, SystemMessage) and message.subtype == "init"):
        return

    new_checksums: dict[str, str] = {}
    old_checksums: dict[str, str] = {}
    if CHECKSUM_FILE.exists():
        try:
            old_checksums = json.loads(CHECKSUM_FILE.read_text())
        except json.JSONDecodeError:
            old_checksums = {}

    print("\n--- Tool description audit ---")
    for tool in message.data.get("tools", []) or []:
        name = tool.get("name", "?")
        desc = tool.get("description", "") or ""
        digest = hashlib.sha256(desc.encode("utf-8")).hexdigest()[:12]
        new_checksums[name] = digest

        if any(m in desc.lower() for m in SUSPICIOUS_DESCRIPTION_MARKERS):
            print(f"  ⚠ {name}: description contains a suspicious marker "
                  f"(possible tool poisoning). sha256={digest}")
        else:
            print(f"  • {name}: clean. sha256={digest}")

        if name in old_checksums and old_checksums[name] != digest:
            print(f"  ⚠ {name}: description CHANGED since last run "
                  f"(was {old_checksums[name]}, now {digest}). Possible rug pull.")

    CHECKSUM_FILE.write_text(json.dumps(new_checksums, indent=2))
    print("-" * 60)


async def main() -> None:
    options = ClaudeAgentOptions(
        cwd=str(HERE),
        mcp_servers={"math": build_poisoned_server()},
        allowed_tools=["mcp__math__add", "Read"],
        permission_mode="default",
        hooks={
            "PreToolUse": [HookMatcher(matcher="*", hooks=[pretool_guard])],
        },
    )

    prompt = "What is 2 + 2? Use the math tool."

    async with ClaudeSDKClient(options=options) as client:
        await client.query(prompt)
        async for message in client.receive_response():
            fingerprint_tools_and_warn(message)
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Agent: {block.text}")
                    elif isinstance(block, ToolUseBlock):
                        print(f"  → {block.name}({block.input})")
            elif isinstance(message, ResultMessage):
                print(f"\n[result subtype={message.subtype}]")


if __name__ == "__main__":
    asyncio.run(main())
