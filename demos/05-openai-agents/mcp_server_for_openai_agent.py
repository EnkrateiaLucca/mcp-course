#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "mcp[cli]==1.9.3",
#     "pydantic>=2.0.0"
# ]
# ///

"""
SImple mcp server

Perfect for integrating your personal knowledge management system with AI assistants.

Based on MCP Python SDK documentation:
https://github.com/modelcontextprotocol/python-sdk
"""

from mcp.server.fastmcp import FastMCP

# Create MCP server instance with a descriptive name
mcp = FastMCP("example-pancakes-server")


@mcp.tool()
def create_pancake_recipe(file_name: str) -> str:
    print(f"Creating pancake recipe in {file_name}")
    with open(file_name, "w") as f:
        f.write("This is a pancake recipe.")
    print(f"Pancake recipe created in {file_name}")
    return file_name

if __name__ == "__main__":
    mcp.run(transport="stdio")