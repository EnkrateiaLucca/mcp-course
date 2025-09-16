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