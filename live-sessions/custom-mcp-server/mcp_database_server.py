#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["mcp[cli]==1.9.3", "pandas>=2.0.0"]
# ///

# Above is inline metadata for running single independent scripts 
# with uv: https://docs.astral.sh/uv/guides/scripts/
# Dependencies for running the code with uv

from mcp.server.fastmcp import FastMCP
import pandas as pd

# Can you read this comment?
mcp = FastMCP("query-csv")

@mcp.tool()
def query_sample_data_from_csv(csv_path: str) -> str:
    """
    Simple function to query and return data from a CSV file.
    """
    try:
        df = pd.read_csv(csv_path)
        df_sample = df.sample(n=50)
        return df_sample.to_string(index=False)
    except Exception as e:
        return f"Error reading CSV: {e}"

@mcp.tool()
def get_sales_summary(csv_path: str) -> str:
    """
    Calculate and return total sales, average order value, and total quantity sold from the CSV.
    """
    try:
        df = pd.read_csv(csv_path)
        total_sales = df["total_amount"].sum()
        avg_order_value = df["total_amount"].mean()
        total_quantity = df["quantity"].sum()
        # Formatting summary
        summary = (
            f"Total Sales: ${total_sales:,.2f}\n"
            f"Average Order Value: ${avg_order_value:,.2f}\n"
            f"Total Quantity Sold: {total_quantity:,}"
        )
        return summary
    except Exception as e:
        return f"Error in sales summary: {e}"

@mcp.tool()
def top_products_by_category(csv_path: str, category: str, n: int = 5) -> str:
    """
    Show the top N selling products (by total sales amount) for a given category from the CSV.
    """
    try:
        df = pd.read_csv(csv_path)
        df_cat = df[df["category"].str.lower() == category.lower()]
        if df_cat.empty:
            return f"No data found for category: {category}"
        top_products = (
            df_cat.groupby("product")["total_amount"].sum()
            .sort_values(ascending=False)
            .head(n)
        )
        result = f"Top {n} products in '{category}':\n"
        for product, total in top_products.items():
            result += f"- {product}: ${total:,.2f}\n"
        return result.strip()
    except Exception as e:
        return f"Error finding top products: {e}"

@mcp.tool()
def top_customers(csv_path: str, metric: str = "orders", n: int = 5) -> str:
    """
    Show the top N customers ranked by a chosen metric.
    metric can be: "orders" (number of orders), "spending" (total amount spent), or "quantity" (total items bought).
    """
    try:
        df = pd.read_csv(csv_path)
        # Detect the customer column
        customer_col = None
        for col in df.columns:
            if col.lower() in ("customer", "customer_name", "user", "user_name", "client"):
                customer_col = col
                break
        if customer_col is None:
            return f"No customer column found. Available columns: {', '.join(df.columns)}"

        if metric == "orders":
            ranked = df.groupby(customer_col).size().sort_values(ascending=False).head(n)
            label = "orders"
        elif metric == "spending":
            ranked = df.groupby(customer_col)["total_amount"].sum().sort_values(ascending=False).head(n)
            label = "total spent"
        elif metric == "quantity":
            ranked = df.groupby(customer_col)["quantity"].sum().sort_values(ascending=False).head(n)
            label = "items bought"
        else:
            return f"Unknown metric '{metric}'. Use 'orders', 'spending', or 'quantity'."

        result = f"Top {n} customers by {label}:\n"
        for i, (customer, value) in enumerate(ranked.items(), 1):
            formatted = f"${value:,.2f}" if metric == "spending" else f"{value:,}"
            result += f"{i}. {customer}: {formatted}\n"
        return result.strip()
    except Exception as e:
        return f"Error finding top customers: {e}"


@mcp.tool()
def customer_order_history(csv_path: str, customer_name: str) -> str:
    """
    Show all orders for a specific customer, including products, quantities, and amounts.
    """
    try:
        df = pd.read_csv(csv_path)
        # Detect the customer column
        customer_col = None
        for col in df.columns:
            if col.lower() in ("customer", "customer_name", "user", "user_name", "client"):
                customer_col = col
                break
        if customer_col is None:
            return f"No customer column found. Available columns: {', '.join(df.columns)}"

        orders = df[df[customer_col].str.lower() == customer_name.lower()]
        if orders.empty:
            return f"No orders found for customer: {customer_name}"

        total_spent = orders["total_amount"].sum()
        result = f"Order history for {customer_name} ({len(orders)} orders, ${total_spent:,.2f} total):\n"
        for _, row in orders.iterrows():
            result += f"- {row.get('product', 'N/A')} | Qty: {row.get('quantity', 'N/A')} | ${row.get('total_amount', 0):,.2f}\n"
        return result.strip()
    except Exception as e:
        return f"Error fetching order history: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
    