#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp[cli]>=2.3,<3"]
# ///
"""What can the agent see? Call the module 04 MCP server's tools directly, the way the agent does.

No model and no API spend: this is a plain MCP client. Run it twice:

    # terminal 1, in demos/04-shop-analytics-agent
    docker compose up --build                  # PII_GUARD off (the default)
    # terminal 2
    uv run exposure_check.py                   # -> LEAK

    # restart only the MCP server with the guard on
    PII_GUARD=1 docker compose up -d mcp
    uv run exposure_check.py                   # -> BLOCKED, metrics still work

Usage: uv run exposure_check.py [url]   (default http://127.0.0.1:8001/mcp, token from MCP_TOKEN)
"""

import asyncio
import json
import os
import sys

import httpx2
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8001/mcp"
TOKEN = os.environ.get("MCP_TOKEN", "local-dev-token")  # compose's local default

PROBES = [
    ("A governed metric tool", "kpi_summary", {"start_date": "2025-11-01", "end_date": "2025-11-30"}),
    ("run_sql, asked for personal data", "run_sql", {"sql": "SELECT name, email, country FROM customers LIMIT 3"}),
    ("run_sql, the lazy way: SELECT *", "run_sql", {"sql": "SELECT * FROM customers LIMIT 3"}),
]


def text_of(result) -> str:
    return "".join(getattr(block, "text", "") for block in result.content)


async def main() -> None:
    print(f"MCP server: {URL}\n")
    async with httpx2.AsyncClient(headers={"Authorization": f"Bearer {TOKEN}"}) as http:
        async with streamable_http_client(URL, http_client=http) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                for label, tool, args in PROBES:
                    result = await session.call_tool(tool, args)
                    body = text_of(result)
                    if result.is_error:
                        verdict = "BLOCKED"
                    elif "@example.com" in body:
                        verdict = "LEAK   "
                    else:
                        verdict = "OK     "
                    print(f"[{verdict}] {label}: {tool}({json.dumps(args)})")
                    print(f"          {body[:220]}{'…' if len(body) > 220 else ''}\n")


if __name__ == "__main__":
    asyncio.run(main())
