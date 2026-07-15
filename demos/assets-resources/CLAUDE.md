# CLAUDE.md — assets-resources

This folder contains reference materials, diagrams, and cheatsheets for the O'Reilly MCP course.

## Course Structure (July 2026 redesign — 7 modules)

```
demos/
├── 00-intro-agents/                # Agents are loops — hand-rolled, bare Claude API
├── 01-introduction-to-mcp/         # First MCP server + thin client + real hosts
├── 02-research-agent-sdk/          # Claude Agent SDK as MCP host (+ in-process servers)
├── 03-skills-and-mcp/              # Skills vs MCP + mcp-builder skill
├── 04-production-research-agent/   # HTTP transport, auth seam, hooks, evals
├── 05-deploy-remote-mcp/           # Deploy remote server (Vercel) + MCP Apps
├── 06-security-and-composition/    # Tool-poisoning lab; multi-server, subagents, sessions
├── exercises/                      # Take-home exercises (link checker)
├── archive/                        # Retired demos, kept for reference
└── assets-resources/               # This folder — reference materials
```

## Key Dependencies

- **claude-agent-sdk** — Claude Agent SDK (all agent demos)
- **mcp[cli]>=1.12,<2** — official MCP Python SDK, pinned to v1 (v2 renames FastMCP → MCPServer)
- **ANTHROPIC_API_KEY** — required for all agent demos

## Running Any Demo

```bash
# UV handles dependencies automatically
uv run demos/<demo-folder>/<script>.py

# Test MCP servers interactively
mcp dev demos/<demo-folder>/<server>.py
```
