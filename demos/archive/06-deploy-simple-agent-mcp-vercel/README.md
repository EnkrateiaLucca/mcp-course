# Data Analysis Chat Agent

A teaching reference app for the **Claude Agent SDK** course. A chat UI analyzes
a bundled synthetic Portuguese SME dataset and renders results as inline charts,
tables, and KPI cards — a "dashboard in a chat".

The app demonstrates, end-to-end:

1. **Claude Agent SDK (Python)** as the agent core.
2. A **custom in-process MCP server** (`create_sdk_mcp_server`) as the *only*
   tool surface — the teaching focus of the course.
3. **Vercel Sandbox** (Firecracker microVM) as the secure execution layer for
   agent-generated pandas/matplotlib/plotly code.
4. Full deploy to Vercel (Next.js frontend + Python serverless function).

## Architecture at a glance

```
 Browser ──SSE── /api/agent/stream (Python) ──► ClaudeSDKClient
                                                 └── analysis MCP server
                                                      ├── list_tables        (in-proc)
                                                      ├── describe_table     (in-proc)
                                                      ├── query_sql          ─┐
                                                      ├── run_pandas         ─┤ Vercel Sandbox
                                                      └── create_chart       ─┘
```

## Repository map

| Path | What / why |
|------|-----------|
| `api/mcp_tools.py` | **The teaching core.** Five tools; typed-dict outputs. |
| `api/sandbox_exec.py` | `run_in_sandbox()` — Vercel Sandbox in prod, subprocess fallback locally. |
| `api/agent.py` | FastAPI `/api/agent/stream` (SSE) and `/cleanup` endpoints. |
| `scripts/generate_dataset.py` | Deterministic synthetic data → `data/sabi_synth.duckdb`. |
| `components/Chat.tsx` | Chat UI + SSE consumer. |
| `components/MessageRenderer.tsx` | Dispatches tool results to renderers by `type`. |
| `components/{Chart,Table,KPI}Card.tsx` | Dashboard card primitives. |
| `vercel.json` | Routes `/api/agent/*` → `api/agent.py` Python function. |

## Dataset — `sabi_synth`

6 tables modeled on `schema_blueprint.md`, with English column and table names
(proper nouns like company names and districts stay in Portuguese):

- `companies` — 150 Portuguese SMEs (name, tax_id, district, municipality, sector)
- `main_financials` — 5-year wide pivot (`_0`..`_4`): revenue, gross_margin, ebitda, net_income, employees, exports, total_assets, equity, total_liabilities
- `operating_expenses` — 8 opex categories (subcontracting, advertising, professional_fees, energy, rent, insurance, maintenance, specialized_services), 5-year pivot
- `ownership` — 1–4 shareholders per company
- `subsidiaries` — ~30% of companies own another
- `hubspot` — CRM deals, joined on `tax_id`

All tables join on `tax_id`. Seeded with intentional signal: one sector in
decline, one over-leveraged company (`Leverage Example SA`), a few export
outliers, regional concentration in Lisboa/Porto.

## Local setup

Requirements: Node 20+, Python 3.12+, `uv`, the Vercel CLI.

```bash
# 1. Install deps
npm install

# 2. Generate the dataset (already committed, but regenerate anytime)
uv run scripts/generate_dataset.py

# 3. (Optional) pull Vercel env vars — skips the in-process sandbox fallback
vercel link
vercel env pull .env.local

# 4. Run the dev server
#    - If you have VERCEL_OIDC_TOKEN: sandboxed code execution
#    - Otherwise: set ALLOW_INPROCESS_SANDBOX=1 for in-process subprocess exec
ANTHROPIC_API_KEY=... ALLOW_INPROCESS_SANDBOX=1 vercel dev
```

Open http://localhost:3000.

## Try these prompts

- “List the available tables.”
- “Show me the top 10 companies by 2025 revenue as a bar chart.”
- “Compare EBITDA margin across sectors over 5 years as a line chart.”
- “Which sector is in decline? Show me a chart.”
- “Find companies with the highest debt-to-equity ratio.”
- “Total HubSpot deal amount by pipeline stage.”

## How each piece maps to the course docs

- **`api/mcp_tools.py`** — `create_sdk_mcp_server`, `@tool`, typed-dict outputs
  → maps to the *Custom Tools via MCP* section of the course.
- **`api/agent.py` — system prompt + `allowed_tools=["mcp__analysis__*"]`** —
  the tool-allowlist pattern from *Agent Permissions*.
- **`api/sandbox_exec.py`** — Firecracker isolation pattern from *Secure
  Deployment* ("sandbox-for-code-exec").
- **Stateless per-request + per-session sandbox** — maps to *Ephemeral Sessions*
  in the hosting docs.

## Security posture (demo scope)

- All agent-generated code runs inside Vercel Sandbox (Firecracker microVM).
- `query_sql` validates via `sqlglot` AST — only `SELECT` allowed.
- Tool allowlist: only `mcp__analysis__*`. No `Bash`, `Read`, `Write`, or `WebFetch`.
- No user uploads. The dataset is bundled into the deploy.
- `ANTHROPIC_API_KEY` is server-side only; `VERCEL_OIDC_TOKEN` is auto-injected.

**Not production-ready as-is.** A real deployment would add: per-user sandbox
quotas, a credential proxy, rate limiting, prompt-injection logging, and a
full audit trail. See `plan.md` for the full list.

## Deploy

```bash
vercel link       # once
vercel env add ANTHROPIC_API_KEY
vercel --prod
```

Vercel auto-injects `VERCEL_OIDC_TOKEN` in production. No other secrets needed.

## Known limits

- **Cold start** ~1–2s on the Python function. First chart in a fresh session
  pays an extra ~500ms for sandbox boot + dataset upload.
- **Serverless timeout** capped at 300s (Pro) / 60s (Hobby). `max_turns=10`
  keeps runs bounded.
- **No cross-request state.** If the function is evicted, the sandbox cache is
  lost; next tool call boots a fresh sandbox.
- **Bundled dataset** (~2 MB). Don't use this pattern for real data — ship it
  to Vercel Blob / a DB instead.
