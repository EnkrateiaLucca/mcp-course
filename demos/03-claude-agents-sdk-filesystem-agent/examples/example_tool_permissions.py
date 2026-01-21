#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "anthropic-claude-sdk",
# ]
# ///
"""
Tool Enumeration and Permissions

This example demonstrates comprehensive tool configuration and permission
management in the Claude Agent SDK.

Source: https://github.com/anthropics/claude-agent-sdk-python
Examples: https://github.com/anthropics/claude-agent-sdk-python/tree/main/examples
Specific: https://raw.githubusercontent.com/anthropics/claude-agent-sdk-python/main/examples/tool_permission_callback.py

Learning Objectives:
1. Configure built-in tools (Read, Write, Edit, Bash, Glob, Grep)
2. Use tool presets for common configurations
3. Implement custom permission callbacks
4. Control tool authorization at runtime
5. Apply principle of least privilege

Key Concepts:
- Tools must be explicitly allowed in ClaudeAgentOptions
- Permission modes: 'default', 'acceptEdits', or custom callback
- Tool names follow pattern: mcp__<server>__<tool> for MCP tools
- Permission callbacks can allow, deny, or modify tool inputs
"""

import asyncio
from typing import Any
from pathlib import Path

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    tool,
    create_sdk_mcp_server,
    ToolPermissionContext,
    PermissionResultAllow,
    PermissionResultDeny,
    AssistantMessage,
    TextBlock,
    ResultMessage,
)


# =============================================================================
# PART 1: Built-in Tool Configuration
# =============================================================================

async def example_builtin_tools():
    """
    Example 1: Configure built-in tools.

    Built-in tools provided by Claude Agent SDK:
    - Read: Read file contents
    - Write: Write/overwrite files
    - Edit: Edit specific parts of files
    - Bash: Execute shell commands
    - Glob: Find files by pattern
    - Grep: Search file contents

    Only tools in allowed_tools list will be available to the agent.
    """

    print("="*60)
    print("Example 1: Built-in Tool Configuration")
    print("="*60)

    # Method 1: Specific tools only
    options_read_only = ClaudeAgentOptions(
        allowed_tools=["Read", "Grep", "Glob"],  # Read-only operations
        cwd=Path.cwd()
    )

    print("\nRead-only configuration:")
    print("  Allowed: Read, Grep, Glob")
    print("  Use case: Safe file exploration without modifications")

    # Method 2: Read and write operations
    options_read_write = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Edit"],  # Add write capabilities
        cwd=Path.cwd()
    )

    print("\nRead-write configuration:")
    print("  Allowed: Read, Write, Edit")
    print("  Use case: File management and editing")

    # Method 3: Full toolset (use with caution)
    options_full = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
        cwd=Path.cwd()
    )

    print("\nFull toolset configuration:")
    print("  Allowed: All built-in tools including Bash")
    print("  Use case: Advanced operations (⚠️  requires careful permission management)")


# =============================================================================
# PART 2: Tool Presets
# =============================================================================

async def example_tool_presets():
    """
    Example 2: Use tool presets for common configurations.

    Presets provide predefined tool sets for common use cases.
    """

    print("\n" + "="*60)
    print("Example 2: Tool Presets")
    print("="*60)

    # Using claude_code preset (includes common development tools)
    options = ClaudeAgentOptions(
        tools={"type": "preset", "preset": "claude_code"},
        cwd=Path.cwd()
    )

    print("\nUsing 'claude_code' preset:")
    print("  Includes: Standard development tools")
    print("  Use case: General development tasks")

    # Disable all tools
    options_no_tools = ClaudeAgentOptions(
        tools=[],  # Empty list disables all built-in tools
        cwd=Path.cwd()
    )

    print("\nDisabling all tools:")
    print("  Use case: Pure conversation without file access")


# =============================================================================
# PART 3: Permission Modes
# =============================================================================

async def example_permission_modes():
    """
    Example 3: Different permission modes.

    Permission modes control how tool usage is authorized:
    - 'default': Prompt user for each operation (interactive)
    - 'acceptEdits': Auto-approve file operations (autonomous)
    - Custom callback: Fine-grained control (programmatic)
    """

    print("\n" + "="*60)
    print("Example 3: Permission Modes")
    print("="*60)

    # Mode 1: Default (interactive)
    options_default = ClaudeAgentOptions(
        permission_mode='default',  # User prompted for each tool use
        allowed_tools=["Read", "Write"],
        cwd=Path.cwd()
    )

    print("\nDefault mode:")
    print("  Behavior: User prompted for each tool use")
    print("  Use case: Interactive development, learning")

    # Mode 2: Accept edits (autonomous)
    options_accept = ClaudeAgentOptions(
        permission_mode='acceptEdits',  # Auto-approve file operations
        allowed_tools=["Read", "Write", "Edit"],
        cwd=Path.cwd()
    )

    print("\nAccept edits mode:")
    print("  Behavior: Automatically approve file operations")
    print("  Use case: Automated workflows, trusted environments")


# =============================================================================
# PART 4: Custom Permission Callback
# =============================================================================

async def simple_permission_callback(
    tool_name: str,
    input_data: dict,
    context: ToolPermissionContext
) -> PermissionResultAllow | PermissionResultDeny:
    """
    Simple permission callback - Allow read, block write to system paths.

    Args:
        tool_name: Name of the tool being invoked
        input_data: Parameters passed to the tool
        context: Additional context about the request

    Returns:
        PermissionResultAllow or PermissionResultDeny
    """

    # Always allow Read operations
    if tool_name == "Read":
        print(f"  ✓ Allowing read: {input_data.get('file_path', 'unknown')}")
        return PermissionResultAllow()

    # Check Write operations
    if tool_name == "Write":
        file_path = input_data.get("file_path", "")

        # Block writes to system directories
        system_paths = ["/etc/", "/usr/", "/sys/", "/bin/", "/sbin/"]
        if any(file_path.startswith(path) for path in system_paths):
            print(f"  ✗ Blocking write to system path: {file_path}")
            return PermissionResultDeny(
                message=f"Access denied: Cannot write to system path {file_path}"
            )

        print(f"  ✓ Allowing write: {file_path}")
        return PermissionResultAllow()

    # Default: allow other operations
    print(f"  ✓ Allowing tool: {tool_name}")
    return PermissionResultAllow()


async def advanced_permission_callback(
    tool_name: str,
    input_data: dict,
    context: ToolPermissionContext
) -> PermissionResultAllow | PermissionResultDeny:
    """
    Advanced permission callback with path redirection and command validation.

    Demonstrates:
    1. Path validation and sanitization
    2. Dangerous command blocking
    3. Input modification (path redirection)
    4. Comprehensive logging
    """

    print(f"\n  Permission check: {tool_name}")

    # ==========================================================================
    # Read Operations: Always allow
    # ==========================================================================
    if tool_name == "Read":
        file_path = input_data.get("file_path", "")
        print(f"    File: {file_path}")
        return PermissionResultAllow()

    # ==========================================================================
    # Write Operations: Validate and potentially redirect
    # ==========================================================================
    if tool_name == "Write":
        file_path = input_data.get("file_path", "")
        print(f"    File: {file_path}")

        # Block protected directories
        protected_dirs = ["/etc/", "/usr/", "/sys/", "/bin/", "/var/", "/root/"]
        for protected in protected_dirs:
            if file_path.startswith(protected):
                print(f"    ✗ DENIED: Protected directory")
                return PermissionResultDeny(
                    message=f"Access denied: Cannot write to {protected}"
                )

        # Redirect /tmp/ to safer location
        if file_path.startswith("/tmp/"):
            safe_path = file_path.replace("/tmp/", "/home/user/temp/")
            print(f"    ↪ Redirecting to: {safe_path}")
            return PermissionResultAllow(
                updated_input={"file_path": safe_path, "content": input_data.get("content", "")}
            )

        # Block sensitive file patterns
        sensitive_patterns = [".env", "credentials", "secrets", "private_key"]
        filename = Path(file_path).name.lower()
        if any(pattern in filename for pattern in sensitive_patterns):
            print(f"    ✗ DENIED: Sensitive filename pattern")
            return PermissionResultDeny(
                message=f"Access denied: Cannot write to sensitive file"
            )

        print(f"    ✓ ALLOWED")
        return PermissionResultAllow()

    # ==========================================================================
    # Bash Operations: Block dangerous commands
    # ==========================================================================
    if tool_name == "Bash":
        command = input_data.get("command", "")
        print(f"    Command: {command[:50]}...")

        # Define dangerous command patterns
        dangerous_patterns = [
            ("rm -rf", "Recursive deletion"),
            ("sudo", "Elevated privileges"),
            ("chmod 777", "Insecure permissions"),
            ("dd", "Disk operations"),
            ("mkfs", "Filesystem formatting"),
            (":(){ :|:& };:", "Fork bomb"),
            ("> /dev/sd", "Direct disk write"),
            ("curl | bash", "Remote code execution"),
            ("wget | sh", "Remote code execution"),
        ]

        # Check each dangerous pattern
        for pattern, reason in dangerous_patterns:
            if pattern in command:
                print(f"    ✗ DENIED: {reason}")
                return PermissionResultDeny(
                    message=f"Blocked dangerous command: {reason} ({pattern})"
                )

        print(f"    ✓ ALLOWED")
        return PermissionResultAllow()

    # ==========================================================================
    # Default: Allow with logging
    # ==========================================================================
    print(f"    ✓ ALLOWED (default)")
    return PermissionResultAllow()


async def example_permission_callbacks():
    """
    Example 4: Using permission callbacks for fine-grained control.
    """

    print("\n" + "="*60)
    print("Example 4: Permission Callbacks")
    print("="*60)

    # Simple callback
    print("\nSimple callback (allow read, validate writes):")

    options_simple = ClaudeAgentOptions(
        can_use_tool=simple_permission_callback,
        allowed_tools=["Read", "Write"],
        cwd=Path.cwd()
    )

    print("  ✓ Configuration created")
    print("  Behavior: Blocks system path writes, allows reads")

    # Advanced callback
    print("\nAdvanced callback (validation, redirection, blocking):")

    options_advanced = ClaudeAgentOptions(
        can_use_tool=advanced_permission_callback,
        allowed_tools=["Read", "Write", "Bash"],
        cwd=Path.cwd()
    )

    print("  ✓ Configuration created")
    print("  Features:")
    print("    - Path validation and sanitization")
    print("    - Dangerous command blocking")
    print("    - Automatic path redirection")
    print("    - Comprehensive logging")


# =============================================================================
# PART 5: Custom Tools with Permissions
# =============================================================================

@tool("safe_delete", "Safely delete a file with validation", {"filepath": str})
async def safe_delete(args: dict[str, Any]) -> dict[str, Any]:
    """
    Custom tool with built-in safety checks.

    Demonstrates implementing security at the tool level
    (in addition to permission callbacks).
    """
    filepath = args['filepath']
    path = Path(filepath)

    # Safety check 1: File must exist
    if not path.exists():
        return {
            "content": [{"type": "text", "text": f"Error: File not found: {filepath}"}],
            "is_error": True
        }

    # Safety check 2: Must be a file (not directory)
    if not path.is_file():
        return {
            "content": [{"type": "text", "text": f"Error: Not a file: {filepath}"}],
            "is_error": True
        }

    # Safety check 3: Block system paths
    system_prefixes = ["/etc", "/usr", "/sys", "/bin", "/var"]
    if any(str(path.absolute()).startswith(prefix) for prefix in system_prefixes):
        return {
            "content": [{"type": "text", "text": f"Error: Cannot delete system file: {filepath}"}],
            "is_error": True
        }

    # Safety check 4: Require explicit confirmation in filename
    if not path.name.startswith("delete_me_"):
        return {
            "content": [{"type": "text", "text": f"Error: File must start with 'delete_me_': {filepath}"}],
            "is_error": True
        }

    # Perform deletion
    try:
        path.unlink()
        return {
            "content": [{"type": "text", "text": f"Successfully deleted: {filepath}"}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error deleting file: {str(e)}"}],
            "is_error": True
        }


async def example_custom_tool_permissions():
    """
    Example 5: Custom tools with built-in safety.
    """

    print("\n" + "="*60)
    print("Example 5: Custom Tools with Safety Checks")
    print("="*60)

    # Create MCP server with safe delete tool
    delete_server = create_sdk_mcp_server(
        name="safe-delete",
        version="1.0.0",
        tools=[safe_delete]
    )

    options = ClaudeAgentOptions(
        mcp_servers={"delete": delete_server},
        allowed_tools=["mcp__delete__safe_delete"],
        cwd=Path.cwd()
    )

    print("\nCustom tool: safe_delete")
    print("  Safety features:")
    print("    1. File existence check")
    print("    2. Type validation (file vs directory)")
    print("    3. System path blocking")
    print("    4. Explicit naming requirement (delete_me_*)")
    print("\n  This demonstrates defense-in-depth:")
    print("    - Permission callback (outer layer)")
    print("    - Tool validation (inner layer)")


# =============================================================================
# PART 6: Best Practices
# =============================================================================

def demonstrate_best_practices():
    """
    Best practices for tool permissions.
    """

    print("\n" + "="*60)
    print("Best Practices for Tool Permissions")
    print("="*60)

    practices = [
        {
            "principle": "Principle of Least Privilege",
            "guidance": "Only grant tools that are necessary for the task",
            "example": "Use ['Read', 'Grep'] for analysis, not full toolset"
        },
        {
            "principle": "Defense in Depth",
            "guidance": "Implement security at multiple layers",
            "example": "Permission callback + tool validation + input sanitization"
        },
        {
            "principle": "Explicit Allowlists",
            "guidance": "Never use implicit 'allow all' patterns",
            "example": "Specify exact tools: ['Read', 'Write'], not ['*']"
        },
        {
            "principle": "Path Validation",
            "guidance": "Always validate and sanitize file paths",
            "example": "Block '../', check against protected paths"
        },
        {
            "principle": "Command Validation",
            "guidance": "Block dangerous shell commands",
            "example": "Reject 'rm -rf', 'sudo', 'dd', fork bombs"
        },
        {
            "principle": "Audit Logging",
            "guidance": "Log all tool usage for security review",
            "example": "Log tool name, inputs, decisions, outcomes"
        },
        {
            "principle": "Fail Secure",
            "guidance": "Default to deny when uncertain",
            "example": "Return PermissionResultDeny() for unknown tools"
        },
    ]

    for i, practice in enumerate(practices, 1):
        print(f"\n{i}. {practice['principle']}")
        print(f"   Guidance: {practice['guidance']}")
        print(f"   Example: {practice['example']}")


# =============================================================================
# PART 7: Common Pitfalls
# =============================================================================

def demonstrate_pitfalls():
    """
    Common pitfalls to avoid.
    """

    print("\n" + "="*60)
    print("Common Pitfalls to Avoid")
    print("="*60)

    pitfalls = [
        {
            "mistake": "❌ Granting Unnecessary Tools",
            "why": "Increases attack surface",
            "fix": "✓ Only include tools needed for specific task"
        },
        {
            "mistake": "❌ Using 'acceptEdits' in Production",
            "why": "No authorization checks",
            "fix": "✓ Implement custom permission callback"
        },
        {
            "mistake": "❌ Skipping Input Validation",
            "why": "Vulnerable to path traversal, injection",
            "fix": "✓ Validate all file paths and command strings"
        },
        {
            "mistake": "❌ Ignoring Permission Callbacks",
            "why": "Missing security layer",
            "fix": "✓ Always implement for production systems"
        },
        {
            "mistake": "❌ Not Logging Tool Usage",
            "why": "No audit trail for security review",
            "fix": "✓ Log all tool invocations and decisions"
        },
        {
            "mistake": "❌ Trusting User Input",
            "why": "Can lead to arbitrary code execution",
            "fix": "✓ Sanitize and validate all inputs"
        },
    ]

    for pitfall in pitfalls:
        print(f"\n{pitfall['mistake']}")
        print(f"  Why dangerous: {pitfall['why']}")
        print(f"  {pitfall['fix']}")


# =============================================================================
# Main Execution
# =============================================================================

async def main():
    """
    Run all tool permission examples.
    """

    print("Tool Permission Configuration Examples")
    print("Source: https://github.com/anthropics/claude-agent-sdk-python\n")

    try:
        # Example 1: Built-in tools
        await example_builtin_tools()

        # Example 2: Tool presets
        await example_tool_presets()

        # Example 3: Permission modes
        await example_permission_modes()

        # Example 4: Permission callbacks
        await example_permission_callbacks()

        # Example 5: Custom tool safety
        await example_custom_tool_permissions()

        # Best practices
        demonstrate_best_practices()

        # Common pitfalls
        demonstrate_pitfalls()

        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60)

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
