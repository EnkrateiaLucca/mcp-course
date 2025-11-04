from mcp.server.fastmcp import FastMCP
from glob import glob

mcp = FastMCP("lucas-never-quits-mcp")

DOCS_PATH = "./docs"

@mcp.tool(
    name="read_doc",
    description="Function to read documents"
)
def read_doc(filepath: str) -> str:
    """Read the contents of a file at the specified filepath."""
    with open(filepath, "r") as f:
        return f.read()

@mcp.tool(
    name='write_file',
    description='Function that writes to file'
)
def write_file(filepath: str, contents: str) -> str:
    """Write contents to a file at the specified filepath."""
    with open(filepath, "w") as f:
        f.write(contents)

    return f"File written successfully to: {filepath}"

@mcp.resource(f"docs://documents/{DOCS_PATH}", mime_type="text/plain")
def list_docs() -> list[str]:
    return glob(f"{DOCS_PATH}/*.md")

@mcp.resource("docs://documents/{doc_name}", mime_type="text/plain")
def fetch_doc(doc_name: str) -> str:
    """Fetch a document from the docs folder by name."""
    filepath = f"{DOCS_PATH}/{doc_name}"
    try:
        with open(filepath, "r") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: Document '{doc_name}' not found in docs folder"

if __name__ == "__main__":
    mcp.run(transport='stdio')