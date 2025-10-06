#!/usr/bin/env python3
"""
Production-ready MCP Server with tools, resources, and prompts
This server provides task management capabilities for the OpenAI agent
"""


from datetime import datetime
import asyncio
import json
import os
import sqlite3
from typing import List, Dict, Optional
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP


# Initialize the MCP server
mcp = FastMCP("task-management-server")

# Data models
class Task(BaseModel):
    """Task model for task management"""
    id: str
    title: str
    description: str
    status: str  # pending, in_progress, completed
    priority: int  # 1-5, 5 being highest
    created_at: str
    updated_at: str
    due_date: Optional[str] = None
    assignee: Optional[str] = None
    tags: List[str] = []

# In-memory task storage (in production, use a proper database)
tasks_db: Dict[str, Task] = {}

# SQLite persistence helpers
DB_PATH = os.path.join(os.path.dirname(__file__), "tasks.db")

def ensure_db_initialized() -> None:
    """Ensure the database is initialized before any operation."""
    if not os.path.exists(DB_PATH):
        init_db()

def init_db() -> None:
    """Initialize the SQLite database and create the tasks table if needed."""
    # Ensure the database file exists by creating it if it doesn't
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL,
                priority INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                due_date TEXT,
                assignee TEXT,
                tags TEXT
            )
            """
        )

def save_task_to_db(task: Task) -> None:
    """Insert or replace a task record in the database."""
    ensure_db_initialized()
    tags_json = json.dumps(task.tags or [])
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO tasks (
                id, title, description, status, priority,
                created_at, updated_at, due_date, assignee, tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task.id,
                task.title,
                task.description,
                task.status,
                int(task.priority),
                task.created_at,
                task.updated_at,
                task.due_date,
                task.assignee,
                tags_json,
            ),
        )

def update_task_in_db(task: Task) -> None:
    """Update an existing task's fields in the database."""
    ensure_db_initialized()
    tags_json = json.dumps(task.tags or [])
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            UPDATE tasks
            SET title = ?, description = ?, status = ?, priority = ?,
                created_at = ?, updated_at = ?, due_date = ?, assignee = ?, tags = ?
            WHERE id = ?
            """,
            (
                task.title,
                task.description,
                task.status,
                int(task.priority),
                task.created_at,
                task.updated_at,
                task.due_date,
                task.assignee,
                tags_json,
                task.id,
            ),
        )

def delete_task_from_db(task_id: str) -> None:
    """Delete a task from the database by ID."""
    ensure_db_initialized()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

def load_tasks_from_db() -> None:
    """Load tasks from the database into the in-memory cache."""
    if not os.path.exists(DB_PATH):
        return
    ensure_db_initialized()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            """
            SELECT id, title, description, status, priority,
                   created_at, updated_at, due_date, assignee, tags
            FROM tasks
            """
        )
        tasks_db.clear()
        for (
            row_id,
            title,
            description,
            status,
            priority,
            created_at,
            updated_at,
            due_date,
            assignee,
            tags_json,
        ) in cursor.fetchall():
            try:
                tags_list = json.loads(tags_json) if tags_json else []
            except Exception:
                tags_list = []
            tasks_db[row_id] = Task(
                id=row_id,
                title=title,
                description=description,
                status=status,
                priority=int(priority),
                created_at=created_at,
                updated_at=updated_at,
                due_date=due_date,
                assignee=assignee,
                tags=tags_list,
            )

# Helper functions
def generate_task_id() -> str:
    """Generate a unique task ID"""
    return f"task_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

def serialize_task(task: Task) -> dict:
    """Convert task to dictionary"""
    return task.model_dump()

# MCP Tools
@mcp.tool()
async def create_task(
    title: str,
    description: str,
    priority: int = 3,
    due_date: Optional[str] = None,
    assignee: Optional[str] = None,
    tags: List[str] = []
) -> dict:
    """
    Create a new task with the given details.
    Priority ranges from 1 (lowest) to 5 (highest).
    """
    task_id = generate_task_id()
    now = datetime.now().isoformat()

    task = Task(
        id=task_id,
        title=title,
        description=description,
        status="pending",
        priority=max(1, min(5, priority)),  # Ensure priority is between 1-5
        created_at=now,
        updated_at=now,
        due_date=due_date,
        assignee=assignee,
        tags=tags
    )

    tasks_db[task_id] = task
    # Persist to SQLite
    save_task_to_db(task)

    return {
        "success": True,
        "task": serialize_task(task),
        "message": f"Task '{title}' created successfully with ID {task_id}"
    }

@mcp.tool()
async def update_task_status(task_id: str, new_status: str) -> dict:
    """
    Update the status of an existing task.
    Valid statuses: pending, in_progress, completed
    """
    if task_id not in tasks_db:
        return {
            "success": False,
            "error": f"Task {task_id} not found"
        }

    valid_statuses = ["pending", "in_progress", "completed"]
    if new_status not in valid_statuses:
        return {
            "success": False,
            "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        }

    task = tasks_db[task_id]
    old_status = task.status
    task.status = new_status
    task.updated_at = datetime.now().isoformat()
    # Persist change
    update_task_in_db(task)

    return {
        "success": True,
        "task": serialize_task(task),
        "message": f"Task {task_id} status updated from '{old_status}' to '{new_status}'"
    }

@mcp.tool()
async def list_tasks(
    status_filter: Optional[str] = None,
    priority_filter: Optional[int] = None,
    assignee_filter: Optional[str] = None
) -> dict:
    """
    List all tasks with optional filters.
    Can filter by status, priority, or assignee.
    """
    filtered_tasks = []

    for task in tasks_db.values():
        if status_filter and task.status != status_filter:
            continue
        if priority_filter and task.priority != priority_filter:
            continue
        if assignee_filter and task.assignee != assignee_filter:
            continue

        filtered_tasks.append(serialize_task(task))

    return {
        "success": True,
        "count": len(filtered_tasks),
        "tasks": filtered_tasks,
        "filters_applied": {
            "status": status_filter,
            "priority": priority_filter,
            "assignee": assignee_filter
        }
    }

@mcp.tool()
async def delete_task(task_id: str) -> dict:
    """Delete a task by its ID"""
    if task_id not in tasks_db:
        return {
            "success": False,
            "error": f"Task {task_id} not found"
        }

    task = tasks_db.pop(task_id)
    # Remove from SQLite
    delete_task_from_db(task_id)

    return {
        "success": True,
        "message": f"Task '{task.title}' (ID: {task_id}) has been deleted"
    }

@mcp.tool()
async def search_tasks(query: str) -> dict:
    """
    Search tasks by title or description.
    Returns tasks that contain the query string.
    """
    query_lower = query.lower()
    matching_tasks = []

    for task in tasks_db.values():
        if (query_lower in task.title.lower() or
            query_lower in task.description.lower() or
            any(query_lower in tag.lower() for tag in task.tags)):
            matching_tasks.append(serialize_task(task))

    return {
        "success": True,
        "query": query,
        "count": len(matching_tasks),
        "tasks": matching_tasks
    }

# MCP Resources
@mcp.resource("uri://tasks/all")
async def get_all_tasks() -> str:
    """Get all tasks as a resource"""
    all_tasks = [serialize_task(task) for task in tasks_db.values()]
    return json.dumps({
        "total_tasks": len(all_tasks),
        "tasks": all_tasks,
        "last_updated": datetime.now().isoformat()
    }, indent=2)

@mcp.resource("uri://tasks/pending")
async def get_pending_tasks() -> str:
    """Get all pending tasks as a resource"""
    pending_tasks = [
        serialize_task(task)
        for task in tasks_db.values()
        if task.status == "pending"
    ]
    return json.dumps({
        "pending_count": len(pending_tasks),
        "tasks": pending_tasks,
        "last_updated": datetime.now().isoformat()
    }, indent=2)

@mcp.resource("uri://tasks/high-priority")
async def get_high_priority_tasks() -> str:
    """Get high priority tasks (priority >= 4)"""
    high_priority = [
        serialize_task(task)
        for task in tasks_db.values()
        if task.priority >= 4
    ]
    return json.dumps({
        "high_priority_count": len(high_priority),
        "tasks": high_priority,
        "last_updated": datetime.now().isoformat()
    }, indent=2)

# MCP Prompts
@mcp.prompt()
async def task_summary() -> str:
    """Generate a summary of all tasks"""
    total = len(tasks_db)
    pending = sum(1 for t in tasks_db.values() if t.status == "pending")
    in_progress = sum(1 for t in tasks_db.values() if t.status == "in_progress")
    completed = sum(1 for t in tasks_db.values() if t.status == "completed")
    high_priority = sum(1 for t in tasks_db.values() if t.priority >= 4)

    return f"""Task Management Summary:

Total Tasks: {total}
- Pending: {pending}
- In Progress: {in_progress}
- Completed: {completed}

High Priority Tasks (4-5): {high_priority}

Use the available tools to:
- create_task: Add new tasks
- update_task_status: Change task status
- list_tasks: View tasks with filters
- search_tasks: Find specific tasks
- delete_task: Remove completed or unnecessary tasks
"""

@mcp.prompt()
async def daily_standup() -> str:
    """Generate a daily standup report"""
    today = datetime.now().date().isoformat()

    in_progress_tasks = [
        f"- {t.title} (Priority: {t.priority})"
        for t in tasks_db.values()
        if t.status == "in_progress"
    ]

    high_priority_pending = [
        f"- {t.title} (Priority: {t.priority})"
        for t in tasks_db.values()
        if t.status == "pending" and t.priority >= 4
    ]

    recently_completed = [
        f"- {t.title}"
        for t in tasks_db.values()
        if t.status == "completed" and t.updated_at.startswith(today)
    ]

    report = f"""Daily Standup Report - {today}

**In Progress:**
{chr(10).join(in_progress_tasks) if in_progress_tasks else '- No tasks in progress'}

**High Priority Pending:**
{chr(10).join(high_priority_pending) if high_priority_pending else '- No high priority tasks pending'}

**Completed Today:**
{chr(10).join(recently_completed) if recently_completed else '- No tasks completed today'}

Total Active Tasks: {len([t for t in tasks_db.values() if t.status != 'completed'])}
"""
    return report

@mcp.prompt()
async def task_prioritization_guide() -> str:
    """Provide guidance on task prioritization"""
    return """Task Prioritization Guide:

**Priority Levels:**
- Priority 5: Critical/Urgent - Must be done immediately
- Priority 4: High - Should be done today
- Priority 3: Medium - Should be done this week
- Priority 2: Low - Can be scheduled for later
- Priority 1: Nice to have - When time permits

**Best Practices:**
1. Review high priority tasks first
2. Keep no more than 3 tasks "in_progress" at once
3. Update task status regularly
4. Add clear descriptions for context
5. Use tags for better organization

**Suggested Workflow:**
1. List pending tasks by priority
2. Move highest priority to "in_progress"
3. Complete or update progress
4. Mark as "completed" when done
5. Review and plan next tasks
"""

# Initialize with sample data if needed
async def initialize_sample_data():
    """Add some sample tasks for demonstration"""
    if not tasks_db:
        await create_task(
            title="Deploy MCP server to Render",
            description="Set up and deploy the MCP server on Render platform",
            priority=5,
            tags=["deployment", "infrastructure"]
        )
        await create_task(
            title="Test OpenAI agent integration",
            description="Verify that the OpenAI agent can communicate with MCP server",
            priority=4,
            tags=["testing", "integration"]
        )
        await create_task(
            title="Write documentation",
            description="Create comprehensive documentation for the deployment",
            priority=3,
            tags=["documentation"]
        )

# Initialize database when module is imported
init_db()
load_tasks_from_db()

# Run the server
if __name__ == "__main__":
    # Initialize sample data only if DB is empty
    if not tasks_db:
        asyncio.run(initialize_sample_data())

    # Run the MCP server
    mcp.run(transport="stdio")