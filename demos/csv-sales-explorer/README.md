# CSV Sales Explorer — an MCP server with an MCP App dashboard

Explore a CSV of company sales data **visually, inline in a Claude chat**.
The server loads `data/sales_data.csv` (mock data for *Voltaic Gear*, a
consumer-electronics company: 5,867 order lines, Jan 2025 – Jun 2026, with
seasonality, a Black Friday spike, and a spring promo) and ships an
**MCP App**: ask Claude to "show me the sales dashboard" and the chat renders
KPI tiles, a monthly revenue line, product/region bars, and category/channel
breakdowns — with working filter dropdowns that call back into the server.

## Files

| File | Purpose |
|---|---|
| `server.py` | FastMCP server — 3 tools + the `ui://` app resource |
| `app.html` | the MCP App page (vanilla JS + inline SVG, `ui/initialize` handshake) |
| `data/sales_data.csv` | mock sales data (regenerate: `uv run generate_data.py`) |
| `generate_data.py` | seeded data generator (stable numbers) |
| `test_client.py` | protocol pre-flight — run after ANY change here |
| `preview.html` | mock MCP Apps host for developing `app.html` without Claude |
| `evaluation.xml` | 10 Q&A pairs with ground-truth answers for agent evals |

## Tools

- **`sales_dashboard(start_date?, end_date?, region?, category?)`** — the MCP
  App. Returns KPIs, monthly series, top products, and breakdowns; renders as
  interactive charts in hosts that support MCP Apps (Claude web/desktop, Goose).
- **`query_sales(group_by, metric?, ...filters, top?)`** — ad-hoc aggregation by
  product / category / region / channel / sales_rep / month.
- **`get_dataset_info()`** — schema, valid dimension values, date range.

## Run it

```bash
uv run server.py              # streamable HTTP → http://127.0.0.1:8010/mcp
uv run test_client.py         # pre-flight: protocol + MCP Apps wiring
```

### Connect from Claude (browser — where the MCP App renders)

Custom connectors need a public URL:

```bash
npx cloudflared tunnel --url http://localhost:8010
# Claude → Settings → Connectors → Add custom connector → https://<tunnel>/mcp
uv run test_client.py https://<tunnel-host>/mcp     # verify through the tunnel first
```

Then in a chat: *"Open the Voltaic Gear sales dashboard"* — the charts render
inline; the model can also answer ad-hoc questions with `query_sales`.

### Connect from Claude Desktop / Claude Code (stdio)

```bash
claude mcp add sales-explorer -- uv run $PWD/server.py stdio
```

### Develop the app UI without a host

```bash
python3 -m http.server 8020        # from this folder
open http://127.0.0.1:8020/preview.html
```

`preview.html` plays host: it answers `ui/initialize` and pushes
`sample_dashboard.json` as the tool result (filters are stubbed).

## How the MCP App is wired (extension rev 2026-01-26)

1. `sales_dashboard` declares `meta={"ui": {"resourceUri": "ui://csv-sales-explorer/app.html"}}`.
2. The resource at that URI returns self-contained HTML with mimeType
   `text/html;profile=mcp-app`.
3. The host renders it in a sandboxed iframe; `app.html` does the
   `ui/initialize` postMessage handshake, receives the tool result via
   `ui/notifications/tool-result`, and re-queries via `tools/call` when you
   change a filter. No CDNs — the sandbox blocks external hosts.
