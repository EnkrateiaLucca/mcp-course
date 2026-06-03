"""Verify the demo-04 PreToolUse hook blocks bad inputs without an LLM call."""
from __future__ import annotations

import asyncio

import research_agent as ra


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro) if False else asyncio.run(coro)


def test_pre_tool_blocks_short_topic():
    result = _run(ra.pre_tool_validate(
        {"tool_name": "mcp__research__research_topic", "tool_input": {"topic": "a"}},
        None, None,
    ))
    decision = result["hookSpecificOutput"]["permissionDecision"]
    assert decision == "deny"


def test_pre_tool_blocks_path_traversal_in_read_brief():
    result = _run(ra.pre_tool_validate(
        {"tool_name": "mcp__research__read_brief",
         "tool_input": {"brief_path": "../../secrets.txt"}},
        None, None,
    ))
    decision = result["hookSpecificOutput"]["permissionDecision"]
    assert decision == "deny"


def test_pre_tool_blocks_absolute_path_in_read_brief():
    result = _run(ra.pre_tool_validate(
        {"tool_name": "mcp__research__read_brief",
         "tool_input": {"brief_path": "/etc/passwd"}},
        None, None,
    ))
    decision = result["hookSpecificOutput"]["permissionDecision"]
    assert decision == "deny"


def test_pre_tool_allows_valid_topic():
    result = _run(ra.pre_tool_validate(
        {"tool_name": "mcp__research__research_topic",
         "tool_input": {"topic": "Model Context Protocol authentication"}},
        None, None,
    ))
    assert result == {}
