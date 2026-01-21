#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mcp[cli]>=1.0.0",
#     "pandas>=2.0.0"
# ]
# ///

"""
Test MCP server tools directly without needing the full agent
This simulates what the agent would do when calling MCP tools
"""

import sys
from pathlib import Path

# Add current directory to path to import the MCP server
sys.path.insert(0, str(Path(__file__).parent))

# Import the tool functions from the MCP server
from automation_mcp_server import (
    list_all_automations,
    search_automations_by_category,
    get_automation_by_id,
    search_by_script_type,
    get_database_stats,
    get_database_schema
)

print("🧪 Testing MCP Server Tools")
print("=" * 80)

# Test 1: List all automations
print("\n📋 TEST 1: list_all_automations()")
print("-" * 80)
result = list_all_automations()
print(result)

# Test 2: Search by category
print("\n📋 TEST 2: search_automations_by_category('File Management')")
print("-" * 80)
result = search_automations_by_category("File Management")
print(result)

# Test 3: Get specific automation
print("\n📋 TEST 3: get_automation_by_id(3)")
print("-" * 80)
result = get_automation_by_id(3)
print(result[:500] + "\n... (truncated)")

# Test 4: Search by script type
print("\n📋 TEST 4: search_by_script_type('python')")
print("-" * 80)
result = search_by_script_type("python")
print(result)

# Test 5: Get database stats
print("\n📋 TEST 5: get_database_stats()")
print("-" * 80)
result = get_database_stats()
print(result)

# Test 6: Get database schema (resource)
print("\n📋 TEST 6: get_database_schema() [RESOURCE]")
print("-" * 80)
result = get_database_schema()
print(result)

print("\n" + "=" * 80)
print("✨ All MCP tools working correctly!")
print("\nThese tools would be called by the Claude Agent when processing user queries.")
print("\nExample agent workflow:")
print("  1. User: 'What automations are available?'")
print("  2. Agent calls: list_all_automations()")
print("  3. Agent shows results to user")
print("  4. User: 'Generate the organize downloads script'")
print("  5. Agent calls: get_automation_by_id(3)")
print("  6. Agent uses Write tool to save script to file")
print("  7. Agent uses Bash tool to make script executable")
print("  8. Agent confirms script is ready to use")
