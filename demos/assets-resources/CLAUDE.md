# CLAUDE.md — assets-resources

This folder contains reference materials, diagrams, and cheatsheets for the O'Reilly MCP course.

## Course Structure

```
demos/
├── 00-intro-agents/                              # AI agent fundamentals
├── 01-introduction-to-mcp/                       # FastMCP basics, first MCP server
├── 02-study-case-anthropic-tools-resources-prompts-chat-app/  # Chat app with Claude tool use
├── 03-claude-agents-sdk-filesystem-agent/        # Claude Agent SDK + filesystem MCP
├── 04-query-tabular-data/                        # CSV querying with Claude Agent SDK
├── 05-automations-agent/                         # Link health checker (Claude SDK + MCP)
├── 06-deploy-simple-agent-mcp-vercel/            # Data analysis agent + Vercel deployment
├── 07-hacks-tips-tools-workflows/                # Tips, tools, MCP builder skill
└── assets-resources/                             # This folder — reference materials
```

## Key Dependencies

- **claude-agent-sdk** — Claude Agent SDK (all agent demos)
- **mcp[cli]** — Core MCP SDK
- **fastmcp / mcp.server.fastmcp** — MCP server implementation
- **fastapi / uvicorn** — HTTP layer for deployment demo
- **ANTHROPIC_API_KEY** — Required for all agent demos

## Running Any Demo

```bash
# UV handles dependencies automatically
uv run demos/<demo-folder>/<script>.py

# Test MCP servers interactively
mcp dev demos/<demo-folder>/<server>.py
```
