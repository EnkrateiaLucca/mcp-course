# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

O'Reilly Live Training course repo: **"Building AI Agents with MCP: From Agent Loop to Production Servers"** (redesigned July 2026; formerly subtitled "The HTTP Moment of AI?"). Hands-on demos for learning the Model Context Protocol and AI agent development.

Seven modules grow ONE use case — a personal research assistant — a layer at a time: hand-rolled loop (`00`) → MCP server + thin client (`01`) → Claude Agent SDK host (`02`) → skills (`03`) → production HTTP/auth/hooks/evals (`04`) → deployed remote server + MCP Apps (`05`) → security lab + composition/subagents/sessions (`06`).

## Development Setup

### Package Manager
- **Primary**: UV. Every script has inline UV metadata headers; run with `uv run <script>.py`.
- Alternative: `python -m venv venv && source venv/bin/activate && pip install -r requirements/requirements.txt`

### Version pins (important, July 2026)
- **`mcp[cli]>=1.12,<2`** everywhere. Official SDK v2 (tracking spec 2026-07-28) renames `FastMCP` → `MCPServer` and changes low-level APIs — do NOT bump to v2 without migrating all servers. The standalone "FastMCP 3" (PrefectHQ/fastmcp) is a different package; this course uses the official SDK's built-in FastMCP.
- **`claude-agent-sdk>=0.1.0`** (0.2.x current) — bundles the Claude Code CLI, Python ≥3.10.

### Environment Variables (`.env` at repo root)
- `ANTHROPIC_API_KEY` — all agent demos
- `MCP_AUTH_TOKEN` — module 04 (required); module 05 (optional bearer auth)

## Demo Organization

1. **`00-intro-agents/`** — hand-rolled agent loop, tools as plain Python functions. `basic_personal_agent.py` + teaching notebook. KEEP AS-IS: loop-first pedagogy is intentional (presenter notes are in the notebook).
2. **`01-introduction-to-mcp/`** — same tools behind FastMCP (`mcp_server.py`); `mcp_client.py` is a thin, standalone-runnable protocol client. The old hand-rolled host lives in `archive/01-full-host-client/`.
3. **`02-research-agent-sdk/`** — Agent SDK as MCP host (`research_agent.py`, ~15 LOC core); `in_process_agent.py` shows `create_sdk_mcp_server`; `research_agent_multiturn.py` shows `ClaudeSDKClient`.
4. **`03-skills-and-mcp/`** — skills vs MCP teaching module + `mcp-builder-skill/` (agent scaffolds MCP servers) + `skill_loader_demo.py` (SDK skills gotchas).
5. **`04-production-research-agent/`** — intent-grouped tools (7→3), `streamable-http`, bearer-auth seam, hooks, permission callback, `evals.py` (3-layer correctness), `structured_output_demo.py`.
6. **`05-deploy-remote-mcp/`** — stateless remote server (`stateless_http=True`, `json_response=True`), Vercel wrapping (`api/index.py`, `vercel.json`), **MCP App** (`app.html`, vanilla-JS `ui/initialize` handshake), `test_client.py` pre-flight. Run `test_client.py` after ANY change here.
7. **`06-security-and-composition/`** — `security-lab/` (tool-poisoning attack/defense) + `composition/` (multi-server, subagent via the `Agent` tool, resume/fork sessions).

- **`exercises/link-checker/`** — take-home exercise with reference solution.
- **`archive/`** — retired demos (old 03 tabular, old 06 FastAPI+SSE Vercel, full host, OpenAI alternative). Do not modify; do not resurrect into the live flow without asking.
- **`assets-resources/`** — cheatsheet, diagrams, security report.

## MCP Server Patterns

**FastMCP, external (stdio or HTTP) — modules 01, 04, 05:**
```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp[cli]>=1.12,<2"]
# ///
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("server-name")            # module 05 adds: stateless_http=True, json_response=True,
                                        # and transport_security=TransportSecuritySettings(
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
    "research": {"type": "http", "url": "http://127.0.0.1:8765/mcp",
                  "headers": {"Authorization": f"Bearer {token}"}}
})
```

**MCP App — module 05:** tool declares `meta={"ui": {"resourceUri": "ui://..."}}`; resource at that URI has `mime_type="text/html;profile=mcp-app"` and returns self-contained HTML implementing the `ui/initialize` postMessage handshake (protocol version "2026-01-26").

## Agent Integration Guidelines

- The SDK is an MCP host: `allowed_tools=["mcp__<server>__*"]` for gating (MCP tools are NOT auto-approved by permission modes).
- Subagent tool is named **`Agent`** (renamed from `Task`); subagents run in background by default.
- Sessions are cwd-sensitive: `resume=session_id` silently starts fresh if cwd changed.
- Skills via SDK need `setting_sources=["user","project"]`; SKILL.md `allowed-tools` frontmatter is CLI-only.
- Tool search is ON by default in the SDK — tool definitions are deferred/loaded on demand.
- Hooks: `PreToolUse` to block, `PostToolUse` to log. Permission callback `can_use_tool` for defense in depth.

## When Creating MCP Servers
- UV inline metadata always; descriptive docstrings (the LLM reads them); type hints (schemas auto-generate).
- Prefer **intent-grouped tools** over API mirrors (module 04's 7→3).
- Test with `mcp dev <server>.py`; module 05 additionally with `uv run test_client.py`.
- Validate paths (workspace sandboxing pattern in modules 01/04); structured dict returns.

## Testing / Verifying

```bash
mcp dev <path-to-server.py>                     # Inspector UI
uv run demos/05-deploy-remote-mcp/test_client.py [url]   # protocol pre-flight
claude mcp add research -- uv run $PWD/demos/01-introduction-to-mcp/mcp_server.py
```

Claude Desktop config: macOS `~/Library/Application Support/Claude/claude_desktop_config.json`, Windows `%APPDATA%\Claude\claude_desktop_config.json`. Absolute paths; restart after edits.

## Troubleshooting
- Module 04 401 → `MCP_AUTH_TOKEN` in BOTH terminals; port 8765 free.
- Module 05 → server binds 8000; Claude custom connectors need a public URL (cloudflared tunnel or Vercel) and support OAuth-or-no-auth only (no bearer header field).
- Module 05 `421 Misdirected Request` via tunnel/Vercel (localhost works) → the mcp SDK auto-enables DNS-rebinding protection when binding 127.0.0.1 and rejects non-localhost `Host` headers at the origin. `server.py` opts out via `transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False)` — keep that when editing, and pre-flight with `uv run test_client.py <public-url>/mcp` (the localhost pre-flight can't catch this).
- DDGS empty results → throttling; tools degrade gracefully, retry.
- `mcp` not found → `pip install "mcp[cli]>=1.12,<2"`.

## Additional Resources
- Spec 2025-11-25: https://modelcontextprotocol.io/specification/2025-11-25 (course teaches against this; 2026-07-28 revision covered in slides)
- Claude Agent SDK: https://code.claude.com/docs/en/agent-sdk/overview
- MCP Apps extension: https://modelcontextprotocol.io/extensions/apps
- Production post (basis for modules 04–05): https://claude.com/blog/building-agents-that-reach-production-systems-with-mcp
