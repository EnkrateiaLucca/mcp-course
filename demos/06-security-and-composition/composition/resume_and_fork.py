#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["claude-agent-sdk>=0.1.0", "python-dotenv"]
# ///
"""Demo 10 — Sessions: resume a long task, fork to explore an alternative.

Use case: 'Stop and resume a long research task. Fork to try a different
angle without losing the original.'

Three calls:

  1. First pass — capture session_id from the ResultMessage.
  2. Resume later — ClaudeAgentOptions(resume=session_id). Full
     conversation context restored.
  3. Fork — ClaudeAgentOptions(resume=session_id, fork_session=True).
     New session id; the original is untouched.

Gotchas to teach:
  - Sessions persist CONVERSATION, not the filesystem. A forked agent's
    file edits are real and shared with the original session's files.
  - Sessions live at:
      ~/.claude/projects/<encoded-cwd>/<session_id>.jsonl
    A resume that 'starts fresh' almost always means mismatched cwd.

Run:
    export ANTHROPIC_API_KEY=sk-...
    uv run resume_and_fork.py
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)
from dotenv import load_dotenv

load_dotenv()

CWD = str(Path(__file__).parent.resolve())


async def consume(stream, label: str) -> str | None:
    """Print text and return the session_id from the ResultMessage."""
    session_id = None
    async for message in stream:
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"[{label}] {block.text}")
        elif isinstance(message, ResultMessage):
            session_id = message.session_id
    return session_id


async def main() -> None:
    # --- 1. First pass --------------------------------------------------
    print("=== 1. first pass ===")
    opts = ClaudeAgentOptions(cwd=CWD)
    sid = await consume(
        query(prompt="List three transport options for MCP and one tradeoff each.",
              options=opts),
        "first",
    )
    print(f"\ncaptured session_id={sid!r}\n")
    if not sid:
        raise SystemExit("no session_id captured — cannot continue demo")

    # --- 2. Resume ------------------------------------------------------
    print("=== 2. resume same session ===")
    opts_resume = ClaudeAgentOptions(cwd=CWD, resume=sid)
    await consume(
        query(prompt="Now expand option #2 into a paragraph aimed at SRE readers.",
              options=opts_resume),
        "resumed",
    )

    # --- 3. Fork --------------------------------------------------------
    print("\n=== 3. fork to a parallel angle ===")
    opts_fork = ClaudeAgentOptions(cwd=CWD, resume=sid, fork_session=True)
    forked_sid = await consume(
        query(prompt="Redo your earlier answer but focus on stdio-only setups for local agents.",
              options=opts_fork),
        "forked",
    )
    print(f"\noriginal session_id={sid!r}\nforked   session_id={forked_sid!r}")
    print("The original session is untouched; the forked one diverges from this prompt.")


if __name__ == "__main__":
    asyncio.run(main())
