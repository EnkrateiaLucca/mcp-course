#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["claude-agent-sdk", "python-dotenv"]
# ///
"""Demo 03 — Production-shaped research agent on the Claude Agent SDK.

The agent from demo 02 wearing a production jacket: same use case, same SDK,
but now talking to a **remote HTTP MCP server** with the four production
hardening pieces wired in:

    • Auth     — bearer token sent on every MCP request.
    • Permissions — explicit allow-list + a `can_use_tool` callback.
    • Hooks    — PreToolUse validates inputs, PostToolUse logs outcomes.
    • Evals    — an ExecutionTracker captures tool calls, duration, cost.

Start the server first (in another terminal):
    export MCP_AUTH_TOKEN=demo-secret
    uv run research_server.py

Then run the agent:
    export ANTHROPIC_API_KEY=sk-...
    export MCP_AUTH_TOKEN=demo-secret
    uv run research_agent.py "Research how MCP authentication works"
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    HookContext,
    HookMatcher,
    PermissionResultAllow,
    PermissionResultDeny,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ToolPermissionContext,
    ToolUseBlock,
)
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("research-agent")


SERVER_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8765/mcp")
AUTH_TOKEN = os.getenv("MCP_AUTH_TOKEN", "demo-secret")

SYSTEM_PROMPT = (
    "You are a production research assistant. You have three MCP tools under "
    "the `mcp__research__` namespace: `research_topic`, `list_briefs`, "
    "`read_brief`. Prefer ONE call to `research_topic` over orchestrating "
    "primitives — the server already handles search, formatting, and saving. "
    "Be concise. Cite the brief path you produced."
)

# Allow-list: ONLY our three intent-grouped MCP tools. Anything else (Bash,
# Read, WebFetch, ...) the SDK might offer is rejected by the permission
# callback below. Defense in depth — the allow-list AND the callback.
ALLOWED_TOOLS = {
    "mcp__research__research_topic",
    "mcp__research__list_briefs",
    "mcp__research__read_brief",
}


# --- Hooks -----------------------------------------------------------------


async def pre_tool_validate(input_data: dict, tool_use_id: str | None, context: HookContext) -> dict:
    """PreToolUse: cheap input validation before the tool runs.

    Catches obviously-bad inputs (empty topic, suspicious paths) BEFORE we
    spend a network round-trip or hit the LLM context with an error result.
    """
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    if tool_name == "mcp__research__research_topic":
        topic = (tool_input.get("topic") or "").strip()
        if len(topic) < 3:
            log.warning("blocked: empty/too-short topic")
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": "Topic must be at least 3 chars",
                },
            }

    if tool_name == "mcp__research__read_brief":
        path = tool_input.get("brief_path", "")
        if ".." in path or path.startswith("/"):
            log.warning("blocked: suspicious brief_path %r", path)
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": "Path must be relative, under briefs/",
                },
            }
    return {}


async def post_tool_log(input_data: dict, tool_use_id: str | None, context: HookContext) -> dict:
    """PostToolUse: observability. One log line per tool call."""
    name = input_data.get("tool_name", "?")
    response = input_data.get("tool_response", {})
    ok = isinstance(response, dict) and response.get("ok", True)
    log.info("tool %s -> %s", name, "ok" if ok else f"error: {response!r}"[:200])
    return {}


# --- Permission callback ---------------------------------------------------


async def can_use_tool(
    tool_name: str, input_data: dict, context: ToolPermissionContext
) -> PermissionResultAllow | PermissionResultDeny:
    if tool_name not in ALLOWED_TOOLS:
        return PermissionResultDeny(message=f"Tool {tool_name} not in allow-list")
    return PermissionResultAllow()


# --- Eval / tracking -------------------------------------------------------


@dataclass
class ExecutionTracker:
    """Minimal eval signal: was the task done, with what tools, at what cost."""

    started: datetime = field(default_factory=datetime.now)
    ended: datetime | None = None
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    cost_usd: float = 0.0
    status: str = "running"

    def on_message(self, message: Any) -> None:
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    self.tool_calls.append({"name": block.name, "input": block.input})
        elif isinstance(message, ResultMessage):
            self.ended = datetime.now()
            self.cost_usd = message.total_cost_usd or 0.0
            self.status = message.subtype

    def print_summary(self) -> None:
        dur = (self.ended - self.started).total_seconds() if self.ended else 0.0
        counts: dict[str, int] = {}
        for c in self.tool_calls:
            counts[c["name"]] = counts.get(c["name"], 0) + 1
        print("\n" + "─" * 60)
        print(f"status: {self.status}   duration: {dur:.2f}s   cost: ${self.cost_usd:.4f}")
        for name, n in counts.items():
            print(f"  {name}: {n}")
        print("─" * 60)


# --- Options builder -------------------------------------------------------


def build_options() -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        model="claude-sonnet-4-6",
        system_prompt=SYSTEM_PROMPT,
        mcp_servers={
            "research": {
                "type": "http",
                "url": SERVER_URL,
                "headers": {"Authorization": f"Bearer {AUTH_TOKEN}"},
            }
        },
        allowed_tools=sorted(ALLOWED_TOOLS),
        can_use_tool=can_use_tool,
        hooks={
            "PreToolUse": [HookMatcher(matcher="mcp__research__*", hooks=[pre_tool_validate])],
            "PostToolUse": [HookMatcher(matcher="mcp__research__*", hooks=[post_tool_log])],
        },
    )


# --- Run -------------------------------------------------------------------


async def run(user_prompt: str) -> ExecutionTracker:
    tracker = ExecutionTracker()
    print(f"\nUser: {user_prompt}\n")

    async with ClaudeSDKClient(options=build_options()) as client:
        await client.query(user_prompt)
        async for message in client.receive_response():
            tracker.on_message(message)
            if isinstance(message, SystemMessage) and message.subtype == "init":
                tools = message.data.get("tools", [])
                log.info("session init — %d tools available", len(tools))
            elif isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)
                    elif isinstance(block, ToolUseBlock):
                        print(f"  → {block.name}({block.input})")

    tracker.print_summary()
    return tracker


if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]) or "Research what the Model Context Protocol is."
    asyncio.run(run(prompt))
