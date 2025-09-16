# MCP + Ollama in Python — Minimal End‑to‑End Demo

This tutorial shows the **simplest working setup** to connect a **local LLM (Ollama)** to **MCP tools** using Python. You’ll:

1. spin up a tiny MCP server exposing a couple of tools;
2. write a minimal Python client that chats with a local Ollama model and calls those tools when needed.

> Works on macOS, Linux, and Windows. Commands below use `python`/`pip`; feel free to swap for `uv` if you prefer.

---

## 0) Prerequisites

* **Python 3.10+**
* **Ollama** installed and running locally ([https://ollama.com](https://ollama.com)).
  After installing, pull a small model, e.g.:

```bash
ollama pull qwen2.5:7b   # or: llama3.2:3b, gemma3, mistral, etc.
```

* A terminal and a text editor.

Create a fresh folder:

```bash
mkdir mcp-ollama-demo && cd mcp-ollama-demo
```

---

## 1) Install Python dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install "mcp[cli]" ollama
```

This installs:

* `mcp` — the official Python SDK for Model Context Protocol (servers + clients)
* `ollama` — the official Ollama Python library

---

## 2) Create a tiny MCP server (2 tools)

Create a file **`server_demo.py`** with this content:

```python
# server_demo.py
from datetime import datetime, timezone
from mcp.server.fastmcp import FastMCP

app = FastMCP("DemoTools")

@app.tool()
def add(a: float, b: float) -> float:
    """Add two numbers and return the result."""
    return a + b

@app.tool()
def get_time() -> str:
    """Get the current UTC time as an ISO string."""
    return datetime.now(timezone.utc).isoformat()

if __name__ == "__main__":
    # Run as an MCP stdio server
    app.run(transport="stdio")
```

Keep this terminal ready to run it later. (You can also run it now in a separate terminal: `python server_demo.py` — it’ll wait for a client to connect.)

---

## 3) Write a minimal **Ollama‑powered MCP client**

The client will:

1. launch/connect to the MCP server over **stdio**,
2. list available tools and their JSON schemas,
3. ask the LLM to decide if a tool is needed (via a **very small tool‑calling convention**),
4. execute the tool,
5. return a final answer.

Create **`client_ollama_mcp.py`**:

```python
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

        first = await ollama.chat(model=model, messages=messages)
        text = first.message.content

        # 4) Detect a tool call
        m = re.search(r"<tool_call>\s*\{.*\}\s*</tool_call>", text, flags=re.S)
        if not m:
            return text  # No tool needed

        tool_json = json.loads(re.search(r"\{.*\}", m.group(0), flags=re.S).group(0))
        tool_name = tool_json.get("tool_name")
        tool_args = tool_json.get("arguments", {})

        # 5) Execute the tool over MCP
        tool_result = await session.call_tool(tool_name, tool_args)
        # tool_result.content is a list of content blocks; stringify for simplicity
        tool_result_text = json.dumps([c.model_dump() for c in tool_result.content])

        # 6) Ask the model for the final answer
        messages.extend([
            {"role": "assistant", "content": text},
            {
                "role": "user",
                "content": (
                    f"Tool `{tool_name}` returned this JSON content: {tool_result_text}.\n"
                    "Use it to answer the original question succinctly."
                ),
            },
        ])

        second = await ollama.chat(model=model, messages=messages)
        return second.message.content


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
```

---

## 4) Run the demo

In **Terminal A** (MCP server):

```bash
python server_demo.py
```

In **Terminal B** (client + Ollama):

```bash
python client_ollama_mcp.py --model qwen2.5:7b \
  "Add 2.5 and 7 using a tool if needed, then tell me the current UTC time too."
```

You should see the model either answer directly or emit a `<tool_call>{...}</tool_call>`, the client will run the tool(s) and print a final answer.

> Tip: try different models: `--model llama3.2:3b`, `--model gemma3`, `--model mistral:7b` (after `ollama pull ...`).

---

## 5) (Optional) Zero‑code path with a ready client

Prefer to skip writing the client? Use a maintained CLI that already wires **Ollama ⇄ MCP** with thinking / streaming / multi‑server features:

```bash
pip install -U ollmcp
ollmcp --mcp-server ./server_demo.py --model qwen2.5:7b
```

This gives you an interactive TUI: type a question and watch the model call tools.

---

## 6) Troubleshooting

* **Model doesn’t call tools**: Smaller models sometimes need stronger nudges. Re‑ask with phrasing like *“Use a tool if helpful”* or *“Call `add` with a and b inferred from the question”*. You can also lower ambiguity in `TOOL_CALL_GUIDE`.
* **Tool JSON parse errors**: The convention is intentionally strict (single‑line JSON inside `<tool_call>`). If the model returns code blocks, remove backticks in the parser, or instruct the model *“Do not use code fences when emitting `<tool_call>`”.*
* **Ollama not responding**: Ensure the daemon is running (`ollama serve`) and you’ve pulled the model you’re referencing.
* **Server not found**: Verify the path to `server_demo.py` and that Python is on your PATH.

---

## 7) What’s next

* Add more tools (web search, files, shell, etc.) by creating `@app.tool()` functions in your MCP server.
* Swap the simple tool‑call convention for a more structured approach (e.g., a parser that tolerates code fences, or a prompt that forces a function‑call schema).
* Turn the MCP server into **SSE** or **Streamable HTTP** (`app.run(transport="sse")`) and connect over HTTP instead of stdio.

---

## File tree recap

```
mcp-ollama-demo/
├─ server_demo.py          # MCP server exposing two tools
└─ client_ollama_mcp.py    # Minimal Ollama-powered client that can call MCP tools
```

You now have a minimal local **LLM + MCP** stack you can extend for real workflows.
