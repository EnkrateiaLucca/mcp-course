# Plan — Data Analysis Chat Agent (Claude Agent SDK + MCP + Vercel)

## Context

You're teaching a class on building agents with the **Claude Agent SDK** where the tooling is provided by an **MCP server**. You want a deployable reference app — a chat agent that analyzes a bundled synthetic business dataset (Portuguese SME financials, modeled on `schema_blueprint.md`) and renders its output as a **dashboard-style chat**: charts, tables, KPI cards inline with the conversation. Target deploy: **Vercel**. Not a polished product; a production-shaped teaching artifact that demonstrates:

1. Claude Agent SDK in Python as the agent core.
2. A **custom in-process MCP server** (`create_sdk_mcp_server`) as the sole source of tools — the course's teaching focus.
3. **Vercel Sandbox** as the secure execution layer for agent-generated pandas/matplotlib code.
4. End-to-end deploy on Vercel (Next.js frontend + Python serverless functions).

## Architecture

```
┌──────────────────────────────── Vercel Deployment ────────────────────────────────┐
│                                                                                   │
│  ┌─────────────────────────────┐     ┌──────────────────────────────────────┐     │
│  │  Next.js App (Edge/Node)    │     │  Python Serverless Function          │     │
│  │  /                          │     │  /api/agent/stream  (FastAPI/ASGI)   │     │
│  │  - Chat UI                  │     │                                      │     │
│  │  - Dashboard renderers      │SSE  │  ClaudeSDKClient                     │     │
│  │    (Plotly, tables, KPI)    │────▶│    └── in-process MCP server         │     │
│  │  - Message history in       │     │          ├── list_tables             │     │
│  │    localStorage             │     │          ├── describe_table          │     │
│  └─────────────────────────────┘     │          ├── query_sql               │     │
│           ▲                          │          ├── run_pandas              │     │
│           │ stream JSON events       │          └── create_chart            │     │
│           │                          │                 │                    │     │
│           │                          └─────────────────┼────────────────────┘     │
│           │                                            │ @vercel/sandbox         │
│           │                                            ▼                          │
│           │                          ┌──────────────────────────────────────┐     │
│           │                          │  Vercel Sandbox (Firecracker µVM)    │     │
│           └──────── UI events ◀──────│  python3.13 + pandas + plotly        │     │
│                                      │  executes agent-generated code       │     │
│                                      │  returns JSON {type, payload}        │     │
│                                      └──────────────────────────────────────┘     │
│                                                                                   │
│  Bundled data: /data/sabi_synth.duckdb  (generated at build time)                 │
└───────────────────────────────────────────────────────────────────────────────────┘
```

**Key decisions**

- **Python backend on Vercel serverless** (user choice). The Python Agent SDK bundles its own Claude Code binary; Vercel's Python 3.12 runtime on Linux x86_64 is compatible.
- **In-process MCP server**, not external stdio/HTTP. One file, one import — easy to teach. Tools live in `api/mcp_tools.py`. Agent connects via `ClaudeAgentOptions(mcp_servers={"analysis": create_sdk_mcp_server(...)})`.
- **Vercel Sandbox** spawned from each code-executing tool (`query_sql`, `run_pandas`, `create_chart`). The dataset is uploaded into the sandbox on first use per session and cached via the sandbox's writable FS. Sandbox calls made via the `@vercel/sandbox` Python SDK.
- **Dashboard rendering**: MCP tools return structured JSON (`{type: "chart"|"table"|"kpi"|"text", payload: ...}`); the frontend inspects tool results on the SSE stream and renders the right React component inline with the message.
- **Session management**: stateless per request. Frontend owns the conversation; each request POSTs full history. This matches Vercel serverless and is the simplest thing that works for a class.

## Synthetic dataset — `sabi_synth`

Based on `/Users/greatmaster/Downloads/schema_blueprint.md`. Generated once at build time by `scripts/generate_dataset.py` into `data/sabi_synth.duckdb` (DuckDB = single file, fast analytical queries, SQL-compatible, pandas-friendly). Keep the table names from the blueprint so the class can map docs → code.

**Scope** (subset — skip the 300-column balance-sheet detail; keep the teaching signal high):

- `nif` — 150 Portuguese companies (name, `n_contribuinte`, `distrito`, `concelho`, CAE sector code, `ultimo_ano_disponivel`=2025)
- `main_financials` — 5-year wide pivot (`_0`..`_4`) for revenue, margins, EBITDA, net income, headcount, exports, total assets, equity, debt
- `fse` — 5-year operating expenses by category (subset of ~8 categories: subcontratos, publicidade, honorarios, energia, rendas, seguros, conservacao, servicos_especializados)
- `ownership` — a few shareholder rows per company
- `subsidiaries` — partial parent→child graph (~30% of companies own another)
- `hubspot` — CRM deals (pipeline stage, amount, close date) joined on `contribuinte`

**Synthetic generator design** — `scripts/generate_dataset.py`:
- Use `faker` for names/addresses (pt_PT locale), `numpy` for log-normal revenue, sector-typical EBITDA margins, random-walk YoY growth with occasional shocks.
- Ensure intentionally interesting patterns the agent can find: one sector in decline, one company with big debt-to-equity, a few with recent revenue jumps from HubSpot deals closing, regional concentration in Lisboa/Porto.
- Commit the generated `.duckdb` file to the repo (small, deterministic with fixed seed, simpler than regenerating in CI).

## Repository layout

```
data-analysis-chat-agent/
├── app/                               # Next.js App Router
│   ├── page.tsx                       # Chat page
│   ├── layout.tsx
│   └── api/agent/stream/route.ts      # Thin proxy → Python function (or direct)
├── api/                               # Vercel Python serverless functions
│   ├── agent.py                       # FastAPI app: POST /api/agent/stream (SSE)
│   ├── mcp_tools.py                   # create_sdk_mcp_server + @tool definitions
│   ├── sandbox_exec.py                # @vercel/sandbox wrapper: run_code(code, dataset_path)
│   └── requirements.txt               # claude-agent-sdk, fastapi, vercel-sandbox, duckdb, pydantic
├── components/
│   ├── Chat.tsx                       # Message list + input
│   ├── MessageRenderer.tsx            # Switches on tool-result type → Chart/Table/KPI
│   ├── ChartCard.tsx                  # Plotly.js (react-plotly.js)
│   ├── TableCard.tsx                  # AG Grid or simple HTML table
│   └── KPICard.tsx
├── data/
│   └── sabi_synth.duckdb              # Generated; committed
├── scripts/
│   └── generate_dataset.py            # One-shot synthetic data generator
├── vercel.json                        # Python runtime config, function regions
├── package.json
└── README.md                          # Student instructions
```

## MCP server — `api/mcp_tools.py` (teaching core)

Five tools, decorated with `@tool`, registered via `create_sdk_mcp_server(name="analysis", tools=[...])`. Tool results return typed dicts that the frontend can dispatch on.

| Tool | Input | Output | Where code runs |
|---|---|---|---|
| `list_tables` | — | `{type:"text", tables:[{name, columns[], row_count}]}` | In-process (cheap metadata read) |
| `describe_table` | `table_name` | `{type:"table", payload:{schema, sample_rows, stats}}` | In-process |
| `query_sql` | `sql` (SELECT-only, validated) | `{type:"table", payload:{columns, rows}}` | **Vercel Sandbox** |
| `run_pandas` | `code` (Python snippet operating on `df` dict of DataFrames) | `{type:"text" or "table", payload:...}` | **Vercel Sandbox** |
| `create_chart` | `data` (from prior tool), `spec` (chart_type, x, y, color, title) | `{type:"chart", payload: <Plotly JSON figure>}` | **Vercel Sandbox** |

**Why five, why this split:**
- `list_tables` + `describe_table` are cheap, safe, run in-process — teaches that not every tool needs a sandbox.
- `query_sql` is the agent's primary workhorse (DuckDB is fast, SQL is the natural language for this data). Validate with `sqlglot` to reject non-SELECT.
- `run_pandas` handles what SQL can't easily (melting wide years → long, complex transforms). Pure pandas, no `eval`/`exec` leakage because it runs in the Sandbox microVM.
- `create_chart` takes a tabular payload + a JSON spec and returns a full Plotly figure JSON. The agent never writes plotting code directly — keeps charts consistent, teaches how to design narrow tool contracts.

**Agent system prompt** (concise, in `api/agent.py`): explains the dataset schema, lists tables, tells the agent to always end with a chart when the user asks a "show me" question, keep tool inputs small, and always prefer `query_sql` over `run_pandas` when possible.

**Tool allowlist** (per MCP docs): `allowed_tools=["mcp__analysis__*"]` — no built-in Bash/Read/Write tools exposed.

## Vercel Sandbox integration — `api/sandbox_exec.py`

One reusable function: `run_in_sandbox(code: str, timeout_s: int = 30) -> dict`.

- Uses `@vercel/sandbox` Python SDK (per https://vercel.com/docs/vercel-sandbox — `python3.13` runtime).
- On first tool call per session, the sandbox is created and the DuckDB file + a small `runner.py` harness are uploaded. Sandbox ID is cached in a module-level dict keyed by `session_id` (serverless instance warm-reuse; fresh sandbox if cold).
- Harness protocol: write `code` to `/vercel/sandbox/user_code.py`, execute with a wrapper that captures `stdout` JSON, enforces timeout, and returns stderr on failure.
- Sandboxes are ephemeral — explicit cleanup on session end via a small `/api/agent/cleanup` endpoint the frontend calls on unmount/`beforeunload`. Idle sandboxes also time out on Vercel's side.

**Auth**: `VERCEL_OIDC_TOKEN` is auto-injected in production; for local dev, `vercel link && vercel env pull` gets a dev token.

## Frontend — dashboard-in-chat rendering

- `components/MessageRenderer.tsx` iterates over an assistant message's content blocks. For each `tool_use` → `tool_result` pair, parse the result JSON and dispatch:
  - `type: "chart"` → `<ChartCard>` with `react-plotly.js` consuming the Plotly figure JSON verbatim.
  - `type: "table"` → `<TableCard>` (paginated, up to 500 rows, ellipsize wide tables).
  - `type: "kpi"` → `<KPICard>` (big number + delta + label).
  - `type: "text"` → rendered inline as monospace block.
- Text content from the assistant renders as markdown between cards, giving the "dashboard in a chat" feel.
- Stream via SSE: the Python backend emits `data: {"type":"delta","text":"..."}` for assistant text and `data: {"type":"tool_result", ...}` for tool results; frontend appends in order.
- No auth, no DB — history lives in `localStorage` keyed by session UUID. A "New chat" button clears it.

## API route — `api/agent.py`

```
POST /api/agent/stream
body: { session_id: str, messages: [{role, content}] }
response: text/event-stream
```

Implementation sketch:
- FastAPI + `sse_starlette`.
- Build `ClaudeAgentOptions` with `mcp_servers={"analysis": <server>}`, `allowed_tools=["mcp__analysis__*"]`, `system_prompt=...`, `max_turns=10`.
- Use `ClaudeSDKClient` in streaming mode; forward SDK messages to SSE as they arrive. For `AssistantMessage` text blocks stream deltas; for tool-result JSON pass through.
- On error / finish, emit a terminal `done` event.

## Security (from the secure-deployment doc, scoped for a class demo)

- **All agent-generated code runs in Vercel Sandbox (Firecracker).** The backend never executes agent code directly — addresses the "lethal trifecta" for this app.
- **SQL allowlist**: `sqlglot.parse(sql).find(exp.DDL|exp.DML_not_select)` → reject. Belt-and-suspenders even though it's running in a sandbox.
- **Tool allowlist**: only `mcp__analysis__*`. No `Bash`, `Read`, `Write`, `WebFetch`.
- **No user uploads** in v1 — eliminates an ingestion attack surface.
- **API key**: `ANTHROPIC_API_KEY` set as a Vercel Environment Variable, only available to the Python function.
- Document in README what would change for multi-tenant production (per-user sandbox quotas, credential proxy, rate limiting, prompt-injection logging).

## Deployment

1. `vercel link` the repo.
2. Set env vars: `ANTHROPIC_API_KEY`. `VERCEL_OIDC_TOKEN` is auto-provided.
3. `vercel.json`:
   ```json
   {
     "functions": {
       "api/agent.py": { "runtime": "python3.12", "maxDuration": 300, "memory": 1024 }
     }
   }
   ```
4. `vercel --prod`. Frontend and Python function deploy together.

## Known limits (flag in README, not hidden)

- **Cold starts** on the Python function (~1–2s). First chart in a fresh session also pays sandbox-create cost (~hundreds of ms).
- **Serverless timeout** capped at 300s (Pro) / 60s (Hobby). `max_turns=10` keeps runs bounded; long analyses may hit this.
- **No cross-request state**. If the serverless instance is evicted between turns, the sandbox ID cache is lost and the next tool call creates a fresh sandbox (and re-uploads the dataset). Acceptable for a demo.
- **Dataset is bundled in the deploy**. ~5–20 MB DuckDB file is fine; don't use this pattern for real data.

## Build sequence

1. **Scaffold repo** — `npx create-next-app@latest`, add `app/api/agent/stream/route.ts` as a pass-through, add `vercel.json`.
2. **Generate data** — write `scripts/generate_dataset.py`, run once, commit `data/sabi_synth.duckdb`.
3. **MCP server** — `api/mcp_tools.py` with the five tools. Start with in-process DuckDB; stub `run_in_sandbox` to also run in-process. Verify agent works end-to-end locally via `claude-agent-sdk` CLI or a small Python harness.
4. **Vercel Sandbox wrapper** — `api/sandbox_exec.py`. Swap the stub. Verify one round-trip (sandbox boot → upload DB → run trivial pandas → return JSON).
5. **FastAPI + SSE endpoint** — `api/agent.py`. Stream SDK messages as SSE.
6. **Frontend chat UI** — `components/Chat.tsx` + `MessageRenderer.tsx`. Wire SSE consumption.
7. **Dashboard renderers** — `ChartCard` (react-plotly.js), `TableCard`, `KPICard`. Style with Tailwind.
8. **Deploy** to Vercel preview; verify end-to-end; promote to prod.
9. **README for students** — architecture diagram, how each doc link maps to a file, local dev setup, "try these prompts" list.

## Verification (end-to-end)

Local (`vercel dev`):
- [ ] `POST /api/agent/stream` with `"List the available tables."` → SSE stream ends with a tool result from `list_tables` naming the six tables.
- [ ] `"Show me the top 10 companies by 2025 revenue as a bar chart."` → agent calls `query_sql` then `create_chart`; frontend renders a Plotly bar chart inline.
- [ ] `"Compare EBITDA margin across sectors over 5 years."` → agent calls `run_pandas` (melt wide years), then `create_chart` (line chart). Dashboard shows a multi-series line.
- [ ] Invalid SQL (`DROP TABLE nif`) → `query_sql` returns a validation error; agent recovers and explains.
- [ ] Break the network to `api.anthropic.com` in dev → SSE surfaces the error cleanly.

Deployed (Vercel prod):
- [ ] Same three prompts work from the public URL.
- [ ] Check Vercel function logs show MCP tool calls + sandbox invocations.
- [ ] Cold-start first prompt completes under 300s.
- [ ] `VERCEL_OIDC_TOKEN` picked up automatically; no explicit token in code.

## Critical files to create

- `scripts/generate_dataset.py`
- `api/mcp_tools.py` ← **primary teaching artifact**
- `api/sandbox_exec.py`
- `api/agent.py`
- `api/requirements.txt`
- `app/page.tsx`, `app/api/agent/stream/route.ts`
- `components/Chat.tsx`, `components/MessageRenderer.tsx`, `components/ChartCard.tsx`, `components/TableCard.tsx`, `components/KPICard.tsx`
- `vercel.json`
- `README.md`

## Reused references

- `schema_blueprint.md` → dataset design (table names, 5-year pivot convention, relationships).
- Claude Agent SDK Python docs — `ClaudeSDKClient`, `ClaudeAgentOptions`, `create_sdk_mcp_server`, `allowed_tools` pattern.
- Vercel Sandbox Python SDK — `@vercel/sandbox` create/upload/exec.
- Hosting doc — "Ephemeral Sessions" pattern maps to our per-request function + per-session sandbox.
- Secure Deployment doc — tool allowlist, sandbox-for-code-exec, no credential exposure to agent.
