from mcp.server.fastmcp import FastMCP

mcp = FastMCP("lucas-never-quits-mcp")


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

if __name__ == "__main__":
    mcp.run(transport='stdio')