#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp[cli]>=1.12,<2", "ddgs"]
# ///
"""Demo 05 — A remote, deployable MCP server (+ an MCP App).

This is the deployment story for 2026: you don't wrap your agent in a web
framework — you deploy the **MCP server itself** and let every host connect
to it (Claude, Claude Code, Cursor, ChatGPT...). One server, many hosts.

Two things make this server deployment-ready:

    1. **stateless_http=True** — no session state between requests, so the
       server works behind load balancers and on serverless platforms
       (this is also the direction of the 2026-07-28 spec revision, which
       makes the *protocol core* stateless).
    2. **json_response=True** — plain JSON responses instead of SSE
       streams, which serverless platforms are happier with.

It also ships an **MCP App** (the first official MCP extension, Jan 2026):
the `research_explorer` tool declares a `ui://` resource in its `_meta`,
and hosts that support MCP Apps (Claude web/desktop, Goose, VS Code)
render the returned HTML in a sandboxed iframe *inside the chat*.

Run locally:
    uv run server.py                  # http://127.0.0.1:8000/mcp

Expose to the internet for testing with Claude (custom connector):
    npx cloudflared tunnel --url http://localhost:8000

Deploy to Vercel:  see README.md (api/index.py wraps this same app).

Auth note: Claude's "custom connector" UI supports either OAuth or no
auth — you can't type a bearer header there. So this demo server is open
by default; set MCP_AUTH_TOKEN to require a bearer token when calling it
from clients that DO let you set headers (Claude Agent SDK, Claude Code).
Demo 04 shows the full auth seam.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from ddgs import DDGS
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

mcp = FastMCP(
    "research-explorer",
    stateless_http=True,   # serverless/load-balancer friendly
    json_response=True,    # no SSE stream; plain JSON responses
    host="127.0.0.1",
    port=8000,
    # FastMCP auto-enables DNS-rebinding protection when host is localhost,
    # which rejects any non-localhost Host header with 421 — including the
    # cloudflared tunnel and Vercel hostnames this server exists to serve.
    # This server is meant to be reached through a public hostname, so turn
    # the localhost-only Host check off.
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)

# ---------------------------------------------------------------------------
# MCP App wiring — a tool + a ui:// resource, linked through _meta.
#
# Wire format (MCP Apps extension, 2026-01-26):
#   - the TOOL carries _meta = {"ui": {"resourceUri": "ui://..."}}
#   - the RESOURCE lives at that ui:// URI with mimeType
#     "text/html;profile=mcp-app" and returns a self-contained HTML page
#   - the host renders the page in a sandboxed iframe and pushes the tool
#     result to it over postMessage (see app.html for the handshake)
# ---------------------------------------------------------------------------

APP_RESOURCE_URI = "ui://research-explorer/app.html"
APP_HTML_PATH = Path(__file__).parent / "app.html"


def _search(query: str, max_results: int = 6) -> list[dict]:
    try:
        hits = DDGS().text(query, max_results=max_results)
        return [
            {
                "title": h.get("title") or "(untitled)",
                "url": h.get("href") or "",
                "snippet": h.get("body") or "",
            }
            for h in hits
        ]
    except Exception:  # noqa: BLE001 — ddgs raises ad-hoc types; degrade gracefully
        return []


@mcp.tool(meta={"ui": {"resourceUri": APP_RESOURCE_URI}})
def research_explorer(topic: str, max_sources: int = 6) -> dict:
    """Search the web for a topic and open an interactive source explorer.

    Returns structured results; in hosts that support MCP Apps this renders
    as an interactive card grid the user can click through and re-search.
    """
    hits = _search(topic, max_results=max_sources)
    return {
        "ok": bool(hits),
        "topic": topic,
        "count": len(hits),
        "sources": hits,
    }


@mcp.tool()
def quick_search(query: str, max_results: int = 5) -> dict:
    """Plain web search returning {title, url, snippet} items (no UI)."""
    hits = _search(query, max_results=max_results)
    return {"ok": bool(hits), "query": query, "results": hits}


@mcp.resource(APP_RESOURCE_URI, mime_type="text/html;profile=mcp-app")
def research_explorer_app() -> str:
    """The MCP App page for research_explorer (self-contained HTML)."""
    return APP_HTML_PATH.read_text()


# ---------------------------------------------------------------------------
# Optional bearer auth (off by default — see module docstring).
# ---------------------------------------------------------------------------


def build_app():
    """Build the ASGI app (used by uvicorn locally AND by Vercel)."""
    app = mcp.streamable_http_app()

    token = os.environ.get("MCP_AUTH_TOKEN")
    if token:
        from starlette.middleware.base import BaseHTTPMiddleware
        from starlette.responses import JSONResponse

        class BearerAuth(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                if request.headers.get("authorization") != f"Bearer {token}":
                    return JSONResponse({"error": "unauthorized"}, status_code=401)
                return await call_next(request)

        app.add_middleware(BearerAuth)
    return app


app = build_app()

if __name__ == "__main__":
    import uvicorn

    print("🚀 research-explorer MCP server on http://127.0.0.1:8000/mcp")
    print("   stateless_http=True json_response=True — deployable anywhere")
    if os.environ.get("MCP_AUTH_TOKEN"):
        print("   auth: bearer token REQUIRED (MCP_AUTH_TOKEN is set)")
    else:
        print("   auth: OPEN (set MCP_AUTH_TOKEN to require a bearer token)")
    uvicorn.run(app, host="127.0.0.1", port=8000)
