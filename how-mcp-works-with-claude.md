# How MCP Servers Work with Claude Desktop

## What is MCP?

[Inference based on official documentation] The Model Context Protocol (MCP) is an open standard developed by Anthropic that enables AI assistants like Claude to connect with external data sources and tools through a standardized interface.

## Core Architecture

### Three Main Components

1. **Host Application** (Claude Desktop)
   - [Based on documentation] Manages connections to MCP servers
   - Enforces security policies and handles user permissions
   - Creates and coordinates MCP clients

2. **MCP Client** (Built into Claude Desktop)
   - [Based on documentation] Maintains stateful 1:1 sessions with MCP servers
   - Selects which tools to use for tasks
   - Requests resources and generates prompts for the LLM

3. **MCP Server** (Your custom tools/integrations)
   - [Based on documentation] Provides access to external tools, databases, and APIs
   - Can offer three types of capabilities:
     - **Resources**: File-like data (API responses, file contents)
     - **Tools**: Functions the LLM can call with user approval
     - **Prompts**: Pre-written templates for common tasks

## How It Works: Step-by-Step

[Inference based on documentation] When you use Claude Desktop with MCP servers:

1. **Connection Phase**
   - Claude Desktop starts and reads your configuration file (`claude_desktop_config.json`)
   - Launches configured MCP servers
   - Each server announces its capabilities (available tools, resources, prompts)

2. **Discovery Phase**
   - Claude Desktop displays available tools (hammer icon in UI)
   - You can see which MCP servers are active and what they offer

3. **Request Phase**
   - You ask Claude a question or give it a task
   - Claude determines if it needs external tools to complete the task
   - Claude identifies the appropriate MCP server and tool to use

