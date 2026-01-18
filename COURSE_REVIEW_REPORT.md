# MCP Course Code Review Report

**Review Date:** January 2026
**Reviewer:** Claude (Automated Code Review)

---

## Executive Summary

This report covers a comprehensive code review of the MCP (Model Context Protocol) course materials. Overall, the course is well-structured and provides excellent hands-on examples. However, I identified several bugs, typos, security considerations, and areas for improvement that should be addressed before teaching.

---

## Critical Issues (Must Fix)

### 1. Bug: Incorrect Method Call in `mcp_client.py` (Demo 01)

**File:** `demos/01-introduction-to-mcp/mcp_client.py:86`

```python
# BUG: Extra parentheses - self.session() calls session as a method
result = await self.session().read_resource(AnyUrl(uri))
```

**Should be:**
```python
result = await self.session.read_resource(AnyUrl(uri))
```

The `self.session` is a `ClientSession` object, not a method. The extra parentheses cause a TypeError.

---

### 2. Bug: Non-existent Model Names

Multiple files reference `"gpt-5-mini"` which does not exist. Should be `"gpt-4o-mini"`:

| File | Line |
|------|------|
| `demos/02-study-case.../chat_app.py` | 245 |
| `demos/03-openai-agents/openai_agent_filesystem_mcp.py` | 20 |
| `demos/03-openai-agents/intro-openai-agents-sdk.ipynb` | cell-1, cell-3 |
| `demos/04-query-tabular-data/openai_mcp_csv_demo.ipynb` | cell-7, cell-9 |

**Note:** Demo 06 correctly uses `"gpt-4o-mini"` and the complex query example in Demo 04 notebook (cell-21) correctly uses `"gpt-4o-mini"`.

---

### 3. Bug: Inconsistent Model in Same File

**File:** `demos/02-study-case.../chat_app.py`

- Line 245: Uses `"gpt-5-mini"` (invalid)
- Line 277: Uses `"gpt-4-turbo-preview"` (valid but different)

This inconsistency will cause confusion and potential runtime errors.

---

### 4. Missing Data File: `sample_data.csv`

**File:** `demos/04-query-tabular-data/csv_query_mcp_server.py`

The server references `sample_data.csv` but this file does not exist in the repository. The notebook shows what the data should look like, but the actual CSV file is missing.

**Action:** Create `demos/04-query-tabular-data/sample_data.csv` with the expected data.

---

### 5. Bug: `read_resource` Return Value Mismatch

**File:** `demos/01-introduction-to-mcp/mcp_client.py`

The `read_resource` method (lines 85-91) extracts and returns text:
```python
async def read_resource(self, uri: str) -> Any:
    result = await self.session().read_resource(AnyUrl(uri))
    resource = result.contents[0]
    if isinstance(resource, types.TextResourceContents):
        if resource.mimeType == "text/plain":
            return resource.text  # Returns string
```

But `interactive_mode` (line 139) tries to access `.contents[0].text`:
```python
result = await self.read_resource('docs://documents.txt')
print(f"Document content:\n{result.contents[0].text if result.contents else 'No content'}")
```

The returned value is already the text string, not an object with `.contents`.

---

## Medium Priority Issues

### 6. Duplicate Shebang Line

**File:** `demos/02-study-case.../chat_app.py`

```python
#!/usr/bin/env -S uv run --script  # Line 1
...
#!/usr/bin/env python3              # Line 12 (duplicate!)
```

Remove line 12.

---

### 7. Typos in Comments/Docstrings

| File | Line | Issue |
|------|------|-------|
| `demos/01-introduction-to-mcp/mcp_client.py` | 93 | "SImulation" should be "Simulation" |
| `demos/03-openai-agents/mcp_server_for_openai_agent.py` | 11 | "SImple" should be "Simple" |

---

### 8. Help Text Mismatch

**File:** `demos/01-introduction-to-mcp/mcp_client.py:109`

Help says:
```
write F C     - Write to file C content F
```

But the actual command format (line 126-127) is:
```python
parts = command.split(maxsplit=2)  # write <filename> <content>
filename = parts[1]
content = parts[2]
```

**Correct help text should be:**
```
write F C     - Write content C to file F
```

---

### 9. Unused Import

**File:** `demos/03-openai-agents/mcp_server_for_openai_agent.py:23`

```python
from typing import List  # Never used in the file
```

---

### 10. Resource URI Pattern Issue

**File:** `demos/02-study-case.../mcp_server.py:28`

```python
@mcp.resource(f"docs://documents/{DOCS_PATH}", mime_type="text/plain")
```

This creates URI: `docs://documents/./docs` which is unusual. Consider:
```python
@mcp.resource("docs://documents/list", mime_type="text/plain")
```

---

### 11. Deprecated FastAPI Event Handlers

**File:** `demos/05-deployment-example/main.py:332-346`

```python
@app.on_event("startup")  # Deprecated
@app.on_event("shutdown")  # Deprecated
```

FastAPI recommends using `lifespan` context manager instead:
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    yield
    # Shutdown code

app = FastAPI(lifespan=lifespan)
```

---

### 12. Missing Dependency: `beautifulsoup4`

**File:** `demos/06-deploy-simple-agent-mcp-vercel/mcp_fetch_server.py`

Uses `from bs4 import BeautifulSoup` but `beautifulsoup4` is not in `requirements/requirements.txt`.

---

## Security Considerations (Educational Notes)

These aren't bugs per se, but worth mentioning to students:

### 13. Path Traversal Risk in File Tools

**Files:**
- `demos/01-introduction-to-mcp/mcp_server.py` - `write_file()`
- `demos/02-study-case.../mcp_server.py` - `read_doc()`, `write_file()`
- `demos/03-openai-agents/mcp_server_for_openai_agent.py` - `write_file()`, `read_file()`

None of these validate file paths. A malicious prompt could potentially:
- Write to sensitive locations: `write_file("/etc/passwd", "...")`
- Read sensitive files: `read_doc("../../.env")`

**Recommendation:** Add this as a teaching moment about input validation:
```python
import os

def safe_path(filepath: str, allowed_dir: str = "./docs") -> str:
    abs_path = os.path.abspath(filepath)
    allowed_abs = os.path.abspath(allowed_dir)
    if not abs_path.startswith(allowed_abs):
        raise ValueError(f"Access denied: {filepath}")
    return abs_path
```

---

### 14. CORS Wildcard in Production Example

**File:** `demos/05-deployment-example/main.py:47`

```python
allow_origins=["*"],  # In production, specify your frontend domain
```

The comment is good, but consider adding a stronger warning or using an environment variable pattern.

---

## Minor Improvements

### 15. Test File Reference Doesn't Exist

**File:** `demos/02-study-case.../mcp_client.py:75`

```python
result = await client.call_tool("read_doc", {"filepath": "./file.txt"})
```

The file `./file.txt` doesn't exist. Should reference an actual file in `./docs/`.

---

### 16. Inconsistent Return Types

**File:** `demos/03-openai-agents/mcp_server_for_openai_agent.py:53`

```python
@mcp.tool()
def list_files(dir_path: str) -> str:  # Type hint says str
    return os.listdir(dir_path)         # Returns list[str]
```

---

### 17. Print Statement in MCP Server

**File:** `demos/04-query-tabular-data/csv_query_mcp_server.py:180`

```python
print("Starting CSV Query MCP Server...")
```

When running as a subprocess via stdio, print statements can interfere with the MCP protocol. Use logging or stderr instead:
```python
import sys
print("Starting CSV Query MCP Server...", file=sys.stderr)
```

---

## Summary Checklist

### Must Fix Before Teaching
- [ ] Fix `self.session()` bug in Demo 01 mcp_client.py (line 86)
- [ ] Replace all `gpt-5-mini` with `gpt-4o-mini`
- [ ] Create missing `sample_data.csv` file for Demo 04
- [ ] Fix `read_resource` return handling in Demo 01 (line 139)

### Should Fix
- [ ] Remove duplicate shebang in Demo 02 chat_app.py
- [ ] Fix typos (SImulation, SImple)
- [ ] Correct help text in Demo 01 mcp_client.py
- [ ] Remove unused `List` import in Demo 03
- [ ] Add `beautifulsoup4` to requirements

### Good Teaching Opportunities
- [ ] Discuss path validation/security when covering file tools
- [ ] Mention CORS configuration for production
- [ ] Explain deprecated vs. modern FastAPI patterns

---

## Files Reviewed

| Demo | Files |
|------|-------|
| 00 | intro-agents.ipynb |
| 01 | mcp_server.py, mcp_client.py |
| 02 | chat_app.py, mcp_server.py, mcp_client.py |
| 03 | openai_agent_filesystem_mcp.py, mcp_server_for_openai_agent.py, intro-openai-agents-sdk.ipynb |
| 04 | csv_query_mcp_server.py, openai_mcp_csv_demo.ipynb |
| 05 | mcp_server.py, main.py |
| 06 | main.py, mcp_fetch_server.py |
| Other | requirements/requirements.txt |

---

*Good luck with the course!*
