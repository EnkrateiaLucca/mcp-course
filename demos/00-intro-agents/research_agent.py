#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["anthropic", "ddgs", "python-dotenv"]
# ///
"""Standalone research-assistant agent — the .py companion to the notebook.

Same tools, same agent loop, runnable end-to-end:

    uv run research_agent.py "Research the Model Context Protocol and save a brief."
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from anthropic import Anthropic
from ddgs import DDGS
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-4-6"
WORKSPACE = Path("./workspace").resolve()
WORKSPACE.mkdir(exist_ok=True)


def _safe(path: str) -> Path:
    p = (WORKSPACE / path).resolve()
    if WORKSPACE not in p.parents and p != WORKSPACE:
        raise ValueError(f"Path escapes workspace: {path}")
    return p


def web_search(query: str, max_results: int = 5) -> str:
    hits = DDGS().text(query, max_results=max_results)
    return json.dumps(
        [{"title": h.get("title"), "url": h.get("href"), "snippet": h.get("body")} for h in hits],
        indent=2,
    )


def read_file(path: str) -> str:
    return _safe(path).read_text()


def write_file(path: str, content: str) -> str:
    p = _safe(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return f"Wrote {len(content)} chars to {path}"


def edit_file(path: str, old: str, new: str) -> str:
    p = _safe(path)
    text = p.read_text()
    if old not in text:
        return f"Error: substring not found in {path}"
    p.write_text(text.replace(old, new))
    return f"Edited {path}"


def move_file(src: str, dst: str) -> str:
    s, d = _safe(src), _safe(dst)
    d.parent.mkdir(parents=True, exist_ok=True)
    s.rename(d)
    return f"Moved {src} -> {dst}"


def delete_file(path: str) -> str:
    _safe(path).unlink()
    return f"Deleted {path}"


def list_files(directory: str = ".") -> str:
    base = _safe(directory)
    return "\n".join(sorted(str(p.relative_to(WORKSPACE)) for p in base.rglob("*"))) or "(empty)"


TOOLS = [
    {
        "name": "web_search",
        "description": "Search the web with DuckDuckGo. Returns JSON list of {title, url, snippet}.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "max_results": {"type": "integer", "default": 5},
            },
            "required": ["query"],
        },
    },
    {
        "name": "read_file",
        "description": "Read a text file from the workspace.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Create or overwrite a file in the workspace.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
            "required": ["path", "content"],
        },
    },
    {
        "name": "edit_file",
        "description": "Replace a substring in an existing file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "old": {"type": "string"},
                "new": {"type": "string"},
            },
            "required": ["path", "old", "new"],
        },
    },
    {
        "name": "move_file",
        "description": "Move or rename a file inside the workspace.",
        "input_schema": {
            "type": "object",
            "properties": {"src": {"type": "string"}, "dst": {"type": "string"}},
            "required": ["src", "dst"],
        },
    },
    {
        "name": "delete_file",
        "description": "Delete a file from the workspace.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
    {
        "name": "list_files",
        "description": "List files under a directory in the workspace.",
        "input_schema": {
            "type": "object",
            "properties": {"directory": {"type": "string", "default": "."}},
            "required": [],
        },
    },
]

FUNCTIONS = {
    "web_search": web_search,
    "read_file": read_file,
    "write_file": write_file,
    "edit_file": edit_file,
    "move_file": move_file,
    "delete_file": delete_file,
    "list_files": list_files,
}

SYSTEM = (
    "You are a personal research assistant. You can search the web and organize "
    "findings as files in the user's workspace. When asked to 'research X', search "
    "the web and save a short markdown brief with sources. Keep filenames "
    "lowercase-hyphenated."
)


def run_agent(user_query: str, max_iterations: int = 10) -> str:
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    messages = [{"role": "user", "content": user_query}]
    print(f"User: {user_query}\n")

    for i in range(max_iterations):
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM,
            messages=messages,
            tools=TOOLS,
        )

        if response.stop_reason != "tool_use":
            text = "".join(b.text for b in response.content if hasattr(b, "text"))
            print(f"\nAgent: {text}")
            return text

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                args_preview = json.dumps(block.input)[:120]
                print(f"  [{i + 1}] {block.name}({args_preview})")
                try:
                    result = FUNCTIONS[block.name](**block.input)
                except Exception as e:
                    result = f"Error: {e}"
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                })
        messages.append({"role": "user", "content": tool_results})

    return "(max iterations reached)"


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or (
        "Research what the Model Context Protocol is and save a short markdown "
        "brief to research/mcp-brief.md with bullets and a sources section."
    )
    run_agent(query)
