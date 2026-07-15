# Link Health Checker Agent

Claude Agent SDK + MCP server that audits markdown files for broken links.

## Quick Start

```bash
uv run link_checker_agent.py
```

## What to Try

```
"Audit all course links"
"Check only the demos folder"
"Find broken links in the presentation"
```

The agent will scan markdown files, extract every URL, check each one with an HTTP request, and write a report to `reports/`.

## How It Works

The **MCP server** (`link_checker_mcp_server.py`) exposes 4 tools:

| Tool | What it does |
|------|-------------|
| `list_markdown_files(directory)` | Recursively finds all `.md` files |
| `extract_links(filepath)` | Pulls unique URLs from a markdown file |
| `check_url(url)` | HEAD request — returns status code + response time |
| `write_report(filename, content)` | Writes the audit report to `reports/` |

The **agent** (`link_checker_agent.py`) uses Claude to compose these tools intelligently: it discovers files, deduplicates URLs across files before checking, and produces a structured report with broken/working/redirect counts.

## Test the MCP Server Independently

```bash
mcp dev link_checker_mcp_server.py
```
