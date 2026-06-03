#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "claude-agent-sdk>=0.1.0",
#     "pandas>=2.0.0",
#     "python-dotenv",
# ]
# ///
"""Demo 03 — Exact-match eval runner for the tabular-data agent.

Pattern from Anthropic's official `tool_evaluation` cookbook:
https://github.com/anthropics/claude-cookbooks/tree/main/tool_evaluation

For tasks with a single correct answer (counts, top-N lookups), grade by
EXACT STRING MATCH between the model's answer and ground truth — not by
LLM-as-judge. The judge system prompt constrains output to <response>...
</response> tags with a strict format (just the number, no units, no commas)
so the match is fair.

We also capture:
  - the agent's <feedback>...</feedback> on the tools, which is the signal
    to improve tool *descriptions and schemas* (the "writing tools for agents"
    feedback loop, made measurable)
  - tool-call count per task: a correct answer that needed 8 calls is a smell
    that the tool docs are bad and the agent had to trial-and-error

Run:
    export ANTHROPIC_API_KEY=sk-...
    uv run eval_runner.py
"""

from __future__ import annotations

import asyncio
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
)
from dotenv import load_dotenv

load_dotenv()

HERE = Path(__file__).parent
EVAL_FILE = HERE / "evaluation.xml"

JUDGE_SYSTEM_PROMPT = (
    "You are answering questions about a product CSV using the available tools. "
    "After you compute the answer, write your final answer ONLY inside "
    "<response>...</response> tags. Give the bare value: just the number with "
    "no commas, no currency symbol, no units; or just the product name with no "
    "extra punctuation. "
    "Also give <feedback>...</feedback> on the tools you used: were the names, "
    "parameters, and descriptions clear? Did you hit errors? Be specific — this "
    "feedback is used to improve the tool definitions."
)


def load_cases(path: Path) -> list[dict[str, str]]:
    tree = ET.parse(path)
    return [
        {"prompt": task.findtext("prompt", "").strip(),
         "truth": task.findtext("response", "").strip()}
        for task in tree.findall("task")
    ]


def extract_tag(text: str, tag: str) -> str:
    m = re.search(rf"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
    return m.group(1).strip() if m else ""


def score_exact(model_answer: str, truth: str) -> int:
    return int(model_answer.strip() == truth.strip())


async def run_one(prompt: str) -> tuple[str, int, float]:
    """Run one task. Returns (full_text, tool_call_count, cost_usd_est)."""
    # Import the tool functions from the main demo and assemble the server here
    # so the eval doesn't depend on demo-specific glue.
    from claude_agent_sdk import create_sdk_mcp_server
    from claude_agents_sdk_demo import (  # type: ignore[attr-defined]
        search_products_by_category,
        search_products_by_price_range,
        get_top_rated_products,
        get_category_statistics,
    )

    server = create_sdk_mcp_server(
        name="csv",
        version="1.0.0",
        tools=[
            search_products_by_category,
            search_products_by_price_range,
            get_top_rated_products,
            get_category_statistics,
        ],
    )
    options = ClaudeAgentOptions(
        model="claude-sonnet-4-6",
        system_prompt=JUDGE_SYSTEM_PROMPT,
        mcp_servers={"csv": server},
        allowed_tools=["mcp__csv__*"],
    )

    text_parts: list[str] = []
    tool_calls = 0
    cost = 0.0

    async with ClaudeSDKClient(options=options) as client:
        await client.query(prompt)
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        text_parts.append(block.text)
                    elif isinstance(block, ToolUseBlock):
                        tool_calls += 1
            elif isinstance(message, ResultMessage):
                cost = message.total_cost_usd or 0.0

    return "\n".join(text_parts), tool_calls, cost


async def main() -> int:
    cases = load_cases(EVAL_FILE)
    print(f"Loaded {len(cases)} eval cases from {EVAL_FILE.name}\n")

    results = []
    for i, case in enumerate(cases, 1):
        print(f"[{i}/{len(cases)}] {case['prompt']}")
        try:
            text, tool_calls, cost = await run_one(case["prompt"])
        except Exception as exc:  # pragma: no cover
            print(f"  ERROR: {exc}")
            results.append({"prompt": case["prompt"], "score": 0, "error": str(exc)})
            continue

        model_answer = extract_tag(text, "response")
        feedback = extract_tag(text, "feedback")
        score = score_exact(model_answer, case["truth"])
        results.append({
            "prompt": case["prompt"],
            "truth": case["truth"],
            "answer": model_answer,
            "score": score,
            "tool_calls": tool_calls,
            "cost_usd_est": cost,
            "feedback": feedback,
        })
        marker = "✓" if score else "✗"
        print(f"  {marker} got={model_answer!r}  truth={case['truth']!r}  "
              f"tools={tool_calls}  cost=${cost:.4f}")

    total = sum(r["score"] for r in results)
    print(f"\n{total}/{len(results)} exact-match passes")

    # Surface tool-quality smells.
    bad_smells = [r for r in results if r.get("tool_calls", 0) > 5]
    if bad_smells:
        print("\n⚠ High tool-call counts (smell: tool docs may be unclear):")
        for r in bad_smells:
            print(f"  - {r['tool_calls']} calls for: {r['prompt']}")

    return 0 if total == len(results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
