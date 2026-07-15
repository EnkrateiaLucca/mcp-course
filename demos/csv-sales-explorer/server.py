#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp[cli]>=1.12,<2"]
# ///
"""CSV Sales Explorer — an MCP server with an MCP App dashboard.

Loads data/sales_data.csv (mock Voltaic Gear sales, 18 months) and exposes:

    sales_dashboard   -> aggregated slice + an MCP App (interactive charts
                         rendered INSIDE the chat in hosts that support the
                         MCP Apps extension: Claude web/desktop, Goose, ...)
    query_sales       -> generic group-by aggregation for ad-hoc questions
    get_dataset_info  -> schema, dimensions, date range

MCP App wiring (extension rev 2026-01-26), same pattern as demo 05:
    - the TOOL carries _meta = {"ui": {"resourceUri": "ui://..."}}
    - the RESOURCE at that URI returns self-contained HTML with mimeType
      "text/html;profile=mcp-app" (see app.html for the postMessage handshake)

Run:
    uv run server.py          # streamable HTTP on http://127.0.0.1:8010/mcp
    uv run server.py stdio    # stdio (Claude Desktop / claude mcp add)

Expose to claude.ai as a custom connector:
    npx cloudflared tunnel --url http://localhost:8010
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations

mcp = FastMCP(
    "csv-sales-explorer",
    stateless_http=True,
    json_response=True,
    host="127.0.0.1",
    port=8010,
    # allow non-localhost Host headers (cloudflared tunnel / Vercel) — see
    # demo 05 for why this is required behind a public hostname
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)

# ---------------------------------------------------------------------------
# Data loading — one pass at import time; the CSV is the source of truth.
# ---------------------------------------------------------------------------

CSV_PATH = Path(__file__).parent / "data" / "sales_data.csv"
APP_RESOURCE_URI = "ui://csv-sales-explorer/app.html"
APP_HTML_PATH = Path(__file__).parent / "app.html"

GROUPABLE = ("product", "category", "region", "channel", "sales_rep", "month")
FILTERABLE = ("product", "category", "region", "channel", "sales_rep")


def _load() -> list[dict]:
    rows = []
    with CSV_PATH.open() as f:
        for r in csv.DictReader(f):
            r["units"] = int(r["units"])
            r["unit_price"] = float(r["unit_price"])
            r["discount_pct"] = int(r["discount_pct"])
            r["revenue"] = float(r["revenue"])
            r["month"] = r["date"][:7]  # "YYYY-MM"
            rows.append(r)
    return rows


ROWS = _load()
DIMENSIONS = {
    dim: sorted({r[dim] for r in ROWS}) for dim in FILTERABLE
}
DATE_MIN = min(r["date"] for r in ROWS)
DATE_MAX = max(r["date"] for r in ROWS)


def _filter(start_date: str | None = None, end_date: str | None = None,
            **dims: str | None) -> list[dict]:
    """Filter rows by ISO date range and exact dimension matches."""
    out = ROWS
    if start_date:
        out = [r for r in out if r["date"] >= start_date]
    if end_date:
        out = [r for r in out if r["date"] <= end_date]
    for dim, value in dims.items():
        if value:
            out = [r for r in out if r[dim] == value]
    return out


def _aggregate(rows: list[dict], by: str) -> list[dict]:
    """Group rows by a dimension -> revenue/units/orders, sorted by revenue."""
    acc: dict[str, list[float]] = defaultdict(lambda: [0.0, 0, 0])
    for r in rows:
        a = acc[r[by]]
        a[0] += r["revenue"]
        a[1] += r["units"]
        a[2] += 1
    out = [{by: k, "revenue": round(v[0], 2), "units": v[1], "orders": v[2]}
           for k, v in acc.items()]
    key = (lambda d: d[by]) if by == "month" else (lambda d: -d["revenue"])
    return sorted(out, key=key)


def _bad_dim(name: str, value: str | None, dim: str) -> dict | None:
    """Actionable error payload for an unknown dimension value, else None."""
    if value and value not in DIMENSIONS[dim]:
        return {"ok": False,
                "error": f"unknown {name}: {value!r}",
                "valid_values": DIMENSIONS[dim]}
    return None


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool(meta={"ui": {"resourceUri": APP_RESOURCE_URI}},
          annotations=ToolAnnotations(readOnlyHint=True))
def sales_dashboard(start_date: str | None = None, end_date: str | None = None,
                    region: str | None = None, category: str | None = None) -> dict:
    """Open an interactive sales dashboard for Voltaic Gear (mock CSV data).

    Aggregates the sales CSV into KPIs, a monthly revenue series, top
    products, and region/category/channel breakdowns. In hosts that support
    MCP Apps this renders inline in the chat as charts with working filters;
    everywhere else the returned JSON is still fully readable.

    Args:
        start_date: inclusive ISO date filter, e.g. "2025-10-01" (data starts 2025-01-01)
        end_date:   inclusive ISO date filter, e.g. "2025-12-31" (data ends 2026-06-30)
        region:     exact region name (see get_dataset_info for valid values)
        category:   exact product category (see get_dataset_info)
    """
    for err in (_bad_dim("region", region, "region"),
                _bad_dim("category", category, "category")):
        if err:
            return err

    rows = _filter(start_date, end_date, region=region, category=category)
    revenue = round(sum(r["revenue"] for r in rows), 2)
    units = sum(r["units"] for r in rows)
    orders = len(rows)

    return {
        "ok": True,
        "company": "Voltaic Gear",
        "filters": {"start_date": start_date or DATE_MIN,
                    "end_date": end_date or DATE_MAX,
                    "region": region, "category": category},
        "kpis": {
            "total_revenue": revenue,
            "total_units": units,
            "order_count": orders,
            "avg_order_value": round(revenue / orders, 2) if orders else 0,
        },
        "monthly": _aggregate(rows, "month"),
        "top_products": _aggregate(rows, "product")[:8],
        "by_region": _aggregate(rows, "region"),
        "by_category": _aggregate(rows, "category"),
        "by_channel": _aggregate(rows, "channel"),
        # so the app can populate its filter dropdowns
        "dimensions": {"regions": DIMENSIONS["region"],
                       "categories": DIMENSIONS["category"],
                       "date_min": DATE_MIN, "date_max": DATE_MAX},
    }


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
def query_sales(group_by: str, metric: str = "revenue",
                start_date: str | None = None, end_date: str | None = None,
                product: str | None = None, category: str | None = None,
                region: str | None = None, channel: str | None = None,
                sales_rep: str | None = None, top: int = 20) -> dict:
    """Aggregate the sales CSV by any dimension, with optional filters.

    Use this for ad-hoc questions the dashboard doesn't answer directly,
    e.g. "revenue by sales_rep in Europe during Q4 2025" ->
    group_by="sales_rep", region="Europe",
    start_date="2025-10-01", end_date="2025-12-31".

    Args:
        group_by: one of product | category | region | channel | sales_rep | month
        metric:   sort metric, one of revenue | units | orders (all three are returned)
        start_date / end_date: inclusive ISO date filters
        product / category / region / channel / sales_rep: exact-match filters
        top: max number of groups to return (default 20)
    """
    if group_by not in GROUPABLE:
        return {"ok": False, "error": f"unknown group_by: {group_by!r}",
                "valid_values": list(GROUPABLE)}
    if metric not in ("revenue", "units", "orders"):
        return {"ok": False, "error": f"unknown metric: {metric!r}",
                "valid_values": ["revenue", "units", "orders"]}
    for name, value in (("product", product), ("category", category),
                        ("region", region), ("channel", channel),
                        ("sales_rep", sales_rep)):
        err = _bad_dim(name, value, name)
        if err:
            return err

    rows = _filter(start_date, end_date, product=product, category=category,
                   region=region, channel=channel, sales_rep=sales_rep)
    groups = _aggregate(rows, group_by)
    if group_by != "month":
        groups.sort(key=lambda d: -d[metric])
    return {"ok": True, "group_by": group_by, "metric": metric,
            "row_count": len(rows), "groups": groups[:top]}


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
def get_dataset_info() -> dict:
    """Describe the sales dataset: schema, valid dimension values, date range.

    Call this first to learn what filters sales_dashboard and query_sales accept.
    """
    return {
        "ok": True,
        "company": "Voltaic Gear (mock consumer-electronics sales data)",
        "csv": str(CSV_PATH.name),
        "row_count": len(ROWS),
        "date_range": {"min": DATE_MIN, "max": DATE_MAX},
        "columns": ["order_id", "date", "product", "category", "region",
                    "channel", "sales_rep", "units", "unit_price",
                    "discount_pct", "revenue"],
        "dimensions": {"products": DIMENSIONS["product"],
                       "categories": DIMENSIONS["category"],
                       "regions": DIMENSIONS["region"],
                       "channels": DIMENSIONS["channel"],
                       "sales_reps": DIMENSIONS["sales_rep"]},
        "notes": "revenue = units * unit_price * (1 - discount_pct/100). "
                 "Black Friday promo week: 2025-11-24..30. "
                 "Spring Sale: 2026-04-06..19.",
    }


# ---------------------------------------------------------------------------
# The MCP App resource
# ---------------------------------------------------------------------------


@mcp.resource(APP_RESOURCE_URI, mime_type="text/html;profile=mcp-app")
def sales_dashboard_app() -> str:
    """The MCP App page for sales_dashboard (self-contained HTML)."""
    return APP_HTML_PATH.read_text()


if __name__ == "__main__":
    if "stdio" in sys.argv[1:]:
        mcp.run(transport="stdio")
    else:
        print("📊 csv-sales-explorer on http://127.0.0.1:8010/mcp")
        print(f"   {len(ROWS)} rows loaded from {CSV_PATH.name} "
              f"({DATE_MIN} .. {DATE_MAX})")
        mcp.run(transport="streamable-http")
