#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["claude-agent-sdk>=0.1.0", "python-dotenv"]
# ///
"""Demo 04 — Correctness eval harness for the research agent.

`ExecutionTracker` (in research_agent.py) is *telemetry*: cost, duration,
tool counts. It tells you the agent ran. It does NOT tell you the agent was
right. This file is the correctness layer.

Three layers, cheap to expensive:

  1. Deterministic assertions  — grade_brief(): file exists, has Sources,
     mentions topic, non-trivial length. Free, fast, catches the obvious.
  2. LLM-as-judge              — judge_brief(): use the SDK itself, locked to
     Read-only, to score faithfulness/coverage/usefulness 1–5.
  3. Runnable gate             — run_evals(): execute every CASE end-to-end,
     combine the two grades, exit 1 if any case fails. Wire into CI.

The split between telemetry/observability and evals is intentional and
matches the SDK docs: cost-tracking + observability tell you what happened;
evals tell you whether it was right.

Run:
    export ANTHROPIC_API_KEY=sk-...
    export MCP_AUTH_TOKEN=demo-secret
    # In another terminal: uv run research_server.py
    uv run evals.py
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from claude_agent_sdk import (
    ClaudeAgentOptions,
    ResultMessage,
    query,
)
from dotenv import load_dotenv

# Reuse the agent module so we run the *real* configured agent.
from research_agent import build_options as build_agent_options
from research_agent import ExecutionTracker
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeSDKClient,
    SystemMessage,
    TextBlock,
    ToolUseBlock,
)

load_dotenv()

WORKSPACE = Path(__file__).parent / "workspace"


# --- 1. Deterministic assertions ------------------------------------------


def grade_brief(brief_path: Path, topic: str) -> dict[str, Any]:
    """Cheap, fast checks. No LLM call."""
    text = brief_path.read_text() if brief_path.exists() else ""
    topic_words = [w.lower() for w in topic.split() if len(w) > 3]
    checks = {
        "file_exists": brief_path.exists(),
        "has_sources_section": "## Sources" in text,
        "has_links": "http" in text,
        "mentions_topic": any(w in text.lower() for w in topic_words),
        "nontrivial_length": len(text) > 300,
    }
    return {"passed": all(checks.values()), "checks": checks}


# --- 2. LLM-as-judge -------------------------------------------------------


JUDGE_PROMPT_TEMPLATE = (
    "You are grading a research brief. Read the file at the absolute path: {path}\n\n"
    "Score 1–5 (integer) for each axis:\n"
    "  - faithfulness: claims are supported by the cited sources.\n"
    "  - coverage:     the brief actually addresses '{topic}'.\n"
    "  - usefulness:   would a busy professional find this useful?\n\n"
    'Reply with ONLY a JSON object on a single line, no prose, no code fences:\n'
    '{{"faithfulness": n, "coverage": n, "usefulness": n, "reason": "..."}}'
)


async def judge_brief(brief_path: Path, topic: str) -> dict[str, Any]:
    """Use the SDK as a judge, restricted to read-only filesystem access."""
    opts = ClaudeAgentOptions(
        model="claude-sonnet-5",
        allowed_tools=["Read"],
    )
    prompt = JUDGE_PROMPT_TEMPLATE.format(path=str(brief_path), topic=topic)

    raw_result: str | None = None
    async for msg in query(prompt=prompt, options=opts):
        if isinstance(msg, ResultMessage) and msg.subtype == "success":
            raw_result = msg.result

    if raw_result is None:
        return {"error": "no_result"}
    try:
        # Strip code fences if the judge ignored instructions.
        cleaned = raw_result.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"error": "non_json", "raw": raw_result}


# --- 3. Run the agent and capture the brief path --------------------------


async def run_agent_capture_brief(topic: str) -> tuple[Path | None, ExecutionTracker]:
    """Drive the agent through one task and return the brief it produced."""
    tracker = ExecutionTracker()
    brief_path: Path | None = None
    prompt = f"Research the topic '{topic}' and save a brief."

    async with ClaudeSDKClient(options=build_agent_options()) as client:
        await client.query(prompt)
        async for message in client.receive_response():
            tracker.on_message(message)
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, ToolUseBlock) and block.name.endswith("research_topic"):
                        # The tool result includes brief_path; we read it back via
                        # the next message. Simpler: derive from topic slug.
                        pass
                    elif isinstance(block, TextBlock):
                        # The agent typically reports the saved path.
                        pass
            if isinstance(message, SystemMessage) and message.subtype == "init":
                continue

    # Find the most recently modified brief — robust to slug variation.
    briefs_dir = WORKSPACE / "briefs"
    if briefs_dir.exists():
        briefs = sorted(briefs_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        if briefs:
            brief_path = briefs[0]

    return brief_path, tracker


# --- 4. The test set + runnable gate --------------------------------------


CASES = [
    {"topic": "MCP authentication", "min_score": 3},
    {"topic": "Claude Agent SDK subagents", "min_score": 3},
    {"topic": "tool poisoning attacks", "min_score": 3},
]


async def run_evals() -> int:
    results = []
    for case in CASES:
        topic = case["topic"]
        min_score = case["min_score"]
        print(f"\n=== {topic} ===")

        brief_path, tracker = await run_agent_capture_brief(topic)
        if brief_path is None:
            results.append({"topic": topic, "pass": False, "error": "no_brief_produced"})
            continue

        det = grade_brief(brief_path, topic)
        jdg = await judge_brief(brief_path, topic)
        worst = min(
            jdg.get("faithfulness", 0),
            jdg.get("coverage", 0),
            jdg.get("usefulness", 0),
        )
        ok = det["passed"] and worst >= min_score
        results.append({
            "topic": topic,
            "pass": ok,
            "brief": str(brief_path.relative_to(WORKSPACE.parent)),
            "deterministic": det,
            "judge": jdg,
            "cost_usd_est": tracker.cost_usd,
            "tool_calls": len(tracker.tool_calls),
        })

    print("\n" + "=" * 60)
    print(json.dumps(results, indent=2))
    failed = [r for r in results if not r["pass"]]
    print(f"\n{len(results) - len(failed)}/{len(results)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(run_evals()))
