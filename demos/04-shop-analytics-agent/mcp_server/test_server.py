"""Smoke test: `MCP_TOKEN=test uv run python test_server.py` (needs shop.db from seed.py)."""


from starlette.testclient import TestClient

import server

CALL = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": "kpi_summary", "arguments": {"start_date": "2025-11-01", "end_date": "2025-11-30"}}}
HEADERS = {"Accept": "application/json, text/event-stream"}

with TestClient(server.app) as client:
    assert client.get("/health").text == "ok"
    assert client.post("/mcp", json=CALL, headers=HEADERS).status_code == 401
    ok = client.post("/mcp", json=CALL, headers=HEADERS | {"Authorization": f"Bearer {server.MCP_TOKEN}"})
    assert ok.status_code == 200 and "revenue" in ok.text, ok.text

try:
    server.query("DELETE FROM orders")
    raise AssertionError("write was allowed")
except server.ToolError as e:
    assert "readonly" in str(e)

assert len(server.query("SELECT * FROM order_items")) == server.MAX_ROWS


# Module 05 lab: the PII guard blocks personal columns, even through SELECT *, and leaves the metrics alone.
server.PII_GUARD = True
for sql in ("SELECT email FROM customers", "SELECT * FROM customers"):
    try:
        server.query(sql)
        raise AssertionError(f"PII guard let through: {sql}")
    except server.ToolError as e:
        assert "prohibited" in str(e), e
assert server.query("SELECT country FROM customers LIMIT 1")
assert server.kpi_summary("2025-11-01", "2025-11-30")["revenue"] > 0
server.PII_GUARD = False
print("ok")
