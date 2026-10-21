#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp[cli]>=2.3,<3"]
# ///
"""Sales Insights MCP server, tuned for the Voltaic Gear sales CSV.

Loads the CSV into an in-memory SQLite table at startup and exposes four tools:

    dataset_guide    -> schema, valid values, and the facts that make comparisons fair
    breakdown        -> revenue / units / orders / AOV / discount / share by any dimension
    compare_periods  -> period-over-period change (year-over-year by default), per group
    run_sql          -> read-only SELECT escape hatch, 200-row cap

Run:
    uv run server.py                       # stdio
    mcp dev server.py                      # Inspector
    claude mcp add sales-insights -- uv run $PWD/server.py
    SALES_CSV=/path/to/other.csv uv run server.py   # same schema, different file
"""

import csv
import os
import sqlite3
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Literal

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

CSV_PATH = Path(os.environ.get(
    "SALES_CSV", Path(__file__).parent.parent / "archive/csv-sales-explorer/data/sales_data.csv"))
MAX_ROWS = 200
QUERY_TIMEOUT_S = 5
# From generate_data.py: promo windows that distort any period they fall in.
PROMOS = {"Black Friday": ("2025-11-24", "2025-11-30"), "Spring Sale": ("2026-04-06", "2026-04-19")}
DIMENSIONS = ("product", "category", "region", "channel", "sales_rep")

# Only reads get past the authorizer: no INSERT/UPDATE/DELETE, PRAGMA, ATTACH or DDL.
ALLOWED = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE}


def read_only(action, *_):
    return sqlite3.SQLITE_OK if action in ALLOWED else sqlite3.SQLITE_DENY


def promo_for(day: str) -> str:
    return next((name for name, (a, b) in PROMOS.items() if a <= day <= b), "none")


def load(path: Path) -> sqlite3.Connection:
    # ponytail: one shared connection, fine for a single-client stdio server.
    con = sqlite3.connect(":memory:", check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("""CREATE TABLE orders (
        order_id TEXT PRIMARY KEY, date TEXT, month TEXT, quarter TEXT,
        product TEXT, category TEXT, region TEXT, channel TEXT, sales_rep TEXT,
        units INTEGER, unit_price REAL, discount_pct INTEGER, revenue REAL, promo TEXT)""")
    with path.open(newline="", encoding="utf-8-sig") as f:
        con.executemany(
            "INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            [(r["order_id"], r["date"], r["date"][:7], f"{r['date'][:4]}-Q{(int(r['date'][5:7]) + 2) // 3}",
              r["product"], r["category"], r["region"], r["channel"], r["sales_rep"],
              int(r["units"]), float(r["unit_price"]), int(r["discount_pct"]), float(r["revenue"]),
              promo_for(r["date"])) for r in csv.DictReader(f)])
    con.set_authorizer(read_only)
    return con


DB = load(CSV_PATH)


def query(sql: str, params: tuple | list = ()) -> list[dict]:
    deadline = time.monotonic() + QUERY_TIMEOUT_S
    DB.set_progress_handler(lambda: time.monotonic() > deadline, 10_000)
    try:
        return [dict(r) for r in DB.execute(sql, params).fetchmany(MAX_ROWS)]
    except sqlite3.Error as e:
        raise ToolError(f"SQL error: {e}") from e


VALUES = {d: [r[d] for r in query(f"SELECT DISTINCT {d} FROM orders ORDER BY 1")] for d in DIMENSIONS}
DATE_MIN, DATE_MAX = query("SELECT MIN(date) AS a, MAX(date) AS b FROM orders")[0].values()

# Enums built from the data, so the input schema lists every valid value and typos can't happen.
Product = Literal[tuple(VALUES["product"])]
Category = Literal[tuple(VALUES["category"])]
Region = Literal[tuple(VALUES["region"])]
Channel = Literal[tuple(VALUES["channel"])]
SalesRep = Literal[tuple(VALUES["sales_rep"])]
GroupBy = Literal["product", "category", "region", "channel", "sales_rep",
                  "month", "quarter", "promo", "discount_pct"]
ORDERED_GROUPS = {"month", "quarter", "discount_pct"}  # sort these by key, not by size

mcp = MCPServer(
    "sales-insights",
    instructions=f"Voltaic Gear consumer-electronics sales, {DATE_MIN} to {DATE_MAX}, one row per order. "
    "Sales are strongly seasonal (Nov-Dec peak), so compare periods year-over-year, not month-to-month. "
    "Call dataset_guide first.",
    dependencies=["mcp[cli]>=2.3,<3"],
)
READ_ONLY = ToolAnnotations(readOnlyHint=True, openWorldHint=False)


def parse_date(value: str, name: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ToolError(f"{name} must be an ISO date like 2026-01-31, got {value!r}") from None


def where(start: str | None, end: str | None, filters: dict) -> tuple[str, list]:
    clauses, params = [], []
    if start:
        clauses.append("date >= ?"), params.append(start)
    if end:
        clauses.append("date <= ?"), params.append(end)
    for col, val in filters.items():
        if val is not None:
            clauses.append(f"{col} = ?"), params.append(val)  # col comes from DIMENSIONS, never input
    return ("WHERE " + " AND ".join(clauses)) if clauses else "", params


def year_earlier(d: date) -> date:
    try:
        return d.replace(year=d.year - 1)
    except ValueError:  # Feb 29
        return d.replace(year=d.year - 1, day=28)


@mcp.tool(annotations=READ_ONLY)
def dataset_guide() -> dict:
    """Call this first. Describes the orders table and the business facts needed to compare fairly:
    which region each sales rep covers, how channels differ, promo windows and seasonality."""
    return {
        "table": "orders (one row per order)",
        "columns": {
            "order_id": "unique id", "date": "ISO date", "month": "YYYY-MM", "quarter": "YYYY-Qn",
            "product/category/region/channel/sales_rep": "dimensions, see valid_values",
            "units": "items in the order", "unit_price": "list price per unit (USD)",
            "discount_pct": "0-35", "revenue": "units * unit_price * (1 - discount_pct/100), USD",
            "promo": "'Black Friday', 'Spring Sale' or 'none'",
        },
        "date_range": [DATE_MIN, DATE_MAX],
        "valid_values": VALUES,
        "rep_regions": {r["sales_rep"]: r["region"] for r in query(
            "SELECT sales_rep, MIN(region) AS region FROM orders GROUP BY 1")},
        "channel_profile": query(
            """SELECT channel, COUNT(*) AS orders, ROUND(AVG(units), 1) AS avg_units,
                      ROUND(AVG(discount_pct), 1) AS avg_discount_pct, ROUND(SUM(revenue) / COUNT(*), 2) AS avg_order_value,
                      ROUND(100.0 * SUM(revenue) / (SELECT SUM(revenue) FROM orders), 1) AS revenue_share_pct
               FROM orders GROUP BY 1 ORDER BY revenue_share_pct DESC"""),
        "promos": PROMOS,
        "facts": [
            "Each sales rep sells in exactly one region: compare reps within a region, not across.",
            "Distributor orders are bulk (20+ units) with structural 20-35% discounts; they dominate revenue.",
            "Strong seasonality: November-December peak, quiet January. Use compare_periods with baseline='year_ago'.",
            "Average order value mixes channels; filter by channel before comparing AOV.",
        ],
    }


@mcp.tool(annotations=READ_ONLY)
def breakdown(
    group_by: GroupBy,
    start_date: str | None = None,
    end_date: str | None = None,
    product: Product | None = None,
    category: Category | None = None,
    region: Region | None = None,
    channel: Channel | None = None,
    sales_rep: SalesRep | None = None,
    sort_by: Literal["revenue", "units", "orders"] = "revenue",
    limit: int = 20,
) -> list[dict]:
    """Revenue, units, orders, average order value, average discount and share of revenue,
    grouped by one dimension, with optional ISO date range (inclusive) and filters.
    month / quarter / discount_pct come back in order; other groups are ranked by sort_by.
    Example: top reps in Europe for Q4 2025 -> group_by="sales_rep", region="Europe",
    start_date="2025-10-01", end_date="2025-12-31"."""
    for value, name in ((start_date, "start_date"), (end_date, "end_date")):
        if value:
            parse_date(value, name)
    w, p = where(start_date, end_date, {"product": product, "category": category, "region": region,
                                        "channel": channel, "sales_rep": sales_rep})
    order = group_by if group_by in ORDERED_GROUPS else f"{sort_by} DESC"
    return query(
        f"""SELECT {group_by}, ROUND(SUM(revenue), 2) AS revenue, SUM(units) AS units, COUNT(*) AS orders,
                   ROUND(SUM(revenue) / COUNT(*), 2) AS avg_order_value, ROUND(AVG(discount_pct), 1) AS avg_discount_pct,
                   ROUND(100.0 * SUM(revenue) / (SELECT SUM(revenue) FROM orders {w}), 1) AS share_pct
            FROM orders {w} GROUP BY 1 ORDER BY {order} LIMIT ?""",
        p + p + [max(1, min(limit, MAX_ROWS))],
    )


@mcp.tool(annotations=READ_ONLY)
def compare_periods(
    start_date: str | None = None,
    end_date: str | None = None,
    baseline: Literal["year_ago", "previous"] = "year_ago",
    group_by: GroupBy | None = None,
    product: Product | None = None,
    category: Category | None = None,
    region: Region | None = None,
    channel: Channel | None = None,
    sales_rep: SalesRep | None = None,
    limit: int = 20,
) -> dict:
    """Compare revenue in a period (ISO dates, inclusive) with a baseline period, in total and per group.
    Defaults to the latest 6 months of data versus the same months a year earlier.
    baseline="year_ago" (default) removes seasonality; "previous" uses the equally long period just before,
    which is misleading across the Nov-Dec peak. Groups are ranked by absolute change and include
    share_of_change_pct: how much of the total change each group explains."""
    e = parse_date(end_date or DATE_MAX, "end_date")
    s = parse_date(start_date, "start_date") if start_date else (e.replace(day=1) - timedelta(days=150)).replace(day=1)
    if s > e:
        raise ToolError("start_date must be on or before end_date")
    if e.isoformat() > DATE_MAX:
        raise ToolError(f"Data ends {DATE_MAX}; a period past that would compare a partial period. Set end_date <= {DATE_MAX}.")
    if baseline == "year_ago":
        bs, be = year_earlier(s), year_earlier(e)
    else:
        be = s - timedelta(days=1)
        bs = be - (e - s)
    if bs.isoformat() < DATE_MIN:
        raise ToolError(f"Baseline {bs}..{be} starts before the data ({DATE_MIN}). "
                        "Pick a later period or baseline='previous'.")

    w, p = where(None, None, {"product": product, "category": category, "region": region,
                              "channel": channel, "sales_rep": sales_rep})
    rows = query(
        f"""SELECT {group_by or "'all'"} AS grp,
                   SUM(CASE WHEN date BETWEEN ? AND ? THEN revenue ELSE 0 END) AS current,
                   SUM(CASE WHEN date BETWEEN ? AND ? THEN revenue ELSE 0 END) AS baseline
            FROM orders {w} GROUP BY 1""",
        [s.isoformat(), e.isoformat(), bs.isoformat(), be.isoformat()] + p,
    )
    cur, base = sum(r["current"] for r in rows), sum(r["baseline"] for r in rows)
    pct = lambda a, b: round(100 * (a - b) / b, 1) if b else None
    out = {
        "current_period": [s.isoformat(), e.isoformat()],
        "baseline_period": [bs.isoformat(), be.isoformat()],
        "total": {"current": round(cur, 2), "baseline": round(base, 2),
                  "change": round(cur - base, 2), "change_pct": pct(cur, base)},
    }
    if group_by:
        total_change = cur - base
        groups = [{group_by: r["grp"], "current": round(r["current"], 2), "baseline": round(r["baseline"], 2),
                   "change": round(r["current"] - r["baseline"], 2), "change_pct": pct(r["current"], r["baseline"]),
                   "share_of_change_pct": round(100 * (r["current"] - r["baseline"]) / total_change, 1)
                   if total_change else None}
                  for r in rows]
        groups.sort(key=lambda g: -abs(g["change"]))
        out["groups"] = groups[:max(1, min(limit, MAX_ROWS))]
    return out


@mcp.tool(annotations=READ_ONLY)
def run_sql(sql: str) -> list[dict]:
    """Run one read-only SQLite SELECT against the `orders` table for questions the other tools
    don't cover (e.g. weekday patterns, price points, order-size buckets). Returns at most 200 rows."""
    return query(sql)


if __name__ == "__main__":
    mcp.run(transport="stdio")
