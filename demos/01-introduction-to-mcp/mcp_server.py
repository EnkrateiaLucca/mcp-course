#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["mcp[cli]==1.9.3"]
# ///

from datetime import datetime
from mcp.server.fastmcp import FastMCP
import logging

# Can you read this comment?
mcp = FastMCP("basic-demo")

# automatically generating the schemas! Which are helpful for the LLM to understand the inputs and outputs of the tools.
@mcp.tool()
def get_current_time() -> str:
    return datetime.now().isoformat()

@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    return a + b

@mcp.tool() #automates generating the schemas!!
def write_file(file_name: str, file_content: str) -> str:
    with open(file_name, "w") as f:
        f.write(file_content)
    return file_name

@mcp.resource("docs://documents.txt")
def get_docs() -> str:
    with open("./documents.txt", "r") as f:
        return f.read() 

if __name__ == "__main__":
    logging.info("🚀 Basic MCP (stdio)")
    mcp.run(transport="stdio")
    # the way the communication with this server will happen
    # is via running it as a command in the terminal
    
    # run it with:
    # uv run ./mcp_server.py
    # run the inspector with:
    # mcp dev ./mcp_server.py
    
