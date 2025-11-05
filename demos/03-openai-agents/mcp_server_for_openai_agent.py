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
from mcp import types
import os
from datetime import datetime
from typing import List

DOCS_DIR = "./docs/"

# Create MCP server instance with a descriptive name
mcp = FastMCP("mcp-server-file-access")


@mcp.tool()
def write_file(file_name: str, file_contents: str) -> str:
    """
    Write contents to a file.

    Args:
        file_name: The name of the file to write.
        file_contents: The contents to write to the file.
    """
    with open(file_name, "w") as f:
        f.write(file_contents)
    return file_name

@mcp.tool()
def read_file(file_name: str) -> str:
    """
    Read the contents of a file.
    """
    with open(file_name, "r") as f:
        return f.read()

@mcp.tool()
def list_files(dir_path: str) -> str:
    """
    Lists the files in a given folder.
    """
    return os.listdir(dir_path)

@mcp.tool()
def get_current_time() -> str:
    """
    Get the current time.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    mcp.run(transport="stdio")