"""
AI Agent API with Claude Agent SDK and Vercel Sandbox
Demonstrates deploying Claude agents with MCP integration to Vercel

This example shows Pattern 1: Ephemeral Sessions - creates a sandbox per request
"""

import os
import asyncio
import json
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="Claude Agent API with Vercel Sandbox",
    description="Deploy Claude Agents SDK with MCP tools using Vercel Sandbox",
    version="3.0.0"
)

# Mount static files for the chat interface
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    # Static directory might not exist in some deployment scenarios
    pass


# =======================
# Data Models
# =======================

class ChatMessage(BaseModel):
    """Represents a single chat message"""
    role: str  # 'user' or 'assistant'
    content: str


class QueryRequest(BaseModel):
    """Request model for agent queries"""
    message: str
    history: Optional[List[ChatMessage]] = []


class QueryResponse(BaseModel):
    """Response model for agent queries"""
    response: str
    status: str
    sandbox_id: Optional[str] = None


# =======================
# Sandbox Management
# =======================

class SandboxManager:
    """
    Manages Vercel Sandbox instances for Claude Agent SDK

    Note: Vercel Sandbox SDK is TypeScript-only, so this is a
    simplified Python wrapper that demonstrates the concept.

    In production, you would:
    1. Use the TypeScript SDK via a Node.js microservice
    2. Or use another sandbox provider (Modal, E2B, etc.) with Python SDK
    """

    @staticmethod
    async def create_sandbox() -> Dict[str, Any]:
        """
        Create a new Vercel Sandbox with Claude Agent SDK

        In a real implementation, this would:
        1. Use @vercel/sandbox TypeScript SDK
        2. Install Claude Code CLI: npm install -g @anthropic-ai/claude-code
        3. Install Python dependencies: pip install claude-agent-sdk mcp
        4. Copy agent code into the sandbox
        5. Start the agent process
        6. Expose a port for communication

        For this demo, we'll simulate the sandbox behavior
        """
        sandbox_id = f"sandbox-{os.urandom(4).hex()}"

        # In production, this would call the Vercel Sandbox SDK:
        # const sandbox = await Sandbox.create({
        #   runtime: 'python3.13',
        #   source: { type: 'git', url: 'your-repo-url' },
        #   ports: [8000],
        #   timeout: ms('5m'),
        # });

        return {
            "id": sandbox_id,
            "status": "ready",
            "url": f"http://sandbox-{sandbox_id}.internal:8000"
        }

    @staticmethod
    async def execute_in_sandbox(sandbox_id: str, message: str, history: List[ChatMessage]) -> str:
        """
        Execute agent task in the sandbox

        In production:
        1. Send HTTP request to sandbox endpoint
        2. Agent processes with Claude Agent SDK
        3. Returns response
        """
        # For demo purposes, we'll use Claude API directly
        # In production, this would communicate with the sandboxed agent
        return await SandboxManager._run_claude_agent(message, history)

    @staticmethod
    async def _run_claude_agent(message: str, history: List[ChatMessage]) -> str:
        """
        Simulates Claude Agent SDK execution

        In production, this runs inside the Vercel Sandbox
        """
        try:
            # Check for API key
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

            # Import Anthropic client
            try:
                from anthropic import Anthropic
            except ImportError:
                return "Error: anthropic package not installed. Run: pip install anthropic"

            client = Anthropic(api_key=api_key)

            # Build conversation history
            messages = []
            for msg in history[-5:]:  # Last 5 messages for context
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

            # Add current message
            messages.append({
                "role": "user",
                "content": message
            })

            # Call Claude API
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                system="""You are a helpful AI assistant with access to web fetching tools via MCP.

Your capabilities:
- Fetch and read content from web pages
- Extract clean text from URLs
- Answer questions with cited sources

When users ask questions:
- Provide clear, concise, and helpful responses
- Be friendly and conversational
- Cite sources when appropriate

Note: In a full implementation, you would have access to MCP tools for web fetching.
For now, provide helpful responses based on your knowledge.""",
                messages=messages
            )

            # Extract response
            return response.content[0].text

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

    @staticmethod
    async def cleanup_sandbox(sandbox_id: str):
        """Clean up sandbox resources"""
        # In production, this would terminate the Vercel Sandbox
        pass


# =======================
# API Endpoints
# =======================

@app.get("/", response_class=HTMLResponse)
async def serve_chat_interface():
    """Serve the chat interface"""
    try:
        with open("static/index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse(
            content="""
            <h1>Chat interface not found</h1>
            <p>Make sure static/index.html exists.</p>
            <p>API is still available at <a href="/docs">/docs</a></p>
            """,
            status_code=404
        )


@app.post("/api/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    """
    Main chat endpoint - creates ephemeral sandbox for each request

    Flow:
    1. Create Vercel Sandbox with Claude Agent SDK
    2. Execute agent task in sandbox
    3. Return response
    4. Clean up sandbox
    """
    sandbox_id = None

    try:
        # Create sandbox
        sandbox = await SandboxManager.create_sandbox()
        sandbox_id = sandbox["id"]

        # Execute agent task in sandbox
        response = await SandboxManager.execute_in_sandbox(
            sandbox_id,
            request.message,
            request.history
        )

        return QueryResponse(
            response=response,
            status="success",
            sandbox_id=sandbox_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up sandbox (Pattern 1: Ephemeral Sessions)
        if sandbox_id:
            await SandboxManager.cleanup_sandbox(sandbox_id)


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "claude-agent-api",
        "version": "3.0.0",
        "deployment_pattern": "Ephemeral Sessions with Vercel Sandbox"
    }


@app.get("/api/info")
async def get_info():
    """Get information about the agent's capabilities"""
    return {
        "name": "Claude Research Assistant",
        "description": "Claude Agent SDK deployed on Vercel Sandbox with MCP integration",
        "architecture": "Claude Agent SDK + Vercel Sandbox + MCP",
        "deployment_pattern": "Ephemeral Sessions",
        "capabilities": [
            "Fetch and read content from URLs (via MCP)",
            "Extract clean text from web pages",
            "Answer questions with cited sources",
            "Long-running command execution in isolated sandbox",
            "File operations within sandbox"
        ],
        "model": "claude-3-5-sonnet-20241022",
        "sandbox_provider": "Vercel Sandbox",
        "tools_via_mcp": ["fetch_url", "fetch_html"],
        "hosting_requirements": {
            "runtime": "Python 3.13",
            "node_required": "Yes (for Claude Code CLI)",
            "ram": "1 GiB",
            "disk": "5 GiB",
            "cpu": "1 vCPU"
        }
    }


# =======================
# Vercel Serverless Handler
# =======================

# For Vercel, export the app
handler = app


if __name__ == "__main__":
    # For local development
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    print(f"🚀 Starting Claude Agent API on http://localhost:{port}")
    print(f"📝 Chat interface: http://localhost:{port}")
    print(f"📚 API docs: http://localhost:{port}/docs")
    print(f"\n⚠️  Note: This demo simulates Vercel Sandbox behavior")
    print(f"    In production, agents run in actual isolated sandboxes")
    uvicorn.run(app, host="0.0.0.0", port=port)
