#!/usr/bin/env python3

from mcp.server.fastmcp import FastMCP
from pydantic import Field
import json

# Create MCP server instance
mcp = FastMCP("SimpleTutorialMCP")

# Sample documents for our tutorial
documents = {
    "notes.txt": "This is a sample note document with some text content.",
    "report.md": "# Project Report\n\nThis is a markdown report with project details.",
    "data.json": '{"users": 10, "projects": 3, "status": "active"}',
    "todo.txt": "1. Review documentation\n2. Test MCP server\n3. Create examples"
}

# Tool: Read document content
@mcp.tool(
    name="read_document",
    description="Read the content of a document by its filename"
)
def read_document(filename: str = Field(description="Name of the document to read")):
    """Read and return the content of a document."""
    if filename not in documents:
        return f"Document '{filename}' not found. Available documents: {list(documents.keys())}"

    return documents[filename]

# Tool: Write/update document content
@mcp.tool(
    name="write_document",
    description="Write or update a document with new content"
)
def write_document(
    filename: str = Field(description="Name of the document to write/update"),
    content: str = Field(description="Content to write to the document")
):
    """Write or update a document with new content."""
    documents[filename] = content
    return f"Successfully wrote to '{filename}'"

# Tool: List all documents
@mcp.tool(
    name="list_documents",
    description="List all available documents"
)
def list_documents():
    """List all available document filenames."""
    return list(documents.keys())

# Tool: Search documents
@mcp.tool(
    name="search_documents",
    description="Search for text across all documents"
)
def search_documents(query: str = Field(description="Text to search for")):
    """Search for text across all documents."""
    results = []
    for filename, content in documents.items():
        if query.lower() in content.lower():
            results.append({
                "filename": filename,
                "content": content[:100] + "..." if len(content) > 100 else content
            })

    if not results:
        return f"No documents found containing '{query}'"

    return results

# Resource: Get document list as JSON
@mcp.resource("documents://list")
def get_document_list():
    """Return list of all document names."""
    return json.dumps(list(documents.keys()))

# Resource: Get specific document content
@mcp.resource("documents://{filename}")
def get_document_content(filename: str):
    """Return content of a specific document."""
    if filename in documents:
        return documents[filename]
    else:
        return f"Document '{filename}' not found"

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()