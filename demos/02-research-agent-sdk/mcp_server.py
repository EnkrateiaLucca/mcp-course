#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp[cli]>=1.9.3", "ddgs"]
# ///
"""Research-assistant MCP server.

Exposes the same tools we hand-rolled in demo 00 — web search + sandboxed
filesystem ops — so that *any* MCP host (Claude Desktop, our own host in
mcp_host.py, the Claude Agent SDK, etc.) can consume them.

Run standalone (for use as a stdio MCP server):
    uv run ./mcp_server.py

Inspect interactively:
    mcp dev ./mcp_server.py
"""

import json
import logging
from pathlib import Path

from ddgs import DDGS
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("research-assistant")

WORKSPACE = (Path(__file__).parent / "workspace").resolve()
WORKSPACE.mkdir(exist_ok=True)


def _safe(path: str) -> Path:
    """Resolve a relative path inside WORKSPACE, blocking traversal."""
    p = (WORKSPACE / path).resolve()
    if WORKSPACE not in p.parents and p != WORKSPACE:
        raise ValueError(f"Path escapes workspace: {path}")
    return p


@mcp.tool()
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web with DuckDuckGo. Returns JSON list of {title, url, snippet}."""
    hits = DDGS().text(query, max_results=max_results)
    return json.dumps(
        [{"title": h.get("title"), "url": h.get("href"), "snippet": h.get("body")} for h in hits],
        indent=2,
    )


@mcp.tool()
def read_file(path: str) -> str:
    """Read a text file from the workspace."""
    return _safe(path).read_text()


@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Create or overwrite a file in the workspace."""
    p = _safe(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return f"Wrote {len(content)} chars to {path}"


@mcp.tool()
def edit_file(path: str, old: str, new: str) -> str:
    """Replace an exact substring in an existing file."""
    p = _safe(path)
    text = p.read_text()
    if old not in text:
        return f"Error: substring not found in {path}"
    p.write_text(text.replace(old, new))
    return f"Edited {path}"


@mcp.tool()
def move_file(src: str, dst: str) -> str:
    """Move or rename a file inside the workspace."""
    s, d = _safe(src), _safe(dst)
    d.parent.mkdir(parents=True, exist_ok=True)
    s.rename(d)
    return f"Moved {src} -> {dst}"


@mcp.tool()
def delete_file(path: str) -> str:
    """Delete a file from the workspace."""
    _safe(path).unlink()
    return f"Deleted {path}"


@mcp.tool()
def list_files(directory: str = ".") -> str:
    """List files under a directory in the workspace."""
    base = _safe(directory)
    entries = sorted(str(p.relative_to(WORKSPACE)) for p in base.rglob("*"))
    return "\n".join(entries) or "(empty)"


@mcp.resource("workspace://files")
def workspace_index() -> str:
    """A live listing of everything currently in the workspace."""
    entries = sorted(str(p.relative_to(WORKSPACE)) for p in WORKSPACE.rglob("*"))
    return "\n".join(entries) or "(empty)"


if __name__ == "__main__":
    logging.info("🚀 research-assistant MCP server (stdio)")
    mcp.run(transport="stdio")
