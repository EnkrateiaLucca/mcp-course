# /// script
# requires-python = ">=3.12"
# dependencies = ["mcp[cli]==1.9.3"]
# ///

from mcp.server.fastmcp import FastMCP
from datetime import datetime

mcp = FastMCP("get-time")

@mcp.tool()
def get_current_time() -> str:
    return datetime.now().isoformat()

mcp.run(transport="stdio")