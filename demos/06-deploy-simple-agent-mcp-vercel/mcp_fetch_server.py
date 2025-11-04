"""
Simple HTTP MCP Fetch Server
Provides web scraping tools via MCP protocol over HTTP/SSE
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional
import httpx
from bs4 import BeautifulSoup
import os

app = FastAPI(
    title="MCP Fetch Server",
    description="MCP server providing web fetch and scraping tools",
    version="1.0.0"
)


class FetchRequest(BaseModel):
    """Request model for fetch operations"""
    url: str
    extract_text: bool = True


class FetchResponse(BaseModel):
    """Response model for fetch operations"""
    content: str
    status_code: int
    url: str


@app.get("/")
async def root():
    """Root endpoint - server info"""
    return {
        "name": "MCP Fetch Server",
        "version": "1.0.0",
        "protocol": "mcp-http",
        "tools": [
            {
                "name": "fetch_url",
                "description": "Fetch and extract text content from a URL"
            },
            {
                "name": "fetch_html",
                "description": "Fetch raw HTML content from a URL"
            }
        ]
    }


@app.post("/tools/fetch_url", response_model=FetchResponse)
async def fetch_url(request: FetchRequest):
    """
    Fetch a URL and extract clean text content

    This tool fetches web pages and extracts readable text,
    removing HTML tags and scripts. Perfect for getting
    article content, documentation, etc.
    """
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            response = await client.get(request.url)
            response.raise_for_status()

            if request.extract_text:
                # Parse HTML and extract text
                soup = BeautifulSoup(response.text, 'html.parser')

                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer"]):
                    script.decompose()

                # Get text
                text = soup.get_text()

                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)

                content = text[:5000]  # Limit to 5000 chars
            else:
                content = response.text[:5000]

            return FetchResponse(
                content=content,
                status_code=response.status_code,
                url=str(response.url)
            )

    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.post("/tools/fetch_html", response_model=FetchResponse)
async def fetch_html(request: FetchRequest):
    """
    Fetch raw HTML content from a URL

    This tool fetches the raw HTML source of a web page.
    Useful when you need to analyze page structure or
    extract specific HTML elements.
    """
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            response = await client.get(request.url)
            response.raise_for_status()

            return FetchResponse(
                content=response.text[:5000],  # Limit to 5000 chars
                status_code=response.status_code,
                url=str(response.url)
            )

    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "mcp-fetch-server"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
