#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "mcp[cli]==1.9.3",
#     "pydantic>=2.0.0"
# ]
# ///

"""
Obsidian Vault MCP Server for Claude Desktop

This server provides tools to interact with your Obsidian vault, allowing you to:
- Read notes from your personal knowledge base
- Create new notes with structured metadata

Perfect for integrating your personal knowledge management system with AI assistants.

Based on MCP Python SDK documentation:
https://github.com/modelcontextprotocol/python-sdk

MCP server config reference:
"obsidian-vault": {
      "command": "uv"
      "args": [
        "--directory",
        "/Users/greatmaster/Desktop/projects/oreilly-live-trainings/mcp-course/demos/02-first-mcp-server/"
        "run",
        "obsidian_vault_server.py"
      ]
    }
"""

import asyncio
import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS

# Create MCP server instance with a descriptive name
mcp = FastMCP("obsidian-vault")

# Configuration: Set your Obsidian vault path here
# You can override this with the OBSIDIAN_VAULT_PATH environment variable
DEFAULT_VAULT_PATH = os.environ.get(
    "OBSIDIAN_VAULT_PATH",
    str(Path(__file__).parent / "sample_vault_notes")
)

print(DEFAULT_VAULT_PATH)

def get_vault_path() -> Path:
    """
    Get the configured Obsidian vault path.
    
    Returns:
        Path object pointing to the Obsidian vault directory
    """
    vault_path = Path(DEFAULT_VAULT_PATH)
    
    # Ensure the vault directory exists
    if not vault_path.exists():
        print(f"❌ Vault directory does not exist: {vault_path}")
        print("💡 Please set the OBSIDIAN_VAULT_PATH environment variable to the correct path.")
        print("💡 For example: export OBSIDIAN_VAULT_PATH=/path/to/your/obsidian/vault")
        print("💡 Or add it to your .zshrc or .bashrc file.")
        print("💡 Then restart your terminal or source the file.")
        print("💡 Or run: source ~/.zshrc or source ~/.bashrc")
        print("💡 Or restart your terminal.")
            
    return vault_path

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to be safe for the filesystem.
    
    Args:
        filename: The proposed filename
        
    Returns:
        A sanitized version of the filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '-')
    
    # Ensure it ends with .md
    if not filename.endswith('.md'):
        filename += '.md'
    
    return filename

def format_note_metadata(title: str, tags: List[str], note_type: str) -> str:
    """
    Create YAML frontmatter metadata for an Obsidian note.
    
    Args:
        title: The note title
        tags: List of tags for the note
        note_type: Type of note (e.g., 'idea', 'project', 'daily', 'reference')
        
    Returns:
        Formatted YAML frontmatter string
    """
    # Generate metadata in YAML format (Obsidian's frontmatter)
    metadata = f"""---
title: {title}
created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
modified: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
type: {note_type}
tags: {' '.join([f'#{tag}' for tag in tags])}
---

"""
    return metadata

@mcp.tool()
def read_note(note_name: str) -> str:
    """
    Read a note from your Obsidian vault.
    
    This tool retrieves the content of any note in your vault, including
    its metadata and markdown content.
    
    Args:
        note_name: Name of the note within the vault (e.g., "Daily Notes/2024-01-15.md")
        
    Returns:
        The complete content of the note including frontmatter and body
        
    Example:
        read_note("Projects/MCP Integration.md") - reads a project note
        read_note("Daily Notes/2024-01-15.md") - reads a daily note
    """
    try:
        vault_path = get_vault_path()
        
        # Construct the full path to the note
        full_path = vault_path / note_name
        
        # Add .md extension if not present
        if not str(full_path).endswith('.md'):
            full_path = Path(str(full_path) + '.md')
        
        # Check if the note exists
        if not full_path.exists():
            # Try to find similar notes for helpful suggestions
            similar_notes = []
            search_term = Path(note_name).stem.lower()
            
            for md_file in vault_path.rglob("*.md"):
                if search_term in md_file.stem.lower():
                    relative_path = md_file.relative_to(vault_path)
                    similar_notes.append(str(relative_path))
            
            if similar_notes:
                suggestions = "\n".join([f"  • {note}" for note in similar_notes[:5]])
                return f"""❌ Note not found: '{note_name}'

Did you mean one of these?
{suggestions}

💡 Tip: Use the exact path including folders, e.g., "Daily Notes/2024-01-15.md"
"""
            else:
                return f"""❌ Note not found: '{note_name}'

The note doesn't exist in your vault at:
{vault_path}

💡 Tip: Make sure to include the folder path if the note is in a subfolder.
Example: "Projects/My Project.md" or "Daily Notes/2024-01-15.md"
"""
        
        # Read the note content
        content = full_path.read_text(encoding='utf-8')
        
        # Get file stats for additional context
        stats = full_path.stat()
        modified_time = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        file_size = stats.st_size
        
        # Format the response with metadata
        response = f"""📝 **Note: {note_name}**

**Last Modified**: {modified_time}
**Size**: {file_size} bytes
**Location**: {full_path}

---

{content}"""
        
        return response
        
    except PermissionError:
        return f"❌ Permission denied: Cannot read '{note_name}'. Please check file permissions."
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"Failed to read note '{note_name}': {str(e)}"
            )
        ) from e

@mcp.tool()
def create_note(
    title: str,
    content: str,
    folder: str = "",
    tags: str = "",
    note_type: str = "general"
) -> str:
    """
    Create a new note in your Obsidian vault with structured metadata.
    
    This tool creates a properly formatted Obsidian note with YAML frontmatter,
    organizing it in the specified folder with appropriate tags.
    
    Args:
        title: The title of the note (will be used as filename)
        content: The main content of the note (markdown supported)
        folder: Folder to place the note in (e.g., "Projects", "Daily Notes", "Ideas")
        tags: Comma-separated tags for the note (e.g., "python,mcp,development")
        note_type: Type of note - one of: general, idea, project, daily, reference, meeting
        
    Returns:
        Confirmation message with the path to the created note
        
    Example:
        create_note(
            title="MCP Integration Ideas",
            content="## Key Features\\n- Tool discovery\\n- Resource management",
            folder="Projects",
            tags="mcp,integration,ai",
            note_type="project"
        )
    """
    try:
        vault_path = get_vault_path()
        
        # Sanitize the filename
        filename = sanitize_filename(title)
        
        # Determine the target folder
        if folder:
            target_folder = vault_path / folder
            target_folder.mkdir(parents=True, exist_ok=True)
        else:
            target_folder = vault_path
        
        # Full path for the new note
        note_path = target_folder / filename
        
        # Check if note already exists
        if note_path.exists():
            return f"""⚠️ Note already exists: '{note_path.relative_to(vault_path)}'

The note '{title}' already exists in {folder if folder else 'root folder'}.

Options:
1. Choose a different title
2. Read the existing note with: read_note("{note_path.relative_to(vault_path)}")
3. Create the note in a different folder
"""
        
        # Process tags
        tag_list = [tag.strip() for tag in tags.split(',')] if tags else []
        
        # Validate note type
        valid_types = ['general', 'idea', 'project', 'daily', 'reference', 'meeting']
        if note_type not in valid_types:
            note_type = 'general'
        
        # Generate the note content with metadata
        frontmatter = format_note_metadata(title, tag_list, note_type)
        
        # Add structure based on note type
        structured_content = frontmatter + f"# {title}\n\n"
        
        # Add type-specific template structure
        if note_type == 'project':
            structured_content += """## Overview


## Goals
- [ ] 

## Tasks
- [ ] 

## Resources


## Notes

"""
        elif note_type == 'meeting':
            structured_content += f"""## Meeting Details
**Date**: {datetime.now().strftime('%Y-%m-%d')}
**Attendees**: 
**Purpose**: 

## Agenda


## Discussion


## Action Items
- [ ] 

## Next Steps


"""
        elif note_type == 'daily':
            structured_content += f"""## {datetime.now().strftime('%A, %B %d, %Y')}

### Morning Thoughts


### Today's Tasks
- [ ] 

### Notes


### Reflection


"""
        elif note_type == 'idea':
            structured_content += """## The Idea


## Why This Matters


## Implementation Thoughts


## Next Steps
- [ ] Research
- [ ] Prototype
- [ ] Validate

"""
        
        # Add the user's content
        structured_content += content
        
        # Add footer with creation context
        structured_content += f"""

---
*Created via MCP Server on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*
"""
        
        # Write the note to disk
        note_path.write_text(structured_content, encoding='utf-8')
        
        # Generate success response
        relative_path = note_path.relative_to(vault_path)
        response = f"""✅ **Note Created Successfully!**

📝 **Title**: {title}
📁 **Location**: {relative_path}
🏷️ **Tags**: {', '.join([f'#{tag}' for tag in tag_list]) if tag_list else 'none'}
📑 **Type**: {note_type}
⏰ **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Full Path**: {note_path}

Your note has been created and is ready to use in Obsidian!
You can now:
- Open it in Obsidian to see it with full formatting
- Read it back using: read_note("{relative_path}")
- Link to it from other notes using: [[{title}]]
"""
        
        return response
        
    except PermissionError:
        return f"❌ Permission denied: Cannot create note in '{folder}'. Please check folder permissions."
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"Failed to create note '{title}': {str(e)}"
            )
        ) from e

@mcp.tool()
def list_notes(folder: str = "", limit: int = 20) -> str:
    """
    List notes in your Obsidian vault, optionally filtered by folder.
    
    Args:
        folder: Specific folder to list notes from (empty for all notes)
        limit: Maximum number of notes to return (default: 20, max: 50)
        
    Returns:
        A formatted list of notes with their paths and modification times
    """
    try:
        vault_path = get_vault_path()
        
        # Determine search path
        if folder:
            search_path = vault_path / folder
            if not search_path.exists():
                return f"❌ Folder not found: '{folder}'"
        else:
            search_path = vault_path
        
        # Limit the number of results
        limit = min(limit, 50)
        
        # Find all markdown files
        notes = []
        for md_file in search_path.rglob("*.md"):
            relative_path = md_file.relative_to(vault_path)
            modified_time = datetime.fromtimestamp(md_file.stat().st_mtime)
            notes.append((relative_path, modified_time, md_file))
        
        # Sort by modification time (newest first)
        notes.sort(key=lambda x: x[1], reverse=True)
        
        # Format response
        if not notes:
            return f"📭 No notes found in {'folder: ' + folder if folder else 'vault'}"
        
        response = f"📚 **Notes in {'folder: ' + folder if folder else 'your vault'}**\n\n"
        response += f"Found {len(notes)} notes (showing {min(len(notes), limit)})\n\n"
        
        for i, (rel_path, mod_time, full_path) in enumerate(notes[:limit], 1):
            # Try to extract title from frontmatter or first heading
            try:
                content = full_path.read_text(encoding='utf-8')
                lines = content.split('\n')
                title = None
                
                # Look for title in frontmatter
                if lines[0] == '---':
                    for line in lines[1:]:
                        if line == '---':
                            break
                        if line.startswith('title:'):
                            title = line.replace('title:', '').strip()
                            break
                
                # If no title in frontmatter, use first # heading
                if not title:
                    for line in lines:
                        if line.startswith('# '):
                            title = line.replace('# ', '').strip()
                            break
                
                # Default to filename without extension
                if not title:
                    title = full_path.stem
                    
            except:
                title = full_path.stem
            
            response += f"{i}. **{title}**\n"
            response += f"   📄 Path: `{rel_path}`\n"
            response += f"   🕒 Modified: {mod_time.strftime('%Y-%m-%d %H:%M')}\n\n"
        
        if len(notes) > limit:
            response += f"\n*Showing {limit} of {len(notes)} notes. Increase limit or specify a folder to see more.*"
        
        return response
        
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"Failed to list notes: {str(e)}"
            )
        ) from e

@mcp.resource("obsidian://vault/info")
def vault_info() -> str:
    """
    Get information about your Obsidian vault configuration and statistics.
    
    This resource provides an overview of your vault structure and contents.
    """
    try:
        vault_path = get_vault_path()
        
        # Gather statistics
        total_notes = len(list(vault_path.rglob("*.md")))
        
        # Count notes by folder
        folder_stats = {}
        for md_file in vault_path.rglob("*.md"):
            folder = md_file.parent.relative_to(vault_path)
            folder_name = str(folder) if str(folder) != "." else "Root"
            folder_stats[folder_name] = folder_stats.get(folder_name, 0) + 1
        
        # Get vault size
        total_size = sum(f.stat().st_size for f in vault_path.rglob("*.md"))
        size_mb = total_size / (1024 * 1024)
        
        # Format response
        response = f"""🗂️ **Obsidian Vault Information**

**Location**: {vault_path}
**Total Notes**: {total_notes}
**Total Size**: {size_mb:.2f} MB

**📁 Notes by Folder**:
"""
        
        for folder, count in sorted(folder_stats.items()):
            response += f"  • {folder}: {count} notes\n"
        
        response += f"""
**🛠️ Available Tools**:
  • `read_note(note_path)` - Read any note from your vault
  • `create_note(title, content, ...)` - Create structured notes
  • `list_notes(folder, limit)` - Browse your notes

**💡 Tips**:
  • Notes are stored as Markdown files with YAML frontmatter
  • Use folders to organize: Projects/, Daily Notes/, Ideas/, etc.
  • Tags help with cross-referencing and discovery
  • All notes are compatible with Obsidian's features

*Vault accessed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return response
        
    except Exception as e:
        return f"❌ Could not retrieve vault information: {str(e)}"

@mcp.prompt()
def obsidian_assistant_prompt() -> str:
    """
    A specialized prompt for Obsidian vault assistance.
    
    This prompt configures the assistant to be helpful with note-taking
    and knowledge management tasks.
    """
    return f"""You are a helpful Obsidian vault assistant with direct access to the user's personal knowledge base.

**Your capabilities include:**

📖 **Reading Notes**: Use `read_note(note_path)` to retrieve any note from the vault
✍️ **Creating Notes**: Use `create_note(title, content, folder, tags, note_type)` to create structured notes
📚 **Browsing**: Use `list_notes(folder, limit)` to explore the vault contents
ℹ️ **Vault Info**: Reference the `obsidian://vault/info` resource for vault statistics

**Vault Location**: {get_vault_path()}

**Note Types Available**:
- **general**: Standard notes
- **idea**: For capturing thoughts and concepts
- **project**: For project documentation with goals and tasks
- **daily**: For daily journaling with reflection sections
- **reference**: For storing reference materials
- **meeting**: For meeting notes with agenda and action items

**Common Folders**:
- Daily Notes: For daily journaling
- Projects: For project-related documentation
- Ideas: For capturing thoughts and ideas
- References: For storing reference materials

**Best Practices**:
- Always use descriptive titles for new notes
- Add relevant tags to improve discoverability
- Use the appropriate note_type for better structure
- Create notes in appropriate folders for organization
- Link between notes using [[Note Title]] syntax
- Include context and timestamps in notes

When users ask about their notes or want to create new ones, help them effectively manage their personal knowledge base!
"""

if __name__ == "__main__":
    print("🗂️ Obsidian Vault MCP Server Starting...")
    print("=" * 50)
    
    vault_path = get_vault_path()
    print(f"📁 Vault Location: {vault_path}")
    
    if not vault_path.exists():
        print("⚠️  Vault doesn't exist - it will be created with sample structure")
    else:
        note_count = len(list(vault_path.rglob("*.md")))
        print(f"📝 Found {note_count} notes in vault")
    
    print("\n🛠️ Available tools:")
    print("   • read_note(note_path) - Read any note")
    print("   • create_note(title, content, ...) - Create structured notes")
    print("   • list_notes(folder, limit) - Browse vault contents")
    
    print("\n📊 Available resources:")
    print("   • obsidian://vault/info - Vault statistics and configuration")
    
    print("\n📝 Available prompts:")
    print("   • obsidian_assistant_prompt - Specialized knowledge management prompt")
    
    print("\n💡 To use with Claude Desktop:")
    print("   1. Set OBSIDIAN_VAULT_PATH environment variable (optional)")
    print("   2. Add this server to Claude Desktop config")
    print("   3. Restart Claude Desktop")
    print("   4. Start managing your knowledge base with AI!")
    
    print("\n🚀 Starting server on stdio transport...")
    
    # Run the server using stdio transport (standard for Claude Desktop)
    mcp.run(transport="stdio")