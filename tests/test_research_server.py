"""Smoke tests for the demo-04 research server.

These tests don't spin up the HTTP server — they import the in-process tool
callables directly and verify the security-relevant invariants:

  - read_brief blocks path traversal
  - the search retry returns [] instead of raising on persistent failure
  - the fetch helper rejects non-http(s) schemes
"""
from __future__ import annotations

import research_server as rs


def test_read_brief_blocks_traversal():
    out = rs.read_brief("../../../etc/passwd")
    assert out["ok"] is False
    assert out["error"] == "path_outside_briefs"


def test_read_brief_blocks_absolute_path():
    out = rs.read_brief("/etc/passwd")
    assert out["ok"] is False


def test_read_brief_not_found_for_missing_relative():
    out = rs.read_brief("does-not-exist.md")
    # Could be 'not_found' or 'path_outside_briefs' depending on resolution;
    # both are non-ok and that's the security contract.
    assert out["ok"] is False


def test_fetch_page_rejects_non_http(monkeypatch):
    # Even with httpx available, file:// must be rejected before any request.
    assert rs._fetch_page("file:///etc/passwd") == ""
    assert rs._fetch_page("ftp://example.com/x") == ""


def test_search_returns_empty_on_persistent_failure(monkeypatch):
    """When DDGS keeps raising, _search returns [] rather than crashing."""
    class BoomDDGS:
        def text(self, *_a, **_kw):
            raise RuntimeError("ratelimit")

    monkeypatch.setattr(rs, "DDGS", lambda: BoomDDGS())
    monkeypatch.setattr(rs.time, "sleep", lambda _s: None)  # no real backoff
    assert rs._search("anything", max_results=3) == []
