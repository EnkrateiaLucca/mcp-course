# Demo 06 — Data Analysis Agent with Gradio + Claude Agent SDK + Vercel

A Gradio chat UI backed by the **Claude Agent SDK** with an **in-process MCP server** for data analysis. Ask questions about a dataset in plain English — the agent picks the right tool, runs it, and renders tables and plots inline in the chat.

## Architecture

```
User → Gradio ChatInterface
           ↓
       chat_fn (async generator)
           ↓
       ClaudeSDKClient (Claude Agent SDK)
           ↓
       In-process MCP server ("analysis")
           ↓
       Tools operate on pandas DataFrame (tips dataset)
           ↓
       Text  → returned via tool result → rendered as markdown
       Plots → saved to /tmp → pushed to artifact queue → rendered as gr.Image
```

**Key design decisions:**
- **In-process MCP** via `create_sdk_mcp_server` — no subprocess, no HTTP, tools run in the same Python process
- **Side-channel artifacts** — plots travel outside MCP (which is text-only) via a module-level `_ARTIFACTS` list drained between messages
- **ALLOWED_TOOLS whitelist** — skips per-tool permission prompts, required for Vercel

## Available Tools

| Tool | What it does |
|---|---|
| `describe_data` | pandas `.describe()` summary stats |
| `show_head` | First N rows as a markdown table |
| `column_info` | Dtypes, non-null counts, unique values per column |
| `group_aggregate` | GroupBy + aggregate (mean / sum / count / median / min / max / std) |
| `correlation_matrix` | Heatmap + numeric correlation table |
| `plot_data` | bar, line, scatter, hist, or box plot |

## Project Structure

```
06-deploy-simple-agent-mcp-vercel/
├── main.py           # Gradio app + MCP tools + Claude Agent SDK
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

Open **http://localhost:7860** in your browser.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key — get one at https://console.anthropic.com |

## Example Prompts

- "Describe the dataset"
- "Show me the first 10 rows"
- "What's the average tip by day of the week?"
- "Plot a histogram of total_bill"
- "Show a scatter plot of total_bill vs tip"
- "Create a bar chart of average tip by day"
- "Show the correlation matrix"
- "Box plot of total_bill by smoker status"

## Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Add your Anthropic API key as a secret
vercel env add ANTHROPIC_API_KEY

# Deploy
vercel --prod
```

The `vercel.json` routes all traffic to `main.py`, which exports `app = demo.app` as the ASGI handler.

> **Note:** Vercel's hobby plan has a 10s function timeout. The Claude Agent SDK calls can take longer — upgrade to Pro (60s timeout) for reliable production use.

## Tech Stack

- **AI:** Claude (via Claude Agent SDK)
- **MCP:** In-process MCP server (`create_sdk_mcp_server`)
- **UI:** Gradio 5.x (`gr.ChatInterface`)
- **Data:** pandas, seaborn, matplotlib
- **Deployment:** Vercel (ASGI / `@vercel/python`)

## Troubleshooting

**`ANTHROPIC_API_KEY not set`** — Copy `.env.example` to `.env` and add your key, then restart.

**Gradio deprecation warnings** — Safe to ignore; they relate to Gradio 6.0 API changes that don't affect functionality with the pinned `<6.0.0` version.

**Plot not rendering** — Make sure `matplotlib` is installed (`pip install matplotlib seaborn`).

## Learn More

- [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [Gradio Docs](https://www.gradio.app/docs)
- [Vercel Python Runtime](https://vercel.com/docs/functions/runtimes/python)
