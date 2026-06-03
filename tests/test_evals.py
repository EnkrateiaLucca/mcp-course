"""Tests for the deterministic part of the demo-04 eval harness."""
from __future__ import annotations

from pathlib import Path

import evals


def test_grade_brief_passes_well_formed(tmp_path: Path):
    brief = tmp_path / "mcp-auth.md"
    brief.write_text(
        "# MCP Authentication\n\n"
        "## Findings\n\n"
        "- Authentication in MCP is typically OAuth-based.\n"
        + ("Lorem ipsum dolor sit amet, " * 20)
        + "\n\n## Sources\n\n- https://example.com\n"
    )
    result = evals.grade_brief(brief, "MCP authentication")
    assert result["passed"] is True


def test_grade_brief_fails_missing_file(tmp_path: Path):
    result = evals.grade_brief(tmp_path / "nope.md", "anything")
    assert result["passed"] is False
    assert result["checks"]["file_exists"] is False


def test_grade_brief_fails_missing_sources(tmp_path: Path):
    brief = tmp_path / "x.md"
    brief.write_text("# Topic\n\nlots of words " * 50)
    result = evals.grade_brief(brief, "topic")
    assert result["passed"] is False
    assert result["checks"]["has_sources_section"] is False
