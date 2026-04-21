# Plan: Replace Demo 05 — Link Health Checker Agent

## Context

Demo 05 currently demos an agent that writes and runs Python automation scripts — too meta ("automation to build automation"). Replace with a practical demo that showcases MCP server + agentic loop using real, existing data from the course repo itself.

**Chosen use case: Link Health Checker Agent**
- Data = the course repo's own markdown files (already exist, no fake files)
- Agentic loop is clearly visible: discover files → extract links → check each URL → write report
- Output is a concrete audit report with broken/working links
- Orthogonal to all existing demos
- Zero new dependencies (stdlib `urllib`, `re` + mcp + claude-agent-sdk)

---

## Files

| File | Action |
|------|--------|
| `automation_agent.py` → `link_checker_agent.py` | Rename + update |
| `automation_mcp_server.py` → `link_checker_mcp_server.py` | Rename + replace tools |
| `reports/` | New — auto-created, agent writes audit reports here |
| `README.md` | Update — single file, serves as walkthrough |
| `WALKTHROUGH.md` | Delete |
| `generated_scripts/` | Delete |

---

## MCP Server: `link_checker_mcp_server.py`

4 tools, all stdlib (`urllib`, `re`, `os`):

```python
REPORTS_DIR = .../reports/   # auto-created

list_markdown_files(directory: str)
# → newline list of .md file paths found recursively under directory

extract_links(filepath: str)
# → newline list of unique URLs found in the markdown file
# uses re to find [text](url) and bare https:// links

check_url(url: str) -> str
# → "200 OK (312ms)" or "404 Not Found" or "Connection error: ..."
# uses urllib.request.urlopen with HEAD request, 10s timeout
# catches HTTPError, URLError, timeout

write_report(filename: str, content: str) -> str
# → writes to reports/ directory, returns absolute path
# validates: no path separators, must end in .txt or .md
```

---

## Agent: `link_checker_agent.py`

**Keep verbatim from current file:**
- ANSI color constants
- `format_tool_result` (15-line truncation)
- `ClaudeAgentOptions` structure
- `async for message in query(...)` loop
- `ResultMessage` cost/turns footer
- UV inline script metadata header

**TOOL_LABELS:**
```python
TOOL_LABELS = {
    "list_markdown_files": ("Scanning for markdown", CYAN),
    "extract_links":       ("Extracting links",      CYAN),
    "check_url":           ("Checking URL",           YELLOW),
    "write_report":        ("Writing report",         GREEN),
}
```

**`format_tool_call` detail extraction:**
```python
detail = ""
if isinstance(block.input, dict):
    if "filepath" in block.input:
        detail = f" [{os.path.basename(block.input['filepath'])}]"
    if "url" in block.input:
        u = block.input["url"]
        detail = f" [{u[:60]}{'...' if len(u) > 60 else ''}]"
    if "filename" in block.input:
        detail = f" [{block.input['filename']}]"
```

**System prompt:**
```
You are a link health checker assistant. You help developers find broken links
in their markdown documentation by checking each URL and producing an audit report.

Your workflow:
1. list_markdown_files — discover all .md files in the given directory
2. extract_links — get all URLs from each file
3. check_url — check each unique URL (deduplicate before checking)
4. write_report — always write a structured report at the end

Your report should include:
- Total links checked
- Broken links (4xx, 5xx, connection errors) with the file they came from
- Redirects worth noting (3xx)
- Working links count
- Recommendation if many links are broken

Name report files descriptively: link_audit_demos_2026-04-20.txt
You MUST always write a report file — do not just describe findings in chat.
Deduplicate URLs before checking — the same URL may appear in multiple files.
```

**Banner + example prompts:**
```
┌────────────────────────────────────────────────┐
│   Link Health Checker — Audit Markdown Links   │
│   Powered by Claude Agent SDK + MCP            │
└────────────────────────────────────────────────┘

  Reports directory: demos/05-link-checker/reports/

  Try:
    "Check all links in the demos/ folder"
    "Find broken links in the presentation/"
    "Audit README.md for dead links"

  Type quit to exit
```

---

## Example Classroom Interaction

```
You: Check all links in the demos/ folder

  [Scanning for markdown [demos/]]
  | demos/01-introduction-to-mcp/README.md
  | demos/02-study-case.../README.md
  | ... (8 files)

  [Extracting links [README.md]]
  | https://modelcontextprotocol.io/specification/
  | https://github.com/modelcontextprotocol/python-sdk

  [Checking URL [https://modelcontextprotocol.io/specification/]]
  | 200 OK (412ms)

  [Checking URL [https://old-sdk-link.example.com]]
  | 404 Not Found

  [Writing report [link_audit_demos_2026-04-20.txt]]
  | Wrote: /path/to/reports/link_audit_demos_2026-04-20.txt

Found 23 links across 8 files. 1 broken, 2 redirecting.
Report written to reports/link_audit_demos_2026-04-20.txt

  (9 turns, $0.0028)
```

---

## README.md (walkthrough inline)

Single file covering:
1. What the demo does
2. Quick start (`uv run link_checker_agent.py`)
3. How to test the MCP server independently (`mcp dev link_checker_mcp_server.py`)
4. What to try (3 example prompts)
5. How it works: agent uses 4 MCP tools to compose the full loop

---

## Verification

1. `uv run link_checker_agent.py` — starts without error
2. Prompt: `"Check all links in the demos/ folder"` — agent completes full loop, writes report file
3. Report exists at `reports/link_audit_*.txt` with broken/working summary
4. `mcp dev link_checker_mcp_server.py` — all 4 tools visible and callable
5. Prompt: `"How many markdown files are in demos/"` — agent uses only `list_markdown_files`, no write (tests partial loop)
