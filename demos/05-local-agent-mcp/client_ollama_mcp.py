# client_ollama_mcp.py
import asyncio
import json
import re
from contextlib import AsyncExitStack
from typing import Any, Dict, List

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from ollama import AsyncClient

# --- A tiny convention for tool calls ---------------------------------------
# We ask the model to emit exactly one JSON object between <tool_call> ... </tool_call>
# when it wants to call a tool. Otherwise it should just answer the user.
# This keeps the example dependency-free and model-agnostic.

TOOL_CALL_GUIDE = """
You can call tools if needed.
When you want to call a tool, output EXACTLY one JSON object on a single line,
wrapped in <tool_call> ... </tool_call> tags, with the following shape:

<tool_call>{"tool_name": "<name>", "arguments": { /* inputs per JSON schema */ }}</tool_call>

After the tool result is given back to you, produce the final answer for the user.
If no tool is needed, just answer normally without any tags.
"""


def tools_as_readable_spec(tools: List[Dict[str, Any]]) -> str:
    lines = ["Available tools (name, description, json-schema for arguments):\n"]
    for t in tools:
        lines.append(f"- {t['name']}: {t.get('description') or ''}\n  schema: {json.dumps(t['input_schema'])}")
    return "\n".join(lines)


async def run_chat(query: str, model: str, server_path: str) -> str:
    ollama = AsyncClient()  # defaults to http://localhost:11434

    async with AsyncExitStack() as stack:
        # 1) Launch/connect to the MCP server over stdio
        params = StdioServerParameters(command="python", args=[server_path])
        stdio = await stack.enter_async_context(stdio_client(params))
        read, write = stdio
        session = await stack.enter_async_context(ClientSession(read, write))
        await session.initialize()

        # 2) Discover tools
        tools_resp = await session.list_tools()
        tools = [
            {
                "name": t.name,
                "description": t.description or "",
                "input_schema": t.inputSchema,
            }
            for t in tools_resp.tools
        ]

        # 3) Ask the model
        system_prompt = (
            "You are a helpful assistant that can use tools via an MCP server.\n\n"
            + TOOL_CALL_GUIDE
            + "\n\n"
            + tools_as_readable_spec(tools)
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]

        # Loop to handle multiple tool calls
        max_iterations = 5  # Prevent infinite loops
        for _ in range(max_iterations):
            response = await ollama.chat(model=model, messages=messages)
            text = response.message.content

            # Check for tool call
            m = re.search(r"<tool_call>\s*(\{.*\})\s*</tool_call>", text, flags=re.S)
            if not m:
                return text  # No more tools needed, return final answer

            try:
                # Extract and parse tool call
                json_str = m.group(1)
                tool_json = json.loads(json_str)
                tool_name = tool_json.get("tool_name")
                tool_args = tool_json.get("arguments", {})

                # Execute the tool
                tool_result = await session.call_tool(tool_name, tool_args)
                tool_result_text = json.dumps([c.model_dump() for c in tool_result.content])

                # Add the interaction to message history
                messages.extend([
                    {"role": "assistant", "content": text},
                    {
                        "role": "user",
                        "content": (
                            f"Tool `{tool_name}` returned: {tool_result_text}.\n"
                            "Continue with the next tool if needed, or provide the final answer."
                        ),
                    },
                ])

            except json.JSONDecodeError as e:
                return text + f"\n\n[Error parsing tool call: {e}]"
            except Exception as e:
                return text + f"\n\n[Error executing tool: {e}]"

        return "Maximum iterations reached."


async def main():
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("query", nargs="?", default="What time is it in UTC now? Use a tool if helpful.")
    p.add_argument("--model", default="qwen2.5:7b")
    p.add_argument("--server", default="server_demo.py")
    args = p.parse_args()

    out = await run_chat(args.query, args.model, args.server)
    print("\n=== Final Answer ===\n" + out)


if __name__ == "__main__":
    asyncio.run(main())