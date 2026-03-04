#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["mcp[cli]==1.9.3"]
# ///

from datetime import datetime
from mcp.server.fastmcp import FastMCP
import logging

mcp = FastMCP("basic-demo")

# (creates the schema for the tool)
@mcp.tool() # this registers the function as an mcp tool 
def get_current_time() -> str:
    """Gets current time"""
    return datetime.now().isoformat()

@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    """Adds 2 numbers (floats) together"""
    return a + b

@mcp.tool()
def write_file(file_name: str, file_contents: str) -> str:
    with open(file_name, "w") as f:
        f.write(file_contents)
    
    return file_name + " created successfully!"

@mcp.resource("docs://documents.txt")
def get_docs() -> str:
    with open("./documents.txt", "r") as f:
        return f.read()

if __name__=="__main__":
    logging.info("Basic MCP Test! (stdio)")
    mcp.run(transport="stdio")

print(get_current_time())