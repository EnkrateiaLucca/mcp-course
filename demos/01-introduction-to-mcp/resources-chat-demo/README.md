# MCP Resources Chat Demo

A minimal example of **MCP resources** (read-only context, vs. tools which are
actions) wired into a tiny chat UI.

## Architecture

```
┌─────────────┐   stdio    ┌──────────────────┐
│ chat_app.py │ ─────────► │  mcp_server.py   │
│  (FastAPI)  │            │ (4 docs as       │
│             │            │  resources)      │
└──────┬──────┘            └──────────────────┘
       │ Anthropic API
       ▼
   Claude (sonnet-4-5)
```

The browser UI:
1. Lists every resource the MCP server exposes.
2. Lets you pick which ones go into the model's context.
3. On send, the server reads the selected resources via the MCP client
   session and injects them into Claude's system prompt.

## Run

```bash
export ANTHROPIC_API_KEY=sk-ant-...
uv run chat_app.py
```

Then open http://127.0.0.1:8770

## Try it

- All resources checked → "What's the warranty on the RS-9?"
- Uncheck *Product Specs* → ask the same → model will say it doesn't know.
- Check only *Pricing* → "How much for 12 standard anvils?"
