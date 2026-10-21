# Shop Analytics Agent

A chat agent that answers business questions about an online shop ("How did Black Friday go?", "What's driving revenue?") with numbers and charts. It runs on the Claude Agent SDK. All data access goes through a custom MCP server that you deploy alongside it.

```
Browser ──HTTPS──▶ agent (FastAPI + Claude Agent SDK) ──MCP over HTTP──▶ mcp_server (SQLite) 
                        │                                   ▲
                        └──▶ api.anthropic.com              └── Claude Code / Claude Desktop can connect too
```

## Why a separate MCP server?

The MCP server is the **governed data layer** for the database. It is not a wrapper for its own sake.

- **One definition of the metrics.** "Revenue" means completed orders minus refunds. That rule lives once, in the `sales` view and the metric tools. The model doesn't re-derive it on every question.
- **Safe by construction.** The SQLite connection opens read-only (`mode=ro`). Queries are capped at 200 rows and 5 seconds. A bearer token guards the endpoint. Read-only is not the same as safe: module 05 shows what `run_sql` can still read. The agent has **no** built-in tools (`tools=[]`), so it reaches the data through the MCP server only.
- **Build once, use from any client.** The deployed server works with Claude Code, Claude Desktop or any MCP client, with the same tools and guardrails. The chat agent is one consumer among several.
- **Independent lifecycle.** Data people can change tools and queries without redeploying the agent, and the reverse holds too. The server is stateless, so it scales and restarts freely.

| Tool | What it does |
| --- | --- |
| `describe_schema` | Tables and views, so the model can write correct SQL |
| `kpi_summary` | Revenue, orders, AOV, active and new customers, refund rate for a date range |
| `revenue_over_time` | Revenue by day, week or month |
| `top_products` | Best sellers by revenue or units |
| `run_sql` | Read-only escape hatch for anything else |

## Project layout

```
mcp_server/   server.py (MCP server), seed.py (demo data), test_server.py, Dockerfile
agent/        app.py (FastAPI + Agent SDK), static/index.html (chat UI), Dockerfile
compose.yaml  run both containers locally
render.yaml   deploy both services to Render in one step
```

## Run it (students: start here)

You need Docker and your own [Anthropic API key](https://console.anthropic.com). Nothing else.

```bash
cp .env.example .env          # set ANTHROPIC_API_KEY, leave the rest commented out
docker compose up --build     # builds and starts both containers
```

Open http://localhost:8000: any username, password `demo`. Ask "How did Black Friday go?"

Both ports bind to `127.0.0.1`, so nobody else on your network can use the app or your key. The default `MCP_TOKEN` and `APP_PASSWORD` exist for this local setup only. Never deploy with them.

### Without Docker (two terminals, needs [uv](https://docs.astral.sh/uv/))

```bash
# Terminal 1: MCP server on :8001
cd mcp_server
uv run python seed.py
MCP_TOKEN=dev uv run python server.py

# Terminal 2: agent on :8000
cd agent
MCP_TOKEN=dev APP_PASSWORD=demo ANTHROPIC_API_KEY=sk-ant-... uv run uvicorn app:app --reload
```

Smoke-test the MCP server (no API spend): `cd mcp_server && MCP_TOKEN=test uv run python test_server.py`

Inspect the tools by hand: `npx @modelcontextprotocol/inspector`, then connect to `http://localhost:8001/mcp` with header `Authorization: Bearer local-dev-token` (Docker) or `Bearer dev` (two terminals).

## Telemetry: tokens and cost per message

Every reply in the chat shows a footer like `14210 in · 412 out tokens · ~$0.0490 (session ~$0.0710) · 4 steps · 9.8s`. The agent also prints one JSON line per message (the numbers below are illustrative):

```bash
docker compose logs -f agent | grep chat_turn
```

```json
{"event": "chat_turn", "session_id": "…", "status": "success", "model": "claude-sonnet-5",
 "input_tokens": 9, "output_tokens": 412, "cache_read_tokens": 12890, "cache_write_tokens": 1311,
 "turn_cost_usd": 0.049, "session_cost_usd": 0.071, "agent_steps": 4,
 "tool_calls": ["kpi_summary", "revenue_over_time"], "seconds": 9.8}
```

Structured logs on stdout are the standard first step. Docker, Render and every log platform can collect and query them without new infrastructure. Three rules come from the SDK docs:

- **`total_cost_usd` is an estimate.** The SDK computes it from a price table bundled at build time. Compare it with the Usage page in the Claude Console. Never bill anyone from it.
- **A resumed session reports its running total.** So the cost of one message is the difference from the previous total (`turn_cost_usd`). Summing `session_cost_usd` would double-count.
- **Expect most input tokens to be cache reads.** The system prompt and tool definitions repeat on every step, and the SDK caches them automatically. Cache reads cost a fraction of normal input tokens.

Next step: set the `OTEL_*` env vars (see Production notes) and the SDK exports traces, metrics and logs to any OpenTelemetry collector.

## What happens when things go wrong

| Situation | What the user sees | Log event |
| --- | --- | --- |
| Agent hits `max_turns` or `max_budget_usd` | A friendly "try a narrower question" reply (200) | `chat_turn` with `status: error_max_turns` / `error_max_budget_usd`, cost included |
| MCP server down or wrong `MCP_TOKEN` | 503 "analytics data service is unavailable" before the model spends tokens | `mcp_unavailable` with the server status |
| Invalid or missing-credit API key | 502 "The model call failed: …" | `chat_turn` with `is_error: true`, `api_error_status` |
| Anything else that stops the run | 502 "check the server logs" | `chat_error` |

The data-service check reads the MCP server status from the SDK's `init` message. A wrong token or an unreachable server shows `failed` there, before the first model call.

## Deploy to Render

1. Push this folder to a GitHub repo.
2. In Render, choose **New → Blueprint** and select the repo. Render reads `render.yaml`.
3. Enter `ANTHROPIC_API_KEY` and a strong `APP_PASSWORD` when asked. Render generates `MCP_TOKEN` and wires the agent to the MCP server over Render's private network.

Both services deploy again on every push to `main`. The health checks are `/health` on each service.

### Use the deployed MCP server from Claude Code

Copy `MCP_TOKEN` from the `shop-analytics-mcp` service's environment in Render, then:

```bash
claude mcp add --transport http shop-analytics https://<your-mcp-service>.onrender.com/mcp \
  --header "Authorization: Bearer <MCP_TOKEN>"
```

The tools and guardrails are identical to the chat agent's.

## Production notes

| Concern | What this project does | When to go further |
| --- | --- | --- |
| Inbound auth | HTTP Basic password on the agent | Real users: put SSO or an auth gateway in front, and check that each `session_id` belongs to the caller |
| MCP auth | Static bearer token | Many clients or users: OAuth 2.1 (the MCP SDK supports it) |
| Cost | `max_turns=12`, `MAX_BUDGET_USD` (default 0.50) per message, cost per message in logs | A daily cap per user; reconcile with the Console's Usage and Cost API |
| Chat history | Stored on the agent container's disk; a redeploy clears it, and a second instance can't resume the first one's chats | Add a `SessionStore` (S3, Redis, Postgres) |
| Personal data | `run_sql` can read customer names and emails | Module 05 data-exposure lab: `PII_GUARD=1` (SQLite authorizer) |
| Browser rendering | Markdown images in replies load from any URL | Module 05 exercise: a CSP `img-src` rule or no `<img>` |
| Replies | The whole answer arrives at the end | Stream with SSE (the hosting cookbook's `/sessions/{id}/messages` contract) |
| Host/Origin check | Off (server binds `0.0.0.0`); the bearer token guards the endpoint | `transport_security=TransportSecuritySettings(allowed_hosts=[...])` |
| Outbound network | Unrestricted; the agent has no tool that reaches the internet | An egress allowlist: the Anthropic API and the MCP server only |
| Data | Demo SQLite file baked into the image | Point `DB_PATH` at a mounted volume, or swap SQLite for Postgres in `query()` |
| Observability | One JSON line per message | Set the `OTEL_*` env vars; the SDK exports traces natively |
