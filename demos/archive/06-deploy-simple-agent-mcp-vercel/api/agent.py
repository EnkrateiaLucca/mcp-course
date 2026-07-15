"""
Vercel Python function. Two endpoints, dispatched via vercel.json rewrites:

  POST /api/agent/stream   → stream assistant messages as SSE
  POST /api/agent/cleanup  → stop the per-session Vercel Sandbox

The function is stateless per-request — the client owns the conversation and
POSTs full history each turn.
"""

from __future__ import annotations

import json
import os
from typing import Any, AsyncIterator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)

from .mcp_tools import build_server, KNOWN_TABLES
from .sandbox_exec import cleanup_sandbox

app = FastAPI()


SYSTEM_PROMPT = f"""You are a data analyst working with a synthetic Portuguese SME
dataset called `sabi_synth`. The data lives in DuckDB and is exposed ONLY through
the `analysis` MCP tools. You have no other tools.

All column and table names are in English. All tables join on `tax_id` (the
Portuguese tax identifier / NIF) as the canonical company key.

Tables:
{chr(10).join('  - ' + t for t in KNOWN_TABLES)}

5-year pivot convention: numeric columns are suffixed `_0` (most recent year,
2025) through `_4` (4 years ago). Example: `revenue_0` is 2025 revenue,
`revenue_4` is 2021 revenue. When a user asks about "trends over time", melt
wide-year columns into long form with `run_pandas`.

Note that some *values* are in Portuguese — specifically company names,
district names, and municipality names — because those are authentic Portuguese
place/entity names. Treat them as opaque strings.

How to work:
  1. If you don't remember the schema, call `list_tables` first, then
     `describe_table` for any table you plan to query.
  2. Prefer `query_sql` — it's faster and the data model is SQL-native.
  3. Reach for `run_pandas` only when SQL is awkward (wide→long reshapes,
     multi-table custom aggregations).
  4. When the user asks "show me" / "plot" / "chart", ALWAYS follow up with
     `create_chart` using the prior result's columns+rows. Pick the simplest
     chart that answers the question (bar for ranked categories, line for
     trends over time, pie only for <6 categories summing to a whole).
  5. Keep tool inputs small. Don't echo giant tables back into prompts.
  6. After tools return, write a one-paragraph plain-language summary
     highlighting the finding (not the methodology).
"""


@app.post("/api/agent/stream")
async def stream(request: Request):
    body = await request.json()
    session_id: str = body.get("session_id", "default")
    messages: list[dict[str, Any]] = body.get("messages", [])
    if not messages:
        return JSONResponse({"error": "messages required"}, status_code=400)

    async def event_source() -> AsyncIterator[dict[str, str]]:
        server = build_server()
        options = ClaudeAgentOptions(
            system_prompt=SYSTEM_PROMPT,
            mcp_servers={"analysis": server},
            allowed_tools=["mcp__analysis__*"],
            max_turns=10,
        )

        # Flatten conversation into a single prompt. The SDK's streaming API
        # takes one user turn at a time; past turns are conveyed via history.
        # Simplest teaching-safe approach: concatenate prior turns as tagged
        # blocks before the final user message.
        prompt = _build_prompt(messages)

        try:
            async with ClaudeSDKClient(options=options) as client:
                await client.query(prompt)
                async for msg in client.receive_response():
                    async for evt in _translate(msg):
                        yield evt
            yield {"event": "done", "data": "{}"}
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"message": f"{type(e).__name__}: {e}"}),
            }

    return EventSourceResponse(event_source())


@app.post("/api/agent/cleanup")
async def cleanup(request: Request):
    body = await request.json()
    session_id = body.get("session_id", "default")
    await cleanup_sandbox(session_id)
    return JSONResponse({"ok": True})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_prompt(messages: list[dict[str, Any]]) -> str:
    """Fold all prior turns into a single prompt string. Cheap and transparent;
    for a class demo this beats building up a streaming conversation state."""
    if len(messages) == 1:
        return messages[0]["content"]
    parts = []
    for m in messages[:-1]:
        role = m["role"].upper()
        parts.append(f"<{role}>\n{m['content']}\n</{role}>")
    parts.append(f"<CURRENT_USER_MESSAGE>\n{messages[-1]['content']}\n</CURRENT_USER_MESSAGE>")
    return "\n\n".join(parts)


async def _translate(msg: Any) -> AsyncIterator[dict[str, str]]:
    """Map an SDK message to one or more SSE events the frontend understands."""
    if isinstance(msg, AssistantMessage):
        for block in msg.content:
            if isinstance(block, TextBlock):
                yield {
                    "event": "delta",
                    "data": json.dumps({"text": block.text}),
                }
            elif isinstance(block, ToolUseBlock):
                yield {
                    "event": "tool_use",
                    "data": json.dumps({
                        "id": block.id,
                        "name": block.name,
                        "input": block.input,
                    }),
                }
    elif isinstance(msg, UserMessage):
        # Tool results come back wrapped in a UserMessage.
        for block in msg.content:
            if isinstance(block, ToolResultBlock):
                # The tool's content is a list of {"type":"text","text": ...}
                # where `text` is our typed-dict JSON. Unwrap for the frontend.
                payload_text = ""
                if isinstance(block.content, list):
                    for c in block.content:
                        if isinstance(c, dict) and c.get("type") == "text":
                            payload_text += c.get("text", "")
                elif isinstance(block.content, str):
                    payload_text = block.content
                try:
                    parsed = json.loads(payload_text) if payload_text else {}
                except json.JSONDecodeError:
                    parsed = {"type": "text", "payload": {"text": payload_text}}
                yield {
                    "event": "tool_result",
                    "data": json.dumps({
                        "tool_use_id": block.tool_use_id,
                        "is_error": bool(block.is_error),
                        "result": parsed,
                    }),
                }
    elif isinstance(msg, ResultMessage):
        yield {
            "event": "result",
            "data": json.dumps({
                "stop_reason": msg.stop_reason,
                "num_turns": msg.num_turns,
                "total_cost_usd": msg.total_cost_usd,
            }),
        }
