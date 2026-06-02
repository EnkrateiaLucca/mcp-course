# Claude Agents SDK - CSV Query Demo with MCP Tools

A comprehensive demonstration of using **Claude Agents SDK** with in-process MCP (Model Context Protocol) tools to query tabular data from CSV files using natural language.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [How It Works](#how-it-works)
- [Key Components](#key-components)
- [Code Walkthrough](#code-walkthrough)
- [Examples Explained](#examples-explained)
- [API Patterns](#api-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

This demo shows how to build an AI agent that can query CSV data using natural language. Instead of writing complex pandas queries, users can simply ask questions like "What are the top-rated electronics?" and the agent handles the data retrieval automatically.

### What You'll Learn

- Building in-process MCP tools with the `@tool` decorator
- Configuring Claude Agents SDK with MCP servers
- Handling stateful multi-turn conversations
- Processing streaming responses from Claude
- Implementing data query tools with pandas

### What's Included

- **[claude_agents_sdk_demo.py](claude_agents_sdk_demo.py)** - Complete working demo with 5 examples
- **[claude_agents_csv_demo.ipynb](claude_agents_csv_demo.ipynb)** - Interactive Jupyter notebook walkthrough
- **[sample_data.csv](sample_data.csv)** - Product catalog with 15 items (Electronics & Furniture)
- **[csv_query_mcp_server.py](csv_query_mcp_server.py)** - Standalone MCP server (alternative approach)

---

## Quick Start

### Prerequisites

```bash
# Set your Anthropic API key
export ANTHROPIC_API_KEY='your-anthropic-api-key'
```

### Run the Demo

```bash
# Using UV (recommended - handles dependencies automatically)
uv run claude_agents_sdk_demo.py

# Or install dependencies manually
pip install claude-agent-sdk>=0.1.0 anthropic>=0.40.0 pandas>=2.0.0
python claude_agents_sdk_demo.py
```

### Expected Output

The demo runs 5 examples automatically:

1. **Category Search** - "What electronics products do we have?"
2. **Price Range Query** - "Show me products between $50 and $150"
3. **Top Rated Products** - "What are the top 3 highest-rated products?"
4. **Category Statistics** - "Give me a summary with average prices and ratings"
5. **Complex Multi-Step** - "Find a keyboard, furniture under $200, check stock" (verbose mode)

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   claude_agents_sdk_demo.py                  │
│                                                               │
│  1. Define tools with @tool decorator                        │
│  2. Create SDK MCP server (in-process)                       │
│  3. Configure ClaudeAgentOptions                             │
│  4. Run queries with ClaudeSDKClient                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ In-Process (No subprocess!)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Claude Agent SDK                                │
│  - Tool discovery and execution                              │
│  - Conversation state management                             │
│  - Streaming response handling                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTPS API Call
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Anthropic API (Claude Sonnet 4.5)               │
│  - Natural language understanding                            │
│  - Tool selection and reasoning                              │
│  - Response generation                                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ pandas queries
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                      sample_data.csv                         │
│  15 products: Electronics (9) + Furniture (6)                │
└─────────────────────────────────────────────────────────────┘
```

### Key Architectural Decisions

**In-Process Tools (What We Use):**
- Tools run directly in the Python application
- No subprocess overhead or IPC complexity
- Simpler deployment (single Python file)
- Better performance and easier debugging
- Ideal for custom business logic

**Alternative: External MCP Server:**
- MCP server runs as separate process (see [csv_query_mcp_server.py](csv_query_mcp_server.py))
- Connected via stdio or HTTP transport
- Can be written in any language
- Better process isolation
- Useful for sharing tools across multiple applications

---

## How It Works

### Step-by-Step Execution Flow

#### 1. Tool Definition Phase

```python
@tool("search_products_by_category", "Search for products by category", {"category": str})
async def search_products_by_category(args: dict[str, Any]) -> dict[str, Any]:
    category = args["category"]
    df = pd.read_csv(CSV_FILE_PATH)
    filtered_df = df[df['category'].str.lower() == category.lower()]
    return {"content": [{"type": "text", "text": filtered_df.to_string(index=False)}]}
```

**What happens:**
- `@tool` decorator registers the function with the SDK
- Tool name, description, and parameter schema are captured
- Function becomes available to Claude for execution

#### 2. MCP Server Creation

```python
csv_server = create_sdk_mcp_server(
    name="csv-query",
    version="1.0.0",
    tools=[
        search_products_by_category,
        search_products_by_price_range,
        get_top_rated_products,
        get_category_statistics,
    ]
)
```

**What happens:**
- SDK packages all tools into an in-process MCP server
- No subprocess spawned - tools run in same Python process
- Server is ready to provide tools to Claude

#### 3. Configuration Phase

```python
options = ClaudeAgentOptions(
    model="claude-sonnet-4-5",
    system_prompt="You are a helpful product assistant...",
    mcp_servers={"csv": csv_server},
    permission_mode="bypassPermissions",
    max_turns=10,
)
```

**What happens:**
- SDK validates configuration
- Links MCP server to Claude instance
- Sets permission rules (auto-approve for demo)
- Configures conversation limits

#### 4. Query Execution

```python
async with ClaudeSDKClient(options=options) as client:
    await client.query("What electronics products do we have?")
    async for message in client.receive_response():
        # Process messages...
```

**What happens:**
1. SDK sends user query to Claude API
2. Claude receives available tools in context
3. Claude analyzes query → decides to use `search_products_by_category`
4. Claude generates tool call: `{"category": "Electronics"}`
5. SDK executes tool locally (in-process)
6. Tool returns filtered DataFrame as text
7. Claude receives results and generates natural language response
8. SDK streams messages back to application

#### 5. Response Processing

```python
if isinstance(message, AssistantMessage):
    for block in message.content:
        if isinstance(block, TextBlock):
            print(f"Response: {block.text}")
        elif isinstance(block, ToolUseBlock):
            print(f"[Using tool: {block.name}]")
```

**What happens:**
- Application processes streaming messages
- `TextBlock` contains Claude's natural language response
- `ToolUseBlock` contains tool execution metadata
- `ResultMessage` provides cost and usage statistics

---

## Key Components

### 1. The @tool Decorator

Transforms Python functions into MCP tools that Claude can discover and use.

```python
@tool(
    name="tool_name",              # Identifier (must be unique)
    description="What this does",  # Shown to Claude for selection
    input_schema={"param": type}   # Parameter types
)
async def my_tool(args: dict[str, Any]) -> dict[str, Any]:
    """Docstring for developers"""
    result = process(args["param"])
    return {
        "content": [
            {"type": "text", "text": result}
        ]
    }
```

**Return format:**
- Must return `dict` with `"content"` key
- Content is list of blocks (usually text)
- Can also return images, errors, etc.

### 2. ClaudeAgentOptions

Central configuration object for the SDK.

```python
ClaudeAgentOptions(
    # Model Configuration
    model="claude-sonnet-4-5",        # Primary model
    fallback_model="claude-opus-4-1", # Backup if unavailable

    # System Instructions
    system_prompt="Your instructions for Claude...",

    # MCP Server Integration
    mcp_servers={
        "server-name": server_object,  # In-process server
        # OR for external servers:
        "external": {
            "type": "stdio",
            "command": "python",
            "args": ["server.py"]
        }
    },

    # Security & Permissions
    permission_mode="bypassPermissions",  # See permission modes below
    allowed_tools=["tool1", "tool2"],     # Whitelist (optional)

    # Resource Limits
    max_turns=10,                 # Maximum agent loop iterations
    max_budget_usd=5.0,           # Cost limit

    # Environment
    cwd="/path/to/working/dir",   # Working directory for file operations
)
```

**Permission Modes:**

| Mode | Description | Use Case |
|------|-------------|----------|
| `"default"` | Ask user for approval before each tool use | Interactive applications |
| `"bypassPermissions"` | Auto-approve all tool calls | Demos, trusted environments |
| `"acceptEdits"` | Auto-approve file edits only | Development workflows |
| `"plan"` | Generate plan before execution | Review-before-execute workflows |

### 3. ClaudeSDKClient

Stateful client for multi-turn conversations with context retention.

```python
async with ClaudeSDKClient(options=options) as client:
    # First turn
    await client.query("What's the best keyboard?")
    async for msg in client.receive_response():
        process(msg)

    # Second turn (maintains context from first)
    await client.query("Is it in stock?")  # Claude knows "it" = the keyboard
    async for msg in client.receive_response():
        process(msg)
```

**When to use:**
- Chatbots and conversational interfaces
- When follow-up questions need previous context
- Complex workflows with dependent steps

**Alternative: `query()` function** (stateless, one-shot):

```python
async for message in query("Single question", options=options):
    process(message)
```

Use for: batch processing, independent queries, stateless APIs.

### 4. Message Types

#### AssistantMessage

Contains Claude's response content (text and/or tool uses).

```python
class AssistantMessage:
    content: List[Union[TextBlock, ToolUseBlock]]
    stop_reason: Optional[str]  # Why generation stopped
```

**Content blocks:**

- **TextBlock** - Natural language from Claude
  ```python
  TextBlock(text="We have 9 electronics products...")
  ```

- **ToolUseBlock** - Tool call request
  ```python
  ToolUseBlock(
      id="toolu_abc123",
      name="search_products_by_category",
      input={"category": "Electronics"}
  )
  ```

#### ResultMessage

Final result with cost and usage metadata.

```python
class ResultMessage:
    total_cost_usd: float      # Total API cost for this interaction
    turn_count: int            # Number of agent loop iterations
    usage: dict                # Token counts (input/output)
    session_id: Optional[str]  # For resuming conversations
```

---

## Code Walkthrough

Let's break down the main demo file: [claude_agents_sdk_demo.py](claude_agents_sdk_demo.py:1)

### 1. Imports and Setup (Lines 22-46)

```python
import pandas as pd
from claude_agent_sdk import (
    tool,
    create_sdk_mcp_server,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ResultMessage
)

# Ensure API key is set
if not os.getenv('ANTHROPIC_API_KEY'):
    print("⚠️  Warning: ANTHROPIC_API_KEY not set!")
    exit(1)

# Get CSV file path
SCRIPT_DIR = Path(__file__).parent
CSV_FILE_PATH = SCRIPT_DIR / "sample_data.csv"
```

**Purpose:** Import SDK components, validate API key, locate data file.

### 2. Tool Definitions (Lines 50-98)

```python
@tool("search_products_by_category", "Search for products by category", {"category": str})
async def search_products_by_category(args: dict[str, Any]) -> dict[str, Any]:
    category = args["category"]
    df = pd.read_csv(CSV_FILE_PATH)
    filtered_df = df[df['category'].str.lower() == category.lower()]

    if filtered_df.empty:
        return {"content": [{"type": "text", "text": f"No products found in category: {category}"}]}

    return {"content": [{"type": "text", "text": filtered_df.to_string(index=False)}]}
```

**Pattern:** Each tool follows the same structure:
1. Extract parameters from `args` dict
2. Load and query CSV with pandas
3. Handle empty results gracefully
4. Return formatted text in MCP content format

**Available Tools:**
- `search_products_by_category(category: str)` - Filter by category
- `search_products_by_price_range(min_price: float, max_price: float)` - Price filter
- `get_top_rated_products(limit: int)` - Top N by rating
- `get_category_statistics()` - Aggregate stats by category

### 3. Helper Function: run_example (Lines 101-129)

```python
async def run_example(client: ClaudeSDKClient, query_text: str, title: str, verbose: bool = False):
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    print(f"Query: {query_text}\n")

    await client.query(query_text)

    tools_used = []
    async for message in client.receive_response():
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Response: {block.text}")
                elif isinstance(block, ToolUseBlock):
                    tools_used.append(block.name)
                    if verbose:
                        print(f"[Using tool: {block.name}]")

        elif isinstance(message, ResultMessage):
            if verbose:
                print(f"\n💰 Cost: ${message.total_cost_usd:.4f}")
                print(f"📊 Tokens: {message.usage.get('input_tokens', 0)} in, {message.usage.get('output_tokens', 0)} out")
                if tools_used:
                    print(f"🔧 Tools used: {', '.join(tools_used)}")
```

**Purpose:** Reusable function to run queries and format output.

**Features:**
- Sends query to Claude
- Processes streaming responses
- Extracts and displays text responses
- Tracks tool usage
- Shows cost/token statistics (verbose mode)

### 4. Main Function (Lines 132-204)

```python
async def main():
    # Create SDK MCP server with our tools
    csv_server = create_sdk_mcp_server(
        name="csv-query",
        version="1.0.0",
        tools=[
            search_products_by_category,
            search_products_by_price_range,
            get_top_rated_products,
            get_category_statistics,
        ]
    )

    # Configure Claude
    options = ClaudeAgentOptions(
        model="claude-sonnet-4-5",
        system_prompt="You are a helpful product assistant...",
        mcp_servers={"csv": csv_server},
        permission_mode="bypassPermissions",
        max_turns=10,
    )

    # Run examples with stateful client
    async with ClaudeSDKClient(options=options) as client:
        await run_example(client, "What electronics products do we have?", "Example 1: Category Search")
        await run_example(client, "Show me products that cost between $50 and $150", "Example 2: Price Range Query")
        # ... more examples
```

**Flow:**
1. Create in-process MCP server with all tools
2. Configure Claude with server and options
3. Create stateful client (maintains conversation context)
4. Run 5 different examples sequentially
5. Client automatically closes on context exit

---

## Examples Explained

### Example 1: Simple Category Search

**Query:** "What electronics products do we have? List them with their prices."

**Execution Flow:**
1. Claude receives query + available tools
2. Claude identifies keyword "electronics" → maps to category parameter
3. Claude calls: `search_products_by_category({"category": "Electronics"})`
4. Tool executes: `df[df['category'].str.lower() == 'electronics']`
5. Returns 9 matching products with all columns
6. Claude formats response naturally: "We have 9 electronics products: ..."

**Why it works:**
- Claude's NLU extracts "electronics" as category filter
- Tool handles case-insensitive matching
- pandas DataFrame formatted as readable table
- Claude presents data in user-friendly format

### Example 2: Price Range Query

**Query:** "Show me products that cost between $50 and $150"

**Execution Flow:**
1. Claude parses "between $50 and $150" → extracts min=50, max=150
2. Claude calls: `search_products_by_price_range({"min_price": 50, "max_price": 150})`
3. Tool executes: `df[(df['price'] >= 50) & (df['price'] <= 150)]`
4. Returns 4 matching products
5. Claude formats with product details and recommendations

**Why it works:**
- Claude understands numeric range expressions
- Automatically maps to function parameters
- Tool performs efficient pandas boolean indexing

### Example 3: Top Rated Products

**Query:** "What are the top 3 highest-rated products?"

**Execution Flow:**
1. Claude identifies "top 3" + "highest-rated" → needs sorting by rating
2. Claude calls: `get_top_rated_products({"limit": 3})`
3. Tool executes: `df.nlargest(3, 'rating')`
4. Returns top 3 products sorted by rating
5. Claude presents with rating highlights and context

**Why it works:**
- Claude recognizes superlative "highest-rated"
- Extracts limit parameter from "top 3"
- Tool uses pandas `nlargest()` for efficient sorting

### Example 4: Category Statistics

**Query:** "Give me a summary of our product categories with average prices and ratings"

**Execution Flow:**
1. Claude identifies aggregation request → needs stats by category
2. Claude calls: `get_category_statistics({})`
3. Tool executes:
   ```python
   df.groupby('category').agg({
       'product_id': 'count',
       'price': 'mean',
       'rating': 'mean',
       'stock': 'sum'
   })
   ```
4. Returns aggregated statistics for Electronics and Furniture
5. Claude formats as structured summary with insights

**Why it works:**
- Claude recognizes "summary" + "categories" → aggregation needed
- Tool provides pre-computed aggregate functions
- Claude adds business context to raw numbers

### Example 5: Complex Multi-Step Query (Verbose Mode)

**Query:**
```
I need to buy some office equipment. Can you help me find:
1. A good keyboard (check ratings)
2. Any furniture items under $200
3. Tell me if they're in stock
```

**Execution Flow (Multi-Turn Agent Loop):**

**Turn 1:** Find keyboards
- Claude calls: `search_products_by_category({"category": "Electronics"})`
- Scans results for keyboards
- Identifies: "Mechanical Keyboard" with 4.8 rating

**Turn 2:** Check keyboard stock
- Claude calls: `get_top_rated_products({"limit": 10})`
- Confirms Mechanical Keyboard has 75 units in stock

**Turn 3:** Find affordable furniture
- Claude calls: `search_products_by_category({"category": "Furniture"})`
- Filters results client-side for price < $200
- Finds: Desk Lamp LED ($79.99), Laptop Stand ($39.99), Desk Mat Large ($34.99)

**Turn 4:** Synthesize response
- No tool calls - Claude uses cached results
- Generates organized recommendation with:
  - Keyboard details (rating + stock)
  - Furniture options with prices
  - Stock confirmation for all items
  - Optional bundle suggestions

**Why it works:**
- Multi-turn agent loop allows sequential tool calls
- Claude maintains context between turns
- SDK handles multiple tool executions automatically
- Claude synthesizes results into coherent recommendations

**Verbose Output Shows:**
```
💰 Cost: $0.0237
🔧 Tools used: search_products_by_category, get_top_rated_products
```

---

## API Patterns

### Pattern 1: Stateless Query (One-Shot)

**Use case:** Single independent questions without conversation history.

```python
from claude_agent_sdk import query

async def one_shot_query(user_question: str):
    options = ClaudeAgentOptions(
        model="claude-sonnet-4-5",
        mcp_servers={"csv": csv_server},
        permission_mode="bypassPermissions",
    )

    async for message in query(user_question, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
                    return block.text
```

**Advantages:**
- Simple API for single questions
- No state management needed
- Perfect for batch processing

### Pattern 2: Stateful Conversation

**Use case:** Multi-turn conversations where context matters.

```python
async def chat_session():
    options = ClaudeAgentOptions(...)

    async with ClaudeSDKClient(options=options) as client:
        # Turn 1
        await client.query("What's your best product?")
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

        # Turn 2 (Claude remembers "best product" from Turn 1)
        await client.query("Is it in stock?")
        async for msg in client.receive_response():
            # Process response...
```

**Advantages:**
- Context retention across turns
- Natural follow-up questions
- Reduced token usage (no need to repeat context)

### Pattern 3: Tool Usage Monitoring

**Use case:** Track which tools are used for debugging/analytics.

```python
async def monitor_tools(user_query: str):
    tool_calls = []

    async with ClaudeSDKClient(options=options) as client:
        await client.query(user_query)

        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, ToolUseBlock):
                        tool_calls.append({
                            'name': block.name,
                            'input': block.input,
                            'id': block.id
                        })
                        print(f"🔧 Tool: {block.name}({block.input})")

    return tool_calls
```

**Advantages:**
- Debug tool selection logic
- Track usage patterns
- Audit tool execution

### Pattern 4: Cost Control

**Use case:** Monitor and limit API costs.

```python
async def cost_controlled_query(user_query: str, max_cost: float = 1.0):
    options = ClaudeAgentOptions(
        model="claude-sonnet-4-5",
        mcp_servers={"csv": csv_server},
        max_budget_usd=max_cost,  # Hard limit
        permission_mode="bypassPermissions",
    )

    total_cost = 0.0

    async for message in query(user_query, options=options):
        if isinstance(message, ResultMessage):
            total_cost = message.total_cost_usd
            print(f"💰 Cost: ${total_cost:.4f}")
            print(f"📊 Tokens: {message.usage.get('input_tokens')} in, {message.usage.get('output_tokens')} out")

            if total_cost > max_cost * 0.8:
                print("⚠️  Warning: Approaching cost limit!")

    return total_cost
```

**Advantages:**
- Prevent unexpected charges
- Budget-aware execution
- Token usage visibility

### Pattern 5: Error Handling

**Use case:** Robust error handling for production applications.

```python
async def robust_query(user_query: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            async with ClaudeSDKClient(options=options) as client:
                await client.query(user_query)

                async for msg in client.receive_response():
                    if isinstance(msg, AssistantMessage):
                        for block in msg.content:
                            if isinstance(block, TextBlock):
                                return block.text
                    elif hasattr(msg, 'error'):
                        print(f"❌ Error: {msg.error}")
                        if attempt < max_retries - 1:
                            print(f"Retrying... ({attempt + 1}/{max_retries})")
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                            break
                        else:
                            raise Exception(f"Failed after {max_retries} attempts")

        except Exception as e:
            print(f"Exception: {e}")
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)
```

**Advantages:**
- Handles transient failures
- Exponential backoff
- Graceful degradation

---

## Best Practices

### 1. Tool Design

**Do:**
- Keep tools focused and single-purpose
- Provide clear, descriptive names and descriptions
- Return structured, parseable data
- Handle edge cases (empty results, invalid inputs)

```python
@tool("search_by_category", "Search for products in a specific category", {"category": str})
async def search_by_category(args: dict[str, Any]) -> dict[str, Any]:
    category = args["category"]

    # Validate input
    if not category or not isinstance(category, str):
        return {"content": [{"type": "text", "text": "Error: Invalid category parameter"}]}

    # Query data
    df = pd.read_csv(CSV_FILE_PATH)
    results = df[df['category'].str.lower() == category.lower()]

    # Handle empty results
    if results.empty:
        return {"content": [{"type": "text", "text": f"No products found in category: {category}"}]}

    # Return formatted data
    return {"content": [{"type": "text", "text": results.to_string(index=False)}]}
```

**Don't:**
- Create overly broad "do everything" tools
- Assume parameters are valid without checking
- Return raw Python objects or pickle data
- Ignore error cases

### 2. Permission Management

**Development/Demo:**
```python
permission_mode="bypassPermissions"  # Auto-approve everything
```

**Production:**
```python
permission_mode="default"  # Ask user for approval

# Or whitelist specific tools:
allowed_tools=[
    "search_products_by_category",
    "get_top_rated_products"
]
```

### 3. Cost Optimization

**Use appropriate models:**
```python
# For complex reasoning:
model="claude-sonnet-4-5"

# For simple queries (cheaper):
model="claude-haiku-4-5"
```

**Set budget limits:**
```python
ClaudeAgentOptions(
    max_budget_usd=5.0,  # Stop after $5
    max_turns=10,        # Limit agent loops
)
```

### 4. Error Handling in Tools

```python
@tool("safe_operation", "Perform operation safely", {"input": str})
async def safe_operation(args: dict[str, Any]) -> dict[str, Any]:
    try:
        result = perform_operation(args["input"])
        return {"content": [{"type": "text", "text": result}]}
    except ValueError as e:
        return {"content": [{"type": "text", "text": f"Validation error: {str(e)}"}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Operation failed: {str(e)}"}]}
```

### 5. Performance Optimization

**Cache expensive operations:**
```python
# Bad: Read CSV on every tool call
@tool("search", "Search products", {"category": str})
async def search_bad(args):
    df = pd.read_csv(CSV_FILE_PATH)  # Slow!
    return filter_df(df, args["category"])

# Good: Load once, cache globally
PRODUCTS_DF = pd.read_csv(CSV_FILE_PATH)

@tool("search", "Search products", {"category": str})
async def search_good(args):
    return filter_df(PRODUCTS_DF, args["category"])
```

**Use in-process servers for custom tools:**
```python
# Better performance than subprocess:
csv_server = create_sdk_mcp_server(
    name="csv-query",
    tools=[tool1, tool2]  # In-process
)
```

### 6. Logging and Debugging

```python
async def debug_query(query_text: str):
    print(f"[DEBUG] Starting query: {query_text}")

    async with ClaudeSDKClient(options=options) as client:
        await client.query(query_text)

        turn = 0
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                turn += 1
                print(f"[DEBUG] Turn {turn}:")
                for block in msg.content:
                    if isinstance(block, ToolUseBlock):
                        print(f"  🔧 Tool: {block.name}")
                        print(f"  📥 Input: {json.dumps(block.input, indent=2)}")
                    elif isinstance(block, TextBlock):
                        print(f"  💬 Text: {block.text[:100]}...")
            elif isinstance(msg, ResultMessage):
                print(f"[DEBUG] Final cost: ${msg.total_cost_usd:.4f}")
                print(f"[DEBUG] Total turns: {msg.turn_count}")
```

---

## Troubleshooting

### Issue: "ANTHROPIC_API_KEY not set"

**Solution:**
```bash
export ANTHROPIC_API_KEY='your-key-here'

# Or add to ~/.bashrc or ~/.zshrc:
echo 'export ANTHROPIC_API_KEY="your-key"' >> ~/.bashrc
source ~/.bashrc
```

### Issue: "Module 'claude_agent_sdk' not found"

**Solution:**
```bash
pip install claude-agent-sdk>=0.1.0 anthropic>=0.40.0

# Or with UV:
uv add claude-agent-sdk anthropic
```

### Issue: "FileNotFoundError: sample_data.csv"

**Solution:**
```python
# Ensure script runs from correct directory
import os
os.chdir(os.path.dirname(__file__))

# Or use absolute path:
CSV_FILE_PATH = Path(__file__).parent / "sample_data.csv"
```

### Issue: Tools not being called / Claude ignores tools

**Possible causes:**
1. Tool description unclear → Claude doesn't understand when to use it
2. System prompt conflicts → Conflicting instructions
3. Query doesn't match tool capabilities → No relevant tool available

**Solutions:**
```python
# 1. Improve tool descriptions
@tool(
    "search_products",
    "Search for products by category name (e.g., Electronics, Furniture)",  # More specific
    {"category": str}
)

# 2. Adjust system prompt
system_prompt="""You are a product assistant with access to a CSV database.
ALWAYS use the available tools to answer questions about products.
Never make up product information - only use data from tool results."""

# 3. Verify tools are loaded
async with ClaudeSDKClient(options=options) as client:
    print("Available tools:", client.list_tools())  # If method exists
```

### Issue: High API costs

**Solutions:**
```python
# 1. Use cheaper model for simple queries
ClaudeAgentOptions(model="claude-haiku-4-5")

# 2. Set budget limits
ClaudeAgentOptions(max_budget_usd=1.0)

# 3. Reduce max_turns
ClaudeAgentOptions(max_turns=5)

# 4. Optimize system prompt (shorter = less tokens)
```

### Issue: Slow performance

**Solutions:**
```python
# 1. Cache data loading
PRODUCTS_DF = pd.read_csv(CSV_FILE_PATH)  # Global, load once

# 2. Use in-process tools (not stdio)
csv_server = create_sdk_mcp_server(...)  # Fast

# 3. Optimize pandas queries
# Bad:
for _, row in df.iterrows():  # Slow
    if row['category'] == 'Electronics':
        results.append(row)

# Good:
results = df[df['category'] == 'Electronics']  # Fast vectorized operation
```

---

## Next Steps

### 1. Extend Tool Capabilities

Add more sophisticated queries:

```python
@tool("search_by_multiple_filters", "Search with multiple criteria", {
    "category": str,
    "min_price": float,
    "max_price": float,
    "min_rating": float,
    "in_stock_only": bool
})
async def advanced_search(args: dict[str, Any]) -> dict[str, Any]:
    df = pd.read_csv(CSV_FILE_PATH)

    # Apply filters conditionally
    if args.get("category"):
        df = df[df['category'].str.lower() == args["category"].lower()]
    if args.get("min_price"):
        df = df[df['price'] >= args["min_price"]]
    if args.get("max_price"):
        df = df[df['price'] <= args["max_price"]]
    if args.get("min_rating"):
        df = df[df['rating'] >= args["min_rating"]]
    if args.get("in_stock_only"):
        df = df[df['stock'] > 0]

    return {"content": [{"type": "text", "text": df.to_string(index=False)}]}
```

### 2. Add Write Operations

```python
@tool("add_product", "Add a new product to catalog", {
    "name": str,
    "category": str,
    "price": float,
    "stock": int,
    "rating": float
})
async def add_product(args: dict[str, Any]) -> dict[str, Any]:
    df = pd.read_csv(CSV_FILE_PATH)

    new_product = pd.DataFrame([{
        'product_id': df['product_id'].max() + 1,
        'product_name': args['name'],
        'category': args['category'],
        'price': args['price'],
        'stock': args['stock'],
        'rating': args['rating']
    }])

    df = pd.concat([df, new_product], ignore_index=True)
    df.to_csv(CSV_FILE_PATH, index=False)

    return {"content": [{"type": "text", "text": f"Added product: {args['name']}"}]}
```

**Note:** Change `permission_mode` to `"default"` for write operations!

### 3. Support Multiple Data Sources

```python
# Tool for querying database
@tool("query_database", "Query PostgreSQL database", {"sql": str})
async def query_db(args: dict[str, Any]) -> dict[str, Any]:
    import psycopg2
    conn = psycopg2.connect(DATABASE_URL)
    df = pd.read_sql(args["sql"], conn)
    return {"content": [{"type": "text", "text": df.to_string(index=False)}]}

# Tool for querying API
@tool("fetch_live_prices", "Get current prices from external API", {"product_ids": list})
async def fetch_prices(args: dict[str, Any]) -> dict[str, Any]:
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/prices?ids={args['product_ids']}") as resp:
            data = await resp.json()
    return {"content": [{"type": "text", "text": json.dumps(data, indent=2)}]}
```

### 4. Build Web Interface

```python
from fastapi import FastAPI, WebSocket
from claude_agent_sdk import query, ClaudeAgentOptions

app = FastAPI()

@app.websocket("/chat")
async def chat_endpoint(websocket: WebSocket):
    await websocket.accept()

    options = ClaudeAgentOptions(
        model="claude-sonnet-4-5",
        mcp_servers={"csv": csv_server},
        permission_mode="bypassPermissions",
    )

    while True:
        user_message = await websocket.receive_text()

        async for msg in query(user_message, options=options):
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        await websocket.send_text(block.text)
```

### 5. Deploy to Production

See [demos/06-deploy-simple-agent-mcp-vercel/](../06-deploy-simple-agent-mcp-vercel/) for a complete deployment example with:
- FastAPI web server
- MCP HTTP transport
- Vercel serverless deployment
- Production-ready error handling

---

## Resources

### Documentation
- [Claude Agents SDK Documentation](https://platform.claude.com/docs/en/agent-sdk/overview)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Anthropic API Documentation](https://docs.anthropic.com/)

### Related Demos
- [01-introduction-to-mcp/](../01-introduction-to-mcp/) - MCP basics with FastMCP
- [02-study-case-anthropic-tools-resources-prompts-chat-app/](../02-study-case-anthropic-tools-resources-prompts-chat-app/) - OpenAI Agents SDK comparison
- [05-deployment-example/](../05-deployment-example/) - Production deployment patterns

### Tools Used
- [pandas](https://pandas.pydata.org/) - Data manipulation
- [FastMCP](https://github.com/modelcontextprotocol/python-sdk) - MCP server framework
- [UV](https://github.com/astral-sh/uv) - Fast Python package manager

---

## License

This demo is part of the O'Reilly Live Training course materials: "Building AI Agents with MCP"

MIT License - See course repository for details.
