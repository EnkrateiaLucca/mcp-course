#!/usr/bin/env python3
"""
FastAPI Application for Render Deployment
Wraps the MCP server and agent in a web API
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Import our MCP server components
from mcp_server import (
    create_task,
    update_task_status,
    list_tasks,
    delete_task,
    search_tasks,
    get_all_tasks,
    get_pending_tasks,
    get_high_priority_tasks,
    task_summary,
    daily_standup,
    task_prioritization_guide
)

# Initialize FastAPI app
app = FastAPI(
    title="Task Management MCP Server API",
    description="Production-ready MCP server deployed on Render with task management capabilities",
    version="1.0.0"
)

# Configure CORS for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class CreateTaskRequest(BaseModel):
    title: str
    description: str
    priority: int = 3
    due_date: Optional[str] = None
    assignee: Optional[str] = None
    tags: List[str] = []

class UpdateStatusRequest(BaseModel):
    task_id: str
    new_status: str

class ListTasksRequest(BaseModel):
    status_filter: Optional[str] = None
    priority_filter: Optional[int] = None
    assignee_filter: Optional[str] = None

class SearchRequest(BaseModel):
    query: str

class AgentRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Task Management MCP Server",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "tasks": "/api/tasks",
            "docs": "/docs",
            "mcp_tools": "/api/mcp/tools",
            "mcp_resources": "/api/mcp/resources",
            "mcp_prompts": "/api/mcp/prompts"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "mcp-task-server"
    }

# Task Management Endpoints
@app.post("/api/tasks/create")
async def api_create_task(request: CreateTaskRequest):
    """Create a new task via API"""
    result = await create_task(
        title=request.title,
        description=request.description,
        priority=request.priority,
        due_date=request.due_date,
        assignee=request.assignee,
        tags=request.tags
    )
    return JSONResponse(content=result)

@app.put("/api/tasks/status")
async def api_update_status(request: UpdateStatusRequest):
    """Update task status via API"""
    result = await update_task_status(
        task_id=request.task_id,
        new_status=request.new_status
    )
    return JSONResponse(content=result)

@app.post("/api/tasks/list")
async def api_list_tasks(request: ListTasksRequest):
    """List tasks with optional filters"""
    result = await list_tasks(
        status_filter=request.status_filter,
        priority_filter=request.priority_filter,
        assignee_filter=request.assignee_filter
    )
    return JSONResponse(content=result)

@app.delete("/api/tasks/{task_id}")
async def api_delete_task(task_id: str):
    """Delete a task by ID"""
    result = await delete_task(task_id=task_id)
    return JSONResponse(content=result)

@app.post("/api/tasks/search")
async def api_search_tasks(request: SearchRequest):
    """Search tasks by query"""
    result = await search_tasks(query=request.query)
    return JSONResponse(content=result)

# MCP Resource Endpoints
@app.get("/api/mcp/resources/all-tasks")
async def api_get_all_tasks():
    """Get all tasks as MCP resource"""
    result = await get_all_tasks()
    return JSONResponse(content=json.loads(result))

@app.get("/api/mcp/resources/pending-tasks")
async def api_get_pending_tasks():
    """Get pending tasks as MCP resource"""
    result = await get_pending_tasks()
    return JSONResponse(content=json.loads(result))

@app.get("/api/mcp/resources/high-priority")
async def api_get_high_priority():
    """Get high priority tasks as MCP resource"""
    result = await get_high_priority_tasks()
    return JSONResponse(content=json.loads(result))

# MCP Prompt Endpoints
@app.get("/api/mcp/prompts/summary")
async def api_task_summary():
    """Get task summary prompt"""
    result = await task_summary()
    return {"prompt": "task_summary", "content": result}

@app.get("/api/mcp/prompts/standup")
async def api_daily_standup():
    """Get daily standup prompt"""
    result = await daily_standup()
    return {"prompt": "daily_standup", "content": result}

@app.get("/api/mcp/prompts/prioritization")
async def api_prioritization_guide():
    """Get task prioritization guide"""
    result = await task_prioritization_guide()
    return {"prompt": "task_prioritization_guide", "content": result}

# MCP Information Endpoints
@app.get("/api/mcp/tools")
async def get_mcp_tools():
    """List all available MCP tools"""
    return {
        "tools": [
            {
                "name": "create_task",
                "description": "Create a new task with given details",
                "parameters": ["title", "description", "priority", "due_date", "assignee", "tags"]
            },
            {
                "name": "update_task_status",
                "description": "Update the status of an existing task",
                "parameters": ["task_id", "new_status"]
            },
            {
                "name": "list_tasks",
                "description": "List all tasks with optional filters",
                "parameters": ["status_filter", "priority_filter", "assignee_filter"]
            },
            {
                "name": "delete_task",
                "description": "Delete a task by its ID",
                "parameters": ["task_id"]
            },
            {
                "name": "search_tasks",
                "description": "Search tasks by title or description",
                "parameters": ["query"]
            }
        ]
    }

@app.get("/api/mcp/resources")
async def get_mcp_resources():
    """List all available MCP resources"""
    return {
        "resources": [
            {
                "uri": "uri://tasks/all",
                "description": "Get all tasks as a resource"
            },
            {
                "uri": "uri://tasks/pending",
                "description": "Get all pending tasks"
            },
            {
                "uri": "uri://tasks/high-priority",
                "description": "Get high priority tasks (priority >= 4)"
            }
        ]
    }

@app.get("/api/mcp/prompts")
async def get_mcp_prompts():
    """List all available MCP prompts"""
    return {
        "prompts": [
            {
                "name": "task_summary",
                "description": "Generate a summary of all tasks"
            },
            {
                "name": "daily_standup",
                "description": "Generate a daily standup report"
            },
            {
                "name": "task_prioritization_guide",
                "description": "Provide guidance on task prioritization"
            }
        ]
    }

# Agent Integration Endpoint (simplified for deployment)
@app.post("/api/agent/chat")
async def agent_chat(request: AgentRequest):
    """
    Simplified agent endpoint for processing natural language requests.
    In production, this would connect to the full agent implementation.
    """
    message = request.message.lower()

    # Simple intent detection (in production, use the full agent)
    if "create" in message or "add" in message:
        # Extract basic task info (simplified)
        return {
            "response": "To create a task, use the /api/tasks/create endpoint",
            "suggested_action": "create_task"
        }

    elif "list" in message or "show" in message:
        tasks = await list_tasks()
        return {
            "response": f"Found {tasks['count']} tasks",
            "data": tasks
        }

    elif "search" in message:
        # Extract query (simplified)
        query = message.replace("search", "").strip()
        if query:
            results = await search_tasks(query=query)
            return {
                "response": f"Found {results['count']} matching tasks",
                "data": results
            }

    elif "summary" in message:
        summary = await task_summary()
        return {
            "response": summary,
            "type": "summary"
        }

    elif "standup" in message:
        standup = await daily_standup()
        return {
            "response": standup,
            "type": "standup"
        }

    else:
        return {
            "response": "I can help you create, list, search, and manage tasks. What would you like to do?",
            "available_actions": ["create_task", "list_tasks", "search_tasks", "task_summary", "daily_standup"]
        }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "path": str(request.url.path)}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "message": str(exc)}
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    print("🚀 Task Management MCP Server starting...")
    print(f"📍 Environment: {os.getenv('RENDER_SERVICE_NAME', 'local')}")
    print(f"🔗 Port: {os.getenv('PORT', '8000')}")

    # Initialize sample data
    from mcp_server import initialize_sample_data
    await initialize_sample_data()

    print("✅ Server initialized successfully")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    print("👋 Task Management MCP Server shutting down...")

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"  # Required for Render

    print(f"Starting server on {host}:{port}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True if os.getenv("ENV") == "development" else False
    )