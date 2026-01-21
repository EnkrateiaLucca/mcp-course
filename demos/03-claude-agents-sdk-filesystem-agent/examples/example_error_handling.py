#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "anthropic-claude-sdk",
# ]
# ///
"""
Error Handling Patterns

This example demonstrates comprehensive error handling strategies for
production-grade Claude Agent SDK applications.

Source: https://github.com/anthropics/claude-agent-sdk-python
Examples: https://github.com/anthropics/claude-agent-sdk-python/tree/main/examples
Specific: https://raw.githubusercontent.com/anthropics/claude-agent-sdk-python/main/examples/hooks.py

Learning Objectives:
1. Handle SDK-specific exceptions
2. Return errors from custom tools
3. Use PreToolUse hooks to block dangerous operations
4. Use PostToolUse hooks to monitor failures
5. Implement comprehensive error logging

Key Concepts:
- SDK provides specific exception types for different failures
- Tools should return is_error: True for error conditions
- Hooks provide interception points before/after tool execution
- PreToolUse can deny operations before execution
- PostToolUse can stop execution on critical errors
"""

import asyncio
import logging
from typing import Any
from pathlib import Path

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    query,
    tool,
    create_sdk_mcp_server,
    HookMatcher,
    HookInput,
    HookContext,
    HookJSONOutput,
    # Exception types
    ClaudeSDKError,
    CLINotFoundError,
    CLIConnectionError,
    ProcessError,
    CLIJSONDecodeError,
    # Message types
    AssistantMessage,
    TextBlock,
    ResultMessage,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# PART 1: SDK Exception Handling
# =============================================================================

async def example_sdk_exceptions():
    """
    Example 1: Handle SDK-specific exceptions.

    Exception Hierarchy:
    - ClaudeSDKError (base)
      ├─ CLINotFoundError (CLI not installed)
      ├─ CLIConnectionError (connection failed)
      ├─ ProcessError (process execution failed)
      └─ CLIJSONDecodeError (invalid JSON response)
    """

    print("="*60)
    print("Example 1: SDK Exception Handling")
    print("="*60)

    @tool("demo", "Demo tool", {})
    async def demo(args: dict[str, Any]) -> dict[str, Any]:
        return {"content": [{"type": "text", "text": "Demo"}]}

    demo_server = create_sdk_mcp_server(
        name="demo",
        version="1.0.0",
        tools=[demo]
    )

    options = ClaudeAgentOptions(
        mcp_servers={"demo": demo_server},
        allowed_tools=["mcp__demo__demo"],
        cwd=Path.cwd()
    )

    print("\nAttempting query with comprehensive error handling...\n")

    try:
        async for message in query(
            prompt="Use demo tool",
            options=options
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Assistant: {block.text}")

            elif isinstance(message, ResultMessage):
                print(f"Completed: ${message.total_cost_usd:.4f}")

    except CLINotFoundError as e:
        logger.error("Claude Code CLI not found")
        print("\n❌ ERROR: Claude Code CLI not installed")
        print("   Install from: https://claude.ai/download")
        print(f"   Details: {e}")

    except CLIConnectionError as e:
        logger.error(f"Connection error: {e}")
        print("\n❌ ERROR: Cannot connect to Claude Code")
        print("   Check if Claude Code is running")
        print(f"   Details: {e}")

    except ProcessError as e:
        logger.error(f"Process error: exit_code={e.exit_code}")
        print("\n❌ ERROR: Process execution failed")
        print(f"   Exit code: {e.exit_code}")
        print(f"   Output: {e.output}")

    except CLIJSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        print("\n❌ ERROR: Invalid JSON response")
        print("   This may indicate a protocol mismatch")
        print(f"   Details: {e}")

    except ClaudeSDKError as e:
        logger.error(f"SDK error: {e}")
        print(f"\n❌ ERROR: SDK error: {e}")

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        raise


# =============================================================================
# PART 2: Tool-Level Error Handling
# =============================================================================

@tool("safe_read", "Safely read a file with validation", {"filepath": str})
async def safe_read(args: dict[str, Any]) -> dict[str, Any]:
    """
    Tool with comprehensive error handling.

    Demonstrates:
    1. Input validation
    2. Multiple error types
    3. Returning is_error flag
    4. Helpful error messages
    """
    filepath = args['filepath']

    # Validation 1: Empty path
    if not filepath:
        logger.warning("Empty filepath provided")
        return {
            "content": [{"type": "text", "text": "Error: No file path provided"}],
            "is_error": True
        }

    # Validation 2: Path traversal protection
    if ".." in filepath:
        logger.warning(f"Path traversal attempt: {filepath}")
        return {
            "content": [{"type": "text", "text": f"Error: Invalid path (contains '..'): {filepath}"}],
            "is_error": True
        }

    # Validation 3: Absolute path check
    path = Path(filepath)
    if path.is_absolute() and not str(path).startswith("/tmp"):
        logger.warning(f"Absolute path outside /tmp: {filepath}")
        return {
            "content": [{"type": "text", "text": f"Error: Absolute paths only allowed in /tmp"}],
            "is_error": True
        }

    # Attempt to read file
    try:
        if not path.exists():
            logger.info(f"File not found: {filepath}")
            return {
                "content": [{"type": "text", "text": f"Error: File not found: {filepath}"}],
                "is_error": True
            }

        if not path.is_file():
            logger.info(f"Not a file: {filepath}")
            return {
                "content": [{"type": "text", "text": f"Error: Not a file: {filepath}"}],
                "is_error": True
            }

        content = path.read_text()
        logger.info(f"Successfully read: {filepath} ({len(content)} bytes)")

        return {
            "content": [{"type": "text", "text": f"Contents of {filepath}:\n\n{content}"}]
        }

    except PermissionError:
        logger.error(f"Permission denied: {filepath}")
        return {
            "content": [{"type": "text", "text": f"Error: Permission denied: {filepath}"}],
            "is_error": True
        }

    except UnicodeDecodeError:
        logger.error(f"Not a text file: {filepath}")
        return {
            "content": [{"type": "text", "text": f"Error: File is not valid text: {filepath}"}],
            "is_error": True
        }

    except Exception as e:
        logger.exception(f"Unexpected error reading {filepath}")
        return {
            "content": [{"type": "text", "text": f"Error: {type(e).__name__}: {str(e)}"}],
            "is_error": True
        }


async def example_tool_errors():
    """
    Example 2: Tool-level error handling.
    """

    print("\n" + "="*60)
    print("Example 2: Tool-Level Error Handling")
    print("="*60)

    file_server = create_sdk_mcp_server(
        name="files",
        version="1.0.0",
        tools=[safe_read]
    )

    options = ClaudeAgentOptions(
        mcp_servers={"files": file_server},
        allowed_tools=["mcp__files__safe_read"],
        cwd=Path.cwd()
    )

    print("\nTesting error scenarios:\n")

    # Test 1: Non-existent file
    print("Test 1: Non-existent file")
    try:
        async for message in query(
            prompt="Read the file 'nonexistent.txt'",
            options=options
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"  {block.text}")
    except Exception as e:
        print(f"  Error: {e}")


# =============================================================================
# PART 3: PreToolUse Hooks - Block Before Execution
# =============================================================================

async def validate_bash_command(
    input_data: HookInput,
    tool_use_id: str | None,
    context: HookContext
) -> HookJSONOutput:
    """
    PreToolUse hook: Validate bash commands before execution.

    Blocks dangerous operations like:
    - rm -rf (recursive deletion)
    - dd (disk operations)
    - mkfs (filesystem formatting)
    - Fork bombs
    - Direct disk writes
    """

    tool_name = input_data.get("tool_name", "")

    # Only validate Bash commands
    if tool_name != "Bash":
        return {}

    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")

    logger.info(f"Validating bash command: {command[:50]}...")

    # Define dangerous patterns
    dangerous_patterns = [
        ("rm -rf", "Recursive file deletion"),
        ("dd if=", "Direct disk operations"),
        ("mkfs", "Filesystem formatting"),
        (":(){ :|:& };:", "Fork bomb"),
        ("> /dev/sd", "Direct disk write"),
        ("chmod -R 777", "Insecure permissions"),
        ("curl | bash", "Remote code execution"),
        ("wget | sh", "Remote code execution"),
    ]

    # Check each pattern
    for pattern, reason in dangerous_patterns:
        if pattern in command:
            logger.warning(f"Blocked dangerous command: {reason} ({pattern})")
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"Blocked: {reason}",
                },
                "systemMessage": f"🚫 Command blocked for safety: {reason}"
            }

    # Warn about sudo
    if "sudo" in command:
        logger.warning("Command uses sudo")
        return {
            "systemMessage": "⚠️  Warning: Command uses elevated privileges",
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": "This command requires elevated privileges"
            }
        }

    logger.info("Command validated successfully")
    return {}


async def validate_file_access(
    input_data: HookInput,
    tool_use_id: str | None,
    context: HookContext
) -> HookJSONOutput:
    """
    PreToolUse hook: Validate file access before execution.

    Blocks access to:
    - System directories (/etc, /sys, etc.)
    - Sensitive files (.env, credentials, etc.)
    """

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Get filepath from different possible keys
    filepath = tool_input.get("filepath") or tool_input.get("file_path") or ""

    if not filepath:
        return {}

    logger.info(f"Validating file access: {filepath}")

    # Block system directories
    system_dirs = ["/etc/", "/sys/", "/usr/", "/bin/", "/sbin/", "/var/", "/root/"]
    for sys_dir in system_dirs:
        if filepath.startswith(sys_dir):
            logger.warning(f"Blocked system directory access: {sys_dir}")
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"System directory access blocked",
                },
                "systemMessage": f"🔒 Access denied: Cannot access {sys_dir}"
            }

    # Block sensitive files
    sensitive_patterns = [".env", "credentials", "secrets", "private_key", "id_rsa"]
    filename = Path(filepath).name.lower()

    for pattern in sensitive_patterns:
        if pattern in filename:
            logger.warning(f"Blocked sensitive file: {pattern}")
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": "Sensitive file access blocked",
                },
                "systemMessage": f"🔒 Access denied: Cannot access sensitive file"
            }

    logger.info("File access validated")
    return {}


async def example_pretooluse_hooks():
    """
    Example 3: PreToolUse hooks to block dangerous operations.
    """

    print("\n" + "="*60)
    print("Example 3: PreToolUse Hooks")
    print("="*60)

    file_server = create_sdk_mcp_server(
        name="files",
        version="1.0.0",
        tools=[safe_read]
    )

    options = ClaudeAgentOptions(
        mcp_servers={"files": file_server},
        allowed_tools=["mcp__files__safe_read", "Bash"],
        hooks={
            "PreToolUse": [
                HookMatcher(matcher="Bash", hooks=[validate_bash_command]),
                HookMatcher(matcher="mcp__files__safe_read", hooks=[validate_file_access]),
            ],
        },
        cwd=Path.cwd()
    )

    print("\nPreToolUse hooks configured:")
    print("  - Bash: Block dangerous commands")
    print("  - File access: Block system directories and sensitive files")
    print("\nHooks will intercept tool calls before execution.\n")


# =============================================================================
# PART 4: PostToolUse Hooks - Monitor After Execution
# =============================================================================

async def review_tool_output(
    input_data: HookInput,
    tool_use_id: str | None,
    context: HookContext
) -> HookJSONOutput:
    """
    PostToolUse hook: Review tool output for errors and warnings.

    Checks output for:
    - Error messages
    - Warnings
    - Success indicators
    """

    tool_response = input_data.get("tool_response", "")
    response_text = str(tool_response).lower()

    logger.info("Reviewing tool output")

    # Check for errors
    if "error" in response_text or "exception" in response_text:
        logger.warning("Tool output contains errors")
        return {
            "systemMessage": "⚠️  Tool execution encountered an error",
            "reason": "Error detected in output",
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": "Check the error message and retry if needed.",
            }
        }

    # Check for warnings
    if "warning" in response_text:
        logger.info("Tool output contains warnings")
        return {
            "systemMessage": "⚠️  Tool execution produced warnings",
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": "Review warnings before proceeding.",
            }
        }

    logger.info("Tool output reviewed successfully")
    return {}


async def stop_on_critical_error(
    input_data: HookInput,
    tool_use_id: str | None,
    context: HookContext
) -> HookJSONOutput:
    """
    PostToolUse hook: Halt execution on critical errors.

    Stops agent execution if critical errors detected:
    - Critical/fatal errors
    - Segmentation faults
    - Out of memory
    - Disk full
    """

    tool_response = input_data.get("tool_response", "")
    response_text = str(tool_response).lower()

    # Define critical error patterns
    critical_patterns = [
        "critical",
        "fatal",
        "segmentation fault",
        "out of memory",
        "disk full",
        "core dumped"
    ]

    for pattern in critical_patterns:
        if pattern in response_text:
            logger.error(f"Critical error detected: {pattern}")
            return {
                "continue_": False,  # Stop execution immediately
                "stopReason": f"Critical error: {pattern}",
                "systemMessage": f"🛑 Execution halted: {pattern} detected",
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "severity": "critical",
                    "error_pattern": pattern
                }
            }

    return {}


async def example_posttooluse_hooks():
    """
    Example 4: PostToolUse hooks to monitor execution.
    """

    print("\n" + "="*60)
    print("Example 4: PostToolUse Hooks")
    print("="*60)

    file_server = create_sdk_mcp_server(
        name="files",
        version="1.0.0",
        tools=[safe_read]
    )

    options = ClaudeAgentOptions(
        mcp_servers={"files": file_server},
        allowed_tools=["mcp__files__safe_read", "Bash"],
        hooks={
            "PostToolUse": [
                HookMatcher(matcher="Bash", hooks=[review_tool_output, stop_on_critical_error]),
                HookMatcher(matcher="mcp__files__safe_read", hooks=[review_tool_output]),
            ],
        },
        cwd=Path.cwd()
    )

    print("\nPostToolUse hooks configured:")
    print("  - Review output for errors/warnings")
    print("  - Stop execution on critical errors")
    print("\nHooks will monitor tool results after execution.\n")


# =============================================================================
# PART 5: Complete Error Handling Example
# =============================================================================

async def example_complete_error_handling():
    """
    Example 5: Complete error handling with all patterns.

    Combines:
    1. SDK exception handling
    2. Tool-level error returns
    3. PreToolUse validation hooks
    4. PostToolUse monitoring hooks
    5. Comprehensive logging
    """

    print("\n" + "="*60)
    print("Example 5: Complete Error Handling")
    print("="*60)

    # Create server
    file_server = create_sdk_mcp_server(
        name="files",
        version="1.0.0",
        tools=[safe_read]
    )

    # Configure with all error handling
    options = ClaudeAgentOptions(
        mcp_servers={"files": file_server},
        allowed_tools=["mcp__files__safe_read", "Bash"],
        hooks={
            "PreToolUse": [
                HookMatcher(matcher="Bash", hooks=[validate_bash_command]),
                HookMatcher(matcher="mcp__files__safe_read", hooks=[validate_file_access]),
            ],
            "PostToolUse": [
                HookMatcher(matcher="Bash", hooks=[review_tool_output, stop_on_critical_error]),
                HookMatcher(matcher="mcp__files__safe_read", hooks=[review_tool_output]),
            ],
        },
        cwd=Path.cwd()
    )

    print("\nMulti-layer error handling configured:")
    print("  Layer 1: SDK exception handling (outer)")
    print("  Layer 2: PreToolUse hooks (validation)")
    print("  Layer 3: Tool implementation (execution)")
    print("  Layer 4: PostToolUse hooks (monitoring)")
    print("\nThis provides defense-in-depth security.\n")

    try:
        async with ClaudeSDKClient(options=options) as client:
            await client.query("Try to read a file")

            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(f"Assistant: {block.text}")

                elif isinstance(message, ResultMessage):
                    print(f"\nCompleted: ${message.total_cost_usd:.4f}")

    except CLINotFoundError:
        logger.error("CLI not found")
        print("\n❌ Claude Code CLI not installed")
        print("   Install from: https://claude.ai/download")

    except ClaudeSDKError as e:
        logger.error(f"SDK error: {e}")
        print(f"\n❌ Error: {e}")

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"\n❌ Unexpected error: {e}")
        raise

    finally:
        logger.info("Cleanup complete")


# =============================================================================
# PART 6: Best Practices
# =============================================================================

def demonstrate_best_practices():
    """
    Best practices for error handling.
    """

    print("\n" + "="*60)
    print("Best Practices for Error Handling")
    print("="*60)

    practices = [
        ("Use Specific Exceptions", "Catch CLINotFoundError before ClaudeSDKError"),
        ("Return is_error in Tools", "Signal errors through protocol"),
        ("Implement PreToolUse Hooks", "Block dangerous operations before execution"),
        ("Use PostToolUse for Monitoring", "Track failures and add context"),
        ("Log All Errors", "Maintain audit trail with Python logging"),
        ("Provide Actionable Messages", "Tell users what went wrong and how to fix"),
        ("Graceful Degradation", "Continue when possible, stop on critical errors"),
        ("Validate Inputs Early", "Check parameters before expensive operations"),
        ("Handle Async Cleanup", "Use try/finally for resource cleanup"),
        ("Set Timeouts", "Prevent hanging on long operations"),
    ]

    for i, (practice, description) in enumerate(practices, 1):
        print(f"\n{i}. {practice}")
        print(f"   {description}")


# =============================================================================
# Main Execution
# =============================================================================

async def main():
    """
    Run all error handling examples.
    """

    print("Error Handling Examples")
    print("Source: https://github.com/anthropics/claude-agent-sdk-python\n")

    try:
        # Example 1: SDK exceptions
        await example_sdk_exceptions()

        # Example 2: Tool errors
        await example_tool_errors()

        # Example 3: PreToolUse hooks
        await example_pretooluse_hooks()

        # Example 4: PostToolUse hooks
        await example_posttooluse_hooks()

        # Example 5: Complete error handling
        await example_complete_error_handling()

        # Best practices
        demonstrate_best_practices()

        print("\n" + "="*60)
        print("All examples completed!")
        print("="*60)

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
