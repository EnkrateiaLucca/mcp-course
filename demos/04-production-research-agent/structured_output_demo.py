#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["claude-agent-sdk>=0.1.0", "pydantic", "python-dotenv"]
# ///
"""Demo 04c — Structured outputs: make the agent's FINAL answer machine-readable.

Tools already return structured dicts (see research_server.py). This closes
the loop on the other end: `output_format` forces the agent's final result
into a JSON schema, validated by the platform — no regex-parsing prose.

This is the natural companion to evals: a structured verdict is gradeable;
a paragraph is not.

Run (needs the demo 04 server up in another terminal):
    export MCP_AUTH_TOKEN=demo-secret ANTHROPIC_API_KEY=sk-...
    uv run structured_output_demo.py
"""

from __future__ import annotations

import asyncio
import json

from pydantic import BaseModel, Field
from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query
from dotenv import load_dotenv

# Reuse the production agent's full configuration (auth, hooks, allow-list).
from research_agent import build_options

load_dotenv()


class ResearchReport(BaseModel):
    """What we want back — as data, not prose."""

    topic: str
    brief_path: str = Field(description="Path of the saved brief, e.g. briefs/x.md")
    source_count: int
    key_findings: list[str] = Field(min_length=1, max_length=5)
    confidence: float = Field(ge=0, le=1, description="Self-assessed confidence")


async def main() -> None:
    options: ClaudeAgentOptions = build_options()
    options.output_format = {
        "type": "json_schema",
        "schema": ResearchReport.model_json_schema(),
    }

    async for message in query(
        prompt="Research the MCP 2026-07-28 spec revision.", options=options
    ):
        if isinstance(message, ResultMessage) and message.structured_output:
            report = ResearchReport.model_validate(message.structured_output)
            print("✅ validated ResearchReport:")
            print(json.dumps(report.model_dump(), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
