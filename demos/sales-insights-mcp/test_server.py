#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp[cli]>=2.3,<3"]
# ///
"""Smoke test: `uv run test_server.py`. Run after ANY server change."""

import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import server

# Known numbers from the Voltaic Gear CSV.
yoy = server.compare_periods()
assert yoy["current_period"] == ["2026-01-01", "2026-06-30"], yoy
assert yoy["baseline_period"] == ["2025-01-01", "2025-06-30"], yoy
assert yoy["total"]["change_pct"] == 59.4, yoy["total"]

by_region = server.compare_periods(group_by="region")
assert by_region["groups"][0]["region"] == "Europe"  # biggest absolute gain
assert round(sum(g["share_of_change_pct"] for g in by_region["groups"])) == 100

channels = server.breakdown("channel")
assert channels[0]["channel"] == "Distributor" and channels[0]["share_pct"] == 68.8, channels
assert [m["month"] for m in server.breakdown("month", start_date="2025-10-01", end_date="2025-12-31")] == \
    ["2025-10", "2025-11", "2025-12"]
assert server.dataset_guide()["rep_regions"]["Maya Chen"] == "North America"

for bad, expect in ((dict(start_date="2024-06-01", end_date="2024-12-31"), "before the data"),
                    (dict(end_date="2026-07-31"), "Data ends"),
                    (dict(start_date="06/01/2026"), "ISO date")):
    try:
        server.compare_periods(**bad)
        raise AssertionError(f"accepted {bad}")
    except server.ToolError as e:
        assert expect in str(e), e

for sql in ("DELETE FROM orders", "PRAGMA writable_schema=ON", "ATTACH 'x.db' AS x", "DROP TABLE orders"):
    try:
        server.run_sql(sql)
        raise AssertionError(f"write allowed: {sql}")
    except server.ToolError as e:
        assert "not authorized" in str(e), e
assert len(server.run_sql("SELECT * FROM orders")) == server.MAX_ROWS


async def protocol_check():
    params = StdioServerParameters(command=sys.executable, args=[str(Path(server.__file__))])
    async with stdio_client(params) as (read, write), ClientSession(read, write) as s:
        await s.initialize()
        tools = {t.name: t for t in (await s.list_tools()).tools}
        assert set(tools) == {"dataset_guide", "breakdown", "compare_periods", "run_sql"}, tools
        # Valid values reach the model as an enum in the input schema.
        assert "Europe" in json.dumps(tools["breakdown"].input_schema["properties"]["region"])
        r = await s.call_tool("breakdown", {"group_by": "region", "region": "Atlantis"})
        assert r.is_error, r


asyncio.run(protocol_check())
print("ok")
