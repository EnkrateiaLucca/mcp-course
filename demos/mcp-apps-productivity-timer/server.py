#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp[cli]>=2.3,<3"]
# ///
"""Minimal MCP App: a productivity timer rendered inside the chat."""
from pathlib import Path

from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

APP_URI = "ui://productivity-timer/timer.html"
HTML = Path(__file__).parent / "timer.html"

mcp = MCPServer("productivity-timer")


@mcp.tool(meta={"ui": {"resourceUri": APP_URI}})
def start_timer(minutes: int = 25, label: str = "Focus", autostart: bool = True) -> dict:
    """Start a countdown timer in the chat. Use for pomodoros, breaks, or any timed focus block."""
    return {"minutes": minutes, "label": label, "autostart": autostart}


@mcp.resource(APP_URI, mime_type="text/html;profile=mcp-app")
def timer_app() -> str:
    return HTML.read_text()


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        stateless_http=True,
        json_response=True,
        transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
    )
