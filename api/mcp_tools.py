"""
In-process MCP server exposing the five analysis tools the agent is allowed to
call. This file is the *primary teaching artifact* — everything the agent can
do lives here.

Design notes (see plan.md for full context):
  - `list_tables` / `describe_table` are cheap, safe metadata reads and run
    in-process directly against the DuckDB file.
  - `query_sql` / `run_pandas` / `create_chart` are code-executing tools: they
    delegate to `sandbox_exec.run_in_sandbox(...)` which, in production, runs
    the code inside a Vercel Sandbox microVM. Locally it falls back to running
    in-process so you can develop without a Vercel OIDC token.
  - Every tool returns a *typed dict* with a top-level `type` field
    ("text" | "table" | "chart" | "kpi" | "error"). The frontend dispatches on
    that field to pick the right React renderer. Keeping the contract narrow
    here lets the UI stay dumb.

Tool allowlist (configured in agent.py): only `mcp__analysis__*`. No Bash,
Read, Write, or WebFetch are ever exposed to the model.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import duckdb
import sqlglot
from sqlglot import exp
from claude_agent_sdk import create_sdk_mcp_server, tool

from .sandbox_exec import run_in_sandbox

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sabi_synth.duckdb"

# Tables we advertise to the agent. Order matters — it appears in the system
# prompt's table listing.
KNOWN_TABLES = ["companies", "main_financials", "operating_expenses",
                "ownership", "subsidiaries", "hubspot"]

# ----------------------------------------------------------------------------
# In-process helpers (cheap metadata reads)
# ----------------------------------------------------------------------------


def _open_readonly() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(str(DATA_PATH), read_only=True)


def _validate_select(sql: str) -> str | None:
    """Return an error string if `sql` is not a pure SELECT, else None."""
    try:
        parsed = sqlglot.parse(sql, read="duckdb")
    except sqlglot.errors.ParseError as e:
        return f"SQL parse error: {e}"
    if len(parsed) != 1:
        return "Only one statement allowed per query."
    stmt = parsed[0]
    if stmt is None:
        return "Empty statement."
    # Reject DDL / DML that isn't SELECT (INSERT, UPDATE, DELETE, CREATE, DROP, …)
    # Accept SELECT, Union (compound SELECTs), and With (CTEs wrapping a SELECT).
    if not isinstance(stmt, (exp.Select, exp.Union, exp.With)):
        return f"Only SELECT statements are allowed. Got: {type(stmt).__name__}"
    forbidden = (exp.Insert, exp.Update, exp.Delete, exp.Create,
                 exp.Drop, exp.Alter, exp.TruncateTable, exp.Command)
    for node in stmt.walk():
        if isinstance(node, forbidden):
            return f"Forbidden statement type: {type(node).__name__}"
    return None


# ----------------------------------------------------------------------------
# Tools
# ----------------------------------------------------------------------------


@tool(
    name="list_tables",
    description=(
        "List all tables available in the sabi_synth dataset. Returns table "
        "names, column counts, and row counts. Call this first if you don't "
        "remember the schema."
    ),
    input_schema={},
)
async def list_tables(args: dict[str, Any]) -> dict[str, Any]:
    con = _open_readonly()
    try:
        tables = []
        for name in KNOWN_TABLES:
            cols = con.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = ? ORDER BY ordinal_position",
                [name],
            ).fetchall()
            row_count = con.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
            tables.append({
                "name": name,
                "columns": [c[0] for c in cols],
                "row_count": int(row_count),
            })
    finally:
        con.close()
    # Render as a table so the UI can show it inline; keeps the "text" type
    # reserved for free-form messages.
    return _table_result(
        columns=["table", "columns", "rows"],
        rows=[[t["name"], len(t["columns"]), t["row_count"]] for t in tables],
        meta={"tables_detail": tables},
    )


@tool(
    name="describe_table",
    description=(
        "Describe a table: full schema (column name + type), 5 sample rows, "
        "and basic stats (min/max/avg) for numeric columns. Use before "
        "writing a query if you're unsure about a column."
    ),
    input_schema={"table_name": str},
)
async def describe_table(args: dict[str, Any]) -> dict[str, Any]:
    table = args["table_name"]
    if table not in KNOWN_TABLES:
        return _error(f"Unknown table '{table}'. Available: {', '.join(KNOWN_TABLES)}")
    con = _open_readonly()
    try:
        schema_rows = con.execute(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_name = ? ORDER BY ordinal_position",
            [table],
        ).fetchall()
        schema = [{"name": r[0], "type": r[1]} for r in schema_rows]

        sample = con.execute(f'SELECT * FROM "{table}" USING SAMPLE 5 ROWS').fetchall()
        sample_cols = [d[0] for d in con.description]
        sample_rows = [dict(zip(sample_cols, r)) for r in sample]

        numeric_cols = [c["name"] for c in schema
                        if c["type"].upper() in ("BIGINT", "DOUBLE", "INTEGER", "DECIMAL")]
        stats = {}
        for col in numeric_cols[:20]:  # cap to keep payload small
            row = con.execute(
                f'SELECT MIN("{col}"), MAX("{col}"), AVG("{col}") FROM "{table}"'
            ).fetchone()
            stats[col] = {"min": row[0], "max": row[1], "avg": row[2]}
    finally:
        con.close()

    return _table_result(
        columns=["column", "type"],
        rows=[[c["name"], c["type"]] for c in schema],
        meta={"sample_rows": sample_rows, "stats": stats, "table": table},
    )


@tool(
    name="query_sql",
    description=(
        "Run a SELECT query against the sabi_synth DuckDB database. Only "
        "SELECT is allowed. Returns columns + up to 500 rows. Prefer this "
        "over run_pandas whenever the question is expressible in SQL."
    ),
    input_schema={"sql": str},
)
async def query_sql(args: dict[str, Any]) -> dict[str, Any]:
    sql = args["sql"].strip()
    err = _validate_select(sql)
    if err:
        return _error(err)

    code = (
        "import duckdb, json, sys\n"
        "con = duckdb.connect('/vercel/sandbox/data/sabi_synth.duckdb', read_only=True)\n"
        f"sql = {json.dumps(sql)}\n"
        "res = con.execute(sql)\n"
        "cols = [d[0] for d in res.description]\n"
        "rows = res.fetchmany(500)\n"
        "print(json.dumps({'columns': cols, 'rows': [list(r) for r in rows]}, default=str))\n"
    )
    out = await run_in_sandbox(code, timeout_s=30)
    if out.get("error"):
        return _error(out["error"])
    parsed = json.loads(out["stdout"])
    return _table_result(columns=parsed["columns"], rows=parsed["rows"])


@tool(
    name="run_pandas",
    description=(
        "Run a Python/pandas snippet against the dataset. The snippet has "
        "access to `df` — a dict mapping each table name to a pandas "
        "DataFrame loaded from sabi_synth. Assign the final value to a "
        "variable named `result`; it must be a DataFrame (returned as a "
        "table), a dict (returned as text), or a scalar (returned as a "
        "KPI). Use this for reshaping (melt/pivot), joins that SQL makes "
        "awkward, or complex aggregations."
    ),
    input_schema={"code": str},
)
async def run_pandas(args: dict[str, Any]) -> dict[str, Any]:
    user_code = args["code"]
    harness = (
        "import duckdb, pandas as pd, json\n"
        "con = duckdb.connect('/vercel/sandbox/data/sabi_synth.duckdb', read_only=True)\n"
        "df = {t: con.execute(f'SELECT * FROM \"{t}\"').df() for t in "
        f"{KNOWN_TABLES!r}"
        "}\n"
        "result = None\n"
        "try:\n"
        + "\n".join("    " + line for line in user_code.splitlines())
        + "\nexcept Exception as e:\n"
        "    print(json.dumps({'kind': 'error', 'message': f'{type(e).__name__}: {e}'}))\n"
        "    raise SystemExit(0)\n"
        "if isinstance(result, pd.DataFrame):\n"
        "    print(json.dumps({'kind': 'table', 'columns': list(result.columns),"
        "                      'rows': result.head(500).astype(object).where(result.head(500).notna(), None).values.tolist()}, default=str))\n"
        "elif isinstance(result, (int, float)):\n"
        "    print(json.dumps({'kind': 'kpi', 'value': result}))\n"
        "elif result is None:\n"
        "    print(json.dumps({'kind': 'text', 'text': 'Code ran but did not assign `result`.'}))\n"
        "else:\n"
        "    print(json.dumps({'kind': 'text', 'text': str(result)[:2000]}, default=str))\n"
    )
    out = await run_in_sandbox(harness, timeout_s=60)
    if out.get("error"):
        return _error(out["error"])
    parsed = json.loads(out["stdout"].strip().splitlines()[-1])
    if parsed["kind"] == "error":
        return _error(parsed["message"])
    if parsed["kind"] == "table":
        return _table_result(columns=parsed["columns"], rows=parsed["rows"])
    if parsed["kind"] == "kpi":
        return _kpi_result(value=parsed["value"], label="result")
    return _text_result(parsed["text"])


@tool(
    name="create_chart",
    description=(
        "Render a chart from tabular data. `data` is an object with "
        "`columns` and `rows` (typically copy-pasted from a prior "
        "query_sql/run_pandas result). `spec` selects chart type and maps "
        "columns to axes. Returns a Plotly figure JSON that the frontend "
        "renders inline."
    ),
    input_schema={
        "data": dict,       # {columns: [...], rows: [[...], ...]}
        "spec": dict,       # {chart_type: 'bar'|'line'|'scatter'|'pie', x, y, color?, title?}
    },
)
async def create_chart(args: dict[str, Any]) -> dict[str, Any]:
    data = args["data"]
    spec = args["spec"]
    # Delegate Plotly figure construction to the sandbox so the agent never
    # writes Python that touches the server process directly.
    code = (
        "import plotly.express as px, pandas as pd, json\n"
        f"data = {json.dumps(data)}\n"
        f"spec = {json.dumps(spec)}\n"
        "df = pd.DataFrame(data['rows'], columns=data['columns'])\n"
        "ctype = spec.get('chart_type', 'bar')\n"
        "kwargs = {k: spec[k] for k in ('x','y','color','title') if k in spec}\n"
        "fn = {'bar': px.bar, 'line': px.line, 'scatter': px.scatter, 'pie': px.pie}.get(ctype)\n"
        "if fn is None:\n"
        "    print(json.dumps({'kind':'error','message':f'Unknown chart_type {ctype!r}'}))\n"
        "    raise SystemExit(0)\n"
        "fig = fn(df, **{k:v for k,v in kwargs.items() if k != 'title'})\n"
        "if 'title' in kwargs: fig.update_layout(title=kwargs['title'])\n"
        "fig.update_layout(template='plotly_dark', paper_bgcolor='#121826', plot_bgcolor='#121826')\n"
        "print(json.dumps({'kind':'chart','figure': json.loads(fig.to_json())}))\n"
    )
    out = await run_in_sandbox(code, timeout_s=30)
    if out.get("error"):
        return _error(out["error"])
    parsed = json.loads(out["stdout"].strip().splitlines()[-1])
    if parsed["kind"] == "error":
        return _error(parsed["message"])
    return _chart_result(parsed["figure"])


# ----------------------------------------------------------------------------
# Result helpers — keep the tool-result JSON contract in one place
# ----------------------------------------------------------------------------


def _wrap(payload: dict[str, Any]) -> dict[str, Any]:
    """MCP tools must return {"content": [{"type":"text","text": ...}]}. We
    stuff our typed-dict payload as JSON inside the text block; the frontend
    parses it back out on the SSE stream."""
    return {"content": [{"type": "text", "text": json.dumps(payload)}]}


def _error(msg: str) -> dict[str, Any]:
    return _wrap({"type": "error", "payload": {"message": msg}})


def _text_result(text: str) -> dict[str, Any]:
    return _wrap({"type": "text", "payload": {"text": text}})


def _table_result(columns: list[str], rows: list[list[Any]],
                  meta: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"columns": columns, "rows": rows}
    if meta:
        payload.update(meta)
    return _wrap({"type": "table", "payload": payload})


def _chart_result(figure: dict[str, Any]) -> dict[str, Any]:
    return _wrap({"type": "chart", "payload": {"figure": figure}})


def _kpi_result(value: float, label: str, delta: float | None = None) -> dict[str, Any]:
    return _wrap({"type": "kpi", "payload": {"value": value, "label": label, "delta": delta}})


# ----------------------------------------------------------------------------
# MCP server factory
# ----------------------------------------------------------------------------


def build_server():
    """Build the in-process MCP server. Call from agent.py and pass the
    returned instance in `ClaudeAgentOptions(mcp_servers=...)`."""
    return create_sdk_mcp_server(
        name="analysis",
        version="0.1.0",
        tools=[list_tables, describe_table, query_sql, run_pandas, create_chart],
    )
