#!/usr/bin/env python3
"""
Automation Agent - Day 2 Demo
==============================

An intelligent agent that creates and tests automation scripts from database requirements.

This demo showcases:
- Multi-server MCP integration (database + filesystem)
- Complex multi-step workflows
- Script generation from natural language
- Database-driven task management
- Automatic testing and validation
- Production-ready patterns

Usage:
    python automation_agent.py

    # Or with UV
    uv run automation_agent.py

Requirements:
- Python 3.10+
- Node.js (for MCP filesystem server)
- ANTHROPIC_API_KEY environment variable

# /// script
# dependencies = [
#   "claude-agent-sdk>=0.1.0",
#   "anthropic>=0.40.0",
#   "python-dotenv>=1.0.0",
# ]
# ///
"""

import asyncio
import os
import sqlite3
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from claude_agent_sdk import (
    tool,
    create_sdk_mcp_server,
    ClaudeSDKClient,
    ClaudeAgentOptions,
    HookMatcher
)


# Global database path (set by setup_database)
DB_PATH = None
SCRIPTS_DIR = None


def create_automation_database(db_path: str):
    """Create and populate the automation tasks database"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tasks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS automation_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT NOT NULL,
            description TEXT NOT NULL,
            requirements TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            script_path TEXT,
            test_result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Sample automation tasks
    tasks = [
        (
            "File Organizer",
            "Organize files in a directory by file extension",
            """Create a Python script that:
1. Takes a directory path as command-line argument
2. Scans all files in the directory (not subdirectories)
3. Creates subdirectories for each unique file extension found
4. Moves files into their respective extension directories
5. Prints a summary showing files moved for each extension
6. Handles errors gracefully (permissions, etc.)

Example output:
  Organized 15 files:
  - txt: 5 files
  - pdf: 3 files
  - jpg: 7 files
"""
        ),
        (
            "Log Analyzer",
            "Extract and analyze error patterns from log files",
            """Create a Python script that:
1. Reads a log file specified as command-line argument
2. Searches for lines containing 'ERROR', 'CRITICAL', or 'FATAL'
3. Extracts error messages and groups by error type
4. Counts occurrences of each unique error pattern
5. Outputs a summary report with:
   - Total error count
   - Top 5 most frequent errors
   - Timestamp of first and last occurrence
6. Optionally saves report to a file

Example usage:
  python log_analyzer.py app.log --output report.txt
"""
        ),
        (
            "CSV Data Validator",
            "Validate CSV files against predefined rules",
            """Create a Python script that:
1. Reads a CSV file specified as command-line argument
2. Validates the following:
   - Required columns exist (configurable list)
   - No null/empty values in required fields
   - Data types match expectations (numbers, dates, emails)
   - Value ranges are within bounds (if applicable)
3. Generates a validation report showing:
   - Number of rows validated
   - List of validation errors with row numbers
   - Overall pass/fail status
4. Supports a --strict flag for stricter validation

Example usage:
  python csv_validator.py data.csv --required id,name,email --strict
"""
        ),
        (
            "Backup Creator",
            "Create timestamped backups with automatic cleanup",
            """Create a Python script that:
1. Takes source directory and backup destination as arguments
2. Creates a ZIP archive with timestamp in filename
3. Saves backup to specified backup directory
4. Implements automatic cleanup:
   - Removes backups older than specified days (default: 30)
   - Keeps at least N most recent backups (default: 5)
5. Provides options for:
   - Compression level
   - Exclude patterns (e.g., *.tmp, .git/)
   - Dry-run mode
6. Prints detailed summary of backup and cleanup operations

Example usage:
  python backup_creator.py /data /backups --keep-days 30 --keep-count 5
"""
        ),
        (
            "Duplicate File Finder",
            "Find and report duplicate files based on content hash",
            """Create a Python script that:
1. Scans a directory recursively for files
2. Computes MD5 or SHA256 hash for each file
3. Identifies duplicate files (same hash)
4. Groups duplicates and reports:
   - File paths for each duplicate group
   - File sizes
   - Total space wasted by duplicates
5. Provides options to:
   - Delete duplicates (keep oldest/newest)
   - Create hard links to save space
   - Export report to JSON/CSV
6. Includes safety features (confirmation prompts)

Example usage:
  python duplicate_finder.py /home/user --algorithm sha256 --report dupes.json
"""
        )
    ]

    cursor.executemany(
        "INSERT INTO automation_tasks (task_name, description, requirements) VALUES (?, ?, ?)",
        tasks
    )

    conn.commit()
    conn.close()

    return len(tasks)


# ============================================================================
# MCP Database Tools (In-Process)
# ============================================================================

@tool(
    name="get_pending_tasks",
    description="Retrieve all pending automation tasks from the database",
    input_schema={}
)
async def get_pending_tasks(args):
    """Get all tasks with 'pending' status"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, task_name, description, requirements, status
            FROM automation_tasks
            WHERE status = 'pending'
            ORDER BY id
        """)

        tasks = cursor.fetchall()
        conn.close()

        if not tasks:
            return {"content": [{"type": "text", "text": "No pending tasks found."}]}

        result = "PENDING AUTOMATION TASKS\n" + "=" * 70 + "\n\n"

        for task_id, name, desc, reqs, status in tasks:
            result += f"Task ID: {task_id}\n"
            result += f"Name: {name}\n"
            result += f"Description: {desc}\n"
            result += f"\nRequirements:\n{reqs}\n"
            result += f"\nStatus: {status}\n"
            result += "=" * 70 + "\n\n"

        return {"content": [{"type": "text", "text": result}]}

    except Exception as e:
        return {"content": [{"type": "text", "text": f"Database error: {str(e)}"}]}


@tool(
    name="get_task_by_id",
    description="Get a specific task by its ID",
    input_schema={"task_id": int}
)
async def get_task_by_id(args):
    """Retrieve a specific task"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, task_name, description, requirements, status
            FROM automation_tasks
            WHERE id = ?
        """, (args.get("task_id"),))

        task = cursor.fetchone()
        conn.close()

        if not task:
            return {"content": [{"type": "text", "text": f"Task {args.get('task_id')} not found."}]}

        task_id, name, desc, reqs, status = task
        result = f"""Task Details:
ID: {task_id}
Name: {name}
Description: {desc}
Status: {status}

Requirements:
{reqs}
"""

        return {"content": [{"type": "text", "text": result}]}

    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}]}


@tool(
    name="update_task_status",
    description="Update the status and results of an automation task",
    input_schema={
        "task_id": int,
        "status": str,
        "script_path": str,
        "test_result": str
    }
)
async def update_task_status(args):
    """Update task in database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Build update query dynamically based on provided fields
        updates = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
        values = [args.get("status", "completed")]

        if args.get("script_path"):
            updates.append("script_path = ?")
            values.append(args.get("script_path"))

        if args.get("test_result"):
            updates.append("test_result = ?")
            values.append(args.get("test_result"))

        values.append(args.get("task_id"))

        cursor.execute(
            f"UPDATE automation_tasks SET {', '.join(updates)} WHERE id = ?",
            values
        )

        conn.commit()
        affected = cursor.rowcount
        conn.close()

        if affected == 0:
            return {"content": [{"type": "text", "text": f"Task {args.get('task_id')} not found"}]}

        return {
            "content": [{
                "type": "text",
                "text": f"✅ Successfully updated task {args.get('task_id')} to status: {args.get('status')}"
            }]
        }

    except Exception as e:
        return {"content": [{"type": "text", "text": f"Update error: {str(e)}"}]}


@tool(
    name="get_all_tasks_summary",
    description="Get a summary of all automation tasks and their current status",
    input_schema={}
)
async def get_all_tasks_summary(args):
    """Get overview of all tasks"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Get counts by status
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM automation_tasks
            GROUP BY status
        """)

        status_counts = dict(cursor.fetchall())

        # Get all tasks
        cursor.execute("""
            SELECT id, task_name, status, script_path, test_result
            FROM automation_tasks
            ORDER BY id
        """)

        tasks = cursor.fetchall()
        conn.close()

        result = "AUTOMATION TASKS SUMMARY\n" + "=" * 70 + "\n\n"
        result += "Status Overview:\n"
        for status, count in status_counts.items():
            result += f"  {status}: {count} task(s)\n"
        result += "\n" + "=" * 70 + "\n\n"

        result += "Individual Tasks:\n\n"
        for task_id, name, status, script_path, test_result in tasks:
            status_icon = "✅" if status == "completed" else "⏳" if status == "in_progress" else "📋"
            result += f"{status_icon} [{task_id}] {name}\n"
            result += f"    Status: {status}\n"
            if script_path:
                result += f"    Script: {script_path}\n"
            if test_result:
                result += f"    Test: {test_result}\n"
            result += "\n"

        return {"content": [{"type": "text", "text": result}]}

    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}]}


# ============================================================================
# Agent Setup and Execution
# ============================================================================

def setup_environment():
    """Set up demo environment with database and directories"""
    global DB_PATH, SCRIPTS_DIR

    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix="claude_automation_")

    # Set paths
    DB_PATH = os.path.join(temp_dir, "automation_tasks.db")
    SCRIPTS_DIR = os.path.join(temp_dir, "generated_scripts")
    os.makedirs(SCRIPTS_DIR, exist_ok=True)

    # Create and populate database
    task_count = create_automation_database(DB_PATH)

    print("=" * 70)
    print("🛠️  ENVIRONMENT SETUP")
    print("=" * 70)
    print(f"📁 Working directory: {temp_dir}")
    print(f"🗄️  Database: {DB_PATH}")
    print(f"📁 Scripts directory: {SCRIPTS_DIR}")
    print(f"📝 Created {task_count} automation tasks")
    print("=" * 70)
    print()

    return temp_dir


async def run_automation_agent(task_limit: int = 1):
    """
    Run the automation agent to process tasks

    Args:
        task_limit: Number of tasks to process (default: 1)
    """

    # Create MCP database server with our tools
    database_server = create_sdk_mcp_server(
        name="automation-db",
        version="1.0.0",
        tools=[
            get_pending_tasks,
            get_task_by_id,
            update_task_status,
            get_all_tasks_summary
        ]
    )

    # Configure the agent
    options = ClaudeAgentOptions(
        system_prompt=f"""You are an expert Python automation engineer and code generator.

Your task is to create automation scripts based on requirements from a database.

WORKFLOW:
1. Use get_pending_tasks to see what needs to be done
2. For the first {task_limit} pending task(s):
   a. Read the full requirements carefully
   b. Create a complete, production-ready Python script that implements ALL requirements
   c. Include proper:
      - Docstrings and comments
      - Error handling (try/except)
      - Command-line argument parsing (argparse)
      - Usage examples in docstring
      - Main guard (if __name__ == "__main__")
   d. Save the script with a descriptive filename (lowercase with underscores)
   e. Verify the script was saved correctly by reading it back
   f. Update the database with status='completed' and the script path

IMPORTANT:
- Write complete, executable scripts (not partial code)
- Follow Python best practices (PEP 8)
- Include comprehensive error handling
- Make scripts user-friendly with clear help messages
- Test your work by verifying files were created

Be thorough and professional. Each script should be production-ready.
""",

        mcp_servers={
            "database": database_server,  # In-process database tools
            "filesystem": {  # External filesystem server
                "type": "stdio",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", SCRIPTS_DIR]
            }
        },

        max_turns=30  # Allow multiple iterations for complex tasks
    )

    print("=" * 70)
    print("🤖 AUTOMATION AGENT STARTING")
    print("=" * 70)
    print(f"📊 Will process up to {task_limit} task(s)")
    print(f"💾 Scripts will be saved to: {SCRIPTS_DIR}")
    print("=" * 70)
    print()

    try:
        async with ClaudeSDKClient(options=options) as client:
            # Send the main workflow query
            await client.query(f"""
Please execute the automation workflow for {task_limit} task(s).

Start by getting the pending tasks, then work through them systematically.
For each task, create a complete Python script and update the database.

Take your time and be thorough.
""")

            # Stream the agent's response
            async for msg in client.receive_response():
                print(msg, end="", flush=True)

        print("\n\n" + "=" * 70)
        print("✅ AGENT EXECUTION COMPLETED")
        print("=" * 70)

    except Exception as e:
        print(f"\n\n❌ Error during agent execution: {e}")
        raise


def verify_results():
    """Verify and display results"""
    print("\n" + "=" * 70)
    print("📊 VERIFICATION & RESULTS")
    print("=" * 70)

    # Check generated scripts
    print("\n📁 Generated Scripts:")
    scripts = list(Path(SCRIPTS_DIR).glob("*.py"))

    if scripts:
        for script in sorted(scripts):
            size = script.stat().st_size
            lines = len(script.read_text().splitlines())
            print(f"   ✅ {script.name}")
            print(f"      Size: {size:,} bytes | Lines: {lines}")
    else:
        print("   ⚠️  No scripts found")

    # Check database status
    print("\n" + "=" * 70)
    print("\n🗄️  Database Status:")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get status summary
    cursor.execute("""
        SELECT status, COUNT(*) as count
        FROM automation_tasks
        GROUP BY status
    """)

    for status, count in cursor.fetchall():
        icon = "✅" if status == "completed" else "⏳"
        print(f"   {icon} {status}: {count} task(s)")

    # Get detailed task list
    print("\n   Detailed Task List:")
    cursor.execute("""
        SELECT id, task_name, status, script_path
        FROM automation_tasks
        ORDER BY id
    """)

    for task_id, name, status, script_path in cursor.fetchall():
        status_icon = "✅" if status == "completed" else "⏳"
        print(f"   {status_icon} [{task_id}] {name}")
        if script_path:
            print(f"       Script: {Path(script_path).name}")

    conn.close()

    print("\n" + "=" * 70)


async def main():
    """Main entry point"""

    # Load environment variables
    load_dotenv()

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("=" * 70)
        print("❌ ERROR: ANTHROPIC_API_KEY not found!")
        print("=" * 70)
        print("\nPlease set your Anthropic API key:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        print("\nOr create a .env file with:")
        print("  ANTHROPIC_API_KEY=your-api-key-here")
        print()
        return

    # Setup environment
    temp_dir = setup_environment()

    try:
        # Run the automation agent
        await run_automation_agent(task_limit=2)  # Process 2 tasks

        # Verify results
        verify_results()

    finally:
        # Cleanup option
        print("\n🧹 Cleanup:")
        print(f"   Temporary files are in: {temp_dir}")
        print(f"   Database: {DB_PATH}")
        print(f"   Scripts: {SCRIPTS_DIR}")

        cleanup = input("\n   Delete temporary files? (y/N): ").strip().lower()
        if cleanup == 'y':
            shutil.rmtree(temp_dir)
            print("   ✅ Cleaned up temporary files")
        else:
            print(f"   📁 Files preserved for inspection: {temp_dir}")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║              AUTOMATION AGENT - DAY 2 DEMO                           ║
║              Claude Agents SDK + MCP Integration                     ║
╚══════════════════════════════════════════════════════════════════════╝

This demo showcases an intelligent automation agent that:
  • Reads automation requirements from a SQLite database
  • Generates complete Python scripts from natural language
  • Saves scripts to the filesystem via MCP
  • Updates the database with completion status
  • Handles multiple tasks in a workflow

Key Features:
  ✓ Multi-server MCP integration (database + filesystem)
  ✓ Complex multi-step workflows
  ✓ Production-ready script generation
  ✓ Database-driven task management
  ✓ Automatic status tracking

═══════════════════════════════════════════════════════════════════════
""")

    asyncio.run(main())
