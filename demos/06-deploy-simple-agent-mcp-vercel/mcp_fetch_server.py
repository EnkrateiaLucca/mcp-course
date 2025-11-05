"""
MCP Fetch Server - Built with Official MCP Python SDK
Provides web scraping tools via Model Context Protocol with HTTP transport
"""

from mcp.server.fastmcp import FastMCP
from typing import Optional
import httpx
from bs4 import BeautifulSoup
import os

# Create MCP server instance
mcp = FastMCP(
    name="mcp-fetch-server",
    version="2.0.0"
)


@mcp.tool()
async def fetch_url(url: str, extract_text: bool = True) -> str:
    """
    Fetch a URL and extract clean text content.

    This tool fetches web pages and extracts readable text,
    removing HTML tags and scripts. Perfect for getting
    article content, documentation, etc.

    Args:
        url: The URL to fetch content from
        extract_text: If True, extract clean text; if False, return HTML

    Returns:
        The fetched content as a string
    """
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()

            if extract_text:
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

            return f"Status: {response.status_code}\nURL: {response.url}\n\nContent:\n{content}"

    except httpx.HTTPError as e:
        return f"Error fetching URL: {str(e)}"
    except Exception as e:
        return f"Error processing request: {str(e)}"


@mcp.tool()
async def fetch_html(url: str) -> str:
    """
    Fetch raw HTML content from a URL.

    This tool fetches the raw HTML source of a web page.
    Useful when you need to analyze page structure or
    extract specific HTML elements.

    Args:
        url: The URL to fetch HTML from

    Returns:
        The raw HTML content (limited to 5000 chars)
    """
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()

            content = response.text[:5000]
            return f"Status: {response.status_code}\nURL: {response.url}\n\nHTML:\n{content}"

    except httpx.HTTPError as e:
        return f"Error fetching URL: {str(e)}"
    except Exception as e:
        return f"Error processing request: {str(e)}"


# For production deployment with Vercel
# Create the ASGI app for HTTP transport
def create_app():
    """Create ASGI application for production deployment"""
    return mcp.http_app()


# Export the app for Vercel
app = create_app()


if __name__ == "__main__":
    # For local development, run with HTTP transport
    port = int(os.getenv("PORT", "8001"))
    print(f"🚀 Starting MCP Fetch Server on http://localhost:{port}/mcp")
    print(f"📡 Protocol: Model Context Protocol (HTTP Transport)")
    print(f"🔧 Tools available: fetch_url, fetch_html")
    mcp.run(transport="http", host="0.0.0.0", port=port)
