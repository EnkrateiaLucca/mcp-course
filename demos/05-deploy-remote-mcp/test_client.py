#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp[cli]>=2.3,<3"]
# ///
"""Pre-flight check for the deployed server — run BEFORE class, and again
after deploying to Vercel, to confirm everything a host needs is in place.

Checks, over plain streamable HTTP:
  1. tools/list        — both tools present, research_explorer carries
                          _meta.ui.resourceUri (the MCP Apps link)
  2. resources/read    — the ui:// resource returns HTML with the right
                          mimeType ("text/html;profile=mcp-app")
  3. tools/call        — research_explorer returns structured sources

Usage:
    uv run test_client.py                              # local server
    uv run test_client.py https://<app>.vercel.app/mcp # deployed
"""

from __future__ import annotations

import asyncio
import json
import sys

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000/mcp"

async def main() -> None:
    print(f"→ connecting to {URL}")
    async with streamable_http_client(URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1. tools + MCP Apps metadata
            tools = (await session.list_tools()).tools
            names = {t.name for t in tools}
            print(f"✅ tools/list: {sorted(names)}")
            explorer = next(t for t in tools if t.name == "research_explorer")
            meta = explorer.meta or {}
            ui_uri = (meta.get("ui") or {}).get("resourceUri")
            assert ui_uri, f"research_explorer has no _meta.ui.resourceUri! meta={meta}"
            print(f"✅ MCP Apps link: {ui_uri}")

            # 2. the ui:// resource
            res = await session.read_resource(ui_uri)
            content = res.contents[0]
            assert "text/html" in (content.mime_type or ""), content.mime_type
            assert "ui/initialize" in content.text, "app HTML missing the handshake"
            print(f"✅ ui resource: {content.mime_type}, {len(content.text)} chars of HTML")

            # 3. call the tool
            result = await session.call_tool(
                "research_explorer", {"topic": "model context protocol", "max_sources": 3}
            )
            payload = result.structured_content or json.loads(result.content[0].text)
            if payload.get("ok"):
                print(f"✅ tools/call: ok=True count={payload.get('count')}")
                for s in (payload.get("sources") or [])[:3]:
                    print(f"   • {s['title'][:60]} — {s['url'][:60]}")
            else:
                print("⚠️  tools/call: protocol OK but search returned nothing "
                      "(DDGS throttled/blocked?). Retry before going live.")

    print("\nProtocol checks passed. Safe to connect a host to this server. 🎉")


if __name__ == "__main__":
    asyncio.run(main())
