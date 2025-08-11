#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["mcp[cli]==1.9.3", "uvicorn", "starlette"]
# ///

from datetime import datetime
from starlette.applications import Starlette
from starlette.routing import Mount
from contextlib import AsyncExitStack, asynccontextmanager
from mcp.server.fastmcp import FastMCP

# Can you read this comment?
mcp = FastMCP("basic-demo")

@mcp.tool()
def get_current_time() -> str:
    return datetime.now().isoformat()

@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    return a + b

@mcp.tool()
def write_file_lucas_teaches(file_name: str, file_content: str) -> str:
    with open(file_name, "w") as f:
        f.write(file_content)
    return file_name

@mcp.resource("joke://silly_joke.txt")
def silly_joke() -> str:
    with open("./silly_joke.txt", "r") as f:
        return f.read() 


@asynccontextmanager
async def lifespan(app):
    async with AsyncExitStack() as stack:
        # IMPORTANT for streamable-http when mounting in Starlette
        await stack.enter_async_context(mcp.session_manager.run())
        yield

app = Starlette(
    debug=True,
    routes=[
        # Mount anywhere you like; final endpoint = <mount prefix> + "/mcp"
        Mount("/", app=mcp.streamable_http_app()),
    ],
    lifespan=lifespan,
)

if __name__ == "__main__":
    print("🚀 Basic MCP (streamable-http)")
    print("📡 Server: http://localhost:8000")
    print("🔧 MCP endpoint: http://localhost:8000/mcp")  # <-- correct path
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
    # run it with:
    # uv run ./basic_server.py
    # run the inspector with:
    # mcp dev ./basic_server.py
