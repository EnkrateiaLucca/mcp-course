# Claude Agents SDK with MCP - Complete Guide

## Overview

This guide explains how the **Claude Agents SDK** implementation works for querying CSV data through a Model Context Protocol (MCP) server. We'll break down the architecture, API patterns, and key differences from other agent frameworks.

## Table of Contents

1. [Architecture](#architecture)
2. [How It Works](#how-it-works)
3. [Key Components](#key-components)
4. [API Patterns](#api-patterns)
5. [Comparison with OpenAI Agents SDK](#comparison-with-openai-agents-sdk)
6. [Examples Explained](#examples-explained)
7. [Best Practices](#best-practices)

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Your Application                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           claude_agents_csv_demo.py                   │  │
│  │                                                        │  │
│  │  1. Import claude_agent_sdk                           │  │
│  │  2. Configure ClaudeAgentOptions                      │  │
│  │  3. Call query() with user prompt                     │  │
│  │  4. Process streaming messages                        │  │
│  └────────────────┬───────────────────────────────────────┘  │
│                   │                                           │
└───────────────────┼───────────────────────────────────────────┘
                    │
                    │ API Call (HTTPS)
                    ▼
        ┌───────────────────────┐
        │   Anthropic API       │
        │   (Claude 4.5)        │
        └───────────┬───────────┘
                    │
                    │ MCP Protocol
                    │ (via SDK)
                    ▼
        ┌───────────────────────┐
        │   Claude Agent SDK    │
        │   - Manages MCP       │
        │   - Handles stdio     │
        │   - Tool execution    │
        └───────────┬───────────┘
                    │
                    │ stdio (stdin/stdout)
                    ▼
        ┌───────────────────────┐
        │  csv_query_mcp_server │
        │  (Subprocess)         │
        │                       │
        │  - FastMCP server     │
        │  - 7 tool functions   │
        │  - Pandas queries     │
        └───────────┬───────────┘
                    │
                    │ File I/O
                    ▼
        ┌───────────────────────┐
        │   sample_data.csv     │
        │   (Product catalog)   │
        └───────────────────────┘
```

### Communication Flow

1. **User Query** → Your Python app
2. **SDK Call** → Claude Agents SDK's `query()` function
3. **API Request** → Anthropic API (Claude model)
4. **Tool Discovery** → SDK launches MCP server subprocess
5. **Tool Calls** → Claude decides which tools to use
6. **Execution** → SDK forwards tool calls to MCP server via stdio
7. **Results** → MCP server returns data to SDK
8. **Response** → Claude processes results and streams response
9. **Output** → Your app receives messages via async generator

---

## How It Works

### Step-by-Step Execution

#### 1. Configuration Phase

```python
options = ClaudeAgentOptions(
    model="claude-sonnet-4-5",
    system_prompt="You are a helpful product assistant...",
    mcp_servers={
        "csv-query": {
            "type": "stdio",
            "command": "python",
            "args": ["csv_query_mcp_server.py"]
        }
    },
    permission_mode="bypassPermissions",
    max_turns=10,
)
```

**What happens:**
- SDK validates the configuration
- Prepares to launch the MCP server subprocess
- Sets up tool permission rules
- Configures model parameters

#### 2. Query Initiation

```python
async for message in query(prompt="Show me electronics", options=options):
    # Process messages...
```

**What happens:**
- SDK launches `csv_query_mcp_server.py` as a subprocess
- Establishes stdin/stdout pipes for communication
- Sends MCP `initialize` request
- Server responds with capabilities
- SDK sends `tools/list` request
- Server returns available tools:
  - `mcp__csv-query__get_all_products`
  - `mcp__csv-query__search_products_by_category`
  - `mcp__csv-query__search_products_by_price_range`
  - ... (7 total tools)

#### 3. Claude Reasoning

**What happens:**
- SDK sends the user prompt + system prompt + tools to Claude API
- Claude analyzes the request: "Show me electronics"
- Claude decides to use: `mcp__csv-query__search_products_by_category`
- Claude generates tool call with arguments: `{"category": "Electronics"}`

#### 4. Tool Execution

**What happens:**
- SDK receives tool use request from Claude
- SDK sends MCP `tools/call` request to server via stdin:
  ```json
  {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "search_products_by_category",
      "arguments": {"category": "Electronics"}
    }
  }
  ```
- MCP server receives request
- Server executes: `search_products_by_category("Electronics")`
- Pandas filters the CSV: `df[df['category'].str.lower() == 'electronics']`
- Server returns results via stdout:
  ```json
  {
    "content": [{"type": "text", "text": "product_name  category  price...\n..."}]
  }
  ```

#### 5. Response Generation

**What happens:**
- SDK forwards tool results back to Claude API
- Claude receives the filtered product data
- Claude generates a natural language response
- SDK streams messages back to your app:
  - `AssistantMessage` with `ToolUseBlock`
  - `AssistantMessage` with `TextBlock` (final response)
  - `ResultMessage` with cost and metadata

#### 6. Message Processing

```python
async for message in query(...):
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(block.text)  # "We have 9 electronics products..."
```

**What happens:**
- Your app iterates through streamed messages
- Filters for `TextBlock` content
- Displays Claude's natural language response
- Optionally tracks tool usage and cost

---

## Key Components

### 1. ClaudeAgentOptions

The central configuration object for the Claude Agents SDK.

```python
ClaudeAgentOptions(
    # Model Configuration
    model="claude-sonnet-4-5",           # Model to use
    fallback_model="claude-opus-4-1",    # Fallback if primary unavailable

    # System Instructions
    system_prompt="Your instructions...", # Custom system prompt

    # MCP Servers
    mcp_servers={
        "server-name": {
            "type": "stdio",              # Transport type
            "command": "python",          # Command to run
            "args": ["script.py"]         # Command arguments
        }
    },

    # Permissions
    permission_mode="bypassPermissions",  # How to handle tool permissions
    allowed_tools=["Read", "Write"],     # Whitelist specific tools

    # Limits
    max_turns=10,                        # Maximum agent loop iterations
    max_budget_usd=5.0,                  # Maximum cost limit

    # Working Directory
    cwd="/path/to/project",              # Set working directory
)
```

#### Permission Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `"default"` | Ask user for approval before each tool use | Interactive applications |
| `"bypassPermissions"` | Auto-approve all tool uses | Demos, trusted environments |
| `"acceptEdits"` | Auto-approve file edits only | Development workflows |
| `"plan"` | Generate a plan before execution | Review-before-execute workflows |

### 2. query() Function

Stateless, one-shot query function for simple interactions.

```python
async def query(
    prompt: str,              # User's question/request
    options: ClaudeAgentOptions = None,  # Configuration
    cwd: str = None,          # Override working directory
) -> AsyncGenerator[Message, None]:  # Streams messages
    ...
```

**Returns:**
- `AssistantMessage` - Claude's responses and tool uses
- `ResultMessage` - Final result with cost and metadata
- `ErrorMessage` - If something goes wrong

**When to use:**
- Single questions without conversation history
- Batch processing multiple independent queries
- Stateless API endpoints

### 3. ClaudeSDKClient

Stateful client for multi-turn conversations.

```python
async with ClaudeSDKClient(options=options) as client:
    # First turn
    await client.query("What's the best product?")
    async for msg in client.receive_response():
        print(msg)

    # Second turn (has context from first)
    await client.query("Is it in stock?")
    async for msg in client.receive_response():
        print(msg)
```

**When to use:**
- Chatbots and conversational interfaces
- When follow-up questions need context
- Complex workflows with multiple steps

### 4. Message Types

#### AssistantMessage

Contains Claude's response content.

```python
class AssistantMessage:
    content: List[Union[TextBlock, ToolUseBlock]]
    stop_reason: Optional[str]
```

**Content blocks:**
- `TextBlock` - Natural language text from Claude
  ```python
  TextBlock(text="Here are the electronics products...")
  ```
- `ToolUseBlock` - Tool call requests
  ```python
  ToolUseBlock(
      id="toolu_123",
      name="mcp__csv-query__search_products_by_category",
      input={"category": "Electronics"}
  )
  ```

#### ResultMessage

Final result with metadata.

```python
class ResultMessage:
    total_cost_usd: float      # Total API cost
    turn_count: int            # Number of agent turns
    input_tokens: int          # Tokens in request
    output_tokens: int         # Tokens in response
    session_id: Optional[str]  # Session identifier
```

### 5. MCP Server Configuration

#### External Server (stdio)

```python
mcp_servers={
    "csv-query": {
        "type": "stdio",
        "command": "python",
        "args": ["csv_query_mcp_server.py"]
    }
}
```

**Pros:**
- Separate process isolation
- Can be written in any language
- Easy to deploy independently

**Cons:**
- Subprocess overhead
- Requires external script management

#### SDK Server (in-process)

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("greet", "Greet a user", {"name": str})
async def greet_user(args):
    return {"content": [{"type": "text", "text": f"Hello, {args['name']}!"}]}

server = create_sdk_mcp_server(
    name="greetings",
    version="1.0.0",
    tools=[greet_user]
)

mcp_servers={"greet": server}
```

**Pros:**
- No subprocess overhead
- Simpler deployment (single Python file)
- Easier debugging

**Cons:**
- Must be written in Python
- Shares process memory

---

## API Patterns

### Pattern 1: Simple Query

**Use case:** One-off questions without state.

```python
async def simple_query():
    options = ClaudeAgentOptions(
        model="claude-sonnet-4-5",
        mcp_servers={"csv": {...}},
        permission_mode="bypassPermissions",
    )

    async for message in query("Show electronics", options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
```

### Pattern 2: Stateful Conversation

**Use case:** Multi-turn conversations with context.

```python
async def conversation():
    options = ClaudeAgentOptions(...)

    async with ClaudeSDKClient(options=options) as client:
        # Turn 1
        await client.query("What's the top product?")
        async for msg in client.receive_response():
            process(msg)

        # Turn 2 (knows context)
        await client.query("Show me similar ones")
        async for msg in client.receive_response():
            process(msg)
```

### Pattern 3: Tool Usage Tracking

**Use case:** Monitor which tools are being used.

```python
async def track_tools():
    tools_used = []

    async for message in query("Your prompt", options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    tools_used.append(block.name)
                    print(f"Using: {block.name} with {block.input}")

    print(f"Total tools used: {len(tools_used)}")
```

### Pattern 4: Cost Monitoring

**Use case:** Track API costs for budgeting.

```python
async def monitor_cost():
    total_cost = 0.0

    async for message in query("Your prompt", options=options):
        if isinstance(message, ResultMessage):
            total_cost = message.total_cost_usd
            print(f"Cost: ${total_cost:.4f}")
            print(f"Input tokens: {message.input_tokens}")
            print(f"Output tokens: {message.output_tokens}")
```

---

## Comparison with OpenAI Agents SDK

| Feature | Claude Agents SDK | OpenAI Agents SDK |
|---------|-------------------|-------------------|
| **Main API** | `query()` function | `Agent` + `Runner.run()` |
| **Streaming** | Native async generator | Native async generator |
| **MCP Config** | In `ClaudeAgentOptions` | Via `MCPServerStdio` context manager |
| **Stateful API** | `ClaudeSDKClient` | `Agent` object |
| **Tool Naming** | `mcp__server__tool` | Auto-discovered |
| **Permissions** | `permission_mode` parameter | User callbacks |
| **In-process Tools** | `@tool` decorator + SDK server | Not directly supported |
| **Session Management** | `resume` parameter | Not built-in |

### Code Comparison

#### OpenAI Agents SDK

```python
async with MCPServerStdio(
    name="CSV Query",
    params={"command": "python", "args": ["server.py"]}
) as server:
    agent = Agent(
        name="Assistant",
        model="gpt-5-mini",
        instructions="You are helpful...",
        mcp_servers=[server],
    )

    result = await Runner.run(starting_agent=agent, input="Query")
    print(result.final_output)
```

#### Claude Agents SDK

```python
options = ClaudeAgentOptions(
    model="claude-sonnet-4-5",
    system_prompt="You are helpful...",
    mcp_servers={
        "csv": {"type": "stdio", "command": "python", "args": ["server.py"]}
    },
    permission_mode="bypassPermissions",
)

async for message in query("Query", options=options):
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(block.text)
```

### Key Differences

1. **Configuration Style**
   - OpenAI: Context manager for MCP server, separate Agent object
   - Claude: All configuration in `ClaudeAgentOptions`

2. **Execution Model**
   - OpenAI: `Runner.run()` returns final result
   - Claude: `query()` streams all messages

3. **Tool Discovery**
   - OpenAI: Automatic from MCP server
   - Claude: Namespaced as `mcp__server__tool`

4. **Permissions**
   - OpenAI: Callback functions for approval
   - Claude: Built-in permission modes

---

## Examples Explained

### Example 1: Simple Category Search

```python
await run_agentic_search("What electronics products do we have?")
```

**Execution flow:**
1. SDK launches MCP server subprocess
2. Claude receives prompt + available tools
3. Claude calls: `mcp__csv-query__search_products_by_category("Electronics")`
4. MCP server filters CSV: `df[df['category'] == 'Electronics']`
5. Returns 9 electronics products
6. Claude generates: "We have 9 electronics products: [list]"

**Why it works:**
- Natural language query → Claude understands "electronics" means category
- Tool selection → Claude picks the right tool automatically
- Data processing → MCP server handles Pandas operations
- Response formatting → Claude presents results naturally

### Example 2: Price Range Query

```python
await run_agentic_search("Show me products between $50 and $150")
```

**Execution flow:**
1. Claude parses: "between $50 and $150" → min=50, max=150
2. Claude calls: `mcp__csv-query__search_products_by_price_range(50, 150)`
3. MCP server filters: `df[(df['price'] >= 50) & (df['price'] <= 150)]`
4. Returns 4 matching products
5. Claude formats response with product details

**Why it works:**
- Natural language parsing → Claude extracts numeric ranges
- Argument mapping → Claude converts to function parameters
- Flexible filtering → Server handles the pandas query

### Example 3: Multi-Step Complex Query

```python
await run_agentic_search("""
    I need to buy office equipment:
    1. A good keyboard (check ratings)
    2. Furniture under $200
    3. Tell me if in stock
""")
```

**Execution flow:**
1. **First tool call** - Find keyboards:
   - `get_product_by_name("keyboard")`
   - Returns: Mechanical Keyboard ($149.99, rating 4.8)

2. **Second tool call** - Check it's in stock:
   - `get_products_in_stock(1)`
   - Confirms 75 units available

3. **Third tool call** - Find furniture under $200:
   - `search_products_by_category("Furniture")`
   - Then filters results in-memory for price < 200

4. **Fourth tool call** (optional) - Get stats:
   - Might call `get_category_statistics()` for context

5. **Response generation**:
   - Claude synthesizes all results
   - Formats as organized recommendations

**Why it works:**
- Multi-turn agent loop → SDK allows multiple tool calls
- Context retention → Each tool result informs the next call
- Intelligent synthesis → Claude combines data into coherent answer

---

## Best Practices

### 1. Error Handling

```python
try:
    async for message in query(prompt, options=options):
        if isinstance(message, AssistantMessage):
            # Process message
            pass
        elif isinstance(message, ErrorMessage):
            print(f"Error: {message.error}")
            break
except Exception as e:
    print(f"SDK error: {e}")
```

### 2. Cost Control

```python
options = ClaudeAgentOptions(
    max_budget_usd=5.0,  # Stop after $5
    max_turns=10,        # Limit agent loops
    model="claude-sonnet-4-5",  # Use cost-effective model
)
```

### 3. Tool Filtering

```python
options = ClaudeAgentOptions(
    allowed_tools=[
        "mcp__csv-query__search_products_by_category",
        "mcp__csv-query__get_top_rated_products",
    ],  # Only allow specific tools
)
```

### 4. Session Management

```python
# Save session for later
result_message = None
async for message in query(...):
    if isinstance(message, ResultMessage):
        result_message = message
        session_id = message.session_id

# Resume later
options = ClaudeAgentOptions(
    resume=session_id,  # Continue from previous session
)
```

### 5. Logging and Debugging

```python
async def verbose_query(prompt):
    print(f"Starting query: {prompt}")

    async for message in query(prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    print(f"[TOOL] {block.name}")
                    print(f"[ARGS] {block.input}")
                elif isinstance(block, TextBlock):
                    print(f"[TEXT] {block.text}")
```

### 6. Graceful Degradation

```python
options = ClaudeAgentOptions(
    model="claude-sonnet-4-5",
    fallback_model="claude-opus-4-1",  # Auto-fallback if unavailable
)
```

---

## Common Patterns

### Pattern: Batch Processing

```python
async def batch_queries(queries: list[str]):
    for query_text in queries:
        print(f"\\nProcessing: {query_text}")
        async for msg in query(query_text, options=options):
            if isinstance(msg, AssistantMessage):
                # Process result
                pass
```

### Pattern: Interactive Chat

```python
async def chat_loop():
    async with ClaudeSDKClient(options=options) as client:
        while True:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit']:
                break

            await client.query(user_input)
            async for msg in client.receive_response():
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            print(f"Claude: {block.text}")
```

### Pattern: Tool Result Processing

```python
async def extract_tool_results(prompt):
    tool_results = {}

    async for msg in query(prompt, options=options):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, ToolUseBlock):
                    # Track which tools were called
                    tool_results[block.name] = block.input

    return tool_results
```

---

## Conclusion

The Claude Agents SDK provides a powerful, flexible framework for building AI agents with MCP integration. Key advantages include:

- **Simplicity**: Clean async API with minimal boilerplate
- **Flexibility**: Support for both stateless and stateful patterns
- **Control**: Fine-grained permission and cost management
- **Performance**: Native streaming and in-process tool support
- **Standards**: Built on open MCP protocol

Use this guide as a reference for building your own Claude-powered applications with custom tool integrations!
