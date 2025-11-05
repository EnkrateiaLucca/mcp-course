#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "mcp[cli]>=1.0.0",
#     "pandas>=2.0.0"
# ]
# ///

"""
CSV Query MCP Server

A simple MCP server that provides tools to query and analyze CSV data.
This demonstrates how to create custom tools for data access using MCP.

Based on MCP Python SDK documentation:
https://github.com/modelcontextprotocol/python-sdk
"""

from mcp.server.fastmcp import FastMCP
import pandas as pd
from typing import List, Optional
import os

# Initialize FastMCP server
mcp = FastMCP("csv-query-server")

# Path to the CSV file
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), "sample_data.csv")


@mcp.tool(
    name="get_all_products",
    description="Get all products from the CSV file"
)
def get_all_products() -> str:
    """
    Get all products from the CSV file.

    Returns:
        A string representation of all products.
    """
    df = pd.read_csv(CSV_FILE_PATH)
    return df.to_string(index=False)


@mcp.tool(
    name="search_products_by_category",
    description="Search for products by category"
)
def search_products_by_category(category: str) -> str:
    """
    Search for products by category.

    Args:
        category: The category to filter by (e.g., "Electronics", "Furniture")

    Returns:
        A string representation of filtered products.
    """
    df = pd.read_csv(CSV_FILE_PATH)
    filtered_df = df[df['category'].str.lower() == category.lower()]

    if filtered_df.empty:
        return f"No products found in category: {category}"

    return filtered_df.to_string(index=False)


@mcp.tool(
    name="search_products_by_price_range",
    description="Search for products by price range"
)
def search_products_by_price_range(min_price: float, max_price: float) -> str:
    """
    Search for products within a price range.

    Args:
        min_price: Minimum price
        max_price: Maximum price

    Returns:
        A string representation of products in the price range.
    """
    df = pd.read_csv(CSV_FILE_PATH)
    filtered_df = df[(df['price'] >= min_price) & (df['price'] <= max_price)]

    if filtered_df.empty:
        return f"No products found between ${min_price} and ${max_price}"

    return filtered_df.to_string(index=False)


@mcp.tool(
    name="get_product_by_name",
    description="Get details of a specific product by name"
)
def get_product_by_name(product_name: str) -> str:
    """
    Get details of a specific product by name.

    Args:
        product_name: The name of the product to search for

    Returns:
        Product details as a string.
    """
    df = pd.read_csv(CSV_FILE_PATH)
    filtered_df = df[df['product_name'].str.contains(product_name, case=False, na=False)]

    if filtered_df.empty:
        return f"No product found with name containing: {product_name}"

    return filtered_df.to_string(index=False)


@mcp.tool(
    name="get_top_rated_products",
    description="Get the top-rated products"
)
def get_top_rated_products(limit: int = 5) -> str:
    """
    Get the top-rated products.

    Args:
        limit: Number of top products to return (default: 5)

    Returns:
        A string representation of top-rated products.
    """
    df = pd.read_csv(CSV_FILE_PATH)
    top_products = df.nlargest(limit, 'rating')
    return top_products.to_string(index=False)


@mcp.tool(
    name="get_products_in_stock",
    description="Get products that have at least the specified stock level"
)
def get_products_in_stock(min_stock: int = 1) -> str:
    """
    Get products that have at least the specified stock level.

    Args:
        min_stock: Minimum stock level (default: 1)

    Returns:
        A string representation of products in stock.
    """
    df = pd.read_csv(CSV_FILE_PATH)
    in_stock_df = df[df['stock'] >= min_stock]
    return in_stock_df.to_string(index=False)


@mcp.tool(
    name="get_category_statistics",
    description="Get statistics about products grouped by category"
)
def get_category_statistics() -> str:
    """
    Get statistics about products grouped by category.

    Returns:
        Statistics including count, average price, and average rating per category.
    """
    df = pd.read_csv(CSV_FILE_PATH)
    stats = df.groupby('category').agg({
        'product_id': 'count',
        'price': 'mean',
        'rating': 'mean',
        'stock': 'sum'
    }).round(2)

    stats.columns = ['count', 'avg_price', 'avg_rating', 'total_stock']
    return stats.to_string()


if __name__ == "__main__":
    # Run the MCP server with stdio transport
    print("Starting CSV Query MCP Server...")
    mcp.run(transport="stdio")
