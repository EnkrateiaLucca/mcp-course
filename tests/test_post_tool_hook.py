"""Verify the demo-04 PostToolUse hook reads the tool's dict out of MCP content blocks."""
from __future__ import annotations

import asyncio
import json
import logging

import research_agent as ra


def _log_line(caplog, response) -> str:
    caplog.set_level(logging.INFO, logger="research-agent")
    asyncio.run(ra.post_tool_log(
        {"tool_name": "mcp__research__research_topic", "tool_response": response},
        None, None,
    ))
    return caplog.records[-1].getMessage()


def test_post_tool_reads_ok_from_content_blocks(caplog):
    blocks = [{"type": "text", "text": json.dumps({"ok": True, "topic": "x"})}]
    assert _log_line(caplog, blocks).endswith("-> ok")


def test_post_tool_reports_structured_error(caplog):
    blocks = [{"type": "text", "text": json.dumps({"ok": False, "error": "search_unavailable"})}]
    assert "error: " in _log_line(caplog, blocks)


def test_post_tool_tolerates_non_json_text(caplog):
    assert _log_line(caplog, [{"type": "text", "text": "plain prose"}]).endswith("-> ok")
