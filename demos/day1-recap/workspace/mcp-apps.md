# MCP Apps — Brief

## What they are

MCP Apps is the first official MCP extension (identifier `io.modelcontextprotocol/ui`, SEP-1865). It lets an MCP server ship an interactive HTML UI alongside a tool. The host renders that UI inline in the conversation inside a sandboxed iframe. Plain tools return text and structured data; MCP Apps cover the cases that need a chart, form, canvas, dashboard, or player.

## Timeline

- **Nov 2025** — SEP-1865 proposed. Anthropic, OpenAI, and the MCP-UI maintainers unified MCP-UI and the OpenAI Apps SDK into one open standard.
- **Jan 26, 2026** — Went live as an official extension (spec revision `2026-01-26`). Claude, ChatGPT, Goose, and VS Code shipped host support.
- **Jul 28, 2026** — Referenced as a named extension in the 2026-07-28 core spec release. Tools declare UI templates ahead of time so hosts can prefetch, cache, and security-review them.

## How it works

1. **Declare.** A tool carries `_meta.ui.resourceUri` pointing at a `ui://…` URI.
2. **Serve.** The server exposes that URI as a resource with MIME type `text/html;profile=mcp-app`. That exact MIME type tells the host "render this as an app."
3. **Negotiate.** The client advertises support in `initialize` via the extension identifier `io.modelcontextprotocol/ui`.
4. **Render.** When the tool is called, the host loads the HTML into a sandboxed iframe.
5. **Handshake.** The view sends `ui/initialize`; the host replies with host context and capabilities; the view sends `ui/notifications/initialized`.
6. **Talk.** View and host exchange MCP JSON-RPC messages over `postMessage`. Shared methods include `tools/call`; new ones use the `ui/` prefix (`ui/update-model-context` pushes state into the model's context, `ui/message`, `ui/open-link`).

The bridge reuses the standard `@modelcontextprotocol/sdk`, so UI code needs no bespoke protocol.

## Security model

- The iframe sandbox blocks access to the parent DOM, host cookies, host `localStorage`, and parent navigation.
- Web hosts must use a double-iframe pattern: an intermediate sandbox proxy on a separate origin loads the view with a restrictive CSP and forwards protocol messages.
- The server can declare a CSP for the resource. Outbound API calls still need CORS on the API side.
- Pre-declared templates let hosts review UI before any tool runs.

## SDKs

- **TypeScript:** `@modelcontextprotocol/ext-apps` (v1.1.x). `registerAppTool` / `registerAppResource` on the server; `App` class on the view side. Node 20+.
- **Python (official SDK v2):** `mcp.server.apps` — `apps.add_html_resource("ui://clock/app.html", HTML)` registers the resource with the right MIME type; `@mcp.tool()` options pass through.
- **MCP-UI** (`@mcp-ui/server`) interoperates via the same `_meta.ui.resourceUri` link.

## Host support (Sep 2026)

Claude (Desktop and web), ChatGPT, Goose, VS Code. Claude Code CLI does not render apps; the terminal is text-only.

## Relevance to this course (module 05)

`demos/05-deploy-remote-mcp/` already implements the pattern on the v2 SDK (`mcp>=2.3,<3`): the tool sets `meta={"ui": {"resourceUri": "ui://..."}}`, `app.html` is served with `mime_type="text/html;profile=mcp-app"`, and the vanilla-JS handshake uses protocol version `2026-01-26`. The v2 SDK's `apps.add_html_resource` helper could replace the hand-written resource registration.

## Sources

- https://modelcontextprotocol.io/extensions/apps/overview
- https://modelcontextprotocol.io/seps/1865-mcp-apps-interactive-user-interfaces-for-mcp
- https://github.com/modelcontextprotocol/ext-apps/blob/main/specification/2026-01-26/apps.mdx
- https://blog.modelcontextprotocol.io/posts/2025-11-21-mcp-apps/
- https://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/
- https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/
- https://apps.extensions.modelcontextprotocol.io/api/
- https://py.sdk.modelcontextprotocol.io/advanced/apps/
- https://sunpeak.ai/docs/mcp-apps/security
- https://www.theregister.com/2026/01/26/claude_mcp_apps_arrives/
