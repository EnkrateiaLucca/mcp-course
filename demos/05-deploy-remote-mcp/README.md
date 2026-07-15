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
  Also disables FastMCP's DNS-rebinding protection (`transport_security=...`) —
  without this, recent SDK versions reject any non-localhost `Host` header with
  `421 Misdirected Request`, which breaks tunnels and Vercel (see below).
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

**Claude web/desktop** needs a public URL. Tunnel first — cloudflared is
Cloudflare's tunnel client: it gives your localhost server a temporary public
HTTPS URL (no account needed). Install with `brew install cloudflared`
(macOS) or grab a binary from https://github.com/cloudflare/cloudflared/releases —
or skip installing and use `npx cloudflared` as below:

```bash
npx cloudflared tunnel --url http://localhost:8000

# pre-flight THROUGH the tunnel before touching Claude — this is the check
# that catches Host-header/421 problems the localhost pre-flight can't see:
uv run test_client.py https://<random>.trycloudflare.com/mcp
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

## Troubleshooting: 421 Misdirected Request through a tunnel/Vercel

If remote requests fail with `421` / "Invalid Host header" while localhost
works fine: recent versions of the `mcp` SDK auto-enable DNS-rebinding
protection when the server binds to `127.0.0.1`, allowing only localhost
`Host` headers. A tunnel or Vercel hostname then gets rejected **by the
origin** (it looks like a Cloudflare error, but isn't). This server already
opts out in `server.py`:

```python
from mcp.server.transport_security import TransportSecuritySettings

mcp = FastMCP(..., transport_security=TransportSecuritySettings(
    enable_dns_rebinding_protection=False))
```

That's the right call here because this server exists to be reached through
public hostnames (and is open by default anyway — see the auth note). For a
localhost-only server, keep the protection on.

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
