#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp[cli]>=1.9.3", "ddgs", "starlette", "uvicorn", "httpx"]
# ///
"""Demo 04 — Production-shaped MCP server for the research assistant.

This is the SAME research-assistant use case from demos 00–02, but redesigned
along the four production patterns from Anthropic's "Building agents that
reach production systems with MCP" article:

    1. **Intent-grouped tools, not API mirrors.**
       In demo 01 we exposed seven low-level tools (web_search, write_file,
       edit_file, move_file, ...). The agent had to orchestrate them across
       4–6 turns to produce one research brief. Here we collapse that into
       ONE composite tool — `research_topic` — that does search + format +
       save in a single call. Two helper tools (`list_briefs`, `read_brief`)
       cover follow-ups. Three tools total, one round-trip per task.

    2. **Remote transport (HTTP), not stdio.**
       Production agents run in the cloud. We use `streamable-http` so this
       server can sit behind a load balancer and be reached by web, mobile,
       or cloud-hosted agents — not just a subprocess on the developer's
       laptop.

    3. **Auth seam, not auth absence.**
       We don't ship OAuth in a teaching demo, but we mark the seam where it
       belongs and require a bearer token from an env var so the wiring is
       real. See `AUTH_TOKEN` and the comment block by `if __name__ ...`.

    4. **Structured returns.**
       Every tool returns a small dict the LLM can parse, plus a human-
       readable summary. No raw blobs of search results dumped into context.

Run:
    export MCP_AUTH_TOKEN=demo-secret
    uv run research_server.py
    # Server listens on http://127.0.0.1:8765/mcp

Inspect:
    mcp dev ./research_server.py
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from ddgs import DDGS
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger("research-server")

# --- Configuration ---------------------------------------------------------

WORKSPACE = (Path(__file__).parent / "workspace").resolve()
WORKSPACE.mkdir(exist_ok=True)
BRIEFS_DIR = WORKSPACE / "briefs"
BRIEFS_DIR.mkdir(exist_ok=True)

# In production this would be OAuth/CIMD. For a live demo a shared bearer
# token keeps the auth wiring visible without 100 lines of OAuth code.
# Fail fast if unset rather than silently defaulting to "demo-secret".
try:
    AUTH_TOKEN = os.environ["MCP_AUTH_TOKEN"]
except KeyError as exc:  # pragma: no cover - startup guard
    raise SystemExit(
        "MCP_AUTH_TOKEN must be set. Example: export MCP_AUTH_TOKEN=demo-secret"
    ) from exc

mcp = FastMCP("research-assistant", host="127.0.0.1", port=8765)


# --- Helpers (private, not exposed as tools) -------------------------------


def _slugify(text: str) -> str:
    keep = "".join(c.lower() if c.isalnum() else "-" for c in text.strip())
    return "-".join(filter(None, keep.split("-")))[:60] or "untitled"


def _search(query: str, max_results: int) -> list[dict]:
    hits = DDGS().text(query, max_results=max_results)
    return [
        {"title": h.get("title"), "url": h.get("href"), "snippet": h.get("body")}
        for h in hits
    ]


def _format_brief(topic: str, hits: list[dict]) -> str:
    """Compose the markdown a researcher would write themselves."""
    when = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [f"# {topic}", "", f"_Researched {when}_", "", "## Findings", ""]
    for h in hits:
        snippet = (h["snippet"] or "").replace("\n", " ").strip()
        lines.append(f"- **{h['title']}** — {snippet}")
    lines += ["", "## Sources", ""]
    for h in hits:
        lines.append(f"- [{h['title']}]({h['url']})")
    return "\n".join(lines) + "\n"


# --- Tools (intent-grouped) ------------------------------------------------


@mcp.tool()
def research_topic(topic: str, max_sources: int = 5) -> dict:
    """Search the web for ``topic`` and save a markdown brief.

    This is an *intent-grouped* tool: it does the whole job (search → format
    → persist) in one call instead of forcing the agent to orchestrate
    `web_search` + `write_file` across multiple turns.

    Returns a structured dict so the agent can decide next steps without
    re-parsing prose.
    """
    logger.info("research_topic: %s (max_sources=%d)", topic, max_sources)
    hits = _search(topic, max_results=max_sources)
    if not hits:
        return {"ok": False, "error": "no_results", "topic": topic}

    brief = _format_brief(topic, hits)
    filename = f"{_slugify(topic)}.md"
    (BRIEFS_DIR / filename).write_text(brief)

    return {
        "ok": True,
        "topic": topic,
        "brief_path": f"briefs/{filename}",
        "source_count": len(hits),
        "summary": f"Saved brief with {len(hits)} sources to briefs/{filename}",
    }


@mcp.tool()
def list_briefs() -> dict:
    """List previously saved briefs (filename + modified time)."""
    entries = []
    for p in sorted(BRIEFS_DIR.glob("*.md")):
        entries.append({
            "path": f"briefs/{p.name}",
            "modified": datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat(),
            "size_bytes": p.stat().st_size,
        })
    return {"ok": True, "count": len(entries), "briefs": entries}


@mcp.tool()
def read_brief(brief_path: str) -> dict:
    """Read a saved brief by path (must live under briefs/)."""
    p = (WORKSPACE / brief_path).resolve()
    if BRIEFS_DIR not in p.parents:
        return {"ok": False, "error": "path_outside_briefs"}
    if not p.exists():
        return {"ok": False, "error": "not_found", "path": brief_path}
    return {"ok": True, "path": brief_path, "content": p.read_text()}


@mcp.resource("research://briefs")
def briefs_index() -> str:
    """A live index of all saved briefs — useful for the agent at startup."""
    return json.dumps(list_briefs(), indent=2)


# --- Entry point -----------------------------------------------------------

# --- Auth middleware -------------------------------------------------------
#
# FastMCP's streamable-http transport does not bundle OAuth. In production you
# would put this server behind an API gateway that validates OAuth/CIMD tokens
# (see MCP spec auth section). For the course we validate a static bearer
# token at the ASGI layer — the *seam* where real auth would slot in.
#
# Per the official MCP authentication docs:
#   "The SDK doesn't handle OAuth flows automatically, but you can pass access
#    tokens via headers after completing the OAuth flow in your application."
# So the client attaches `Authorization: Bearer ...` (research_agent.py does),
# and the server validates it (this middleware does). Two halves, one seam.

from starlette.middleware.base import BaseHTTPMiddleware  # noqa: E402
from starlette.requests import Request  # noqa: E402
from starlette.responses import JSONResponse  # noqa: E402


class BearerAuthMiddleware(BaseHTTPMiddleware):
    """Reject any request whose Authorization header doesn't match AUTH_TOKEN."""

    async def dispatch(self, request: Request, call_next):
        header = request.headers.get("authorization", "")
        expected = f"Bearer {AUTH_TOKEN}"
        if header != expected:
            logger.warning("rejected request: bad/missing Authorization header")
            return JSONResponse(
                {"error": "unauthorized", "detail": "missing or invalid bearer token"},
                status_code=401,
            )
        return await call_next(request)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logger.info("🚀 research-assistant MCP server on http://127.0.0.1:8765/mcp")
    logger.info("    auth: Bearer %s  (override with MCP_AUTH_TOKEN)", AUTH_TOKEN)

    # FastMCP exposes the underlying Starlette ASGI app via streamable_http_app().
    # We wrap it with auth middleware before handing it to uvicorn.
    import uvicorn

    app = mcp.streamable_http_app()
    app.add_middleware(BearerAuthMiddleware)
    uvicorn.run(app, host="127.0.0.1", port=8765)
