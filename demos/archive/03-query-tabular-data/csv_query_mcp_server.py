#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "mcp[cli]>=1.12,<2",
#     "pandas>=2.0.0",
#     "matplotlib>=3.0.0",
# ]
# ///

"""
CSV Query MCP Server

A simple MCP server that provides tools to query and analyze CSV data.
This demonstrates how to create custom tools for data access using MCP.

Based on MCP Python SDK documentation:
https://github.com/modelcontextprotocol/python-sdk
"""

from mcp.server.fastmcp import FastMCP, Image
import pandas as pd
from typing import List, Optional
import os
import sys
import io
import matplotlib
matplotlib.use("Agg")  # non-interactive backend — required for headless/subprocess environments
import matplotlib.pyplot as plt

# initialize my FastMCP server
mcp = FastMCP("query-catalog-mcp")

# Path to the CSV file (or path to the product catalog db.)
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), "sample_data.csv")


@mcp.tool(
    name="get_all_products",
    description="Get all products from the csv file"
)
def get_all_products() -> str:
    """
    Get all products from the CSV file.

    Returns:
        A string representation of all products.
    """
    # not necessarily the best approach because if the data was massive this would clog the context window
    df = pd.read_csv(CSV_FILE_PATH)
    return df.to_string(index=False)

if __name__ == "__main__":
    # Run the MCP server with stdio transport
    print("Starting Product Catalog Server...", file=sys.stderr)
    mcp.run(transport="stdio")