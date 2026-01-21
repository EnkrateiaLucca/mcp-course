#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "anthropic-claude-sdk",
# ]
# ///
"""
Response Handling and Summarization

This example demonstrates comprehensive response handling patterns for
Claude Agent SDK messages and results.

Source: https://github.com/anthropics/claude-agent-sdk-python
Examples: https://github.com/anthropics/claude-agent-sdk-python/tree/main/examples
Specific: https://raw.githubusercontent.com/anthropics/claude-agent-sdk-python/main/examples/agents.py

Learning Objectives:
1. Understand different message types (System, Assistant, Result)
2. Process streaming responses in real-time
3. Extract structured data from responses
4. Track costs and tool usage
5. Summarize agent execution

Key Concepts:
- Messages arrive asynchronously via async iterator
- SystemMessage contains initialization data
- AssistantMessage contains Claude's responses and tool calls
- ResultMessage contains final status and cost
- Responses may be partial in streaming mode
"""

import asyncio
from typing import Any, List, Dict
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    query,
    tool,
    create_sdk_mcp_server,
    SystemMessage,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultMessage,
)


# =============================================================================
# PART 1: Understanding Message Types
# =============================================================================

@tool("echo", "Echo a message back", {"message": str})
async def echo(args: dict[str, Any]) -> dict[str, Any]:
    """Simple echo tool for demonstration."""
    return {
        "content": [{"type": "text", "text": f"Echo: {args['message']}"}]
    }


async def example_message_types():
    """
    Example 1: Understanding different message types.

    Message Types:
    - SystemMessage: Initialization, system info, agent events
    - AssistantMessage: Claude's text responses and tool invocations
    - ToolResultMessage: Results from tool execution
    - ResultMessage: Final execution status and metadata
    """

    print("="*60)
    print("Example 1: Message Types")
    print("="*60)

    # Create simple echo server
    echo_server = create_sdk_mcp_server(
        name="echo",
        version="1.0.0",
        tools=[echo]
    )

    options = ClaudeAgentOptions(
        mcp_servers={"echo": echo_server},
        allowed_tools=["mcp__echo__echo"],
        cwd=Path.cwd()
    )

    print("\nProcessing query: 'Say hello using the echo tool'")
    print("\nMessage flow:\n")

    async with ClaudeSDKClient(options=options) as client:
        await client.query("Say hello using the echo tool")

        async for message in client.receive_response():
            # System messages
            if isinstance(message, SystemMessage):
                print(f"[SystemMessage] Subtype: {message.subtype}")
                if message.subtype == "init":
                    print(f"  - Initialized with {len(message.data.get('tools', []))} tools")
                print()

            # Assistant messages (responses and tool calls)
            elif isinstance(message, AssistantMessage):
                print(f"[AssistantMessage]")
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"  - Text: {block.text[:50]}...")
                    elif isinstance(block, ToolUseBlock):
                        print(f"  - Tool call: {block.name}")
                        print(f"    Input: {block.input}")
                print()

            # Tool results
            elif isinstance(message, ToolResultMessage):
                print(f"[ToolResultMessage] Tool: {message.tool_use_id}")
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"  - Result: {block.text[:50]}...")
                print()

            # Final result
            elif isinstance(message, ResultMessage):
                print(f"[ResultMessage]")
                print(f"  - Status: {message.subtype}")
                print(f"  - Cost: ${message.total_cost_usd:.4f}")
                print()


# =============================================================================
# PART 2: Basic Response Iteration
# =============================================================================

async def example_basic_iteration():
    """
    Example 2: Basic response iteration pattern.

    The simplest way to process responses:
    - Use query() convenience function
    - Iterate with async for
    - Handle AssistantMessage and ResultMessage
    """

    print("\n" + "="*60)
    print("Example 2: Basic Response Iteration")
    print("="*60)

    echo_server = create_sdk_mcp_server(
        name="echo",
        version="1.0.0",
        tools=[echo]
    )

    options = ClaudeAgentOptions(
        mcp_servers={"echo": echo_server},
        allowed_tools=["mcp__echo__echo"],
        cwd=Path.cwd()
    )

    print("\nQuery: 'Use echo tool to say: Hello World'\n")

    # Simple iteration pattern
    async for message in query(
        prompt="Use echo tool to say: Hello World",
        options=options
    ):
        # Extract text from assistant messages
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Assistant: {block.text}")

        # Show final cost
        elif isinstance(message, ResultMessage):
            print(f"\nCompleted. Cost: ${message.total_cost_usd:.4f}")


# =============================================================================
# PART 3: Streaming Responses
# =============================================================================

async def example_streaming():
    """
    Example 3: Stream responses for real-time feedback.

    Streaming provides:
    - Immediate user feedback
    - Better UX for long operations
    - Progressive text rendering
    """

    print("\n" + "="*60)
    print("Example 3: Streaming Responses")
    print("="*60)

    echo_server = create_sdk_mcp_server(
        name="echo",
        version="1.0.0",
        tools=[echo]
    )

    options = ClaudeAgentOptions(
        mcp_servers={"echo": echo_server},
        allowed_tools=["mcp__echo__echo"],
        cwd=Path.cwd()
    )

    print("\nStreaming response (watch text appear progressively):\n")

    current_text = ""

    async for message in query(
        prompt="Write a short poem about coding",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    # Print only new text (incremental streaming)
                    new_text = block.text[len(current_text):]
                    if new_text:
                        print(new_text, end='', flush=True)
                        current_text = block.text

        elif isinstance(message, ResultMessage):
            print(f"\n\n[Stream complete. Cost: ${message.total_cost_usd:.4f}]")


# =============================================================================
# PART 4: Advanced Response Tracking
# =============================================================================

@dataclass
class ExecutionTracker:
    """
    Track comprehensive agent execution data.

    Captures:
    - All messages
    - Assistant responses
    - Tool calls and results
    - Costs and timing
    """

    # Message storage
    all_messages: List[Any] = field(default_factory=list)
    system_messages: List[SystemMessage] = field(default_factory=list)
    assistant_messages: List[AssistantMessage] = field(default_factory=list)
    tool_result_messages: List[ToolResultMessage] = field(default_factory=list)

    # Extracted data
    assistant_texts: List[str] = field(default_factory=list)
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    tool_results: List[Dict[str, Any]] = field(default_factory=list)

    # Metadata
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    total_cost: float = 0.0
    status: str = "running"

    def process_message(self, message: Any) -> None:
        """Process and categorize a message."""
        self.all_messages.append(message)

        if isinstance(message, SystemMessage):
            self.system_messages.append(message)

        elif isinstance(message, AssistantMessage):
            self.assistant_messages.append(message)

            # Extract text and tool calls
            for block in message.content:
                if isinstance(block, TextBlock):
                    self.assistant_texts.append(block.text)

                elif isinstance(block, ToolUseBlock):
                    self.tool_calls.append({
                        "id": block.id,
                        "name": block.name,
                        "input": block.input,
                        "timestamp": datetime.now()
                    })

        elif isinstance(message, ToolResultMessage):
            self.tool_result_messages.append(message)

            # Extract results
            for block in message.content:
                if isinstance(block, TextBlock):
                    self.tool_results.append({
                        "tool_use_id": message.tool_use_id,
                        "result": block.text,
                        "is_error": getattr(block, 'is_error', False),
                        "timestamp": datetime.now()
                    })

        elif isinstance(message, ResultMessage):
            self.end_time = datetime.now()
            self.total_cost = message.total_cost_usd or 0.0
            self.status = message.subtype

    def get_summary(self) -> Dict[str, Any]:
        """Generate execution summary."""
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0

        # Count tool usage
        tool_usage = {}
        for call in self.tool_calls:
            tool_name = call["name"]
            tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1

        # Count errors
        error_count = sum(1 for r in self.tool_results if r.get("is_error", False))

        return {
            "status": self.status,
            "duration_seconds": duration,
            "total_cost_usd": self.total_cost,
            "message_counts": {
                "total": len(self.all_messages),
                "system": len(self.system_messages),
                "assistant": len(self.assistant_messages),
                "tool_results": len(self.tool_result_messages),
            },
            "tool_usage": tool_usage,
            "tool_calls_total": len(self.tool_calls),
            "errors": error_count,
            "assistant_response_count": len(self.assistant_texts),
        }

    def print_summary(self) -> None:
        """Print formatted summary."""
        summary = self.get_summary()

        print("\n" + "="*60)
        print("Execution Summary")
        print("="*60)
        print(f"Status: {summary['status']}")
        print(f"Duration: {summary['duration_seconds']:.2f}s")
        print(f"Cost: ${summary['total_cost_usd']:.4f}")
        print(f"\nMessages:")
        print(f"  Total: {summary['message_counts']['total']}")
        print(f"  System: {summary['message_counts']['system']}")
        print(f"  Assistant: {summary['message_counts']['assistant']}")
        print(f"  Tool Results: {summary['message_counts']['tool_results']}")
        print(f"\nTool Usage:")
        if summary['tool_usage']:
            for tool, count in summary['tool_usage'].items():
                print(f"  {tool}: {count}x")
        else:
            print("  No tools used")
        print(f"\nErrors: {summary['errors']}")
        print("="*60)


async def example_advanced_tracking():
    """
    Example 4: Advanced response tracking with ExecutionTracker.
    """

    print("\n" + "="*60)
    print("Example 4: Advanced Response Tracking")
    print("="*60)

    echo_server = create_sdk_mcp_server(
        name="echo",
        version="1.0.0",
        tools=[echo]
    )

    options = ClaudeAgentOptions(
        mcp_servers={"echo": echo_server},
        allowed_tools=["mcp__echo__echo"],
        cwd=Path.cwd()
    )

    print("\nTracking execution with comprehensive data capture...\n")

    # Create tracker
    tracker = ExecutionTracker()

    # Execute and track
    async with ClaudeSDKClient(options=options) as client:
        await client.query("Use echo three times with different messages")

        async for message in client.receive_response():
            tracker.process_message(message)

            # Still show real-time output
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Assistant: {block.text}")

    # Print comprehensive summary
    tracker.print_summary()

    # Access detailed data
    print("\nDetailed Tool Calls:")
    for call in tracker.tool_calls:
        print(f"  {call['name']} at {call['timestamp'].strftime('%H:%M:%S')}")
        print(f"    Input: {call['input']}")


# =============================================================================
# PART 5: Response Summarization Helper
# =============================================================================

def summarize_execution(messages: List[Any]) -> Dict[str, Any]:
    """
    Create comprehensive summary from message list.

    Args:
        messages: List of all messages from agent execution

    Returns:
        Dictionary with execution summary and human-readable text
    """

    summary = {
        "total_messages": len(messages),
        "assistant_responses": [],
        "tool_usage": {},
        "errors": [],
        "final_cost": 0.0,
        "status": "unknown"
    }

    for msg in messages:
        # Collect assistant text
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    summary["assistant_responses"].append(block.text)

                elif isinstance(block, ToolUseBlock):
                    tool_name = block.name
                    summary["tool_usage"][tool_name] = \
                        summary["tool_usage"].get(tool_name, 0) + 1

        # Track errors
        elif isinstance(msg, ToolResultMessage):
            for block in msg.content:
                if hasattr(block, 'is_error') and block.is_error:
                    summary["errors"].append({
                        "tool": msg.tool_use_id,
                        "message": block.text if isinstance(block, TextBlock) else str(block)
                    })

        # Final status
        elif isinstance(msg, ResultMessage):
            summary["final_cost"] = msg.total_cost_usd or 0.0
            summary["status"] = msg.subtype

    # Generate human-readable summary
    tool_usage_str = ', '.join(
        f"{k}({v}x)" for k, v in summary['tool_usage'].items()
    ) if summary['tool_usage'] else "none"

    summary["summary_text"] = f"""
Agent Execution Summary:
- Status: {summary['status']}
- Total messages: {summary['total_messages']}
- Tools used: {tool_usage_str}
- Errors: {len(summary['errors'])}
- Cost: ${summary['final_cost']:.4f}
    """.strip()

    return summary


async def example_summarization():
    """
    Example 5: Using summarization helper.
    """

    print("\n" + "="*60)
    print("Example 5: Response Summarization")
    print("="*60)

    echo_server = create_sdk_mcp_server(
        name="echo",
        version="1.0.0",
        tools=[echo]
    )

    options = ClaudeAgentOptions(
        mcp_servers={"echo": echo_server},
        allowed_tools=["mcp__echo__echo"],
        cwd=Path.cwd()
    )

    print("\nCollecting messages for summarization...\n")

    # Collect all messages
    messages = []

    async with ClaudeSDKClient(options=options) as client:
        await client.query("Say hello and goodbye using echo")

        async for message in client.receive_response():
            messages.append(message)

    # Generate and display summary
    summary = summarize_execution(messages)

    print("\n" + summary["summary_text"])

    print("\nDetailed breakdown:")
    print(f"  Assistant responses: {len(summary['assistant_responses'])}")
    for i, response in enumerate(summary['assistant_responses'], 1):
        print(f"    {i}. {response[:60]}...")


# =============================================================================
# PART 6: Best Practices
# =============================================================================

def demonstrate_best_practices():
    """
    Best practices for response handling.
    """

    print("\n" + "="*60)
    print("Best Practices for Response Handling")
    print("="*60)

    practices = [
        {
            "practice": "Handle All Message Types",
            "why": "Don't miss important system info or errors",
            "how": "Check isinstance() for System, Assistant, ToolResult, Result"
        },
        {
            "practice": "Stream for Long Operations",
            "why": "Better UX with real-time feedback",
            "how": "Print incrementally as text arrives"
        },
        {
            "practice": "Track Costs",
            "why": "Monitor spending, prevent unexpected expenses",
            "how": "Extract total_cost_usd from ResultMessage"
        },
        {
            "practice": "Log Tool Usage",
            "why": "Debugging, optimization, security audit",
            "how": "Track ToolUseBlock names and frequencies"
        },
        {
            "practice": "Preserve Message History",
            "why": "Debugging, analysis, audit trail",
            "how": "Store all messages in list for post-processing"
        },
        {
            "practice": "Extract Structured Data",
            "why": "Enable programmatic decision-making",
            "how": "Parse TextBlocks for patterns, data extraction"
        },
        {
            "practice": "Handle Partial Responses",
            "why": "Streaming may send incremental updates",
            "how": "Track current_text, compute delta for new content"
        },
    ]

    for i, practice in enumerate(practices, 1):
        print(f"\n{i}. {practice['practice']}")
        print(f"   Why: {practice['why']}")
        print(f"   How: {practice['how']}")


# =============================================================================
# Main Execution
# =============================================================================

async def main():
    """
    Run all response handling examples.
    """

    print("Response Handling Examples")
    print("Source: https://github.com/anthropics/claude-agent-sdk-python\n")

    try:
        # Example 1: Message types
        await example_message_types()

        # Example 2: Basic iteration
        await example_basic_iteration()

        # Example 3: Streaming
        await example_streaming()

        # Example 4: Advanced tracking
        await example_advanced_tracking()

        # Example 5: Summarization
        await example_summarization()

        # Best practices
        demonstrate_best_practices()

        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60)

    except Exception as e:
        print(f"\nError running examples: {e}")
        print("\nNote: Examples require Claude Code CLI to be installed.")
        print("Install from: https://claude.ai/download")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
