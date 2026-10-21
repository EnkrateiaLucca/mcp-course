"""Shop Analytics MCP server.

The governed data layer for the shop database. Any MCP client (our agent,
Claude Code, Claude Desktop) gets the same read-only connection, the same
business definitions (see the `sales` view) and the same row and time limits.
"""

import hmac
import os
import sqlite3
import time
from datetime import date
from typing import Literal

import uvicorn
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from starlette.requests import Request
from starlette.responses import PlainTextResponse

DB_PATH = os.environ.get("DB_PATH", "shop.db")
MCP_TOKEN = os.environ["MCP_TOKEN"]  # fail fast: never run this server unauthenticated
MAX_ROWS = 200
QUERY_TIMEOUT_S = 5
# Module 05 security lab: read-only is not the same as safe. With PII_GUARD=1, SQLite itself refuses
# to read personal columns, whatever SQL the model writes. Off by default so the lab can show the leak.
PII_GUARD = os.environ.get("PII_GUARD") == "1"
PII_COLUMNS = {("customers", "name"), ("customers", "email")}


def deny_pii(action, table, column, _db, _trigger):
    if action == sqlite3.SQLITE_READ and (table, column) in PII_COLUMNS:
        return sqlite3.SQLITE_DENY  # the statement fails with "access to customers.email is prohibited"
    return sqlite3.SQLITE_OK

mcp = MCPServer(
    "shop-analytics",
    instructions="Analytics for an outdoor-gear online shop. Revenue always means the `sales` view "
    "(completed orders, refunds excluded). Prefer the metric tools; use run_sql for anything else.",
)
READ_ONLY = ToolAnnotations(readOnlyHint=True, openWorldHint=False)


def query(sql: str, params: tuple = ()) -> list[dict]:
    # mode=ro makes SQLite itself reject writes, whatever SQL the model sends.
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    deadline = time.monotonic() + QUERY_TIMEOUT_S
    con.set_progress_handler(lambda: time.monotonic() > deadline, 10_000)  # abort runaway queries
    if PII_GUARD:
        con.set_authorizer(deny_pii)
    try:
        return [dict(r) for r in con.execute(sql, params).fetchmany(MAX_ROWS)]
    except sqlite3.Error as e:
        # ToolError text reaches the model, so it can fix its SQL. Any other exception arrives
        # as a bare "Error executing tool <name>" (the v2 SDK hides crash details from clients).
        raise ToolError(f"SQL error: {e}") from e
    finally:
        con.close()


def check_dates(start_date: str, end_date: str) -> None:
    if date.fromisoformat(start_date) > date.fromisoformat(end_date):
        raise ToolError("start_date must be on or before end_date")


@mcp.tool(annotations=READ_ONLY)
def describe_schema() -> list[dict]:
    """List every table and view with its CREATE statement. Call this before writing SQL."""
    return query("SELECT type, name, sql FROM sqlite_master WHERE type IN ('table', 'view')")


@mcp.tool(annotations=READ_ONLY)
def kpi_summary(start_date: str, end_date: str) -> dict:
    """Headline KPIs between two ISO dates (inclusive): revenue, orders, average order value,
    active customers, new signups and refund rate."""
    check_dates(start_date, end_date)
    kpis = query(
        """SELECT ROUND(SUM(revenue), 2) AS revenue, COUNT(DISTINCT order_id) AS orders,
                  ROUND(SUM(revenue) / COUNT(DISTINCT order_id), 2) AS avg_order_value,
                  COUNT(DISTINCT customer_id) AS active_customers
           FROM sales WHERE order_date BETWEEN ? AND ?""",
        (start_date, end_date),
    )[0]
    kpis |= query(
        """SELECT (SELECT COUNT(*) FROM customers WHERE signup_date BETWEEN ?1 AND ?2) AS new_customers,
                  ROUND(100.0 * SUM(status = 'refunded') / COUNT(*), 2) AS refund_rate_pct
           FROM orders WHERE order_date BETWEEN ?1 AND ?2""",
        (start_date, end_date),
    )[0]
    return kpis


@mcp.tool(annotations=READ_ONLY)
def revenue_over_time(start_date: str, end_date: str, grain: Literal["day", "week", "month"] = "month") -> list[dict]:
    """Revenue and order count per day, week or month between two ISO dates (inclusive)."""
    check_dates(start_date, end_date)
    fmt = {"day": "%Y-%m-%d", "week": "%Y-W%W", "month": "%Y-%m"}[grain]
    return query(
        """SELECT strftime(?, order_date) AS period, ROUND(SUM(revenue), 2) AS revenue,
                  COUNT(DISTINCT order_id) AS orders
           FROM sales WHERE order_date BETWEEN ? AND ? GROUP BY period ORDER BY period""",
        (fmt, start_date, end_date),
    )


@mcp.tool(annotations=READ_ONLY)
def top_products(
    start_date: str, end_date: str, by: Literal["revenue", "units"] = "revenue", limit: int = 10
) -> list[dict]:
    """Best-selling products between two ISO dates (inclusive), ranked by revenue or units."""
    check_dates(start_date, end_date)
    order_col = "revenue" if by == "revenue" else "units"  # whitelisted, never raw input
    return query(
        f"""SELECT product, category, SUM(quantity) AS units, ROUND(SUM(revenue), 2) AS revenue
            FROM sales WHERE order_date BETWEEN ? AND ?
            GROUP BY product ORDER BY {order_col} DESC LIMIT ?""",
        (start_date, end_date, max(1, min(limit, 50))),
    )


@mcp.tool(annotations=READ_ONLY)
def run_sql(sql: str) -> list[dict]:
    """Run one read-only SQLite SELECT for questions the other tools don't cover.
    Use the `sales` view for anything about revenue. Returns at most 200 rows."""
    return query(sql)


@mcp.custom_route("/health", methods=["GET"])
async def health(_: Request) -> PlainTextResponse:
    return PlainTextResponse("ok")


class BearerAuth:
    """Reject every request without `Authorization: Bearer <MCP_TOKEN>` (except /health)."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"] != "/health":
            header = dict(scope["headers"]).get(b"authorization", b"").decode()
            if not hmac.compare_digest(header, f"Bearer {MCP_TOKEN}"):
                return await PlainTextResponse("Unauthorized", status_code=401)(scope, receive, send)
        await self.app(scope, receive, send)


# Stateless + JSON responses: any replica can answer any request, so the server restarts and scales freely.
app = mcp.streamable_http_app(stateless_http=True, json_response=True, host="0.0.0.0")
app.add_middleware(BearerAuth)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8001)))
