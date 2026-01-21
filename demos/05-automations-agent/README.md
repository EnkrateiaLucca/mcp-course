# Automation Agent: Claude Agent SDK + MCP Integration

A practical example demonstrating how to build an AI agent that generates automation scripts by querying a database through MCP (Model Context Protocol).

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [How It Works](#how-it-works)
- [File Breakdown](#file-breakdown)
- [Example Workflows](#example-workflows)
- [Learning Objectives](#learning-objectives)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This demo shows how to combine three powerful technologies:

1. **MCP (Model Context Protocol)** - Standardized way to provide tools and data to AI
2. **Claude Agent SDK** - Framework for building AI agents with tool use
3. **Automation Database** - Simple CSV storage for script templates

The result is an intelligent agent that can:
- Browse available automation scripts
- Search by category or language
- Generate executable scripts on demand
- Explain how to use each automation

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Input                            │
│              "Generate a file backup script"                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   Automation Agent                           │
│                 (Claude Agent SDK)                           │
│                                                              │
│  • Understands user intent                                   │
│  • Decides which tools to use                                │
│  • Orchestrates workflow                                     │
└───────┬──────────────────────────────────┬──────────────────┘
        │                                   │
        │ Queries                           │ File Operations
        ▼                                   ▼
┌──────────────────────┐         ┌─────────────────────────┐
│   MCP Server         │         │   Built-in Tools        │
│ (automation_mcp_     │         │                         │
│  server.py)          │         │  • Write (create files) │
│                      │         │  • Bash (chmod +x)      │
│  Tools:              │         │  • Glob (find files)    │
│  • list_all_auto..   │         └─────────────────────────┘
│  • search_by_cat..   │
│  • get_auto_by_id    │
│  • search_by_type    │
│  • get_db_stats      │
└──────┬───────────────┘
       │
       │ Reads from
       ▼
┌──────────────────────┐
│  Automation Database │
│ (CSV File)           │
│                      │
│  • ID                │
│  • Name              │
│  • Description       │
│  • Category          │
│  • Script Type       │
│  • Template          │
└──────────────────────┘
```

### Data Flow

1. **User Request** → Agent receives natural language query
2. **Tool Selection** → Agent chooses appropriate MCP tools
3. **Database Query** → MCP server queries CSV database
4. **Template Retrieval** → Full script template returned
5. **File Creation** → Agent uses Write tool to create file
6. **Permissions** → Agent uses Bash tool to make executable
7. **Response** → Agent explains what was created and how to use it

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- UV package manager (recommended) or standard Python environment
- Anthropic API key

### Setup

```bash
# 1. Set your API key
export ANTHROPIC_API_KEY='your-api-key-here'

# 2. Navigate to the demo directory
cd demos/05-automations-agent

# 3. Run the agent (UV handles dependencies automatically)
uv run automation_agent.py
```

### First Interaction

```
👤 You: What automations are available?

🤖 Agent: I'll check the automation database for you...

[Agent lists all available automations with descriptions]

👤 You: Generate the file backup automation

🤖 Agent: I'll create the backup_files.sh script for you...

[Agent creates the script and explains how to use it]
```

## 🔍 How It Works

### Step 1: Database Setup

The `automations_database.csv` contains pre-defined automation templates:

```csv
id,name,description,category,script_type,template
1,backup_files,Backup important files...,File Management,bash,"#!/bin/bash..."
2,clean_temp_files,Remove temporary files...,System Maintenance,bash,"#!/bin/bash..."
...
```

Each entry includes:
- **Metadata**: ID, name, description, category, script type
- **Template**: Complete, ready-to-use script code

### Step 2: MCP Server Provides Tools

The MCP server (`automation_mcp_server.py`) exposes tools:

```python
@mcp.tool()
def list_all_automations() -> str:
    """Browse all available automations"""
    df = pd.read_csv(DB_PATH)
    return df.to_string()

@mcp.tool()
def get_automation_by_id(automation_id: int) -> str:
    """Get full script template"""
    df = pd.read_csv(DB_PATH)
    automation = df[df['id'] == automation_id]
    return automation['template'].iloc[0]
```

**Key Concept**: MCP tools are functions that the agent can call. The MCP server handles data access, keeping the agent focused on orchestration.

### Step 3: Agent Integration

The agent (`automation_agent.py`) connects to the MCP server:

```python
# Configure MCP server connection
mcp_config = MCPServerConfig(
    command="uv",
    args=["run", "--script", str(MCP_SERVER_PATH)]
)

# Create agent with MCP server and built-in tools
agent = Agent(
    name="automation-generator",
    instructions=SYSTEM_INSTRUCTIONS,
    mcp_servers=[mcp_config],  # Attach MCP server
    tools=[Write, Bash, Glob],  # Add file operation tools
    model="claude-sonnet-4-5-20250929"
)
```

**Key Concept**: The agent has access to both MCP tools (for data queries) and built-in tools (for file operations).

### Step 4: Agent Workflow

When you ask "Generate the backup files automation":

1. **Understanding** - Agent parses your request
2. **Discovery** - Agent calls `list_all_automations` to find it
3. **Retrieval** - Agent calls `get_automation_by_id(1)` to get template
4. **Creation** - Agent uses `Write` tool to create `backup_files.sh`
5. **Permissions** - Agent uses `Bash` tool for `chmod +x backup_files.sh`
6. **Response** - Agent explains the script and how to use it

## 📁 File Breakdown

### `automations_database.csv`

**Purpose**: Storage for automation script templates

**Structure**:
- Simple CSV format for easy editing
- 7 pre-configured automations covering common tasks
- Each row is a complete automation template

**Categories**:
- File Management (backup, organize)
- System Maintenance (cleanup, monitoring)
- Database Operations (backup)
- Version Control (auto-commit)
- Reporting (generate reports)

### `automation_mcp_server.py`

**Purpose**: MCP server that provides database query tools

**Key Components**:

```python
# Tool Definition Pattern
@mcp.tool(
    name="tool_name",
    description="What this tool does (visible to agent)"
)
def tool_function(params) -> str:
    # Tool implementation
    return result
```

**Tools Provided**:
1. `list_all_automations` - Browse all automations
2. `search_automations_by_category` - Filter by category
3. `get_automation_by_id` - Retrieve full template
4. `search_by_script_type` - Filter by language (bash/python)
5. `get_database_stats` - Database overview

**Resource Provided**:
- `automation://database/schema` - Database structure documentation

**How to Test**:
```bash
# Run MCP Inspector to test tools interactively
mcp dev automation_mcp_server.py
```

### `automation_agent.py`

**Purpose**: Claude Agent that orchestrates automation generation

**Key Components**:

#### 1. System Instructions
```python
SYSTEM_INSTRUCTIONS = """
You are an Automation Script Generator Agent...
Your workflow:
1. List/search automations
2. Retrieve template
3. Write to file
4. Make executable
5. Provide usage instructions
"""
```

**Why Important**: Instructions guide the agent's behavior and workflow understanding.

#### 2. MCP Server Configuration
```python
mcp_config = MCPServerConfig(
    command="uv",
    args=["run", "--script", str(MCP_SERVER_PATH)]
)
```

**Why Important**: Tells the agent how to launch and communicate with the MCP server.

#### 3. Built-in Tools
```python
tools = [
    builtin_tools.Write(allowed_directories=[str(OUTPUT_DIR)]),
    builtin_tools.Glob(allowed_directories=[str(OUTPUT_DIR)]),
    builtin_tools.Bash(enabled=True)
]
```

**Why Important**: Gives the agent file system capabilities while restricting access for safety.

#### 4. Agent Creation
```python
agent = Agent(
    name="automation-generator",
    instructions=SYSTEM_INSTRUCTIONS,
    mcp_servers=[mcp_config],
    tools=tools,
    model="claude-sonnet-4-5-20250929"
)
```

**Why Important**: Combines everything into a functional agent.

#### 5. Execution
```python
response = await agent.run_async(
    task=user_input,
    stream=False
)
```

**Why Important**: Runs the agent with user query and returns response.

### `generated_scripts/` (Created at Runtime)

**Purpose**: Output directory for generated automation scripts

**Contents**: Scripts created by the agent based on database templates

**Example**:
```bash
generated_scripts/
├── backup_files.sh         # Generated bash script
├── organize_downloads.py   # Generated Python script
└── monitor_disk_space.py   # Generated Python script
```

## 💡 Example Workflows

### Workflow 1: Browse and Generate

```
👤 You: What automations are available?

🤖 Agent: [Lists all 7 automations with descriptions]

👤 You: Tell me more about the file management automations

🤖 Agent: [Filters and shows backup_files and organize_downloads]

👤 You: Generate the organize downloads script

🤖 Agent: [Creates organize_downloads.py and explains usage]
```

### Workflow 2: Direct Request

```
👤 You: I need a script to monitor disk space

🤖 Agent: [Searches database, finds monitor_disk_space, generates script]

         I've created monitor_disk_space.py for you!

         Usage: python monitor_disk_space.py <path> <threshold>
         Example: python monitor_disk_space.py / 80
```

### Workflow 3: Category Search

```
👤 You: Show me all system maintenance automations

🤖 Agent: [Calls search_automations_by_category("System Maintenance")]

         Found 2 system maintenance automations:
         1. clean_temp_files - Remove old temporary files
         2. monitor_disk_space - Monitor disk space and alert
```

## 🎓 Learning Objectives

By studying this demo, you'll understand:

### 1. MCP Fundamentals
- ✅ How to create MCP servers with FastMCP
- ✅ Tool definition patterns and best practices
- ✅ Resource exposure for static content
- ✅ Error handling in MCP tools

### 2. Claude Agent SDK
- ✅ Agent initialization and configuration
- ✅ MCP server attachment (in-process)
- ✅ Built-in tools (Write, Bash, Glob)
- ✅ Tool permission configuration
- ✅ Async agent execution patterns

### 3. Integration Patterns
- ✅ Combining MCP tools with built-in tools
- ✅ Data access through MCP, file operations through built-ins
- ✅ Agent workflow orchestration
- ✅ Interactive vs programmatic usage

### 4. Best Practices
- ✅ Clear system instructions for agent behavior
- ✅ Descriptive tool descriptions (agent reads these!)
- ✅ Directory restrictions for safety
- ✅ Error handling and user feedback
- ✅ Structured data in databases for agent consumption

## 🔧 Customization Ideas

### Add More Automations

Edit `automations_database.csv`:

```csv
8,your_automation,Description here,Category,bash,"#!/bin/bash\n..."
```

### Add New Tool Categories

In `automation_mcp_server.py`:

```python
@mcp.tool()
def search_by_custom_field(value: str) -> str:
    """Your custom search logic"""
    df = pd.read_csv(DB_PATH)
    # Filter logic here
    return results
```

### Enhance Agent Instructions

In `automation_agent.py`, modify `SYSTEM_INSTRUCTIONS`:

```python
SYSTEM_INSTRUCTIONS = """
[Your custom instructions]
- Additional workflow steps
- New behaviors
- Safety guidelines
"""
```

### Change Output Format

Modify the agent to generate different file formats or add comments:

```python
# In system instructions
"Always add detailed comments explaining each section of the script"
```

## 🐛 Troubleshooting

### Issue: "ANTHROPIC_API_KEY not set"

**Solution**:
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

### Issue: "Database file not found"

**Solution**: Ensure you're running from the correct directory:
```bash
cd demos/05-automations-agent
uv run automation_agent.py
```

### Issue: "Permission denied" writing files

**Solution**: Check that `generated_scripts/` directory exists and is writable:
```bash
mkdir -p generated_scripts
chmod 755 generated_scripts
```

### Issue: MCP server not connecting

**Solution**: Test the MCP server independently:
```bash
mcp dev automation_mcp_server.py
```

This opens a web interface to test tools directly.

### Issue: Agent not using MCP tools

**Solution**: Check that:
1. MCP server path is correct in `automation_agent.py`
2. MCP server runs without errors: `uv run automation_mcp_server.py`
3. System instructions mention the MCP tools

## 📚 Additional Resources

### Official Documentation
- [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python)
- [MCP Specification](https://modelcontextprotocol.io/specification/)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk)

### Related Demos
- `demos/01-introduction-to-mcp/` - Basic MCP concepts
- `demos/03-claude-agents-sdk-filesystem-agent/` - More Agent SDK examples
- `demos/04-query-tabular-data/` - Similar CSV querying patterns

## 🎯 Next Steps

1. **Run the demo** - Get hands-on experience with the agent
2. **Add your own automation** - Extend the database with custom scripts
3. **Modify the agent** - Change behavior through system instructions
4. **Create new tools** - Add additional MCP tools for advanced queries
5. **Build your own** - Use this as a template for other agent projects

## 💻 Code Examples

### Adding a New Automation Programmatically

```python
import pandas as pd

# Load database
df = pd.read_csv('automations_database.csv')

# Add new automation
new_row = {
    'id': len(df) + 1,
    'name': 'my_automation',
    'description': 'My custom automation',
    'category': 'Custom',
    'script_type': 'python',
    'template': '#!/usr/bin/env python3\nprint("Hello")'
}

df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
df.to_csv('automations_database.csv', index=False)
```

### Using the Agent Programmatically

```python
import asyncio
from automation_agent import generate_automation_programmatically

# Generate specific automation
response = asyncio.run(
    generate_automation_programmatically(
        automation_id=3,
        output_filename="my_script.py"
    )
)

print(response.final_messages[-1].content)
```

---

**Built with ❤️ for the MCP Course**

*Questions? Check the main course README or open an issue on GitHub.*
