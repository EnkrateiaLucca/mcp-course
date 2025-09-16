# MCP Course Setup with uv

This is a simplified setup guide using [uv](https://docs.astral.sh/uv/), a fast Python package manager that replaces pip, poetry, and virtual environments. This approach eliminates the need to manually manage virtual environments or install dependencies.

## Quick Start

### 1. Install uv

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone and Navigate

```bash
git clone <your-repo-url>
cd mcp-course
```

### 3. Install Dependencies

uv can install all the project dependencies with a single command:

```bash
uv sync
```

This will:
- Create a virtual environment automatically
- Install Python if needed
- Install all dependencies from `requirements/requirements.txt`

## Running the Demos

### Demo 1: Introduction to MCP

The demo files already use uv's inline script dependencies feature. You can run them directly:

```bash
# Run the MCP server
uv run demos/01-introduction-to-mcp/mcp_server.py

# In another terminal, run the client
uv run demos/01-introduction-to-mcp/mcp_client.py demos/01-introduction-to-mcp/mcp_server.py
```

### Other Demos

For demos that have their own `requirements.txt`:

```bash
# Navigate to the demo directory
cd demos/08-automations-agent

# Install demo-specific dependencies
uv sync --extra-requirements requirements.txt

# Run the demo
uv run run_agent.py
```

## Why uv?

- **10-100x faster** than pip for dependency resolution
- **No virtual environment management** - uv handles it automatically
- **Inline dependencies** - Scripts can declare their own dependencies
- **Cross-platform** - Works on macOS, Linux, and Windows
- **All-in-one** - Replaces pip, virtualenv, and pyenv

## Traditional Setup (Alternative)

If you prefer the traditional approach:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/requirements.txt
```

## Development Commands

With uv, you can run commands in the project environment:

```bash
# Run Python scripts
uv run python script.py

# Install additional packages
uv add package-name

# Run specific Python version
uv run --python 3.11 script.py

# Access the shell
uv shell
```

## MCP Inspector

To use the MCP inspector with any server:

```bash
uv run mcp dev demos/01-introduction-to-mcp/mcp_server.py
```

This will start an interactive inspector to test your MCP server.

## Project Structure

```
mcp-course/
├── requirements/
│   ├── requirements.in      # Main dependencies
│   └── requirements.txt     # Locked dependencies (uv compatible)
├── demos/
│   ├── 01-introduction-to-mcp/
│   │   ├── mcp_server.py    # Uses uv script dependencies
│   │   └── mcp_client.py    # Uses uv script dependencies
│   └── ...
└── readme-uv.md            # This file
```

## Troubleshooting

**Command not found: uv**
- Make sure uv is installed and in your PATH
- Restart your terminal after installation

**Permission errors**
- On Unix systems: `chmod +x demos/01-introduction-to-mcp/mcp_server.py`

**Python version issues**
- uv can install Python versions: `uv python install 3.11`
- Pin project Python: `uv python pin 3.11`

## Learn More

- [uv Documentation](https://docs.astral.sh/uv/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/fastmcp)