#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["anthropic", "ddgs", "python-dotenv"]
# ///
"""Standalone personal agent — the .py companion to the notebook.

Same tools (web_search + read/write/edit/bash), same agent loop, runnable end-to-end:

    uv run basic_personal_agent.py "Research the Model Context Protocol and save a brief."
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from anthropic import Anthropic
from ddgs import DDGS
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-5"
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


def run_bash(command: str) -> str:
    """Run a shell command inside the workspace sandbox and return its output."""
    result = subprocess.run(
        command,
        shell=True,
        cwd=WORKSPACE,
        capture_output=True,
        text=True,
        timeout=30,
    )
    output = (result.stdout + result.stderr).strip()
    return output or f"(exit code {result.returncode}, no output)"


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
        "name": "read",
        "description": "Read a text file from the workspace.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
    {
        "name": "write",
        "description": "Create or overwrite a file in the workspace.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
            "required": ["path", "content"],
        },
    },
    {
        "name": "edit",
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
        "name": "bash",
        "description": (
            "Run a shell command inside the workspace directory and return its output. "
            "Use it to list, move, delete, or inspect files (ls, mv, rm, mkdir, wc, grep, cat...)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"command": {"type": "string", "description": "The shell command to run"}},
            "required": ["command"],
        },
    },
]

FUNCTIONS = {
    "web_search": web_search,
    "read": read_file,
    "write": write_file,
    "edit": edit_file,
    "bash": run_bash,
}

SYSTEM = (
    "You are a personal research assistant. You can search the web and organize "
    "findings as files in the user's workspace, using read/write/edit for file "
    "content and bash for everything else (ls, mv, rm, grep, wc...). When asked "
    "to 'research X', search the web and save a short markdown brief with sources. "
    "Keep filenames lowercase-hyphenated."
)


def run_agent(user_query: str, max_iterations: int = 15) -> str:
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
