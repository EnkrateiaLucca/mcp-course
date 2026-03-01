# Test Report - MCP Course Repository

**Date:** 2026-03-01
**Tested by:** Automated test suite (syntax validation, import checks, runtime execution)

---

## Summary

**3 bugs found across 3 files.** Everything else passes.

---

## Bugs Found

### 1. Demo 01 — `mcp_client.py` line 139: `read` command crashes

**File:** `demos/01-introduction-to-mcp/mcp_client.py:139`
**Severity:** Medium (breaks the `read` interactive command; `time`, `add`, and tool listing all work fine)

The `read_resource()` method (lines 85-91) unwraps the MCP response and returns a plain `str`. But line 139 treats it as a raw MCP response object:

```python
# Current (broken):
result = await self.read_resource('docs://documents.txt')
print(f"Document content:\n{result.contents[0].text if result.contents else 'No content'}")
```

**Error:** `AttributeError: 'str' object has no attribute 'contents'`

**Fix:** `print(f"Document content:\n{result}")`

---

### 2. Demo 03 — `example_error_handling.py` line 135: `e.output` doesn't exist

**File:** `demos/03-claude-agents-sdk-filesystem-agent/examples/example_error_handling.py:135`
**Severity:** Low (only triggers in an error-handling demo path)

`ProcessError` has `exit_code` and `stderr` attributes, but **not** `output`:

```python
# Current (broken):
print(f"   Output: {e.output}")
```

**Error:** `AttributeError: 'ProcessError' object has no attribute 'output'`

**Fix:** Change `e.output` to `e.stderr`

---

### 3. Demo 06 — `mcp_fetch_server.py`: `version` kwarg crashes FastMCP

**File:** `demos/06-deploy-simple-agent-mcp-vercel/mcp_fetch_server.py:13-16`
**Severity:** High (MCP fetch server won't start at all)

```python
# Current (broken):
mcp = FastMCP(
    name="mcp-fetch-server",
    version="2.0.0"  # <-- not a valid FastMCP parameter
)
```

**Error:** `TypeError: FastMCP.__init__() got an unexpected keyword argument 'version'`

**Fix:** Remove `version="2.0.0"`

---

## Full Test Matrix

| Demo | Syntax | Imports | Server Starts | End-to-End | Verdict |
|------|--------|---------|---------------|------------|---------|
| 00 - Intro Agents Notebook | PASS | PASS | N/A | PASS (all 14 cells) | **PASS** |
| 01 - MCP Server + Client | PASS | PASS | PASS | `read` cmd fails | **BUG** |
| 02 - Chat App | PASS | PASS | PASS | Starts correctly | **PASS** |
| 03 - Claude SDK Examples | PASS | PASS | N/A | error_handling.py:135 | **BUG** |
| 04 - CSV Query | PASS | PASS | PASS | SDK blocked* | **PASS** |
| 05 - Automations Agent | PASS | PASS | PASS | SDK blocked* | **PASS** |
| 06 - Vercel Deployment | PASS | PASS | mcp_fetch_server crashes | main.py works | **BUG** |
| Assets Notebook (OpenAI) | PASS | PASS | N/A | PASS (all 5 queries) | **PASS** |
| Live Example | PASS | PASS | N/A | SDK blocked* | **PASS** |

*Claude Agent SDK demos cannot be end-to-end tested from within a Claude Code session (nested session restriction). Syntax, imports, and all non-SDK components verified independently.
