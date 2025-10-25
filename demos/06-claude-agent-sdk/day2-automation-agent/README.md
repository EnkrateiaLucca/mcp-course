# Day 2: Building an Automation Agent with Claude Agent SDK + MCP

**Duration**: 60 minutes
**Difficulty**: Intermediate
**Prerequisites**: Completion of Day 1, Python 3.10+, Node.js, Anthropic API key

## 🎯 Learning Objectives

By the end of this session, you will:

1. Integrate multiple MCP servers in a single agent
2. Create custom in-process MCP tools for database operations
3. Build complex multi-step automation workflows
4. Generate and test automation scripts automatically
5. Implement production-ready error handling
6. Track task status and manage workflows via database

## 💡 What You'll Build

An **Automation Agent** that:
- Reads automation task requirements from a SQLite database
- Generates complete, production-ready Python scripts
- Saves scripts to the filesystem via MCP
- Tests generated scripts automatically
- Updates database with completion status
- Handles errors gracefully throughout the workflow

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│              Claude Automation Agent                │
│                                                     │
│  ┌─────────────────┐      ┌───────────────────┐   │
│  │  Database MCP   │      │  Filesystem MCP   │   │
│  │  (In-Process)   │      │  (External)       │   │
│  │                 │      │                   │   │
│  │  • get_tasks    │      │  • write_file     │   │
│  │  • update_task  │      │  • read_file      │   │
│  │  • get_summary  │      │  • list_dir       │   │
│  └────────┬────────┘      └─────────┬─────────┘   │
│           │                         │             │
│           └──────────┬──────────────┘             │
│                      │                             │
│           ┌──────────▼──────────┐                 │
│           │  Workflow Engine    │                 │
│           │  1. Read from DB    │                 │
│           │  2. Generate script │                 │
│           │  3. Save to FS      │                 │
│           │  4. Test script     │                 │
│           │  5. Update DB       │                 │
│           └─────────────────────┘                 │
└─────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Installation

```bash
# Install required packages
pip install claude-agent-sdk anthropic python-dotenv

# Or use UV (recommended)
uv pip install claude-agent-sdk anthropic python-dotenv
```

### Set API Key

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Run the Demo

```bash
# With UV (handles dependencies)
uv run automation_agent.py

# Or traditional Python
python automation_agent.py
```

## 📖 Course Materials

### Interactive Notebook

The notebook provides comprehensive coverage with interactive examples:

```bash
# Install Jupyter
pip install jupyter

# Launch the notebook
jupyter notebook 02-building-automation-agent.ipynb
```

**Notebook Contents:**
1. Database setup with automation tasks
2. Creating custom MCP database tools
3. Multi-server integration
4. Complete automation workflow
5. Error handling and validation
6. Monitoring with hooks
7. Production patterns

### Standalone Demo Script

The `automation_agent.py` script is a complete, runnable example:

**Features:**
- ✅ Automatic database creation and seeding
- ✅ 5 realistic automation tasks
- ✅ Production-ready script generation
- ✅ Status tracking and reporting
- ✅ Verification and testing
- ✅ Clean error handling

## 🔧 Understanding the Components

### 1. Database Schema

```sql
CREATE TABLE automation_tasks (
    id INTEGER PRIMARY KEY,
    task_name TEXT NOT NULL,
    description TEXT NOT NULL,
    requirements TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    script_path TEXT,
    test_result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Fields:**
- `task_name`: Brief name of the automation
- `description`: What the automation does
- `requirements`: Detailed specifications
- `status`: pending | in_progress | completed | failed
- `script_path`: Location of generated script
- `test_result`: Test execution results

### 2. Custom Database Tools

We create in-process MCP tools for database access:

```python
@tool(
    name="get_pending_tasks",
    description="Retrieve all pending automation tasks",
    input_schema={}
)
async def get_pending_tasks(args):
    # Query database for pending tasks
    # Return formatted task list
    pass

@tool(
    name="update_task_status",
    description="Update task status and results",
    input_schema={
        "task_id": int,
        "status": str,
        "script_path": str,
        "test_result": str
    }
)
async def update_task_status(args):
    # Update database record
    # Return confirmation
    pass
```

**Why In-Process?**
- ⚡ No subprocess overhead
- 🔒 Direct access to Python objects (DB_PATH)
- 🚀 Better performance
- 🎯 Type safety

### 3. Multi-Server Configuration

Combining in-process and external MCP servers:

```python
options = ClaudeAgentOptions(
    mcp_servers={
        # In-process: custom database tools
        "database": create_sdk_mcp_server(
            name="automation-db",
            tools=[get_pending_tasks, update_task_status]
        ),

        # External: filesystem operations
        "filesystem": {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", scripts_dir]
        }
    }
)
```

### 4. Agent Workflow

The agent follows a structured workflow:

```
1. Query Database
   ↓
2. Read Task Requirements
   ↓
3. Generate Python Script
   ↓
4. Save to Filesystem
   ↓
5. Verify Creation
   ↓
6. Update Database Status
   ↓
7. Report Results
```

## 📚 Sample Automation Tasks

The demo includes 5 realistic automation tasks:

### 1. File Organizer
Organize files by extension into subdirectories

### 2. Log Analyzer
Extract and analyze error patterns from log files

### 3. CSV Data Validator
Validate CSV files against predefined rules

### 4. Backup Creator
Create timestamped backups with automatic cleanup

### 5. Duplicate File Finder
Find duplicate files using content hashing

Each task includes:
- Clear requirements
- Expected features
- Error handling needs
- Usage examples

## 🛠️ Hands-On Exercise

### Challenge: Extend the System

Add a new automation task to the database:

```python
# Task: Code Documentation Generator
task = (
    "Code Documentation Generator",
    "Generate API documentation from Python code",
    """Create a Python script that:
1. Takes a Python file or directory as input
2. Extracts docstrings from classes and functions
3. Generates markdown documentation
4. Includes function signatures and parameter types
5. Creates a table of contents
6. Saves output to docs/api.md

Example usage:
  python doc_generator.py myproject/ --output docs/api.md
"""
)

# Insert into database
cursor.execute(
    "INSERT INTO automation_tasks (task_name, description, requirements) VALUES (?, ?, ?)",
    task
)
```

Run the agent to generate this script!

## 📊 Advanced Patterns

### Pattern 1: Batch Processing

Process multiple tasks in sequence:

```python
async def process_all_tasks():
    options = ClaudeAgentOptions(
        system_prompt="""Process ALL pending tasks in the database.
        Work through them one at a time, generating scripts for each.""",
        mcp_servers={...},
        max_turns=50  # Allow many iterations
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("Process all pending automation tasks")
        async for msg in client.receive_response():
            print(msg, end="", flush=True)
```

### Pattern 2: Validation Pipeline

Add validation before saving:

```python
@tool(
    name="validate_script",
    description="Validate Python script syntax",
    input_schema={"code": str}
)
async def validate_script(args):
    try:
        compile(args["code"], "<string>", "exec")
        return {"content": [{"type": "text", "text": "✅ Script is valid"}]}
    except SyntaxError as e:
        return {"content": [{"type": "text", "text": f"❌ Syntax error: {e}"}]}
```

### Pattern 3: Testing Generated Scripts

Run basic tests on generated scripts:

```python
import subprocess

@tool(
    name="test_script",
    description="Test a generated script with --help flag",
    input_schema={"script_path": str}
)
async def test_script(args):
    try:
        result = subprocess.run(
            ["python", args["script_path"], "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            return {
                "content": [{
                    "type": "text",
                    "text": f"✅ Test passed\n\nOutput:\n{result.stdout}"
                }]
            }
        else:
            return {
                "content": [{
                    "type": "text",
                    "text": f"❌ Test failed\n\nError:\n{result.stderr}"
                }]
            }
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {e}"}]}
```

### Pattern 4: Progress Tracking

Monitor agent progress with hooks:

```python
progress = {"scripts_generated": 0, "tasks_completed": 0}

async def progress_hook(input_data, tool_use_id, context):
    tool_name = input_data.get("tool_name", "")

    if "update_task_status" in tool_name:
        progress["tasks_completed"] += 1
        print(f"\n📊 Progress: {progress['tasks_completed']} tasks completed")

    return {}

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [HookMatcher(matcher="*", hooks=[progress_hook])]
    }
)
```

## 🎓 Real-World Applications

This pattern can be adapted for:

### DevOps Automation
```
Requirements DB → Deployment Scripts → Cloud Infrastructure
```

### Data Pipeline Generation
```
Schema Definitions → ETL Scripts → Data Warehouse
```

### Test Suite Creation
```
User Stories → Test Cases → Automated Tests
```

### Documentation Automation
```
Code Analysis → Documentation → Published Docs
```

### Migration Tools
```
Schema Comparison → Migration Scripts → Database Updates
```

## 🐛 Troubleshooting

### Issue: "Database is locked"

SQLite can have locking issues with concurrent access.

**Solution:**
```python
# Add timeout and retry logic
conn = sqlite3.connect(db_path, timeout=10.0)
conn.execute("PRAGMA busy_timeout = 10000")
```

### Issue: Generated scripts have syntax errors

**Solution:**
Add validation before saving:

```python
import ast

def validate_python_syntax(code: str) -> bool:
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False
```

### Issue: Filesystem MCP server timeout

Large file operations can timeout.

**Solution:**
```python
# Increase max_turns for complex operations
options = ClaudeAgentOptions(
    max_turns=50,  # More iterations allowed
    # ... other options
)
```

### Issue: Database not updating

Check return values from tools.

**Solution:**
```python
# Always return proper structure
return {
    "content": [{
        "type": "text",
        "text": "Success message or error"
    }]
}
```

## 📈 Performance Optimization

### 1. Use In-Process MCP for Performance

In-process servers are faster than external ones:

```python
# Fast: In-process
database_server = create_sdk_mcp_server(...)

# Slower: External process
filesystem_server = {"type": "stdio", ...}
```

### 2. Batch Database Operations

```python
# Good: Single query
cursor.executemany("INSERT INTO ...", tasks)

# Bad: Multiple queries
for task in tasks:
    cursor.execute("INSERT INTO ...", task)
```

### 3. Limit Agent Iterations

```python
options = ClaudeAgentOptions(
    max_turns=20,  # Reasonable limit
    # Prevents runaway loops
)
```

## 🔒 Production Considerations

### Security

```python
# Sanitize database inputs
import sqlite3

def safe_query(task_id: int):
    # Use parameterized queries
    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    )
    # Never use string formatting for SQL
```

### Error Handling

```python
@tool(...)
async def robust_tool(args):
    try:
        # Tool logic
        result = process_data(args)
        return {"content": [{"type": "text", "text": result}]}

    except ValueError as e:
        # Specific error handling
        return {"content": [{"type": "text", "text": f"Invalid input: {e}"}]}

    except Exception as e:
        # Catch-all
        return {"content": [{"type": "text", "text": f"Error: {e}"}]}
```

### Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@tool(...)
async def logged_tool(args):
    logger.info(f"Tool called with: {args}")
    # ... tool logic ...
    logger.info("Tool completed successfully")
```

## 📚 Additional Resources

### Documentation
- [Claude Agents SDK](https://docs.claude.com/en/api/agent-sdk/overview)
- [MCP in the SDK](https://docs.claude.com/en/api/agent-sdk/mcp)
- [SQLite Python](https://docs.python.org/3/library/sqlite3.html)

### Example Projects
- [MCP Servers Repository](https://github.com/modelcontextprotocol/servers)
- [SQLite MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite)

### Community
- [Anthropic Discord](https://discord.gg/anthropic)
- [MCP Community](https://github.com/topics/mcp)

## 🎯 Key Takeaways

### What You Learned

1. **Multi-Server Integration**
   - Combining in-process and external MCP servers
   - When to use each type
   - Performance trade-offs

2. **Complex Workflows**
   - Multi-step automation processes
   - Database-driven task management
   - Automatic script generation

3. **Production Patterns**
   - Error handling in tools
   - Status tracking and updates
   - Validation and testing
   - Activity monitoring with hooks

4. **Agent Design**
   - Clear, detailed system prompts
   - Appropriate iteration limits
   - Monitoring and control mechanisms

### Skills Acquired

- ✅ Create custom MCP tools
- ✅ Integrate multiple data sources
- ✅ Build complex automation workflows
- ✅ Generate code from requirements
- ✅ Track and manage task state
- ✅ Handle errors gracefully
- ✅ Monitor agent activity

## 🚀 Next Steps

### Immediate Extensions

1. **Add More Task Types**
   - Web scraping automation
   - Report generation
   - Data transformation pipelines

2. **Improve Testing**
   - Unit test generation
   - Integration testing
   - Test coverage reporting

3. **Add More MCP Servers**
   - Git for version control
   - Slack for notifications
   - Cloud storage for deployment

### Advanced Topics

1. **Parallel Processing**
   - Process multiple tasks concurrently
   - Use asyncio.gather() for parallel execution

2. **Deployment**
   - Containerize with Docker
   - Deploy to cloud platforms
   - Add REST API wrapper

3. **Monitoring & Observability**
   - Add metrics collection
   - Implement dashboards
   - Set up alerting

## 🏁 Conclusion

You've now built a sophisticated automation agent that:
- Reads requirements from a database
- Generates production-ready code
- Manages complex workflows
- Tracks status and results

This foundation can be adapted to numerous real-world automation scenarios, from DevOps to data engineering to test automation.

**Congratulations on completing Day 2!** 🎉

You now have the skills to build powerful, intelligent automation systems with Claude Agents SDK and MCP.
