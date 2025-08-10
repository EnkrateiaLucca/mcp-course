# Demo 2: Creating Our First MCP Server (Claude Desktop Integration)

## Overview

This demo shows how to create practical MCP servers that integrate directly with Claude Desktop, demonstrating real-world applications including an Obsidian vault integration for personal knowledge management.

## What You'll Learn

- How to create MCP servers optimized for Claude Desktop
- Building tools that interact with local file systems (Obsidian vault)
- How to configure Claude Desktop to use your MCP servers
- Best practices for MCP server development with structured data
- Testing and debugging MCP servers

## Demo Components

### Primary Example: Obsidian Vault Server
1. `obsidian_vault_server.py` - Personal knowledge management MCP server
   - **read_note**: Read any note from your Obsidian vault
   - **create_note**: Create structured notes with metadata
   - **list_notes**: Browse vault contents
   - Includes YAML frontmatter support for Obsidian compatibility

### Additional Examples
1. `file_manager_server.py` - File management MCP server
2. `claude_desktop_config.json` - Configuration for Claude Desktop
3. `test_with_inspector.py` - Testing script using MCP Inspector
4. `requirements.txt` - Dependencies

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Your Obsidian Vault Path (Optional)

The server defaults to `~/Documents/ObsidianVault`. To use a different location:

```bash
# Set environment variable
export OBSIDIAN_VAULT_PATH="/path/to/your/obsidian/vault"

# Or modify in claude_desktop_config.json
```

### 3. Configure Claude Desktop

1. Copy the configuration to Claude Desktop:
   ```bash
   # macOS/Linux
   cp claude_desktop_config.json ~/.config/Claude/claude_desktop_config.json
   
   # Windows
   # Copy to %APPDATA%\Claude\claude_desktop_config.json
   ```

2. Restart Claude Desktop for changes to take effect

### 4. Run the Servers

```bash
# Run the Obsidian vault server
uv run obsidian_vault_server.py
```

### 5. Test with Claude Desktop

Open Claude Desktop and try these prompts:

**For Obsidian Vault Server:**
- "What notes do I have in my vault?"
- "Read my note about MCP Integration"
- "Create a new project note about building an AI assistant"
- "List all notes in my Projects folder"
- "Create a daily note for today with my morning thoughts"

**For Weather Server:**
- "What's the weather like in New York?"
- "Can you check the weather forecast for London?"
- "Compare weather between Tokyo and San Francisco"

## Obsidian Vault Server Features

### Tool: `read_note`
Reads any note from your Obsidian vault including metadata and content.

**Parameters:**
- `note_path` (str): Relative path to the note (e.g., "Projects/AI Assistant.md")

**Example:**
```python
read_note("Daily Notes/2024-01-15.md")
```

### Tool: `create_note`
Creates a new structured note with YAML frontmatter for Obsidian.

**Parameters:**
- `title` (str): Note title (becomes filename)
- `content` (str): Main content in Markdown
- `folder` (str): Target folder (e.g., "Projects", "Ideas")
- `tags` (str): Comma-separated tags
- `note_type` (str): Type of note (general, idea, project, daily, reference, meeting)

**Example:**
```python
create_note(
    title="MCP Integration Planning",
    content="## Goals\n- Implement tool discovery\n- Add resource management",
    folder="Projects",
    tags="mcp,ai,development",
    note_type="project"
)
```

### Tool: `list_notes`
Browse notes in your vault with filtering options.

**Parameters:**
- `folder` (str): Specific folder to list (optional)
- `limit` (int): Maximum notes to return (default: 20, max: 50)

### Note Types and Templates

The server automatically adds structure based on note type:

- **project**: Includes Overview, Goals, Tasks, Resources sections
- **meeting**: Adds Meeting Details, Agenda, Action Items
- **daily**: Creates daily journal with Tasks and Reflection
- **idea**: Structures with The Idea, Why This Matters, Next Steps
- **reference**: Standard note for reference materials
- **general**: Basic note structure

## Testing Your Server

### Using MCP Inspector
```bash
# Test the Obsidian server
mcp dev ./obsidian_vault_server.py

# Test the weather server
mcp dev ./weather_server.py
```

### Manual Testing
```bash
# Terminal 1: Start server
python obsidian_vault_server.py

# Terminal 2: Run test client
python test_client.py
```

## Key Features Demonstrated

- **File System Integration**: Direct interaction with local Obsidian vault
- **Structured Data**: YAML frontmatter and note templates
- **Error Handling**: Graceful handling of missing files and permissions
- **Input Validation**: Parameter validation and sanitization
- **Claude Desktop Integration**: Seamless knowledge management experience

## Troubleshooting

### Server Not Appearing in Claude Desktop
1. Ensure the config file is in the correct location
2. Check file paths are absolute, not relative
3. Restart Claude Desktop after config changes

### Permission Errors
1. Ensure the vault path exists and is accessible
2. Check file permissions for the vault directory
3. The server will create a default vault structure if none exists

### Notes Not Found
1. Use exact paths including folder names
2. Include .md extension or let the server add it
3. Check the vault path configuration

## References

- [Claude Desktop MCP Guide](https://claude.ai/docs/mcp)
- [MCP Server Development Guide](https://modelcontextprotocol.io/docs/concepts/servers)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [Obsidian Documentation](https://help.obsidian.md/)