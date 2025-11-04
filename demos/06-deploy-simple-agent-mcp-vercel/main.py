"""
AI Agent API with OpenAI Agents SDK, Web Search, and MCP Fetch Tools
A beginner-friendly demo showing how to deploy agents to Vercel
"""

import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="AI Agent API",
    description="OpenAI Agents SDK with Web Search and MCP Tools",
    version="1.0.0"
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
# Custom Tools for Agent
# =======================

class FetchTool:
    """
    Custom tool for fetching web content
    Works with our MCP Fetch Server or directly via HTTP
    """

    def __init__(self, fetch_server_url: Optional[str] = None):
        self.fetch_server_url = fetch_server_url or os.getenv(
            "MCP_FETCH_SERVER_URL",
            "http://localhost:8001"
        )

    async def fetch_url(self, url: str, extract_text: bool = True) -> str:
        """
        Fetch content from a URL

        Args:
            url: The URL to fetch
            extract_text: If True, extract clean text; if False, return HTML

        Returns:
            The fetched content as a string
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                endpoint = f"{self.fetch_server_url}/tools/fetch_url"
                response = await client.post(
                    endpoint,
                    json={"url": url, "extract_text": extract_text}
                )
                response.raise_for_status()
                data = response.json()
                return data.get("content", "")
        except Exception as e:
            return f"Error fetching URL: {str(e)}"

    def get_tool_definition(self):
        """Return OpenAI function definition for this tool"""
        return {
            "type": "function",
            "function": {
                "name": "fetch_url",
                "description": "Fetch and extract text content from a web URL. Use this to read articles, documentation, or any web page content.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL to fetch content from"
                        },
                        "extract_text": {
                            "type": "boolean",
                            "description": "Whether to extract clean text (true) or return HTML (false)",
                            "default": True
                        }
                    },
                    "required": ["url"]
                }
            }
        }


# =======================
# Agent Configuration
# =======================

# Note: For a production app, you would use the OpenAI Agents SDK here
# However, for Vercel deployment simplicity, we're using direct OpenAI API calls
# The OpenAI Agents SDK would be structured similarly but with more abstractions

async def run_agent(query: str, history: List[ChatMessage] = None) -> str:
    """
    Run the AI agent with web search and fetch capabilities

    This is a simplified version that demonstrates the core concepts.
    In a full implementation, you would use the OpenAI Agents SDK.

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

    # Initialize fetch tool
    fetch_tool = FetchTool()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Build messages from history
            messages = []

            # System message with instructions
            messages.append({
                "role": "system",
                "content": """You are a helpful AI assistant with access to:
1. Web search capabilities - to find current information
2. URL fetch tool - to read content from specific web pages

When users ask questions:
- Use web search for general queries and current events
- Use fetch_url when you need to read specific web pages or documentation
- Provide clear, concise, and helpful responses
- Always cite your sources when using web search or fetched content"""
            })

            # Add conversation history
            if history:
                for msg in history[-5:]:  # Keep last 5 messages for context
                    messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })

            # Add current query
            messages.append({
                "role": "user",
                "content": query
            })

            # Define available tools
            tools = [
                fetch_tool.get_tool_definition(),
                {
                    "type": "function",
                    "function": {
                        "name": "web_search",
                        "description": "Search the web for current information, news, and general knowledge",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "The search query"
                                }
                            },
                            "required": ["query"]
                        }
                    }
                }
            ]

            # Call OpenAI API with function calling
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",  # Using mini for cost efficiency
                    "messages": messages,
                    "tools": tools,
                    "tool_choice": "auto"
                }
            )
            response.raise_for_status()
            result = response.json()

            # Process response
            message = result["choices"][0]["message"]

            # If agent wants to use tools, execute them
            if message.get("tool_calls"):
                tool_messages = messages.copy()
                tool_messages.append(message)

                for tool_call in message["tool_calls"]:
                    function_name = tool_call["function"]["name"]
                    function_args = eval(tool_call["function"]["arguments"])

                    # Execute the appropriate tool
                    if function_name == "fetch_url":
                        tool_response = await fetch_tool.fetch_url(**function_args)
                    elif function_name == "web_search":
                        # For demo purposes, simulate web search
                        # In production, integrate with a real search API
                        tool_response = f"[Web search simulation] Results for: {function_args.get('query')}\n\nNote: In production, integrate with a real search API like Brave, Tavily, or Bing."
                    else:
                        tool_response = "Unknown tool"

                    # Add tool response to messages
                    tool_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": tool_response
                    })

                # Get final response after tool execution
                final_response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4o-mini",
                        "messages": tool_messages
                    }
                )
                final_response.raise_for_status()
                final_result = final_response.json()
                return final_result["choices"][0]["message"]["content"]

            # Return direct response if no tools were used
            return message.get("content", "I'm sorry, I couldn't generate a response.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


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
        "name": "AI Research Assistant",
        "capabilities": [
            "Web search for current information",
            "Fetch and read content from URLs",
            "Answer questions with cited sources",
            "General conversation and assistance"
        ],
        "models": ["gpt-4o-mini"],
        "tools": ["web_search", "fetch_url"]
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
