# /// script
# requires-python = ">=3.12"
# dependencies = ["mcp[cli]>=1.0.0"]
# ///

"""
MCP Server: Link Health Checker

Provides tools to discover markdown files, extract URLs, check link health,
and write audit reports. Uses only the Python standard library.

Test independently with: mcp dev link_checker_mcp_server.py
"""

from mcp.server.fastmcp import FastMCP
import os
import re
import urllib.request
import urllib.error
import time

mcp = FastMCP("link-checker")

REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


@mcp.tool()
def list_markdown_files(directory: str) -> str:
    """List all markdown files found recursively under a directory.

    Args:
        directory: Path to search for .md files
    """
    if not os.path.isdir(directory):
        return f"Error: {directory} is not a directory"

    results = []
    for root, _, files in os.walk(directory):
        for f in sorted(files):
            if f.endswith(".md"):
                results.append(os.path.join(root, f))

    if not results:
        return "No markdown files found."

    return "\n".join(results)


@mcp.tool()
def extract_links(filepath: str) -> str:
    """Extract all unique URLs from a markdown file.

    Args:
        filepath: Path to the markdown file
    """
    if not os.path.exists(filepath):
        return f"Error: {filepath} not found"

    with open(filepath) as f:
        content = f.read()

    # Match [text](url) markdown links and bare https:// URLs
    inline = re.findall(r'\[(?:[^\]]*)\]\((https?://[^\)\s]+)\)', content)
    bare = re.findall(r'(?<!\()(https?://[^\s\)\]>,"]+)', content)

    urls = set()
    for url in inline + bare:
        urls.add(url.rstrip(".,;)"))

    if not urls:
        return "No URLs found."

    return "\n".join(sorted(urls))


@mcp.tool()
def check_url(url: str) -> str:
    """Check if a URL is reachable and return its HTTP status.

    Args:
        url: The URL to check
    """
    start = time.time()
    try:
        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", "Mozilla/5.0 (link-checker/1.0)")
        with urllib.request.urlopen(req, timeout=10) as response:
            elapsed = int((time.time() - start) * 1000)
            return f"{response.status} OK ({elapsed}ms)"
    except urllib.error.HTTPError as e:
        elapsed = int((time.time() - start) * 1000)
        return f"{e.code} {e.reason} ({elapsed}ms)"
    except urllib.error.URLError as e:
        return f"Connection error: {e.reason}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def write_report(filename: str, content: str) -> str:
    """Write a link audit report to the reports directory.

    Args:
        filename: Report filename, e.g. 'link_audit_2026-04-20.txt'
        content: The report content
    """
    if "/" in filename or "\\" in filename:
        return "Error: filename cannot contain path separators"

    if not (filename.endswith(".txt") or filename.endswith(".md")):
        return "Error: filename must end in .txt or .md"

    filepath = os.path.join(REPORTS_DIR, filename)
    with open(filepath, "w") as f:
        f.write(content)

    return f"Wrote: {filepath}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
