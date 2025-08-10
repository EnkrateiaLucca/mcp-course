# Claude Desktop & Cursor MCP Integration Demo

This demo showcases how to use MCP servers with consumer applications like Claude Desktop and Cursor IDE, demonstrating the practical "end-user" experience of MCP.

## What You'll Learn

- How to configure MCP servers for Claude Desktop
- Setting up MCP integration in Cursor IDE
- Building custom MCP servers for development workflows
- Tips, tricks, and best practices for consumer MCP usage

## Prerequisites

- Claude Desktop app installed
- Cursor IDE installed (optional)
- Basic understanding of JSON configuration
- Sample MCP servers to connect

## Demo Files

- `development_mcp_server.py` - Custom MCP server for development tasks
- `productivity_mcp_server.py` - MCP server for productivity workflows
- `claude_desktop_configs/` - Sample Claude Desktop configurations
- `cursor_configs/` - Sample Cursor IDE configurations
- `setup_scripts/` - Automated setup scripts

## Consumer Applications

### Claude Desktop

Claude Desktop natively supports MCP servers through configuration:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/username/Documents"],
      "env": {}
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-token"
      }
    }
  }
}
```

### Cursor IDE

Cursor supports MCP through extensions and configurations for enhanced coding experiences.

## Demo Scenarios

### 1. Development Workflow
- Code analysis and refactoring
- Git operations and repository management
- Documentation generation
- Testing and debugging assistance

### 2. Productivity Workflow
- File organization and management
- Calendar and task integration
- Note-taking and knowledge management
- Communication and collaboration tools

### 3. Creative Workflow
- Asset management and optimization
- Content creation assistance
- Project planning and tracking
- Research and information gathering

## Key Benefits

### For Developers
- **Seamless Integration**: MCP tools work directly in your IDE
- **Enhanced Productivity**: AI assistance with context about your codebase
- **Workflow Automation**: Automate repetitive development tasks
- **Tool Consistency**: Same tools across different environments

### For End Users
- **Easy Setup**: Simple configuration files
- **Powerful Capabilities**: Access to specialized tools without coding
- **Customizable**: Add your own MCP servers for specific needs
- **Future-Proof**: Works with any MCP-compatible application

## Running the Demo

1. **Set up Claude Desktop:**
```bash
# Copy configuration to Claude Desktop
cp claude_desktop_configs/development.json ~/.claude_desktop_config.json
```

2. **Start MCP servers:**
```bash
# Development server
python development_mcp_server.py

# Productivity server  
python productivity_mcp_server.py
```

3. **Test in Claude Desktop:**
   - Open Claude Desktop
   - Try commands like "What files are in my project directory?"
   - Test development workflows

4. **Optional - Cursor Setup:**
```bash
# Copy Cursor configuration
cp cursor_configs/mcp_extension.json ~/.cursor/extensions/
```

## Tips & Tricks

### Configuration Management
- Keep multiple config files for different scenarios
- Use environment variables for sensitive data
- Test servers independently before adding to configs

### Performance Optimization
- Use local servers when possible for faster response
- Implement caching in custom servers
- Monitor server resource usage

### Security Best Practices
- Restrict file system access to necessary directories
- Use secure token storage
- Regularly audit MCP server permissions

### Debugging
- Check Claude Desktop console for errors
- Test MCP servers with the MCP Inspector tool
- Use logging in custom servers for troubleshooting

## References

- [Claude Desktop MCP Setup Guide](https://docs.anthropic.com/claude/docs/connecting-claude-to-your-data)
- [Official MCP Servers](https://github.com/modelcontextprotocol/servers)
- [MCP Inspector Tool](https://github.com/modelcontextprotocol/inspector)
- [Community MCP Servers](https://github.com/punkpeye/awesome-mcp-servers)
