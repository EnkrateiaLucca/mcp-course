# Take-home exercise — Build an automation agent (link checker)

You've seen the pattern four times now: define an MCP server with a few
well-scoped tools, point the Claude Agent SDK at it, constrain the agent
with `allowed_tools`. This exercise makes you do it end-to-end, solo, on a
real automation: **audit markdown files for broken links.**

## The task

Build an agent that, given a directory:

1. discovers markdown files,
2. extracts and dedupes their URLs,
3. checks each URL's health (status + latency),
4. writes a report to `reports/`.

Design your own MCP server for it. Before you peek at the solution, decide:
*how many tools, and which?* (Hint from demo 04: fewer, intent-grouped
tools beat an API mirror — does `check_all_links(directory)` beat four
primitives here? There are defensible answers on both sides; know why.)

## Solution

This folder contains a complete reference implementation
(`link_checker_mcp_server.py` + `link_checker_agent.py`):

```bash
uv run link_checker_agent.py
```

Compare your tool design with the solution's four-primitive split, then
read `demos/04-production-research-agent/README.md` again and decide which
you'd ship.
