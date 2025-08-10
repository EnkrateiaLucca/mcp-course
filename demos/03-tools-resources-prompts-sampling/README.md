# MCP Tools, Resources, Prompts & Sampling Demo

This demo showcases all four core MCP capabilities:

## What You'll Learn

1. **Tools** - Model-controlled executable functions with side effects
2. **Resources** - Application-controlled read-only data access
3. **Prompts** - User-controlled templates for structured interactions
4. **Sampling** - Server-initiated LLM interactions for complex reasoning

## Files in this Demo

- `comprehensive_mcp_server.py` - Complete MCP server implementing all capabilities
- `test_client.py` - Test client to interact with the server
- `requirements.txt` - Dependencies
- `claude_desktop_config.json` - Configuration for Claude Desktop integration

## Running the Demo

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python comprehensive_mcp_server.py
```

3. Test with the client:
```bash
python test_client.py
```

4. Or use with Claude Desktop by adding the config to your Claude Desktop configuration.

## Key Learning Points

### Tools
- **User approval required** before execution
- Can have **side effects** (modify data, send emails, etc.)
- **Model-controlled** - the LLM decides when to use them

### Resources
- **Read-only** data access
- **Application-controlled** - predefined by the server
- No user approval needed
- Perfect for providing context and information

### Prompts
- **User-controlled** templates
- Guide complex workflows
- Structure interactions between user and AI
- Enable reusable patterns

### Sampling
- **Server-initiated** LLM requests
- Enables complex reasoning workflows
- Two-way communication between server and client
- Advanced capability for agentic behaviors

## References

Based on official MCP documentation:
- [MCP Specification](https://modelcontextprotocol.io/specification/)
- [MCP Tools Guide](https://modelcontextprotocol.io/docs/concepts/tools)
- [MCP Resources Guide](https://modelcontextprotocol.io/docs/concepts/resources)
- [MCP Prompts Guide](https://modelcontextprotocol.io/docs/concepts/prompts)
- [MCP Sampling Guide](https://modelcontextprotocol.io/docs/concepts/sampling)
