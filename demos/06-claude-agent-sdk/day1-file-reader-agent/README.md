# Day 1: Setup & First Working Agent with Claude Agent SDK

**Duration**: 60 minutes
**Difficulty**: Beginner
**Prerequisites**: Python 3.10+, Node.js, Anthropic API key

## 🎯 Learning Objectives

By the end of this session, you will be able to:

1. Install and configure the Claude Agents SDK
2. Understand the difference between in-process and external MCP servers
3. Create streaming sessions with Claude
4. Connect to an MCP filesystem server
5. List available tools programmatically
6. Build a functional file reader agent
7. Use hooks to monitor and control agent behavior

## 📚 What You'll Build

A **File Reader Agent** that can:
- Connect to any directory via MCP filesystem server
- List available tools
- Read and analyze multiple files
- Extract key information and action items
- Provide intelligent summaries

## 🚀 Quick Start

### 1. Installation

```bash
# Install the Claude Agents SDK
pip install claude-agent-sdk anthropic python-dotenv

# Or use UV (recommended)
uv pip install claude-agent-sdk anthropic python-dotenv
```

### 2. Set Your API Key

```bash
# Export in your shell
export ANTHROPIC_API_KEY="your-api-key-here"

# Or create a .env file
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
```

### 3. Run the Demo

```bash
# With UV (handles dependencies automatically)
uv run file_reader_agent.py

# Or traditional Python
python file_reader_agent.py
```

## 📖 Course Materials

### Interactive Notebook (Recommended)

The notebook provides a hands-on, interactive learning experience:

```bash
# Install Jupyter
pip install jupyter

# Run the notebook
jupyter notebook 01-intro-claude-agents-sdk.ipynb
```

**What the notebook covers:**
- Core concepts of Claude Agents SDK
- Creating custom tools with `@tool` decorator
- Connecting to external MCP servers
- Building a complete file reader agent
- Using hooks for monitoring and control

### Standalone Demo Script

The `file_reader_agent.py` script is a complete, production-ready example:

**Features:**
- ✅ Automatic demo directory setup
- ✅ Multi-step file analysis workflow
- ✅ Clear, annotated output
- ✅ Proper error handling and cleanup
- ✅ UV inline dependency metadata

## 🔍 Understanding the Architecture

### Claude Agents SDK Structure

```
┌─────────────────────────────────────────┐
│         Your Python Application         │
│  ┌───────────────────────────────────┐  │
│  │   ClaudeSDKClient                 │  │
│  │   ┌───────────────────────────┐   │  │
│  │   │  ClaudeAgentOptions       │   │  │
│  │   │  - system_prompt          │   │  │
│  │   │  - mcp_servers            │   │  │
│  │   │  - allowed_tools          │   │  │
│  │   │  - hooks                  │   │  │
│  │   │  - max_turns              │   │  │
│  │   └───────────────────────────┘   │  │
│  └───────────────────────────────────┘  │
│                  │                       │
│                  ├── In-Process MCP ────┤
│                  │   (Custom Tools)      │
│                  │                       │
│                  ├── External MCP ───────┤
│                  │   (Filesystem, etc)   │
│                  │                       │
│                  └── Claude API ─────────┤
│                      (Anthropic)         │
└─────────────────────────────────────────┘
```

### MCP Integration: Two Approaches

#### 1. In-Process SDK Servers (Custom Tools)

**Best for:**
- Custom business logic
- Performance-critical operations
- Simple Python functions

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("greet", "Greet a user", {"name": str})
async def greet_user(args):
    return {
        "content": [{
            "type": "text",
            "text": f"Hello, {args['name']}!"
        }]
    }

server = create_sdk_mcp_server(
    name="my-tools",
    version="1.0.0",
    tools=[greet_user]
)
```

**Advantages:**
- ⚡ No subprocess overhead
- 🚀 Better performance
- 📦 Simpler deployment
- 🔒 Type safety

#### 2. External MCP Servers (Separate Processes)

**Best for:**
- Existing MCP servers
- Cross-language tools
- System integrations

```python
options = ClaudeAgentOptions(
    mcp_servers={
        "filesystem": {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"]
        }
    }
)
```

**Advantages:**
- 🔄 Reuse existing servers
- 🌐 Language-agnostic
- 🔌 Standard protocol

## 🎓 Step-by-Step Walkthrough

### Step 1: Simple Query (5 minutes)

The simplest way to use Claude:

```python
from claude_agent_sdk import query

async def simple_query():
    async for message in query(prompt="What is 2 + 2?"):
        print(message, end="", flush=True)

import asyncio
asyncio.run(simple_query())
```

**Key Concepts:**
- `query()` is a one-shot streaming function
- Stateless - each call is independent
- Great for simple tasks

### Step 2: Custom Tools (10 minutes)

Create tools that Claude can use:

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("calculate", "Perform calculations", {"expression": str})
async def calculate(args):
    result = eval(args["expression"])  # Don't use eval in production!
    return {"content": [{"type": "text", "text": str(result)}]}

server = create_sdk_mcp_server(
    name="calculator",
    version="1.0.0",
    tools=[calculate]
)
```

**Key Concepts:**
- `@tool` decorator defines the tool
- Schema defines input parameters
- Tools return structured responses

### Step 3: External MCP Server (15 minutes)

Connect to the filesystem MCP server:

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async def use_filesystem():
    options = ClaudeAgentOptions(
        mcp_servers={
            "filesystem": {
                "type": "stdio",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
            }
        }
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("List all files and read README.md")
        async for msg in client.receive_response():
            print(msg, end="", flush=True)
```

**Key Concepts:**
- External servers run as separate processes
- Communication via stdin/stdout
- Standard MCP protocol

### Step 4: Complete Agent (20 minutes)

Build a production-ready agent:

```python
async def file_reader_agent(directory: str):
    options = ClaudeAgentOptions(
        system_prompt="You are a file analysis assistant...",
        mcp_servers={
            "filesystem": {
                "type": "stdio",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", directory]
            }
        },
        max_turns=10,
        hooks={
            "PreToolUse": [
                HookMatcher(matcher="*", hooks=[log_tool_use])
            ]
        }
    )

    async with ClaudeSDKClient(options=options) as client:
        # Multi-step workflow
        await client.query("Analyze all files...")
        async for msg in client.receive_response():
            print(msg, end="", flush=True)
```

**Key Concepts:**
- System prompts guide behavior
- `max_turns` controls agent iterations
- Hooks enable monitoring and control

### Step 5: Hooks for Control (10 minutes)

Monitor and control Claude's actions:

```python
from claude_agent_sdk import HookMatcher

async def approval_hook(input_data, tool_use_id, context):
    """Ask for user approval before tool execution"""
    tool_name = input_data.get("tool_name")
    print(f"Claude wants to use: {tool_name}")

    approval = input("Allow? (y/n): ")
    if approval.lower() != 'y':
        return {
            "hookSpecificOutput": {
                "permissionDecision": "deny"
            }
        }
    return {}

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="*", hooks=[approval_hook])
        ]
    }
)
```

## 🛠️ Hands-On Exercise

### Challenge: Build a Code Analysis Agent

**Task**: Modify the file reader agent to:

1. Focus on Python files (`.py`)
2. Extract function definitions
3. Count lines of code
4. Identify potential improvements
5. Generate a code quality report

**Starter Code**:

```python
async def code_analysis_agent(directory: str):
    options = ClaudeAgentOptions(
        system_prompt="""You are a code analysis assistant.
        Analyze Python files and provide insights on:
        - Code structure and organization
        - Function complexity
        - Documentation quality
        - Potential improvements
        """,
        mcp_servers={
            "filesystem": {
                "type": "stdio",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", directory]
            }
        },
        max_turns=10
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query(
            "Analyze all Python files and generate a code quality report"
        )
        async for msg in client.receive_response():
            print(msg, end="", flush=True)

# Try it!
# await code_analysis_agent("/path/to/your/python/project")
```

## 📊 Common Patterns

### Pattern 1: Multi-Step Analysis

```python
async def multi_step_analysis(directory: str):
    async with ClaudeSDKClient(options=options) as client:
        # Step 1: Discovery
        await client.query("List all files")
        async for msg in client.receive_response():
            pass

        # Step 2: Analysis
        await client.query("Read and analyze each file")
        async for msg in client.receive_response():
            pass

        # Step 3: Summary
        await client.query("Provide final summary")
        async for msg in client.receive_response():
            print(msg, end="", flush=True)
```

### Pattern 2: Error Handling

```python
from claude_agent_sdk import CLINotFoundError, ProcessError

try:
    async for message in query(prompt="Hello"):
        print(message)
except CLINotFoundError:
    print("Please install Claude Code: npm install -g @anthropic-ai/claude-code")
except ProcessError as e:
    print(f"Process failed with exit code {e.exit_code}")
```

### Pattern 3: Dynamic Tool Selection

```python
def get_allowed_tools(task_type: str) -> list:
    """Return appropriate tools based on task"""
    tool_sets = {
        "read_only": ["mcp__filesystem__read_file", "mcp__filesystem__list_directory"],
        "full_access": ["mcp__filesystem__*"],
        "custom": ["mcp__mytools__analyze", "mcp__filesystem__read_file"]
    }
    return tool_sets.get(task_type, [])

options = ClaudeAgentOptions(
    allowed_tools=get_allowed_tools("read_only")
)
```

## 🐛 Troubleshooting

### Issue: "Module not found: claude_agent_sdk"

**Solution:**
```bash
pip install --upgrade claude-agent-sdk
```

### Issue: "Node.js not found"

The filesystem MCP server requires Node.js.

**Solution:**
```bash
# macOS
brew install node

# Ubuntu/Debian
sudo apt install nodejs npm

# Windows
# Download from https://nodejs.org
```

### Issue: "ANTHROPIC_API_KEY not found"

**Solution:**
```bash
# Set environment variable
export ANTHROPIC_API_KEY="your-key"

# Or create .env file
echo "ANTHROPIC_API_KEY=your-key" > .env
```

### Issue: "MCP server not responding"

**Solution:**
```bash
# Test the filesystem server directly
npx -y @modelcontextprotocol/server-filesystem /tmp

# If it fails, try reinstalling
npm cache clean --force
```

## 📚 Additional Resources

### Documentation
- [Claude Agents SDK Official Docs](https://docs.claude.com/en/api/agent-sdk/overview)
- [MCP Specification](https://modelcontextprotocol.io/specification/)
- [Claude API Reference](https://docs.anthropic.com/claude/reference/)

### Example Projects
- [GitHub Repository](https://github.com/anthropics/claude-agent-sdk-python)
- [MCP Servers Directory](https://github.com/modelcontextprotocol/servers)

### Community
- [Anthropic Discord](https://discord.gg/anthropic)
- [MCP Community Examples](https://github.com/topics/mcp)

## 🎯 Next Steps

After completing Day 1, you should:

1. ✅ Understand Claude Agents SDK basics
2. ✅ Know how to connect MCP servers
3. ✅ Be able to build simple agents
4. ✅ Understand streaming and hooks

**Ready for Day 2?**

In Day 2, we'll build an **Automation Agent** that:
- Creates automation scripts from natural language
- Tests scripts automatically
- Integrates with databases
- Handles complex multi-step workflows

See you tomorrow! 🚀
