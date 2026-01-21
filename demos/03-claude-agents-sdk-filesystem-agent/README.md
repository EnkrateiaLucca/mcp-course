# File Reader Agent Implementation

## Overview

This section covers implementing file reader agents using the Claude Agent SDK for Python. You'll learn how to integrate filesystem operations through MCP (Model Context Protocol) servers, manage tool permissions, handle responses, and implement robust error handling patterns.

## Learning Objectives

By the end of this section, you will be able to:

1. **Attach and configure MCP servers** for filesystem operations
   - Understand MCP architecture and communication flow
   - Create in-process SDK MCP servers
   - Mix in-process and external MCP servers
   - Load filesystem-based agents from configuration

2. **Enumerate and manage tools** with proper permissions
   - Configure built-in tools (Read, Write, Edit, Bash, Glob, Grep)
   - Define custom tools with the `@tool` decorator
   - Implement permission callbacks for security
   - Extract available tools at runtime

3. **Handle agent responses** effectively
   - Process different message types (System, Assistant, Result)
   - Implement streaming for real-time feedback
   - Summarize agent execution results
   - Track costs and tool usage

4. **Implement error handling patterns** for production systems
   - Handle SDK-specific exceptions
   - Return errors from custom tools
   - Use PreToolUse hooks to block dangerous operations
   - Use PostToolUse hooks to monitor and respond to failures
   - Implement comprehensive error logging and recovery

## Prerequisites

Before starting this section, you should:

- ✅ Have completed Section 01 (SDK Setup and Architecture)
- ✅ Have completed Section 02 (Agent Initialization and Message Patterns)
- ✅ Have Claude Code CLI installed and configured
- ✅ Understand Python async/await patterns
- ✅ Be familiar with filesystem operations in Python
- ✅ Have basic understanding of security concepts

## Section Structure

```
03-file-reader-agent/
├── README.md                          # This file
├── examples/                          # Individual topic examples
│   ├── example_mcp_server.py         # MCP server setup
│   ├── example_tool_permissions.py   # Tool configuration and permissions
│   ├── example_response_handling.py  # Response processing patterns
│   └── example_error_handling.py     # Error handling strategies
└── scripts/                           # Complete implementations
    └── file_reader_agent.py          # Full file reader agent
```

## Key Concepts

### 1. MCP (Model Context Protocol)

MCP is an open-source standard that provides a "USB-C port for AI applications" - a standardized way to connect AI models to external systems, tools, and data sources.

**Architecture:**
- **MCP Host**: AI application coordinating multiple clients
- **MCP Client**: Maintains connection to a single MCP server
- **MCP Server**: Provides tools, resources, and prompts

### 2. In-Process SDK Servers

Run MCP servers directly in your Python process:
- ✅ No subprocess management overhead
- ✅ Better performance
- ✅ Simpler deployment and debugging
- ✅ Direct Python function calls with type safety

### 3. Tool Permissions

Control what operations agents can perform:
- **Specific tool arrays**: Grant only needed tools
- **Tool presets**: Use predefined toolsets
- **Permission callbacks**: Fine-grained authorization logic
- **Hooks**: Validate before/after tool execution

### 4. Response Message Types

- **SystemMessage**: Initialization and system info
- **AssistantMessage**: Claude's responses and reasoning
- **ResultMessage**: Final results with cost metadata
- **ToolUseBlock**: Tool invocation details
- **ToolResultBlock**: Tool execution results

### 5. Error Handling

- **SDK exceptions**: CLINotFoundError, ProcessError, etc.
- **Tool-level errors**: Return `is_error: True`
- **PreToolUse hooks**: Block dangerous operations
- **PostToolUse hooks**: Monitor and respond to failures

## Getting Started

1. **Start with MCP basics**: Review `examples/example_mcp_server.py`
2. **Explore tool permissions**: Study `examples/example_tool_permissions.py`
3. **Learn response handling**: Work through `examples/example_response_handling.py`
4. **Master error handling**: Implement patterns from `examples/example_error_handling.py`
5. **Build complete agent**: Run and modify `scripts/file_reader_agent.py`

## Practical Exercises

Each example file includes:
- **Inline comments** explaining every concept
- **Runnable code** you can execute immediately with `uv run`
- **Variations** showing different approaches
- **Best practices** and anti-patterns

## Security Considerations

⚠️ **Important Security Notes:**

1. **Validate all file paths** - Prevent directory traversal attacks
2. **Use permission callbacks** - Don't rely on `permission_mode` alone
3. **Block dangerous commands** - Implement PreToolUse hooks for Bash
4. **Principle of least privilege** - Grant minimal necessary permissions
5. **Log all operations** - Maintain audit trail for security review

## Source Attribution

All course content is derived from official Anthropic documentation and examples:

**Primary Source:** https://github.com/anthropics/claude-agent-sdk-python

**Additional References:**
- Model Context Protocol: https://modelcontextprotocol.io/introduction
- MCP Architecture: https://modelcontextprotocol.io/docs/concepts/architecture
- SDK Examples: https://github.com/anthropics/claude-agent-sdk-python/tree/main/examples

## Next Steps

After completing this section:
- ✅ Proceed to Section 04: Calculator Agent with Custom Tools
- ✅ Build your own file management agent
- ✅ Explore advanced MCP server patterns
- ✅ Implement production-grade error handling

---

**Ready to get started?** Begin with `examples/example_mcp_server.py` to understand MCP server fundamentals.
