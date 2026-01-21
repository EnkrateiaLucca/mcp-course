#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "anthropic-claude-sdk",
# ]
# ///
"""
MCP Server Setup and Configuration

This example demonstrates how to create and configure MCP (Model Context Protocol)
servers for filesystem operations with the Claude Agent SDK.

Source: https://github.com/anthropics/claude-agent-sdk-python
Examples: https://github.com/anthropics/claude-agent-sdk-python/tree/main/examples
MCP Docs: https://modelcontextprotocol.io/introduction

Learning Objectives:
1. Understand MCP architecture (Host, Client, Server)
2. Create in-process SDK MCP servers
3. Define custom tools with @tool decorator
4. Mix in-process and external MCP servers
5. Configure agent with MCP servers

Key Concepts:
- MCP provides standardized AI-to-system connections
- In-process servers run in same Python process (better performance)
- External servers run as subprocesses (use existing tools)
- Tools are defined with name, description, and parameter schema
"""

import asyncio
from typing import Any
from pathlib import Path

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    tool,
    create_sdk_mcp_server,
    AssistantMessage,
    TextBlock,
    ResultMessage,
)


# =============================================================================
# PART 1: Simple Custom Tool
# =============================================================================

@tool(
    "read_config",  # Tool identifier (used in allowed_tools)
    "Read configuration from a file",  # Human-readable description
    {"filename": str}  # Parameter schema with types
)
async def read_config(args: dict[str, Any]) -> dict[str, Any]:
    """
    Custom tool implementation for reading configuration files.

    Args:
        args: Dictionary containing 'filename' parameter

    Returns:
        Dictionary with 'content' array and optional 'is_error' flag

    Tool Return Format:
    {
        "content": [{"type": "text", "text": "..."}],
        "is_error": False  # Optional, indicates error
    }
    """
    filename = args['filename']

    try:
        # Attempt to read file
        with open(filename, 'r') as f:
            content = f.read()

        # Success: return content
        return {
            "content": [
                {"type": "text", "text": f"Configuration from {filename}:\n\n{content}"}
            ]
        }

    except FileNotFoundError:
        # Error: return error flag
        return {
            "content": [
                {"type": "text", "text": f"Error: File '{filename}' not found"}
            ],
            "is_error": True
        }

    except PermissionError:
        return {
            "content": [
                {"type": "text", "text": f"Error: Permission denied for '{filename}'"}
            ],
            "is_error": True
        }


# =============================================================================
# PART 2: Multiple Custom Tools
# =============================================================================

@tool("list_files", "List files in a directory", {"directory": str})
async def list_files(args: dict[str, Any]) -> dict[str, Any]:
    """List files in specified directory."""
    directory = args['directory']

    try:
        path = Path(directory)

        if not path.exists():
            return {
                "content": [{"type": "text", "text": f"Error: Directory '{directory}' not found"}],
                "is_error": True
            }

        if not path.is_dir():
            return {
                "content": [{"type": "text", "text": f"Error: '{directory}' is not a directory"}],
                "is_error": True
            }

        # List all files
        files = [f.name for f in path.iterdir() if f.is_file()]
        files.sort()

        if not files:
            result = f"No files found in {directory}"
        else:
            result = f"Files in {directory}:\n" + "\n".join(f"  - {f}" for f in files)

        return {
            "content": [{"type": "text", "text": result}]
        }

    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "is_error": True
        }


@tool("file_info", "Get information about a file", {"filepath": str})
async def file_info(args: dict[str, Any]) -> dict[str, Any]:
    """Get detailed information about a file."""
    filepath = args['filepath']

    try:
        path = Path(filepath)

        if not path.exists():
            return {
                "content": [{"type": "text", "text": f"Error: File '{filepath}' not found"}],
                "is_error": True
            }

        # Gather file information
        stat = path.stat()
        info = f"""File Information: {filepath}
- Type: {"File" if path.is_file() else "Directory"}
- Size: {stat.st_size} bytes
- Modified: {stat.st_mtime}
- Permissions: {oct(stat.st_mode)[-3:]}
"""

        return {
            "content": [{"type": "text", "text": info}]
        }

    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "is_error": True
        }


# =============================================================================
# PART 3: Create In-Process MCP Server
# =============================================================================

def create_file_tools_server():
    """
    Create an in-process MCP server with file tools.

    Benefits of in-process servers:
    - No subprocess management
    - Better performance (no IPC overhead)
    - Simpler deployment (single Python process)
    - Easier debugging (standard Python tools)
    - Type safety (direct function calls)
    """

    file_server = create_sdk_mcp_server(
        name="file-tools",      # Server name (used in tool identifiers)
        version="1.0.0",        # Version for tracking
        tools=[                 # List of tool functions
            read_config,
            list_files,
            file_info
        ]
    )

    return file_server


# =============================================================================
# PART 4: Agent Configuration with MCP Server
# =============================================================================

async def example_basic_mcp_server():
    """
    Example 1: Basic MCP server configuration.

    Shows how to:
    1. Create an in-process MCP server
    2. Attach it to ClaudeAgentOptions
    3. Specify allowed tools with mcp__ prefix
    4. Query the agent using custom tools
    """

    print("="*60)
    print("Example 1: Basic MCP Server")
    print("="*60)

    # Create MCP server
    file_server = create_file_tools_server()

    # Configure agent with MCP server
    options = ClaudeAgentOptions(
        mcp_servers={
            "files": file_server  # Key "files" becomes part of tool name
        },
        # Tool names follow pattern: mcp__<server_key>__<tool_name>
        allowed_tools=[
            "mcp__files__read_config",
            "mcp__files__list_files",
            "mcp__files__file_info"
        ],
        cwd=Path.cwd()  # Set working directory
    )

    # Use the agent
    async with ClaudeSDKClient(options=options) as client:
        await client.query("List all Python files in the current directory")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"\n{block.text}")

            elif isinstance(message, ResultMessage):
                print(f"\nCompleted. Cost: ${message.total_cost_usd:.4f}")


# =============================================================================
# PART 5: Mixed Server Configuration
# =============================================================================

async def example_mixed_servers():
    """
    Example 2: Mix in-process and external MCP servers.

    Demonstrates combining:
    - In-process SDK server (custom tools)
    - External subprocess server (existing filesystem MCP server)

    Note: This example shows configuration but may not run if external
    MCP server is not installed. Kept for educational purposes.
    """

    print("\n" + "="*60)
    print("Example 2: Mixed Server Configuration")
    print("="*60)

    # Create in-process server
    custom_server = create_file_tools_server()

    # Configure with both server types
    options = ClaudeAgentOptions(
        mcp_servers={
            # In-process SDK server
            "custom": custom_server,

            # External subprocess server (example configuration)
            # Uncomment if you have @modelcontextprotocol/server-filesystem installed
            # "external": {
            #     "type": "stdio",
            #     "command": "npx",
            #     "args": [
            #         "-y",
            #         "@modelcontextprotocol/server-filesystem",
            #         str(Path.cwd())
            #     ]
            # }
        },
        allowed_tools=[
            "mcp__custom__read_config",
            "mcp__custom__list_files",
            # "mcp__external__read_file",  # From external server
            # "mcp__external__write_file",  # From external server
        ],
        cwd=Path.cwd()
    )

    print("\nConfiguration created with mixed servers.")
    print("In production, you would use this with ClaudeSDKClient.")
    print("\nServer configuration:")
    print("  - custom (in-process): read_config, list_files, file_info")
    print("  - external (subprocess): read_file, write_file (if installed)")


# =============================================================================
# PART 6: Tool Discovery at Runtime
# =============================================================================

async def example_tool_discovery():
    """
    Example 3: Discover available tools at runtime.

    Shows how to:
    1. Extract tool information from SystemMessage
    2. List all available tools
    3. Inspect tool configurations
    """

    print("\n" + "="*60)
    print("Example 3: Tool Discovery")
    print("="*60)

    from claude_agent_sdk import SystemMessage

    # Create server and options
    file_server = create_file_tools_server()

    options = ClaudeAgentOptions(
        mcp_servers={"files": file_server},
        allowed_tools=[
            "mcp__files__read_config",
            "mcp__files__list_files",
            "mcp__files__file_info"
        ],
        cwd=Path.cwd()
    )

    # Connect and inspect initialization
    async with ClaudeSDKClient(options=options) as client:
        await client.query("Hello")

        async for message in client.receive_response():
            # SystemMessage with subtype "init" contains tool information
            if isinstance(message, SystemMessage) and message.subtype == "init":
                tools = message.data.get("tools", [])

                print(f"\nFound {len(tools)} tools:")
                for tool_name in tools:
                    print(f"  - {tool_name}")

                break  # Exit after finding init message


# =============================================================================
# PART 7: Best Practices
# =============================================================================

def demonstrate_best_practices():
    """
    Best practices for MCP server configuration.
    """

    print("\n" + "="*60)
    print("Best Practices Summary")
    print("="*60)

    practices = [
        {
            "title": "1. Use In-Process Servers for Custom Tools",
            "why": "Avoid subprocess overhead, better performance",
            "example": "create_sdk_mcp_server(name='custom', tools=[my_tool])"
        },
        {
            "title": "2. Namespace Tools Properly",
            "why": "Prevents conflicts, improves clarity",
            "example": "mcp__servername__toolname"
        },
        {
            "title": "3. Set Working Directory Explicitly",
            "why": "Establishes clear context for file operations",
            "example": "ClaudeAgentOptions(cwd=Path.cwd())"
        },
        {
            "title": "4. Version Your Servers",
            "why": "Track compatibility and changes",
            "example": "create_sdk_mcp_server(name='tools', version='1.0.0')"
        },
        {
            "title": "5. Handle Errors in Tools",
            "why": "Provide helpful feedback to agent",
            "example": "return {'content': [...], 'is_error': True}"
        },
        {
            "title": "6. Validate Tool Inputs",
            "why": "Security and correctness",
            "example": "Check paths, sanitize inputs before processing"
        }
    ]

    for practice in practices:
        print(f"\n{practice['title']}")
        print(f"  Why: {practice['why']}")
        print(f"  Example: {practice['example']}")


# =============================================================================
# Main Execution
# =============================================================================

async def main():
    """
    Run all MCP server examples.

    Note: Some examples may require additional setup (Claude Code CLI, etc.)
    """

    print("MCP Server Configuration Examples")
    print("Source: https://github.com/anthropics/claude-agent-sdk-python\n")

    try:
        # Example 1: Basic MCP server
        await example_basic_mcp_server()

        # Example 2: Mixed servers (configuration only)
        await example_mixed_servers()

        # Example 3: Tool discovery
        await example_tool_discovery()

        # Best practices (informational)
        demonstrate_best_practices()

        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60)

    except Exception as e:
        print(f"\nError running examples: {e}")
        print("\nNote: Examples require Claude Code CLI to be installed.")
        print("Install from: https://claude.ai/download")


if __name__ == "__main__":
    asyncio.run(main())
