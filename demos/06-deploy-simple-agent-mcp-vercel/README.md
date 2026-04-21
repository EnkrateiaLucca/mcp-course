# Demo 06 — Data Analysis Agent with FastAPI + Claude Agent SDK + Vercel

A chat UI backed by the **Claude Agent SDK** with an **in-process MCP server** for data analysis. Ask questions about a synthetic Portuguese company dataset in plain English — the agent picks the right tool, runs it, and renders tables and plots inline in the chat.

## Architecture

```
User → HTML/JS (SSE client)
           ↓  POST /chat
       FastAPI
           ↓
       ClaudeSDKClient (Claude Agent SDK)
           ↓
       In-process MCP server ("analysis")
           ↓
       Tools operate on pandas DataFrame (250 Portuguese companies)
           ↓
       Text  → SSE text events → rendered as markdown
       Plots → base64 PNG → SSE image events → rendered as <img>
```

**Key design decisions:**
- **In-process MCP** via `create_sdk_mcp_server` — no subprocess, no HTTP, tools run in the same Python process
- **SSE streaming** — agent responses stream token-by-token to the browser via Server-Sent Events
- **Base64 plots** — images encoded inline, no temp file disk dependency
- **ALLOWED_TOOLS whitelist** — skips per-tool permission prompts

## Available Tools

| Tool | What it does |
|---|---|
| `describe_data` | pandas `.describe()` summary stats |
| `show_head` | First N rows as a markdown table |
| `column_info` | Dtypes, non-null counts, unique values per column |
| `group_aggregate` | GroupBy + aggregate (mean / sum / count / median / min / max / std) |
| `correlation_matrix` | Heatmap + numeric correlation table |
| `plot_data` | bar, line, scatter, hist, or box plot |

## Dataset

Synthetic dataset of **250 Portuguese companies** based on the `sabi_hubspot` schema (`main_financials` table). Columns: `company_name`, `region`, `sector`, `sector_code`, `size`, `status`, `revenue`, `ebitda`, `ebit`, `net_profit`, `total_assets`, `equity`, `employees`, `exports`.

## Project Structure

```
06-deploy-simple-agent-mcp-vercel/
├── main.py           # FastAPI app + MCP tools + Claude Agent SDK
├── requirements.txt  # Python dependencies
├── vercel.json       # Vercel routing config
├── .env.example      # Environment variable template
└── README.md         # This file
```

## Quick Start (local)

### 1. Set up environment

```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

### 2. Run with UV (recommended)

```bash
uv run main.py
```

### 3. Run with pip

```bash
pip install -r requirements.txt
python main.py
```

Open **http://localhost:8000** in your browser.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key — get one at https://console.anthropic.com |

## Example Prompts

- "Describe the dataset"
- "Show me the first 10 companies"
- "What is the average EBITDA by sector?"
- "Plot a histogram of revenue"
- "Scatter plot of revenue vs net_profit"
- "Which region has the highest average revenue?"
- "Show the correlation matrix"
- "Box plot of ebitda by size"

## Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel
# or with mise:
mise use -g npm:vercel

# Login
vercel login

# Link project and add your API key
vercel link
vercel env add ANTHROPIC_API_KEY production --value YOUR_KEY_HERE --yes

# Deploy
vercel --prod
```

> **Note:** Vercel's hobby plan has a 10s function timeout. The Claude Agent SDK initialization can exceed this on cold starts — the app will show a friendly retry message. Upgrade to Vercel Pro (60s timeout) for reliable production use.

## Tech Stack

- **AI:** Claude (via Claude Agent SDK)
- **MCP:** In-process MCP server (`create_sdk_mcp_server`)
- **UI:** Vanilla HTML + JavaScript (SSE streaming)
- **Data:** pandas, numpy, matplotlib
- **Deployment:** Vercel (`@vercel/python` ASGI runtime)

## Troubleshooting

**`ANTHROPIC_API_KEY not set`** — Copy `.env.example` to `.env` and add your key, then restart.

**"Agent timed out during initialization"** — This is Vercel's hobby plan 10s limit hitting during a cold start. Try again immediately (warm instance) or upgrade to Vercel Pro for the 60s timeout.

**Plot not rendering** — Make sure `matplotlib` is installed (`pip install matplotlib`).

## Learn More

- [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Vercel Python Runtime](https://vercel.com/docs/functions/runtimes/python)
