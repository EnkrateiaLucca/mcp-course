#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp[cli]>=1.9.3"]
# ///
"""Minimal MCP client — pure protocol layer, no UI.

Wraps an stdio MCP server connection and exposes the three primitives we
care about: list_tools, call_tool, read_resource. Used by `mcp_host.py`.

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
        params = StdioServerParameters(command="python", args=[server_path], env=None)
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
