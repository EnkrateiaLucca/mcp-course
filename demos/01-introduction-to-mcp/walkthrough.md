# Demo 1: Practical Introduction to MCP SDK

## Overview

This demo introduces the Model Context Protocol (MCP) SDK and demonstrates how to create a basic MCP server using FastMCP.

## What is MCP?

The Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to LLMs. Think of MCP like a USB-C port for AI applications - it provides a standardized way to connect AI models to different data sources and tools.

## Key Concepts

- **MCP Hosts**: Programs like Claude Desktop, IDEs, or AI tools that want to access data through MCP
- **MCP Clients**: Protocol clients that maintain 1:1 connections with servers
- **MCP Servers**: Lightweight programs that expose specific capabilities through standardized MCP protocol
- **Local Data Sources**: Your computer's files, databases, and services that MCP servers can securely access

## Demo Components

1. `mcp_server.py` - A minimal MCP server using FastMCP
2. `mcp_client.py` - A simple client to test the server
3. `requirements.txt` - Dependencies needed for this demo

## Running the Demo

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the server:
   ```bash
   python mcp_server.py
   ```

3. In another terminal, test with the client:
   ```bash
   python mcp_client.py
   ```

## References

- [MCP Python SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Specification](https://modelcontextprotocol.io/specification)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk)
