# OpenAI Agents SDK + MCP Server CSV Query Demo

This demo demonstrates how to use OpenAI's Agents SDK with a custom MCP (Model Context Protocol) server to query data from a CSV file using stdio transport.

## What's Included

- **`sample_data.csv`** - Sample product catalog data (15 products)
- **`csv_query_mcp_server.py`** - Custom MCP server with 7 data query tools
- **`openai_mcp_csv_demo.ipynb`** - Comprehensive Jupyter notebook with explanations and examples

## Architecture

```
┌─────────────────┐
│  Jupyter        │
│  Notebook       │
└────────┬────────┘
         │
         │ OpenAI Agents SDK
         │
    ┌────▼────────────────┐
    │   MCPServerStdio    │
    │   (subprocess)      │
    └────┬────────────────┘
         │
         │ stdin/stdout pipes
         │
    ┌────▼────────────────┐
    │   MCP Server        │
    │   (FastMCP)         │
    └────┬────────────────┘
         │
         │ pandas
         │
    ┌────▼────────────────┐
    │   sample_data.csv   │
    └─────────────────────┘
```

## Prerequisites

1. **Python 3.9 or higher**
2. **OpenAI API Key**
3. **Required packages:**
   - `openai-agents`
   - `mcp[cli]>=1.0.0`
   - `pandas>=2.0.0`
   - `jupyter` (for running the notebook)

## Setup

### 1. Set your OpenAI API Key

```bash
export OPENAI_API_KEY='your-api-key-here'
```

### 2. Install Dependencies

Using pip:
```bash
pip install openai-agents mcp pandas jupyter
```

Using uv (recommended for the standalone server):
```bash
pip install uv
```

### 3. Run the Jupyter Notebook

```bash
jupyter notebook openai_mcp_csv_demo.ipynb
```

Then run the cells in order to see the examples.

## Quick Test (Without Jupyter)

You can test the MCP server directly:

```bash
# Run the server standalone to test it
python csv_query_mcp_server.py
```

Or test with a simple Python script:

```python
import asyncio
from agents import Agent, Runner
from agents.mcp import MCPServerStdio

async def test():
    async with MCPServerStdio(
        name="CSV Query Server",
        params={
            "command": "python",
            "args": ["csv_query_mcp_server.py"]
        },
    ) as server:
        agent = Agent(
            name="Product Assistant",
            model="gpt-4o-mini",
            instructions="You are a helpful product assistant.",
            mcp_servers=[server],
        )

        result = await Runner.run(
            starting_agent=agent,
            input="What electronics products do we have?"
        )
        print(result.final_output)

asyncio.run(test())
```

## Available MCP Tools

The server provides these tools for querying the CSV data:

1. **`get_all_products()`** - Get all products
2. **`search_products_by_category(category)`** - Filter by category (e.g., "Electronics", "Furniture")
3. **`search_products_by_price_range(min_price, max_price)`** - Filter by price range
4. **`get_product_by_name(product_name)`** - Search by product name
5. **`get_top_rated_products(limit)`** - Get highest-rated products
6. **`get_products_in_stock(min_stock)`** - Get products with minimum stock level
7. **`get_category_statistics()`** - Get aggregated statistics by category

## Example Queries

Try asking the agent:

- "What electronics products do we have?"
- "Show me products between $50 and $150"
- "What are the top 3 highest-rated products?"
- "Give me a summary of our product categories"
- "Find me a good keyboard and check if it's in stock"

## Understanding the Components

### OpenAI Responses API

The newest OpenAI API (March 2025) that combines:
- Chat Completions (conversational AI)
- Assistants API (stateful conversations)
- Native MCP support (tool integration)

### OpenAI Agents SDK

Python framework built on top of the Responses API providing:
- Easy agent creation
- MCP server integration
- Multi-agent workflows
- Automatic tool discovery

### MCP (Model Context Protocol)

Open standard for AI model integration with external tools:
- **stdio transport** - Local subprocess (used here)
- **HTTP/SSE transport** - Remote servers

### FastMCP

Python library for building MCP servers easily:
- Decorator-based tool definition
- Automatic schema generation
- Built-in protocol handling

## Key Concepts Demonstrated

1. **stdio Transport** - Running MCP server as local subprocess
2. **Tool Discovery** - Automatic tool listing via MCP protocol
3. **Tool Execution** - Calling tools through the agent
4. **Natural Language Interface** - Query structured data conversationally
5. **Multi-step Reasoning** - Agent using multiple tools to answer complex queries

## Troubleshooting

### Issue: "OPENAI_API_KEY not set"
**Solution:** Set the environment variable before running:
```bash
export OPENAI_API_KEY='your-key'
```

### Issue: "Module 'agents' not found"
**Solution:** Install openai-agents:
```bash
pip install openai-agents
```

### Issue: "Module 'mcp' not found"
**Solution:** Install mcp with CLI support:
```bash
pip install "mcp[cli]>=1.0.0"
```

### Issue: Server process hangs
**Solution:** Make sure the CSV file exists in the same directory and the paths are correct.

## Next Steps

1. **Modify the CSV data** - Add your own data to `sample_data.csv`
2. **Add new tools** - Extend the MCP server with more query functions
3. **Deploy remotely** - Convert to HTTP/SSE transport for production
4. **Combine with other tools** - Add web_search, code_interpreter, etc.
5. **Build multi-agent systems** - Create specialized agents for different tasks

## Resources

- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [OpenAI Cookbook - MCP Guide](https://cookbook.openai.com/examples/mcp/mcp_tool_guide)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk)

## License

This demo is part of the O'Reilly MCP Course materials.
