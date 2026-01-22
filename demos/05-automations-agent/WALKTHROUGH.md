# Automation Generator: Claude Agent + MCP

A simple demo showing how to build an AI agent that queries an automation database via MCP and generates scripts.

## What This Demo Does

You ask the agent about automation scripts, and it:
1. Queries a CSV database using MCP tools
2. Retrieves script templates
3. Generates the scripts to a folder
4. Explains how to use them

## Architecture

```
┌─────────────────────┐
│      User           │
│  "Show me scripts"  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────┐
│   automation_agent.py       │
│   (Claude Agent SDK)        │
└────────┬────────────────────┘
         │
         │ MCP Tools
         ▼
┌─────────────────────────────┐
│  automation_mcp_server.py   │
│  - list_automations         │
│  - get_automation           │
└────────┬────────────────────┘
         │
         │ Reads CSV
         ▼
┌─────────────────────────────┐
│  automations_database.csv   │
│  Script templates database  │
└─────────────────────────────┘
```

## Quick Start

### Prerequisites

```bash
# Set your API key
export ANTHROPIC_API_KEY='your-key-here'
```

### Run the Agent

```bash
cd 05-automations-agent
uv run automation_agent.py
```

### Try It

```
You: What automations are available?

[Agent lists all scripts from database]

You: Generate the backup files automation

[Agent creates backup_files.sh in generated_scripts/]
```

## File Breakdown

### 1. automations_database.csv

A simple CSV with automation templates:

| id | name | description | category | script_type | template |
|----|------|-------------|----------|-------------|----------|
| 1 | backup_files | Backup files script | File Management | bash | #!/bin/bash... |

Contains 7 pre-built automation scripts.

### 2. automation_mcp_server.py

**An MCP server that provides database tools.**

```python
from mcp.server.fastmcp import FastMCP
import pandas as pd

mcp = FastMCP("automation-database")

@mcp.tool(
    name="list_automations",
    description="List all available automation scripts"
)
def list_automations() -> str:
    df = pd.read_csv(DB_PATH)
    return df[['id', 'name', 'description']].to_string()

@mcp.tool(
    name="get_automation",
    description="Get script template by ID"
)
def get_automation(automation_id: int) -> str:
    # Returns full script template
    ...
```

**Key Points:**
- Uses FastMCP for quick setup
- Two simple tools: list and get
- Returns data from CSV database
- Runs on stdio transport (perfect for agent integration)

### 3. automation_agent.py

**Claude agent that uses the MCP server.**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    model="claude-sonnet-4-5",
    system_prompt="You help generate automation scripts...",
    mcp_servers={
        "automation-db": {
            "type": "stdio",
            "command": "uv",
            "args": ["run", "automation_mcp_server.py"]
        }
    },
    permission_mode="bypassPermissions",
)

async for message in query(prompt=user_input, options=options):
    print(message, end="", flush=True)
```

**Key Points:**
- Uses Claude Agent SDK (simple query interface)
- Connects to MCP server via stdio
- Streams responses to user
- Handles file writing automatically

## How It Works

### Step 1: User asks a question
```
You: Show me file management automations
```

### Step 2: Agent calls MCP tool
Agent uses `list_automations` tool from MCP server.

### Step 3: MCP server queries database
```python
def list_automations():
    df = pd.read_csv("automations_database.csv")
    return df[['id', 'name', 'description', 'category']].to_string()
```

### Step 4: Agent gets results
Returns formatted list of automations.

### Step 5: User requests generation
```
You: Generate automation ID 1
```

### Step 6: Agent retrieves template
Uses `get_automation(1)` to get full script.

### Step 7: Agent writes file
Creates `generated_scripts/backup_files.sh` with the template.

### Step 8: Agent explains usage
Provides instructions on how to run the script.

## Key Concepts

### MCP (Model Context Protocol)

MCP standardizes how AI agents access tools and data:

- **Tools** - Functions the agent can call (list_automations, get_automation)
- **Transport** - How agent communicates with server (stdio)
- **Server** - Provides the tools (automation_mcp_server.py)

### Claude Agent SDK

Simplified SDK for building Claude-powered agents:

- **ClaudeAgentOptions** - Configuration for model, prompts, MCP servers
- **query()** - Simple function to run agent queries
- **Streaming** - Real-time response streaming
- **MCP Integration** - Built-in MCP server support

### Why This Pattern Works

**Separation of Concerns:**
- MCP server = Data access layer
- Agent = Intelligence layer
- CSV database = Storage layer

**Benefits:**
- Clean, maintainable code
- Easy to test each component
- Can swap out database without changing agent
- Can reuse MCP server in other agents

## Testing the MCP Server

Test the server independently:

```bash
mcp dev automation_mcp_server.py
```

This opens a web interface where you can test tools directly.

## Customization

### Add New Automations

Edit `automations_database.csv`:

```csv
8,new_script,My new automation,Custom,python,"#!/usr/bin/env python3
print('Hello')"
```

### Add New Tools

In `automation_mcp_server.py`:

```python
@mcp.tool(
    name="search_by_category",
    description="Search automations by category"
)
def search_by_category(category: str) -> str:
    df = pd.read_csv(DB_PATH)
    return df[df['category'] == category].to_string()
```

### Modify Agent Behavior

In `automation_agent.py`, update the `system_prompt`:

```python
system_prompt="""
Your custom instructions here...
- Always add detailed comments
- Use consistent naming
- Etc.
"""
```

## Common Issues

**"ANTHROPIC_API_KEY not set"**
```bash
export ANTHROPIC_API_KEY='your-key'
```

**"Database file not found"**
Make sure you're in the right directory:
```bash
cd 05-automations-agent
```

**MCP server not connecting**
Test the server independently:
```bash
mcp dev automation_mcp_server.py
```

## Next Steps

1. Run the demo and try different queries
2. Add your own automation to the CSV
3. Create a new MCP tool for searching
4. Modify the system prompt to change agent behavior
5. Build your own agent using this pattern!

## Related Examples

- `live-demo-from-scratch/` - PDF analysis agent (similar pattern)
- `03-claude-agents-sdk-filesystem-agent/` - More Claude SDK examples
- `04-query-tabular-data/` - Similar CSV querying patterns

---

**Built for O'Reilly MCP Course - Simple, Clean, Educational**
