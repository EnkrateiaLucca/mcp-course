# /// script
# requires-python = ">=3.12"
# dependencies = ["mcp[cli]>=1.0.0"]
# ///

"""
MCP Server: Script Automation Sandbox

Provides constrained tools for an AI agent to create, test, and run
Python automation scripts in a sandboxed directory.

The key idea: the MCP server controls WHERE scripts are saved and
HOW they execute (with timeouts, output capture, etc.), while the
agent provides the intelligence to WRITE the scripts.

Test independently with: mcp dev automation_mcp_server.py
"""

from mcp.server.fastmcp import FastMCP
import subprocess
import os

mcp = FastMCP("script-sandbox")

# All scripts live in this directory - our sandbox boundary
SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_scripts")
os.makedirs(SCRIPTS_DIR, exist_ok=True)


@mcp.tool()
def save_script(filename: str, code: str) -> str:
    """Save a Python script to the scripts directory.

    Args:
        filename: Name for the script (e.g. 'hello.py'). Must end in .py
        code: The Python source code to save
    """
    if not filename.endswith(".py"):
        return "Error: filename must end with .py"

    if "/" in filename or "\\" in filename:
        return "Error: filename cannot contain path separators"

    filepath = os.path.join(SCRIPTS_DIR, filename)
    with open(filepath, "w") as f:
        f.write(code)

    return f"Saved: {filepath}"


@mcp.tool()
def list_scripts() -> str:
    """List all Python scripts in the scripts directory."""
    scripts = [f for f in os.listdir(SCRIPTS_DIR) if f.endswith(".py")]

    if not scripts:
        return "No scripts found."

    return "\n".join(f"- {s}" for s in sorted(scripts))


@mcp.tool()
def read_script(filename: str) -> str:
    """Read the contents of a saved script.

    Args:
        filename: Name of the script to read (e.g. 'hello.py')
    """
    filepath = os.path.join(SCRIPTS_DIR, filename)

    if not os.path.exists(filepath):
        return f"Error: {filename} not found"

    with open(filepath) as f:
        return f.read()


@mcp.tool()
def run_script(filename: str, args: str = "") -> str:
    """Run a saved Python script with a 30-second timeout.

    Args:
        filename: Name of the script to run
        args: Optional space-separated arguments to pass to the script
    """
    filepath = os.path.join(SCRIPTS_DIR, filename)

    if not os.path.exists(filepath):
        return f"Error: {filename} not found"

    cmd = ["python3", filepath]
    if args:
        cmd.extend(args.split())

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=SCRIPTS_DIR,
        )

        output = ""
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}"
        output += f"\nExit code: {result.returncode}"

        return output if output.strip() else "Script ran successfully (no output)"

    except subprocess.TimeoutExpired:
        return "Error: Script timed out after 30 seconds"
    except Exception as e:
        return f"Error running script: {e}"


@mcp.tool()
def delete_script(filename: str) -> str:
    """Delete a script from the scripts directory.

    Args:
        filename: Name of the script to delete
    """
    filepath = os.path.join(SCRIPTS_DIR, filename)

    if not os.path.exists(filepath):
        return f"Error: {filename} not found"

    os.remove(filepath)
    return f"Deleted: {filename}"


if __name__ == "__main__":
    print("Starting Script Sandbox MCP Server...")
    mcp.run(transport="stdio")
