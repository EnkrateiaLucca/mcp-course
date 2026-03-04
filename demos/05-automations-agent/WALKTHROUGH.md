# Automation Agent: Claude Agent SDK + MCP

An agent that writes, tests, and runs Python scripts — demonstrating how MCP provides
**constrained capabilities** to an AI agent.

## Architecture

```
┌─────────────────────────┐
│        User              │
│  "Make a CSV converter"  │
└───────────┬──────────────┘
            │
            ▼
┌──────────────────────────────┐
│   automation_agent.py         │
│   Claude Agent SDK            │
│   - Understands the request   │
│   - Writes Python code        │
│   - Tests and iterates        │
└───────────┬──────────────────┘
            │ MCP (stdio)
            ▼
┌──────────────────────────────┐
│   automation_mcp_server.py    │
│   FastMCP Server              │
│   - save_script(name, code)   │
│   - list_scripts()            │
│   - read_script(name)         │
│   - run_script(name, args)    │
│   - delete_script(name)       │
└───────────┬──────────────────┘
            │
            ▼
┌──────────────────────────────┐
│   generated_scripts/          │
│   Sandboxed directory         │
│   - hello.py                  │
│   - csv_converter.py          │
│   - ...                       │
└──────────────────────────────┘
```

## The Key Idea: MCP as a Capability Boundary

The MCP server doesn't just "expose tools" — it defines a **security sandbox**:

| What the agent CAN do          | What the agent CANNOT do        |
|--------------------------------|----------------------------------|
| Save .py files to one folder   | Write files anywhere on disk     |
| Run scripts with 30s timeout   | Run arbitrary shell commands     |
| Read scripts it created        | Access files outside the sandbox |
| Delete scripts it created      | Install packages or modify system|

This is the core MCP pattern: **constrained, auditable capabilities**.

## Quick Start

```bash
export ANTHROPIC_API_KEY='your-key'
cd demos/05-automations-agent
uv run automation_agent.py
```

## Try These Prompts

```
You: Create a script that finds all duplicate files in a given folder

You: Write a CSV to JSON converter

You: Make a script that generates a random password

You: List my scripts

You: Run password_generator.py
```

## File Breakdown

### automation_mcp_server.py — The Capability Layer

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("script-sandbox")

@mcp.tool()
def save_script(filename: str, code: str) -> str:
    """Save a Python script to the scripts directory."""
    # Validates filename, writes to sandboxed directory
    ...

@mcp.tool()
def run_script(filename: str, args: str = "") -> str:
    """Run a script with 30-second timeout."""
    # subprocess.run with capture_output and timeout
    ...
```

5 tools total: `save_script`, `list_scripts`, `read_script`, `run_script`, `delete_script`

### automation_agent.py — The Intelligence Layer

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    model="claude-sonnet-4-5",
    system_prompt="You are a Python automation assistant...",
    mcp_servers={
        "scripts": {
            "type": "stdio",
            "command": "uv",
            "args": ["run", "automation_mcp_server.py"],
        }
    },
    permission_mode="bypassPermissions",
)

# Interactive loop
async for message in query(prompt=user_input, options=options):
    print(message, end="", flush=True)
```

## How the Agent Workflow Looks

1. User: "Create a password generator"
2. Agent writes Python code
3. Agent calls `save_script("password_generator.py", code)`
4. Agent calls `run_script("password_generator.py")` to test it
5. If errors → agent reads output, fixes code, saves again, re-runs
6. Reports back with the working script and output

## Key Concepts for the Course

### MCP Tools vs Raw Shell Access

Instead of giving the agent `Bash` access (dangerous!), we give it **specific tools**
with **built-in guardrails**:
- Filename validation (no path traversal)
- Execution timeouts (no infinite loops)
- Confined to one directory (no system access)

### Claude Agent SDK

The SDK handles the agent loop:
- Sends user prompt to Claude
- Claude decides which MCP tools to call
- SDK executes the tools via MCP
- Claude sees results, decides next action
- Streams responses back to user

### stdio Transport

Agent ↔ MCP server communication uses stdio (stdin/stdout):
- Agent spawns the MCP server as a subprocess
- Sends JSON-RPC messages over stdin
- Receives responses over stdout
- No network setup needed

## Testing the MCP Server Alone

```bash
mcp dev automation_mcp_server.py
```

This opens the MCP Inspector — a web UI where you can test each tool independently.

## Extending This Demo

**Add a new tool** to the MCP server:
```python
@mcp.tool()
def lint_script(filename: str) -> str:
    """Check a script for common issues."""
    # Run py_compile or basic checks
    ...
```

**Change the agent's focus** by editing the system prompt:
```python
system_prompt="You specialize in data processing scripts..."
```
