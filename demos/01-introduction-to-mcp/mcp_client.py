#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp[cli]>=1.12,<2"]
# ///
"""Minimal MCP client — the protocol, demystified in one file.

Wraps an stdio MCP server connection and exposes the three primitives we
care about: list_tools, call_tool, read_resource. In demo 00 the "agent"
called Python functions directly; this is the SAME capability surface,
reached through a protocol — which is why any host (Claude Desktop, Claude
Code, the Agent SDK) can consume the server we just wrote.

Run it standalone to watch the protocol happen:

    uv run mcp_client.py ./mcp_server.py

(The full hand-rolled agent loop that used this client lives in
`demos/archive/01-full-host-client/mcp_host.py` — worth reading once,
but in demo 02 the Claude Agent SDK replaces all of it.)

Reference: https://modelcontextprotocol.io/docs/develop/build-client
"""

from __future__ import annotations

from contextlib import AsyncExitStack
from typing import Any, Optional

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from pydantic import AnyUrl


class SimpleMCPClient:
    def __init__(self) -> None:
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connect_to_server(self, server_path: str) -> None:
        """Spawn the server as a subprocess and initialize the MCP session."""
        # `uv run` honors the server's inline dependency metadata; plain
        # `python` would require the deps to be pre-installed.
        params = StdioServerParameters(command="uv", args=["run", server_path], env=None)
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )
        await self.session.initialize()

        tools = await self.list_tools()
        print(f"✅ Connected. Tools: {[t.name for t in tools]}")

        resources = (await self.session.list_resources()).resources
        if resources:
            print(f"📚 Resources: {[str(r.uri) for r in resources]}")

    async def list_tools(self) -> list[types.Tool]:
        return (await self.session.list_tools()).tools

    async def call_tool(self, name: str, arguments: dict) -> types.CallToolResult:
        return await self.session.call_tool(name, arguments)

    async def read_resource(self, uri: str) -> Any:
        result = await self.session.read_resource(AnyUrl(uri))
        if not result.contents:
            return ""
        resource = result.contents[0]
        if isinstance(resource, types.TextResourceContents):
            return resource.text
        return str(resource)

    async def cleanup(self) -> None:
        await self.exit_stack.aclose()


# --- Standalone demo: one round-trip of each primitive ----------------------

async def _demo(server_path: str) -> None:
    client = SimpleMCPClient()
    try:
        await client.connect_to_server(server_path)

        print("\n— tools/call: web_search('model context protocol') —")
        result = await client.call_tool(
            "web_search", {"query": "model context protocol", "max_results": 2}
        )
        print(result.content[0].text[:400], "…")

        print("\n— tools/call: write_file —")
        result = await client.call_tool(
            "write_file", {"path": "hello-mcp.md", "content": "# Hello from MCP\n"}
        )
        print(result.content[0].text)

        print("\n— resources/read: workspace://files —")
        print(await client.read_resource("workspace://files"))
    finally:
        await client.cleanup()


if __name__ == "__main__":
    import asyncio
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "./mcp_server.py"
    asyncio.run(_demo(path))
