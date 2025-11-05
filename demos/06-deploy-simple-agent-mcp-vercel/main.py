"""
AI Agent API with OpenAI Agents SDK, Web Search, and MCP Fetch Tools
A beginner-friendly demo showing how to deploy agents to Vercel
Using official MCP Python SDK for better integration
"""

import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

# OpenAI Agents SDK imports
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="AI Agent API",
    description="OpenAI Agents SDK with Web Search and MCP Tools",
    version="2.0.0"
)

# Mount static files for the chat interface
app.mount("/static", StaticFiles(directory="static"), name="static")


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


# =======================
# MCP Server Configuration
# =======================

def get_mcp_server_url() -> str:
    """Get the MCP server URL from environment or use default"""
    return os.getenv("MCP_FETCH_SERVER_URL", "http://localhost:8001/mcp")


# =======================
# Agent Configuration
# =======================

async def run_agent(query: str, history: List[ChatMessage] = None) -> str:
    """
    Run the AI agent with MCP fetch capabilities using OpenAI Agents SDK.

    This implementation uses the official OpenAI Agents SDK with proper
    MCP server integration for web fetching capabilities.

    Args:
        query: User's question or request
        history: Previous conversation history

    Returns:
        Agent's response as a string
    """
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    # Set OpenAI API key for the agents SDK
    os.environ["OPENAI_API_KEY"] = api_key

    try:
        # Connect to MCP Fetch Server using OpenAI Agents SDK
        mcp_server_url = get_mcp_server_url()

        async with MCPServerStreamableHttp(
            name="MCP Fetch Server",
            params={
                "url": mcp_server_url,
                "timeout": 30,
            },
            cache_tools_list=True,
            max_retry_attempts=3,
        ) as mcp_server:

            # Build context from conversation history
            context_messages = []
            if history:
                for msg in history[-5:]:  # Keep last 5 messages for context
                    context_messages.append(f"{msg.role}: {msg.content}")

            context_str = "\n".join(context_messages) if context_messages else ""

            # Create instructions with context
            instructions = """You are a helpful AI assistant with access to web fetching tools via MCP.

Your capabilities:
- fetch_url: Fetch and extract clean text from web pages (perfect for reading articles, docs, etc.)
- fetch_html: Fetch raw HTML content from web pages

When users ask questions:
- Use fetch_url to read content from specific web pages or documentation
- Provide clear, concise, and helpful responses
- Always cite your sources when using fetched content

"""
            if context_str:
                instructions += f"\nConversation context:\n{context_str}\n"

            # Create agent with MCP server tools
            agent = Agent(
                name="Web Research Assistant",
                instructions=instructions,
                model="gpt-4o-mini",  # Using mini for cost efficiency
                mcp_servers=[mcp_server],
            )

            # Run the agent with the user query
            result = await Runner.run(agent, query)

            # Extract the response text
            if hasattr(result, 'content'):
                return result.content
            elif isinstance(result, str):
                return result
            else:
                # Try to extract text from the result
                return str(result)

    except Exception as e:
        # Fallback to basic response if MCP connection fails
        error_msg = str(e)
        if "Connection refused" in error_msg or "Failed to connect" in error_msg:
            return f"Sorry, I'm unable to connect to the web fetching service right now. Please make sure the MCP server is running at {mcp_server_url}. Error: {error_msg}"
        raise HTTPException(status_code=500, detail=f"Agent error: {error_msg}")


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
            content="<h1>Chat interface not found</h1><p>Make sure static/index.html exists.</p>",
            status_code=404
        )


@app.post("/api/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    """
    Main chat endpoint
    Send a message and get an AI response
    """
    try:
        # Run the agent
        response = await run_agent(request.message, request.history)

        return QueryResponse(
            response=response,
            status="success"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-agent-api",
        "version": "1.0.0"
    }


@app.get("/api/info")
async def get_info():
    """Get information about the agent's capabilities"""
    return {
        "name": "Web Research Assistant",
        "description": "AI agent with MCP-powered web fetching capabilities",
        "capabilities": [
            "Fetch and read content from URLs (via MCP)",
            "Extract clean text from web pages",
            "Fetch raw HTML for analysis",
            "Answer questions with cited sources",
            "General conversation and assistance"
        ],
        "models": ["gpt-4o-mini"],
        "mcp_server": get_mcp_server_url(),
        "tools_via_mcp": ["fetch_url", "fetch_html"],
        "architecture": "OpenAI Agents SDK + Official MCP Python SDK"
    }


# =======================
# Vercel Serverless Handler
# =======================

# For Vercel, we need to export the app
# Vercel will automatically handle the ASGI app
handler = app


if __name__ == "__main__":
    # For local development
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    print(f"🚀 Starting AI Agent API on http://localhost:{port}")
    print(f"📝 Chat interface: http://localhost:{port}")
    print(f"📚 API docs: http://localhost:{port}/docs")
    uvicorn.run(app, host="0.0.0.0", port=port)
