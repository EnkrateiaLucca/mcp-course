#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp[cli]>=1.12,<2"]
# ///
"""Pre-flight protocol check for csv-sales-explorer. Run with the server up.

Checks, over streamable HTTP:
  1. tools/list      — all three tools present; sales_dashboard carries
                        _meta.ui.resourceUri (the MCP Apps link)
  2. resources/read  — the ui:// resource returns HTML with the mcp-app
                        mimeType and the ui/initialize handshake
  3. tools/call      — sales_dashboard returns KPIs + series; query_sales
                        aggregates and rejects a bad group_by with a
                        valid_values hint

Usage:
    uv run test_client.py                       # local (port 8010)
    uv run test_client.py https://<host>/mcp    # tunneled / deployed
"""

from __future__ import annotations

import asyncio
import json
import sys

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from pydantic import AnyUrl

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8010/mcp"


def payload(result) -> dict:
    data = result.structuredContent or json.loads(result.content[0].text)
    return data.get("result", data) if isinstance(data, dict) else data


async def main() -> None:
    print(f"→ connecting to {URL}")
    async with streamable_http_client(URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1. tools + MCP Apps metadata
            tools = (await session.list_tools()).tools
            names = {t.name for t in tools}
            assert {"sales_dashboard", "query_sales", "get_dataset_info"} <= names, names
            print(f"✅ tools/list: {sorted(names)}")
            dash = next(t for t in tools if t.name == "sales_dashboard")
            ui_uri = ((dash.meta or {}).get("ui") or {}).get("resourceUri")
            assert ui_uri, f"sales_dashboard has no _meta.ui.resourceUri! meta={dash.meta}"
            print(f"✅ MCP Apps link: {ui_uri}")

            # 2. the ui:// resource
            res = await session.read_resource(AnyUrl(ui_uri))
            content = res.contents[0]
            assert "text/html" in (content.mimeType or ""), content.mimeType
            assert "ui/initialize" in content.text, "app HTML missing the handshake"
            print(f"✅ ui resource: {content.mimeType}, {len(content.text)} chars of HTML")

            # 3a. the dashboard tool
            result = await session.call_tool(
                "sales_dashboard",
                {"start_date": "2025-10-01", "end_date": "2025-12-31"},
            )
            data = payload(result)
            assert data["ok"], data
            k = data["kpis"]
            assert k["order_count"] > 0 and len(data["monthly"]) == 3, data["filters"]
            print(f"✅ sales_dashboard (Q4 2025): ${k['total_revenue']:,.0f} revenue, "
                  f"{k['order_count']} orders, {len(data['monthly'])} months")

            # 3b. ad-hoc aggregation
            result = await session.call_tool(
                "query_sales", {"group_by": "sales_rep", "region": "Europe", "top": 3}
            )
            data = payload(result)
            assert data["ok"] and data["groups"], data
            top = data["groups"][0]
            print(f"✅ query_sales: top Europe rep = {top['sales_rep']} "
                  f"(${top['revenue']:,.0f})")

            # 3c. actionable errors
            result = await session.call_tool("query_sales", {"group_by": "planet"})
            data = payload(result)
            assert not data["ok"] and "valid_values" in data, data
            print(f"✅ error shape: {data['error']} → hints {data['valid_values'][:3]}…")

    print("\nProtocol checks passed. Safe to connect a host to this server. 🎉")


if __name__ == "__main__":
    asyncio.run(main())
