#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "anthropic-claude-sdk",
# ]
# ///
"""
Complete File Reader Agent Implementation

A production-ready file reader agent demonstrating:
- MCP server configuration with custom file tools
- Comprehensive permission management
- Real-time streaming responses
- Multi-layer error handling with hooks
- Execution tracking and cost monitoring

Source: https://github.com/anthropics/claude-agent-sdk-python

Usage:
    uv run file_reader_agent.py

Features:
- Safe file reading with validation
- Directory listing and file information
- Text file search capabilities
- Dangerous operation blocking (PreToolUse hooks)
- Error monitoring (PostToolUse hooks)
- Real-time response streaming
- Cost and performance tracking
"""

import asyncio
import logging
from typing import Any, List, Dict
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    tool,
    create_sdk_mcp_server,
    HookMatcher,
    HookInput,
    HookContext,
    HookJSONOutput,
    PermissionResultAllow,
    PermissionResultDeny,
    ToolPermissionContext,
    # Message types
    SystemMessage,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultMessage,
    # Exceptions
    ClaudeSDKError,
    CLINotFoundError,
    CLIConnectionError,
    ProcessError,
)

# =============================================================================
# Logging Configuration
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("FileReaderAgent")


# =============================================================================
# Custom File Tools
# =============================================================================

@tool("read_file", "Read contents of a text file", {"filepath": str})
async def read_file(args: dict[str, Any]) -> dict[str, Any]:
    """
    Read a text file with comprehensive error handling.

    Args:
        filepath: Path to the file to read

    Returns:
        File contents or error message
    """
    filepath = args['filepath']
    logger.info(f"Reading file: {filepath}")

    try:
        path = Path(filepath)

        # Validation checks
        if not path.exists():
            logger.warning(f"File not found: {filepath}")
            return {
                "content": [{"type": "text", "text": f"Error: File not found: {filepath}"}],
                "is_error": True
            }

        if not path.is_file():
            logger.warning(f"Not a file: {filepath}")
            return {
                "content": [{"type": "text", "text": f"Error: '{filepath}' is not a file"}],
                "is_error": True
            }

        # Read file
        content = path.read_text()
        logger.info(f"Successfully read {len(content)} bytes from {filepath}")

        return {
            "content": [{"type": "text", "text": f"Contents of {filepath}:\n\n{content}"}]
        }

    except PermissionError:
        logger.error(f"Permission denied: {filepath}")
        return {
            "content": [{"type": "text", "text": f"Error: Permission denied for '{filepath}'"}],
            "is_error": True
        }

    except UnicodeDecodeError:
        logger.error(f"Not a text file: {filepath}")
        return {
            "content": [{"type": "text", "text": f"Error: '{filepath}' is not a valid text file"}],
            "is_error": True
        }

    except Exception as e:
        logger.exception(f"Error reading file: {e}")
        return {
            "content": [{"type": "text", "text": f"Error: {type(e).__name__}: {str(e)}"}],
            "is_error": True
        }


@tool("list_directory", "List files in a directory", {"directory": str})
async def list_directory(args: dict[str, Any]) -> dict[str, Any]:
    """
    List all files and directories in a given path.

    Args:
        directory: Path to the directory

    Returns:
        List of files and directories
    """
    directory = args['directory']
    logger.info(f"Listing directory: {directory}")

    try:
        path = Path(directory)

        if not path.exists():
            logger.warning(f"Directory not found: {directory}")
            return {
                "content": [{"type": "text", "text": f"Error: Directory not found: {directory}"}],
                "is_error": True
            }

        if not path.is_dir():
            logger.warning(f"Not a directory: {directory}")
            return {
                "content": [{"type": "text", "text": f"Error: '{directory}' is not a directory"}],
                "is_error": True
            }

        # List contents
        files = []
        dirs = []

        for item in sorted(path.iterdir()):
            if item.is_file():
                size = item.stat().st_size
                files.append(f"  📄 {item.name} ({size} bytes)")
            elif item.is_dir():
                dirs.append(f"  📁 {item.name}/")

        result = f"Contents of {directory}:\n\n"

        if dirs:
            result += "Directories:\n" + "\n".join(dirs) + "\n\n"

        if files:
            result += "Files:\n" + "\n".join(files)

        if not dirs and not files:
            result += "(empty directory)"

        logger.info(f"Listed {len(dirs)} directories and {len(files)} files")

        return {
            "content": [{"type": "text", "text": result}]
        }

    except PermissionError:
        logger.error(f"Permission denied: {directory}")
        return {
            "content": [{"type": "text", "text": f"Error: Permission denied for '{directory}'"}],
            "is_error": True
        }

    except Exception as e:
        logger.exception(f"Error listing directory: {e}")
        return {
            "content": [{"type": "text", "text": f"Error: {type(e).__name__}: {str(e)}"}],
            "is_error": True
        }


@tool("file_info", "Get detailed information about a file", {"filepath": str})
async def file_info(args: dict[str, Any]) -> dict[str, Any]:
    """
    Get detailed information about a file.

    Args:
        filepath: Path to the file

    Returns:
        File metadata and statistics
    """
    filepath = args['filepath']
    logger.info(f"Getting file info: {filepath}")

    try:
        path = Path(filepath)

        if not path.exists():
            logger.warning(f"File not found: {filepath}")
            return {
                "content": [{"type": "text", "text": f"Error: File not found: {filepath}"}],
                "is_error": True
            }

        # Gather statistics
        stat = path.stat()
        from datetime import datetime

        info = f"""File Information: {filepath}

Type: {"File" if path.is_file() else "Directory" if path.is_dir() else "Other"}
Size: {stat.st_size:,} bytes
Modified: {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}
Permissions: {oct(stat.st_mode)[-3:]}
Readable: {path.stat().st_mode & 0o400 != 0}
Writable: {path.stat().st_mode & 0o200 != 0}
"""

        if path.is_file():
            try:
                # Try to detect if it's a text file
                with open(path, 'r') as f:
                    f.read(1024)
                info += "File Type: Text file\n"
            except UnicodeDecodeError:
                info += "File Type: Binary file\n"

        logger.info(f"Retrieved file info for {filepath}")

        return {
            "content": [{"type": "text", "text": info}]
        }

    except Exception as e:
        logger.exception(f"Error getting file info: {e}")
        return {
            "content": [{"type": "text", "text": f"Error: {type(e).__name__}: {str(e)}"}],
            "is_error": True
        }


@tool("search_in_file", "Search for text in a file", {"filepath": str, "search_term": str})
async def search_in_file(args: dict[str, Any]) -> dict[str, Any]:
    """
    Search for a term in a text file.

    Args:
        filepath: Path to the file
        search_term: Text to search for

    Returns:
        Matching lines with line numbers
    """
    filepath = args['filepath']
    search_term = args['search_term']
    logger.info(f"Searching for '{search_term}' in {filepath}")

    try:
        path = Path(filepath)

        if not path.exists():
            return {
                "content": [{"type": "text", "text": f"Error: File not found: {filepath}"}],
                "is_error": True
            }

        if not path.is_file():
            return {
                "content": [{"type": "text", "text": f"Error: Not a file: {filepath}"}],
                "is_error": True
            }

        # Search file
        content = path.read_text()
        lines = content.split('\n')

        matches = []
        for i, line in enumerate(lines, 1):
            if search_term.lower() in line.lower():
                matches.append(f"  Line {i}: {line.strip()}")

        if matches:
            result = f"Found {len(matches)} match(es) for '{search_term}' in {filepath}:\n\n"
            result += "\n".join(matches)
            logger.info(f"Found {len(matches)} matches")
        else:
            result = f"No matches found for '{search_term}' in {filepath}"
            logger.info("No matches found")

        return {
            "content": [{"type": "text", "text": result}]
        }

    except UnicodeDecodeError:
        return {
            "content": [{"type": "text", "text": f"Error: File is not a text file: {filepath}"}],
            "is_error": True
        }

    except Exception as e:
        logger.exception(f"Error searching file: {e}")
        return {
            "content": [{"type": "text", "text": f"Error: {type(e).__name__}: {str(e)}"}],
            "is_error": True
        }


# =============================================================================
# Permission Management
# =============================================================================

async def permission_callback(
    tool_name: str,
    input_data: dict,
    context: ToolPermissionContext
) -> PermissionResultAllow | PermissionResultDeny:
    """
    Custom permission callback for tool authorization.

    Security policies:
    - Block access to system directories
    - Block sensitive file patterns
    - Allow read operations in safe locations
    """

    logger.debug(f"Permission check: {tool_name}")

    # Extract filepath from input
    filepath = input_data.get("filepath") or input_data.get("directory") or ""

    if filepath:
        # Block system directories
        system_dirs = ["/etc/", "/sys/", "/usr/", "/bin/", "/sbin/", "/var/", "/root/"]
        for sys_dir in system_dirs:
            if filepath.startswith(sys_dir):
                logger.warning(f"Blocked system directory access: {filepath}")
                return PermissionResultDeny(
                    message=f"Access denied: Cannot access system directory {sys_dir}"
                )

        # Block sensitive files
        sensitive_patterns = [".env", "credentials", "secrets", "private_key", "id_rsa"]
        filename = Path(filepath).name.lower()

        for pattern in sensitive_patterns:
            if pattern in filename:
                logger.warning(f"Blocked sensitive file: {filepath}")
                return PermissionResultDeny(
                    message="Access denied: Cannot access sensitive file"
                )

    logger.debug(f"Permission granted: {tool_name}")
    return PermissionResultAllow()


# =============================================================================
# PreToolUse Hook - Validation
# =============================================================================

async def validate_file_access(
    input_data: HookInput,
    tool_use_id: str | None,
    context: HookContext
) -> HookJSONOutput:
    """
    PreToolUse hook: Validate file access before execution.
    """

    tool_input = input_data.get("tool_input", {})
    filepath = tool_input.get("filepath") or tool_input.get("directory") or ""

    if not filepath:
        return {}

    logger.debug(f"Validating file access: {filepath}")

    # Check for path traversal
    if ".." in filepath:
        logger.warning(f"Path traversal attempt: {filepath}")
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "Path traversal not allowed",
            },
            "systemMessage": "🚫 Invalid path: '..' not allowed"
        }

    return {}


# =============================================================================
# PostToolUse Hook - Monitoring
# =============================================================================

async def monitor_tool_execution(
    input_data: HookInput,
    tool_use_id: str | None,
    context: HookContext
) -> HookJSONOutput:
    """
    PostToolUse hook: Monitor tool execution for errors.
    """

    tool_response = input_data.get("tool_response", "")
    response_text = str(tool_response).lower()

    # Check for errors
    if "error" in response_text or "is_error" in str(tool_response):
        logger.warning("Tool execution resulted in error")
        return {
            "systemMessage": "⚠️  Tool encountered an error",
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "status": "error"
            }
        }

    return {}


# =============================================================================
# Execution Tracker
# =============================================================================

@dataclass
class ExecutionTracker:
    """Track agent execution metrics and data."""

    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None

    messages_received: int = 0
    assistant_responses: List[str] = field(default_factory=list)
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)

    total_cost: float = 0.0
    status: str = "running"

    def process_message(self, message: Any) -> None:
        """Process a message and update tracker."""
        self.messages_received += 1

        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    self.assistant_responses.append(block.text)
                elif isinstance(block, ToolUseBlock):
                    self.tool_calls.append({
                        "name": block.name,
                        "input": block.input,
                        "timestamp": datetime.now()
                    })

        elif isinstance(message, ResultMessage):
            self.end_time = datetime.now()
            self.total_cost = message.total_cost_usd or 0.0
            self.status = message.subtype

    def print_summary(self) -> None:
        """Print execution summary."""
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0

        # Count tool usage
        tool_counts = {}
        for call in self.tool_calls:
            name = call["name"]
            tool_counts[name] = tool_counts.get(name, 0) + 1

        print("\n" + "="*70)
        print("EXECUTION SUMMARY")
        print("="*70)
        print(f"Status: {self.status}")
        print(f"Duration: {duration:.2f}s")
        print(f"Cost: ${self.total_cost:.4f}")
        print(f"\nMessages: {self.messages_received}")
        print(f"Assistant Responses: {len(self.assistant_responses)}")
        print(f"Tool Calls: {len(self.tool_calls)}")

        if tool_counts:
            print("\nTool Usage:")
            for tool, count in sorted(tool_counts.items()):
                print(f"  {tool}: {count}x")

        print("="*70)


# =============================================================================
# Main File Reader Agent
# =============================================================================

class FileReaderAgent:
    """Production-ready file reader agent."""

    def __init__(self, working_dir: Path | None = None):
        """
        Initialize file reader agent.

        Args:
            working_dir: Working directory for file operations (default: current)
        """
        self.working_dir = working_dir or Path.cwd()
        logger.info(f"Initializing FileReaderAgent in {self.working_dir}")

        # Create MCP server with file tools
        self.file_server = create_sdk_mcp_server(
            name="file-reader",
            version="1.0.0",
            tools=[read_file, list_directory, file_info, search_in_file]
        )

        # Configure agent options
        self.options = ClaudeAgentOptions(
            mcp_servers={"files": self.file_server},
            allowed_tools=[
                "mcp__files__read_file",
                "mcp__files__list_directory",
                "mcp__files__file_info",
                "mcp__files__search_in_file",
            ],
            can_use_tool=permission_callback,
            hooks={
                "PreToolUse": [
                    HookMatcher(matcher="mcp__files__read_file", hooks=[validate_file_access]),
                    HookMatcher(matcher="mcp__files__list_directory", hooks=[validate_file_access]),
                    HookMatcher(matcher="mcp__files__file_info", hooks=[validate_file_access]),
                    HookMatcher(matcher="mcp__files__search_in_file", hooks=[validate_file_access]),
                ],
                "PostToolUse": [
                    HookMatcher(matcher="mcp__files__read_file", hooks=[monitor_tool_execution]),
                    HookMatcher(matcher="mcp__files__list_directory", hooks=[monitor_tool_execution]),
                    HookMatcher(matcher="mcp__files__file_info", hooks=[monitor_tool_execution]),
                    HookMatcher(matcher="mcp__files__search_in_file", hooks=[monitor_tool_execution]),
                ],
            },
            cwd=self.working_dir
        )

        logger.info("FileReaderAgent initialized with multi-layer security")

    async def query(self, prompt: str, stream: bool = True) -> ExecutionTracker:
        """
        Execute a query with the file reader agent.

        Args:
            prompt: Query to send to the agent
            stream: Whether to stream responses in real-time

        Returns:
            ExecutionTracker with execution metrics
        """

        logger.info(f"Executing query: {prompt}")
        tracker = ExecutionTracker()

        try:
            async with ClaudeSDKClient(options=self.options) as client:
                await client.query(prompt)

                # Track current text for streaming
                current_text = ""

                async for message in client.receive_response():
                    tracker.process_message(message)

                    # Handle different message types
                    if isinstance(message, SystemMessage):
                        if message.subtype == "init":
                            tools = message.data.get("tools", [])
                            logger.info(f"Session initialized with {len(tools)} tools")

                    elif isinstance(message, AssistantMessage):
                        if stream:
                            for block in message.content:
                                if isinstance(block, TextBlock):
                                    # Stream new text
                                    new_text = block.text[len(current_text):]
                                    if new_text:
                                        print(new_text, end='', flush=True)
                                        current_text = block.text
                                elif isinstance(block, ToolUseBlock):
                                    # Show tool usage
                                    print(f"\n\n[Using tool: {block.name}]", flush=True)

                    elif isinstance(message, ResultMessage):
                        if stream:
                            print("\n")  # Final newline
                        logger.info(f"Query completed: {message.subtype}")

        except CLINotFoundError:
            logger.error("Claude Code CLI not found")
            print("\n❌ ERROR: Claude Code CLI not installed")
            print("   Install from: https://claude.ai/download")
            raise

        except CLIConnectionError as e:
            logger.error(f"Connection error: {e}")
            print(f"\n❌ ERROR: Cannot connect to Claude Code: {e}")
            raise

        except ProcessError as e:
            logger.error(f"Process error: {e}")
            print(f"\n❌ ERROR: Process execution failed: {e}")
            raise

        except ClaudeSDKError as e:
            logger.error(f"SDK error: {e}")
            print(f"\n❌ ERROR: {e}")
            raise

        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            print(f"\n❌ UNEXPECTED ERROR: {e}")
            raise

        return tracker


# =============================================================================
# Demo Queries
# =============================================================================

async def run_demo():
    """Run demonstration queries."""

    print("="*70)
    print("FILE READER AGENT - DEMONSTRATION")
    print("="*70)
    print("\nThis agent can safely read, list, and search files with:")
    print("  • Multi-layer security (permissions + hooks)")
    print("  • Comprehensive error handling")
    print("  • Real-time streaming responses")
    print("  • Execution tracking and cost monitoring")
    print("\nSource: https://github.com/anthropics/claude-agent-sdk-python")
    print("="*70)

    # Initialize agent
    agent = FileReaderAgent()

    # Demo queries
    queries = [
        "List the files in the current directory",
        "Read the README.md file if it exists",
        "Search for the word 'agent' in any Python files",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n\n{'='*70}")
        print(f"QUERY {i}: {query}")
        print('='*70)
        print()

        try:
            tracker = await agent.query(query, stream=True)
            tracker.print_summary()

            # Pause between queries
            if i < len(queries):
                await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Query failed: {e}")
            print(f"\nQuery failed: {e}")
            break

    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)


# =============================================================================
# Main Entry Point
# =============================================================================

async def main():
    """Main entry point."""

    try:
        await run_demo()

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        logger.info("User interrupt")

    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        print(f"\n❌ Fatal error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
