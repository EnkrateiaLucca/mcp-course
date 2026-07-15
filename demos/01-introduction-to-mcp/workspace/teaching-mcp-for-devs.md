# Teaching MCP to Developers — Quick Research Brief

## What the best courses do
- **Hands-on first, spec later**: every major curriculum (Anthropic, Microsoft, HuggingFace, mcp.training) gets devs to a running server fast — "zero to working server in 90 min" is the standard workshop shape.
- **Progressive layering**: Microsoft's 9-module path goes basics → core concepts → security → coding → advanced/case studies. Mirrors the "grow one use case a layer at a time" approach.
- **Both sides of the wire**: Anthropic's course teaches servers AND clients (Python SDK) — understanding the host/client side is treated as essential, not optional.
- **Real integration targets**: connect to Claude Desktop / Cursor early so students see their server used by a real host, not just an inspector.
- **Production as a distinct stage**: auth, security, database-backed servers (Microsoft's 13-lab PostgreSQL path), deployment — kept separate from intro material.
- **Multi-language examples** (Python, TS, .NET, Java) widen reach, but single-SDK depth (FastMCP + Python) is the common intro default.
- **Capstone/take-home projects** to consolidate (Udemy bootcamps, MS curriculum contributions to open-source MCP projects).

## Key resources
- Anthropic official course — servers + clients, Python SDK
- microsoft/mcp-for-beginners — 11 modules, cross-language, security + production labs
- HuggingFace MCP course (with Anthropic) — beginner → informed journey
- mcp.training 90-min workshop — tools/resources/prompts → Claude Desktop
- modelcontextprotocol.info tutorials — "concept to production" + building MCP with LLMs

## Sources
- https://anthropic.skilljar.com/introduction-to-model-context-protocol
- https://github.com/microsoft/mcp-for-beginners/
- https://huggingface.co/learn/mcp-course/en/unit0/introduction
- https://mcp.training/courses/workshop-first-server
- https://modelcontextprotocol.info/docs/tutorials/
- https://developer.microsoft.com/en-us/reactor/series/s-1562/
- https://learn.microsoft.com/en-us/dotnet/ai/resources/mcp-servers
- https://techcommunity.microsoft.com/blog/educatordeveloperblog/kickstart-your-ai-development-with-the-model-context-protocol-mcp-course/4414963
