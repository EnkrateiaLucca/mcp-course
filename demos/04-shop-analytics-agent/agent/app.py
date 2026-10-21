"""Shop Analytics chat agent: a FastAPI app that runs the Claude Agent SDK against our MCP server."""

import hmac
import json
import os
import time
from contextlib import aclosing
from datetime import date
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    SystemMessage,
    ToolUseBlock,
    query,
)
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field

MCP_URL = os.environ.get("MCP_URL") or f"http://{os.environ.get('MCP_HOSTPORT', 'localhost:8001')}/mcp"
os.environ["ANTHROPIC_API_KEY"]  # fail fast at startup instead of "Not logged in" on the first chat
MCP_TOKEN = os.environ["MCP_TOKEN"]
APP_PASSWORD = os.environ["APP_PASSWORD"]  # the public URL spends your API credits: keep it gated
MODEL = os.environ.get("MODEL", "claude-sonnet-5")
MAX_BUDGET_USD = float(os.environ.get("MAX_BUDGET_USD", "0.50"))
CONFIG_DIR = Path(__file__).parent / ".claude-home"  # agent-only Claude config + session transcripts

SYSTEM_PROMPT = """You are the data analyst for an outdoor-gear online shop. Today is {today}.
Answer only with numbers you got from the analytics tools. Never invent data.
Lead with the insight in one or two sentences, then the supporting numbers. Keep it short.
When a trend or comparison helps, add exactly one chart as a fenced code block with the language
`chart` holding a Chart.js config as JSON, for example:
```chart
{{"type": "bar", "data": {{"labels": ["Jan", "Feb"], "datasets": [{{"label": "Revenue ($)", "data": [120, 150]}}]}}}}
```"""

# What the user sees when the agent stops on a limit. The SDK raises after it yields these results.
LIMIT_REPLIES = {
    "error_max_turns": "I ran out of steps before I finished. Try a narrower question, for example one month or one product.",
    "error_max_budget_usd": "This question hit the cost limit for one message. Try a narrower question.",
}

app = FastAPI(title="Shop Analytics Agent")
basic = HTTPBasic()

# ponytail: in-memory, per process. Restarts reset it and several replicas each keep their own.
# Move it to Redis or your database when you run more than one container.
_session_cost: dict[str, float] = {}


def require_password(creds: HTTPBasicCredentials = Depends(basic)) -> None:
    if not hmac.compare_digest(creds.password.encode(), APP_PASSWORD.encode()):
        raise HTTPException(401, "Wrong password", headers={"WWW-Authenticate": "Basic"})


def log_event(event: str, **fields) -> None:
    """One JSON line per event on stdout: docker logs, Render and any log platform can parse it."""
    print(json.dumps({"event": event, "ts": round(time.time(), 3), **fields}), flush=True)


def turn_usage(result: ResultMessage, tools_used: list[str], seconds: float) -> dict:
    """Tokens and estimated cost for one chat message.

    total_cost_usd is a client-side ESTIMATE from the SDK's price table, not billing data.
    For a resumed session it already includes the earlier turns, so this turn's cost is the
    difference from the last total we saw for that session.
    """
    usage = result.usage or {}
    total = result.total_cost_usd or 0.0
    previous = _session_cost.get(result.session_id, 0.0)
    _session_cost[result.session_id] = total
    return {
        "session_id": result.session_id,
        "status": result.subtype,
        "model": MODEL,
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
        "cache_read_tokens": usage.get("cache_read_input_tokens", 0),
        "cache_write_tokens": usage.get("cache_creation_input_tokens", 0),
        "turn_cost_usd": round(max(total - previous, 0.0), 4),
        "session_cost_usd": round(total, 4),
        "agent_steps": result.num_turns,
        "tool_calls": tools_used,
        "seconds": round(seconds, 1),
    }


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    session_id: str | None = None  # returned by the previous turn; continues the conversation


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.get("/", dependencies=[Depends(require_password)])
def index() -> FileResponse:
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.post("/chat", dependencies=[Depends(require_password)])
async def chat(req: ChatRequest) -> dict:
    options = ClaudeAgentOptions(
        model=MODEL,
        system_prompt=SYSTEM_PROMPT.format(today=date.today().isoformat()),
        mcp_servers={
            "analytics": {"type": "http", "url": MCP_URL, "headers": {"Authorization": f"Bearer {MCP_TOKEN}"}}
        },
        tools=[],  # no built-in Bash/Read/Write: the MCP server is the agent's only way to touch anything
        allowed_tools=["mcp__analytics__*"],
        # Isolate from the host's Claude Code setup (CLAUDE.md, settings, plugins, skills, other MCP servers).
        setting_sources=[],
        strict_mcp_config=True,
        env={"CLAUDE_CONFIG_DIR": str(CONFIG_DIR), "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"},
        max_turns=12,
        max_budget_usd=MAX_BUDGET_USD,
        resume=req.session_id,
    )
    started = time.monotonic()
    tools_used: list[str] = []
    result: ResultMessage | None = None
    mcp_status = "missing"
    try:
        async with aclosing(query(prompt=req.message, options=options)) as stream:
            async for msg in stream:
                if isinstance(msg, SystemMessage) and msg.subtype == "init":
                    # Check the data service BEFORE the model spends tokens working around it.
                    # A wrong token or an unreachable server shows up here as "failed".
                    servers = msg.data.get("mcp_servers") or []
                    mcp_status = next((s.get("status") for s in servers if s.get("name") == "analytics"), "missing")
                    if mcp_status not in ("connected", "pending"):
                        break  # closing the stream stops the subprocess
                elif isinstance(msg, AssistantMessage):
                    tools_used += [b.name.removeprefix("mcp__analytics__") for b in msg.content if isinstance(b, ToolUseBlock)]
                elif isinstance(msg, ResultMessage):
                    result = msg
    except Exception as e:
        # The SDK raises AFTER it yields an error result (max turns, budget). Those have a result: keep it.
        # No result means the run never finished: a bad API key, a network error, a crash.
        if result is None:
            log_event("chat_error", error=str(e)[:300], seconds=round(time.monotonic() - started, 1))
            raise HTTPException(502, "The agent failed before it could answer. Check the server logs.") from e

    if mcp_status not in ("connected", "pending"):
        log_event("mcp_unavailable", server="analytics", status=mcp_status, url=MCP_URL)
        raise HTTPException(503, "The analytics data service is unavailable, so I can't answer with real numbers.")
    if result is None:
        log_event("chat_error", error="no result message", seconds=round(time.monotonic() - started, 1))
        raise HTTPException(502, "The agent stopped without an answer. Check the server logs.")

    usage = turn_usage(result, tools_used, time.monotonic() - started)
    log_event("chat_turn", is_error=result.is_error, api_error_status=result.api_error_status, **usage)
    if result.subtype in LIMIT_REPLIES:
        reply = LIMIT_REPLIES[result.subtype]
    elif result.is_error:
        # API failures (bad key, rate limit, overload) arrive as subtype "success" with is_error=True.
        raise HTTPException(502, f"The model call failed: {result.result or result.subtype}")
    else:
        reply = result.result or ""
    # ponytail: sessions live on the container's disk, so a redeploy forgets chats. Add a SessionStore for durability.
    return {"reply": reply, "session_id": result.session_id, "tools_used": tools_used, "usage": usage}
