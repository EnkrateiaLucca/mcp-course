# Claude Agents SDK - CSV Query Demo

This directory contains examples demonstrating how to use the **Claude Agents SDK** with MCP (Model Context Protocol) for querying CSV data.

## Files

### 1. `claude_agents_sdk_demo.py` - **Main Demo** ⭐
A complete, working demonstration using in-process MCP tools with the Claude Agents SDK.

**Features:**
- Uses `@tool` decorator to define custom tools
- In-process MCP server (no subprocess needed)
- 5 complete examples showing different query types
- Demonstrates stateful conversations with `ClaudeSDKClient`

**Run it:**
```bash
export ANTHROPIC_API_KEY='your-key'
uv run claude_agents_sdk_demo.py
```

### 2. `claude_agents_csv_demo.ipynb` - Jupyter Notebook
Interactive walkthrough with educational content (Note: This was created for reference but uses an older approach with external MCP servers - the Python script above is recommended).

### 3. `CLAUDE_SDK_EXPLANATION.md` - Complete Technical Guide
Comprehensive documentation covering:
- Architecture and system flow
- Step-by-step execution details
- API patterns and best practices
- Comparison with OpenAI Agents SDK

### 4. `csv_query_mcp_server.py` - Original MCP Server
The FastMCP server that can be used by any MCP client (OpenAI, Claude, or standalone).

### 5. `sample_data.csv` - Product Data
Sample CSV file with 15 products across Electronics and Furniture categories.

## Quick Start

### Prerequisites
```bash
# Install dependencies (handled automatically by uv)
export ANTHROPIC_API_KEY='your-anthropic-api-key'
```

### Run the Demo
```bash
cd 04-query-tabular-data
uv run claude_agents_sdk_demo.py
```

## How It Works

### Architecture

```
┌─────────────────────────────────┐
│  claude_agents_sdk_demo.py      │
│                                  │
│  1. Define tools with @tool     │
│  2. Create SDK MCP server       │
│  3. Configure ClaudeSDKClient   │
│  4. Run queries                 │
└────────────┬────────────────────┘
             │
             │ In-Process (No subprocess!)
             ▼
┌─────────────────────────────────┐
│  Claude Agent SDK               │
│  - Tool execution               │
│  - Conversation management      │
│  - API calls to Claude          │
└────────────┬────────────────────┘
             │
             │ HTTPS
             ▼
┌─────────────────────────────────┐
│  Anthropic API (Claude 4.5)     │
└─────────────────────────────────┘
```

### In-Process Tools vs External MCP Servers

**In-Process (Recommended - What we use):**
- Tools run directly in your Python application
- No subprocess overhead
- Simpler deployment (single Python file)
- Better performance
- Easier debugging

**External (Alternative):**
- MCP server runs as separate process
- Connected via stdio/HTTP
- Can be written in any language
- Better isolation

## Examples Included

### 1. Category Search
```python
"What electronics products do we have?"
```
→ Uses `search_products_by_category` tool

### 2. Price Range Query
```python
"Show me products between $50 and $150"
```
→ Uses `search_products_by_price_range` tool

### 3. Top Rated Products
```python
"What are the top 3 highest-rated products?"
```
→ Uses `get_top_rated_products` tool

### 4. Category Statistics
```python
"Give me a summary of product categories with average prices"
```
→ Uses `get_category_statistics` tool

### 5. Complex Multi-Step
```python
"I need office equipment: keyboard (check ratings), furniture under $200, check stock"
```
→ Uses multiple tools in sequence

## Key Concepts

### @tool Decorator
```python
@tool("tool_name", "Description for Claude", {"param": type})
async def my_tool(args: dict[str, Any]) -> dict[str, Any]:
    # Implementation
    return {
        "content": [{"type": "text", "text": "Result"}]
    }
```

### Creating MCP Server
```python
server = create_sdk_mcp_server(
    name="my-tools",
    version="1.0.0",
    tools=[tool1, tool2, tool3]
)
```

### Configuring Claude
```python
options = ClaudeAgentOptions(
    model="claude-sonnet-4-5",
    mcp_servers={"my-server": server},
    permission_mode="bypassPermissions",  # Auto-approve
    max_turns=10,
)
```

### Using the Client
```python
async with ClaudeSDKClient(options=options) as client:
    await client.query("Your question")
    async for msg in client.receive_response():
        # Process messages
        pass
```

## Advantages Over OpenAI Agents SDK

1. **In-Process Tools** - No subprocess needed for custom tools
2. **Simpler API** - Single `ClaudeSDKClient` for stateful conversations
3. **Better Integration** - Native MCP support from Anthropic
4. **Permission Control** - Built-in permission modes
5. **Streaming** - Native async streaming responses

## Troubleshooting

### "ANTHROPIC_API_KEY not set"
```bash
export ANTHROPIC_API_KEY='your-key-here'
```

### "Permission denied"
The demo uses `permission_mode="bypassPermissions"` to auto-approve tools. For production, use `"default"` or implement custom permission callbacks.

### Claude CLI Issues
The SDK bundles Claude CLI - no separate installation needed!

## Next Steps

1. **Extend Tools** - Add more CSV query capabilities
2. **Add Validation** - Implement input validation
3. **Error Handling** - Add robust error handling
4. **Multiple Data Sources** - Query multiple CSVs or databases
5. **Deploy** - Convert to web API with FastAPI

## Resources

- [Claude Agents SDK Docs](https://platform.claude.com/docs/en/agent-sdk/overview)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Anthropic API Docs](https://docs.anthropic.com/)

## License

MIT - See course repository for details
