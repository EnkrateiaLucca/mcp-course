# /// script
# requires-python = ">=3.12"
# dependencies = ["mcp[cli]>=1.0.0", "pypdf>=5.0.0"]
# ///

from mcp.server.fastmcp import FastMCP
from pypdf import PdfReader
import os

mcp = FastMCP("pdf-analysis-mcp-server")

@mcp.tool(
    name="pdf-load",
    description="Load a pdf file and return the text",
)
def load_pdf(file_path: str) -> str:
    
    reader = PdfReader(file_path)
    text = "\n\n".join([page.extract_text() for page in reader.pages])
    return text

@mcp.tool(
    name="write-to-markdown-file",
    description="Write content to a markdown file",
)
def write_to_markdown_file(content: str) -> str:
    with open("output.md", "w") as f:
        f.write(content)
    return "File written successfully to: output.md"

if __name__ == "__main__":
    print("Starting PDF analysis MCP server...")
    mcp.run(transport="stdio")
