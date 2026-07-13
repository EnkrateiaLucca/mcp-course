#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "mcp[cli]>=1.9.3",
#   "anthropic>=0.40.0",
#   "fastapi",
#   "uvicorn",
#   "python-dotenv",
# ]
# ///
"""Tiny chat UI that consumes MCP *resources*.

Flow:
  1. On startup, spawn mcp_server.py over stdio and list its resources.
  2. UI shows a checkbox per resource.
  3. On each user message, read the selected resources from the MCP
     server and inject their contents into Claude's system prompt.
"""

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

HERE = Path(__file__).parent
SERVER = HERE / "mcp_server.py"

state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    params = StdioServerParameters(command="uv", args=["run", str(SERVER)])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            state["session"] = session
            print("MCP session ready.", file=sys.stderr)
            yield


app = FastAPI(lifespan=lifespan)
anthropic = Anthropic()


class ChatRequest(BaseModel):
    message: str
    resources: list[str] = []


@app.get("/resources")
async def list_resources():
    session: ClientSession = state["session"]
    result = await session.list_resources()
    return [
        {
            "uri": str(r.uri),
            "name": r.name or str(r.uri),
            "description": r.description or "",
        }
        for r in result.resources
    ]


@app.post("/chat")
async def chat(req: ChatRequest):
    session: ClientSession = state["session"]

    blocks = []
    for uri in req.resources:
        result = await session.read_resource(uri)
        for c in result.contents:
            text = getattr(c, "text", None) or ""
            blocks.append(f'<resource uri="{uri}">\n{text}\n</resource>')

    if blocks:
        system = (
            "You are a helpful assistant for Acme Corp. "
            "Answer using ONLY the facts in the resources below. "
            "If the answer isn't in them, say you don't know.\n\n"
            + "\n\n".join(blocks)
        )
    else:
        system = (
            "You are a helpful assistant. The user has selected no "
            "resources, so you have no Acme context — say so."
        )

    resp = anthropic.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": req.message}],
    )
    return {"reply": resp.content[0].text, "system_preview": system[:400]}


@app.get("/")
async def root():
    return HTMLResponse((HERE / "index.html").read_text())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8770)
