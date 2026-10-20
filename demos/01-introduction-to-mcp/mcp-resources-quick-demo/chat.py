#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["claude-agent-sdk>=0.1.0", "mcp[cli]>=2.3,<3", "prompt_toolkit>=3.0"]
# ///
"""Chat with @-mentions backed by MCP resources.

    you > summarize @mcp-primitives and compare it with @resources-vs-tools
    you > /compare mcp-primitives transport-notes

Type `@` and hit TAB to complete resource names. `/name args...` expands an
MCP prompt (prompts/get) into the message; any @mentions inside it are then
resolved like typed ones. Before the model sees the
message, the host reads each mentioned resource over MCP and prepends it as
context. The model never had to guess which document to fetch: that is the
value of resources over a generic read tool.

Two connections to the same server script:
  * mcp ClientSession   -> resources/templates/list, completion/complete,
                           resources/read, prompts/list, prompts/get (host-controlled)
  * Claude Agent SDK    -> tools (model-controlled)

Run: uv run chat.py
"""

from __future__ import annotations

import asyncio
import re
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage, ClaudeAgentOptions, ClaudeSDKClient, TextBlock, ToolUseBlock,
)
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import ResourceTemplateReference
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion

SERVER = str((Path(__file__).parent / "server.py").resolve())
MENTION = re.compile(r"@([\w-]+)")

OPTIONS = ClaudeAgentOptions(
    system_prompt="You are a concise assistant. Sources the user @-mentions are "
                  "attached above their message in <source> tags; cite them by name.",
    mcp_servers={"sources": {"command": "uv", "args": ["run", SERVER]}},
    allowed_tools=["mcp__sources__*"],
)


class ResourceCompleter(Completer):
    """`@` -> completion/complete on the resource template; `/` -> prompt names."""

    def __init__(self, mcp: ClientSession, template: str, prompts: dict):
        self.mcp, self.template, self.prompts = mcp, template, prompts

    def get_completions(self, document, complete_event):
        return []  # sync path unused; prompt_toolkit calls the async one below

    async def get_completions_async(self, document, complete_event):
        before = document.text_before_cursor
        if (m := re.match(r"/(\w*)$", before)):
            for name, p in self.prompts.items():
                if name.startswith(m.group(1)):
                    args = " ".join(f"<{a.name}>" for a in p.arguments or [])
                    yield Completion(name, start_position=-len(m.group(1)), display=f"/{name} {args}")
            return
        m = re.search(r"@([\w-]*)$", before)
        if not m:
            return
        result = await self.mcp.complete(
            ResourceTemplateReference(type="ref/resource", uri=self.template),
            {"name": "name", "value": m.group(1)})
        for name in result.completion.values:
            yield Completion(name, start_position=-len(m.group(1)))


def expand(text: str, contents: dict[str, str]) -> str:
    """Prepend the content of each @mentioned resource; unknown names stay as-is."""
    blocks = [f'<source name="{n}">\n{contents[n]}\n</source>'
              for n in dict.fromkeys(MENTION.findall(text)) if n in contents]
    return "\n\n".join(blocks + [text]) if blocks else text


async def chat() -> None:
    params = StdioServerParameters(command="uv", args=["run", SERVER])
    async with stdio_client(params) as (r, w), ClientSession(r, w) as mcp:
        await mcp.initialize()
        template = (await mcp.list_resource_templates()).resource_templates[0].uri_template
        print(f"resource template: {template}  (type @ then TAB, 'exit' quits)\n")

        prompts = {p.name: p for p in (await mcp.list_prompts()).prompts}
        print("prompts: " + ", ".join(f"/{n} " + " ".join(f"<{a.name}>" for a in p.arguments or [])
                                       for n, p in prompts.items()) + "\n")

        prompt = PromptSession(completer=ResourceCompleter(mcp, template, prompts),
                               complete_while_typing=True)
        async with ClaudeSDKClient(options=OPTIONS) as agent:
            while True:
                try:
                    text = (await prompt.prompt_async("you > ")).strip()
                except (EOFError, KeyboardInterrupt):
                    break
                if text.lower() in {"exit", "quit", ""}:
                    break

                # Host-side: `/name a b` -> prompts/get, positional args by name.
                if text.startswith("/"):
                    cmd, *args = text[1:].split()
                    if cmd not in prompts:
                        print(f"  unknown prompt /{cmd}"); continue
                    names = [a.name for a in prompts[cmd].arguments or []]
                    got = await mcp.get_prompt(cmd, dict(zip(names, args)))
                    text = "\n".join(m.content.text for m in got.messages)
                    print(f"  [prompt] /{cmd} -> {text!r}")

                # Host-side: resolve @mentions via resources/read, then hand off.
                contents = {}
                for name in set(MENTION.findall(text)):
                    uri = template.replace("{name}", name)
                    try:
                        result = await mcp.read_resource(uri)
                    except Exception as e:  # unknown @name: leave it as plain text
                        print(f"  [resource] {uri} skipped: {e}")
                        continue
                    contents[name] = result.contents[0].text
                    print(f"  [resource] {uri} ({len(contents[name])} chars)")

                await agent.query(expand(text, contents))
                async for msg in agent.receive_response():
                    if isinstance(msg, AssistantMessage):
                        for block in msg.content:
                            if isinstance(block, ToolUseBlock):
                                print(f"  [tool] {block.name} {block.input}")
                            elif isinstance(block, TextBlock):
                                print(f"\nagent > {block.text}")
                print()


if __name__ == "__main__":
    assert expand("hi @a and @b @a", {"a": "A"}) == '<source name="a">\nA\n</source>\n\nhi @a and @b @a'
    asyncio.run(chat())
