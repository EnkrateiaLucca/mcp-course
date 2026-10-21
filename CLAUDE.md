# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

O'Reilly Live Training course repo: **"Building AI Agents with MCP: From Agent Loop to Production Servers"** (redesigned July 2026; formerly subtitled "The HTTP Moment of AI?"). Hands-on demos for learning the Model Context Protocol and AI agent development.

Six modules. `00`–`03` grow ONE use case — a personal research assistant — a layer at a time: hand-rolled loop (`00`) → MCP server + thin client (`01`) → Claude Agent SDK host (`02`) → skills (`03`). `04` ships a production use case end to end: a shop analytics agent (FastAPI + Agent SDK) and its governed MCP server (read-only SQLite) as two containers (`04`). `05` attacks and defends it: data-exposure lab + tool-poisoning lab + composition/subagents/sessions.

## Development Setup

### Package Manager
- **Primary**: UV. Every script has inline UV metadata headers; run with `uv run <script>.py`.
- Alternative: `python -m venv venv && source venv/bin/activate && pip install -r requirements/requirements.txt`

### Version pins (important, October 2026)
- **`mcp[cli]>=2.3,<3`** everywhere — official SDK v2 (migrated 2026-10-17). `from mcp.server.mcpserver import MCPServer` (v1's `FastMCP` is gone). Transport args (`host`, `port`, `stateless_http`, `json_response`, `transport_security`) go on `run()` / `streamable_http_app()`, not the constructor. Fields are snake_case (`mime_type`, `structured_content`, `input_schema`); `McpError` → `MCPError(code, msg)`; `streamable_http_client` yields `(read, write)`. v2 servers speak 2026-07-28 and still accept 2025-11-25 `initialize` clients. The standalone "FastMCP 3" (PrefectHQ/fastmcp) is a different package; never use it here.
- **`claude-agent-sdk>=0.1.0`** (0.2.x current) — bundles the Claude Code CLI, Python ≥3.10.

### Environment Variables (`.env` at repo root)
- `ANTHROPIC_API_KEY` — all agent demos
- Module 04 has its own `.env` (`demos/04-shop-analytics-agent/.env.example`): only `ANTHROPIC_API_KEY` is required for Docker Compose; `MCP_TOKEN`/`APP_PASSWORD` have loopback-only defaults and MUST be set for any deployment.
- `MCP_AUTH_TOKEN` — the archived research server, still used by `05-security-and-composition/composition/`

## Demo Organization

1. **`00-intro-agents/`** — hand-rolled agent loop, tools as plain Python functions. `basic_personal_agent.py` + teaching notebook. KEEP AS-IS: loop-first pedagogy is intentional (presenter notes are in the notebook).
2. **`01-introduction-to-mcp/`** — same tools behind `MCPServer` (`mcp_server.py`); `mcp_client.py` is a thin, standalone-runnable protocol client. The old hand-rolled host lives in `archive/01-full-host-client/`.
3. **`02-research-agent-sdk/`** — Agent SDK as MCP host (`research_agent.py`, ~15 LOC core); `in_process_agent.py` shows `create_sdk_mcp_server`; `research_agent_multiturn.py` shows `ClaudeSDKClient`.
4. **`03-skills-and-mcp/`** — skills vs MCP teaching module + `mcp-builder-skill/` (agent scaffolds MCP servers) + `skill_loader_demo.py` (SDK skills gotchas).
5. **`04-shop-analytics-agent/`** — `agent/app.py` (FastAPI + Agent SDK: `tools=[]`, `strict_mcp_config`, `setting_sources=[]`, `max_turns`, `max_budget_usd`, MCP status check at init → 503, limit results → friendly reply, `is_error` results → 502, one JSON log line per message with tokens + estimated cost) + `agent/static/index.html` (chat UI, usage footer) + `mcp_server/server.py` (stateless HTTP, bearer middleware, read-only SQLite, `sales` view = the one definition of revenue, `ToolError` for anticipated failures, optional `PII_GUARD` SQLite authorizer) + `compose.yaml` (ports on 127.0.0.1) + `render.yaml`. Each service has its own `pyproject.toml`/`uv.lock` (needed for Docker). Run `cd mcp_server && MCP_TOKEN=test uv run python test_server.py` after ANY server change.
6. **`05-security-and-composition/`** — `data-exposure-lab/` (module 04's `run_sql` leaks names/emails; `PII_GUARD=1` blocks them; `exposure_check.py` is a no-spend MCP client) + `security-lab/` (tool-poisoning attack/defense) + `composition/` (multi-server, subagent via the `Agent` tool, resume/fork sessions; still starts the archived research server).

- **`exercises/link-checker/`** — take-home exercise with reference solution.
- **`archive/`** — retired demos (old 03 tabular, old 04 production research agent, old 05 Vercel deploy + MCP App, old 06 FastAPI+SSE Vercel, full host, OpenAI alternative). `tests/` still covers the archived 04 research server. Do not modify; do not resurrect into the live flow without asking.
- **`assets-resources/`** — cheatsheet, diagrams, security report.

## MCP Server Patterns

**MCPServer, external (stdio or HTTP) — modules 01, 04:**
```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp[cli]>=2.3,<3"]
# ///
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("server-name")          # HTTP servers pass to mcp.streamable_http_app(): stateless_http=True,
                                        # json_response=True, transport_security=TransportSecuritySettings(
                                        #   enable_dns_rebinding_protection=False)  # else 421 behind tunnel/Vercel

@mcp.tool()
def tool_function(param: str) -> dict:
    """Docstring is the LLM-facing description."""
    return {"ok": True}

@mcp.resource("uri://path")
def get_resource() -> str: ...

if __name__ == "__main__":
    mcp.run(transport="stdio")          # or "streamable-http"
```

**In-process via the Agent SDK — module 02b:**
```python
from claude_agent_sdk import create_sdk_mcp_server, tool

@tool("name", "description", {"param": str})
async def fn(args): return {"content": [{"type": "text", "text": "..."}]}

server = create_sdk_mcp_server(name="x", version="1.0.0", tools=[fn])
options = ClaudeAgentOptions(mcp_servers={"x": server})
```

**Remote HTTP with auth — module 04:**
```python
# agent side
options = ClaudeAgentOptions(mcp_servers={
    "analytics": {"type": "http", "url": "http://mcp:8001/mcp",
                  "headers": {"Authorization": f"Bearer {token}"}}
})
```

**MCP App — `archive/05-deploy-remote-mcp`, `mcp-apps-productivity-timer`:** tool declares `meta={"ui": {"resourceUri": "ui://..."}}`; resource at that URI has `mime_type="text/html;profile=mcp-app"` and returns self-contained HTML implementing the `ui/initialize` postMessage handshake (protocol version "2026-01-26").

## Agent Integration Guidelines

- The SDK is an MCP host: `allowed_tools=["mcp__<server>__*"]` for gating (MCP tools are NOT auto-approved by permission modes).
- Subagent tool is named **`Agent`** (renamed from `Task`); subagents run in background by default.
- Sessions are cwd-sensitive: `resume=session_id` silently starts fresh if cwd changed.
- Skills via SDK need `setting_sources=["user","project"]`; SKILL.md `allowed-tools` frontmatter is CLI-only.
- Tool search is ON by default in the SDK — tool definitions are deferred/loaded on demand.
- Hooks: `PreToolUse` to block, `PostToolUse` to log. Permission callback `can_use_tool` for defense in depth.

## When Creating MCP Servers
- UV inline metadata always; descriptive docstrings (the LLM reads them); type hints (schemas auto-generate).
- Prefer **intent-grouped tools** over API mirrors (archived research agent's 7→3; module 04's metric tools + one `run_sql` escape hatch).
- Raise `ToolError` (`mcp.server.mcpserver.exceptions`) for failures the model should read; v2 shows any other exception only as "Error executing tool <name>".
- Test with `mcp dev <server>.py`; module 04 additionally with `test_server.py`.
- Validate paths (workspace sandboxing pattern in modules 01/04); structured dict returns.

## Testing / Verifying

```bash
mcp dev <path-to-server.py>                     # Inspector UI
cd demos/04-shop-analytics-agent && docker compose up --build   # module 04, both containers
claude mcp add research -- uv run $PWD/demos/01-introduction-to-mcp/mcp_server.py
```

Claude Desktop config: macOS `~/Library/Application Support/Claude/claude_desktop_config.json`, Windows `%APPDATA%\Claude\claude_desktop_config.json`. Absolute paths; restart after edits.

## Troubleshooting
- Module 04 "analytics data service is unavailable" (503) → agent and server `MCP_TOKEN` differ, or the MCP server is down. Module 04 502 "model call failed: Invalid API key" → the student's `ANTHROPIC_API_KEY`.
- Archived module 05 → server binds 8000; Claude custom connectors need a public URL (cloudflared tunnel or Vercel) and support OAuth-or-no-auth only (no bearer header field).
- Archived module 05 `421 Misdirected Request` via tunnel/Vercel (localhost works) → the mcp SDK auto-enables DNS-rebinding protection when binding 127.0.0.1 and rejects non-localhost `Host` headers at the origin. `server.py` opts out via `transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False)` — keep that when editing, and pre-flight with `uv run test_client.py <public-url>/mcp` (the localhost pre-flight can't catch this).
- DDGS empty results → throttling; tools degrade gracefully, retry.
- `mcp` not found → `pip install "mcp[cli]>=2.3,<3"`.
- `mcp dev` Inspector shows Failed / "Connection closed" → the Inspector spawns the server in a clean env. Keep `MCPServer(..., dependencies=["mcp[cli]>=2.3,<3", "ddgs"])` on stdio servers (01/02) and keep the `ddgs` import lazy so `mcp dev` can import the module before installing deps.
- Skills extension (module 03) not advertised → v2 only puts `capabilities.extensions` in the 2026-07-28 `server/discover` result; clients must call `session.discover()`, not `initialize()`.

## Additional Resources
- Spec 2026-07-28 (**current revision**, shipped final): https://modelcontextprotocol.io/specification/2026-07-28 — stateless core, extensions framework, MRTR; covered in slides (deck positions 23, 26, 66–68)
- Spec 2025-11-25: https://modelcontextprotocol.io/specification/2025-11-25 — previous revision; v2 servers still accept its `initialize` handshake (module 01's thin client uses it)
- Claude Agent SDK: https://code.claude.com/docs/en/agent-sdk/overview
- MCP Apps extension: https://modelcontextprotocol.io/extensions/apps
- Production post (basis for the archived modules 04–05): https://claude.com/blog/building-agents-that-reach-production-systems-with-mcp
