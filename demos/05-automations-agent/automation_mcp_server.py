# /// script
# requires-python = ">=3.12"
# dependencies = ["mcp[cli]>=1.0.0", "pandas>=2.0.0"]
# ///

from mcp.server.fastmcp import FastMCP
import pandas as pd
import os

mcp = FastMCP("automation-database")

DB_PATH = os.path.join(os.path.dirname(__file__), "automations_database.csv")

@mcp.tool(
    name="list_automations",
    description="List all available automation scripts with their ID, name, and description"
)
def list_automations() -> str:
    df = pd.read_csv(DB_PATH)
    return df[['id', 'name', 'description', 'category']].to_string(index=False)

@mcp.tool(
    name="get_automation",
    description="Get the full script template for a specific automation by ID"
)
def get_automation(automation_id: int) -> str:
    df = pd.read_csv(DB_PATH)
    automation = df[df['id'] == automation_id]

    if automation.empty:
        return f"No automation found with ID: {automation_id}"

    auto = automation.iloc[0]
    return f"""ID: {auto['id']}
Name: {auto['name']}
Description: {auto['description']}
Script Type: {auto['script_type']}

Template:
{auto['template']}"""

if __name__ == "__main__":
    print("Starting Automation MCP Server...")
    mcp.run(transport="stdio")
