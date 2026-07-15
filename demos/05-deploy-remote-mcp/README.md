# Demo 05 — Deploy a remote MCP server (+ your first MCP App)

The 2026 deployment story is **not** "wrap your agent in FastAPI." It's:
deploy the **MCP server itself**, and let every host connect to it —
Claude (web/desktop), Claude Code, Cursor, ChatGPT. One server, many hosts.
That's the M×N payoff from demo 01, now over the public internet.

This demo also ships an **MCP App** — the first official MCP extension
(Jan 2026): the `research_explorer` tool carries a `ui://` resource in its
`_meta`, and hosts that support Apps render it as an interactive panel
*inside the chat*.

```
                        ┌──────────────────────────────┐
   Claude (web/desktop) │                              │
   Claude Code          │   research-explorer server   │
   Cursor        ─────▶ │   streamable HTTP, stateless │
   MCP Inspector        │   /mcp                       │
                        │   tools: research_explorer*  │
                        │          quick_search        │
                        │   *renders as an MCP App     │
                        └──────────────────────────────┘
```

## Files

- `server.py` — FastMCP server, `stateless_http=True` + `json_response=True`
  (serverless-friendly; also where the 2026-07-28 spec is headed: a stateless
  protocol core). Declares the MCP App via `meta={"ui": {"resourceUri": ...}}`.
- `app.html` — the MCP App view. Implements the postMessage handshake
  (`ui/initialize` → `initialized` → `tool-result`) in ~50 lines of vanilla
  JS so you can see the protocol with no SDK.
- `test_client.py` — pre-flight check: tools, `_meta.ui.resourceUri`, the
  `ui://` resource, and a live tool call. **Run this before class.**
- `api/index.py`, `vercel.json`, `requirements.txt` — Vercel wrapping.

## 1 · Run locally

```bash
cd demos/05-deploy-remote-mcp
uv run server.py                 # → http://127.0.0.1:8000/mcp

# in another terminal — pre-flight
uv run test_client.py
```

## 2 · Connect hosts to it

**Claude Code** (local URL works directly):

```bash
claude mcp add research-explorer --transport http http://127.0.0.1:8000/mcp
```

**Claude web/desktop** needs a public URL. Tunnel first:

```bash
npx cloudflared tunnel --url http://localhost:8000
```

Then Claude → Settings → Connectors → **Add custom connector** → paste
`https://<random>.trycloudflare.com/mcp`. Ask Claude to
*"use research_explorer to research MCP Apps"* — the interactive panel
renders in the conversation. Click a card; refine the search from inside
the app (the app calls `tools/call` back through the host).

## 3 · Deploy to Vercel

```bash
cd demos/05-deploy-remote-mcp
vercel deploy --prod
# then verify:
uv run test_client.py https://<your-app>.vercel.app/mcp
```

Add the production URL as a custom connector the same way. Same server,
now permanent.

## Auth note (important, and intentional)

Claude's custom-connector UI supports **OAuth or no auth** — there is no
field for a bearer header. So this server is open by default; set
`MCP_AUTH_TOKEN` to require a bearer token for clients that *can* send
headers (Claude Code, the Agent SDK, demo 04's agent). The real production answer is OAuth 2.1 with Client ID Metadata
Documents — see demo 04's README for the full auth story.

## What to notice

- **No FastAPI, no SSE plumbing** — `mcp.streamable_http_app()` IS the web
  app. Compare with the archived demo (`demos/archive/06-…-vercel/`) that
  wrapped an agent in FastAPI+SSE: ~10× the code for a worse outcome.
- **Stateless by construction** — any replica can serve any request. The
  2026-07-28 spec revision bakes this into the protocol core (no
  `initialize` handshake, no `Mcp-Session-Id`).
- **The App is just a tool + a resource** — two primitives you already
  know, linked by `_meta`. The host does the sandboxing and the
  postMessage bridge.
