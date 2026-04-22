# Link Health Audit Report
**Date:** 2026-04-22
**Course:** Building AI Agents with MCP: The HTTP Moment of AI?

---

## Summary

| Metric | Count |
|---|---|
| Directories scanned | 2 (`demos/`, `presentation/`) |
| Markdown files discovered | 26 total (21 content files scanned, 5 `.venv` license files skipped) |
| Files with zero URLs | 12 |
| Total unique URLs checked | 49 |
| ✅ Working (2xx) | 41 |
| ❌ Broken (4xx / connection error) | 8 |
| ⏭️ Skipped (localhost) | 1 |

> **Note:** The `presentation/` directory contained no markdown files.

---

## ❌ Broken Links

### 🔴 Real Broken Links (Action Required)

| URL | Status | Found In |
|---|---|---|
| `https://github.com/modelcontextprotocol/mcp` | 404 Not Found | `demos/assets-resources/MCP_TECHNICAL_CHEATSHEET.md` |
| `https://modelcontextprotocol.io/about` | 404 Not Found | `demos/assets-resources/modelcontextprotocol.io_docs.md` |
| `https://spec.modelcontextprotocol.io/` | SSL Connection Error (EOF) | `demos/04-query-tabular-data/README.md` |

**Recommended fixes:**
- `github.com/modelcontextprotocol/mcp` → replace with `https://github.com/modelcontextprotocol/servers` (alive, 200 OK) or the org root `https://github.com/modelcontextprotocol`
- `modelcontextprotocol.io/about` → no direct replacement found; consider removing or linking to `https://modelcontextprotocol.io/docs/getting-started/intro`
- `spec.modelcontextprotocol.io/` → replace with `https://modelcontextprotocol.io/specification` (alive, 200 OK)

---

### 🟡 Placeholder URLs (Template Code — Not Real Links)

These are RFC 2606 reserved or example domains used in code samples. They are expected to fail but should be noted as they may confuse learners.

| URL | Status | Found In | Notes |
|---|---|---|---|
| `https://example.com/mcp` | 404 Not Found | `demos/07-hacks-tips-tools-workflows/mcp-builder-skill/reference/evaluation.md` | Placeholder |
| `https://example.com/resource` | 404 Not Found | `demos/assets-resources/MCP_TECHNICAL_CHEATSHEET.md` | Placeholder (also has trailing backtick bug) |
| `https://api.example.com/v1` | DNS Failure | `demos/07-hacks-tips-tools-workflows/mcp-builder-skill/reference/node_mcp_server.md`, `reference/python_mcp_server.md` | Placeholder |
| `https://api.example.com/oauth/authorize` | DNS Failure | `demos/assets-resources/MCP_TECHNICAL_CHEATSHEET.md` | Placeholder |
| `https://api.example.com/oauth/token` | DNS Failure | `demos/assets-resources/MCP_TECHNICAL_CHEATSHEET.md` | Placeholder |

---

## ⚠️ Malformed URLs (Trailing Backtick Bug)

The following URLs have a trailing backtick character (`` ` ``) appended, which is a markdown formatting error. The underlying URLs resolve correctly after stripping the backtick — but in rendered markdown these links may break.

| Malformed URL (as written in file) | File |
|---|---|
| `https://modelcontextprotocol.io/llms-full.txt`` ` | `demos/07-hacks-tips-tools-workflows/mcp-builder-skill/SKILL.md` |
| `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md`` ` | `SKILL.md`, `reference/python_mcp_server.md` |
| `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md`` ` | `demos/07-hacks-tips-tools-workflows/mcp-builder-skill/SKILL.md` |
| `https://example.com/resource`` ` | `demos/assets-resources/MCP_TECHNICAL_CHEATSHEET.md` |

**Fix:** Remove the trailing backtick from each URL so it does not get included as part of the hyperlink.

---

## ⏭️ Skipped URLs

| URL | Reason |
|---|---|
| `http://localhost:3000` | Local development URL — expected to be unreachable outside the dev environment. Found in `demos/06-deploy-simple-agent-mcp-vercel/README.md` |

---

## ✅ Working Links (41)

<details>
<summary>Click to expand full list</summary>

| URL | Status |
|---|---|
| `https://github.com/anthropics/claude-agent-sdk-python` | 200 OK |
| `https://github.com/anthropics/claude-agent-sdk-python/tree/main/examples` | 200 OK |
| `https://modelcontextprotocol.io/docs/concepts/architecture` | 200 OK |
| `https://modelcontextprotocol.io/introduction` | 200 OK |
| `https://llmstxt.org/` | 200 OK |
| `https://modelcontextprotocol.io/tutorials/building-mcp-with-llms` | 200 OK |
| `https://modelcontextprotocol.io/llms-full.txt` | 200 OK |
| `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md` | 200 OK |
| `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md` | 200 OK |
| `https://vercel.com/docs/vercel-sandbox` | 200 OK |
| `https://docs.anthropic.com/` | 200 OK |
| `https://github.com/astral-sh/uv` | 200 OK |
| `https://github.com/modelcontextprotocol/python-sdk` | 200 OK |
| `https://pandas.pydata.org/` | 200 OK |
| `https://platform.claude.com/docs/en/agent-sdk/overview` | 200 OK |
| `https://github.com/modelcontextprotocol/servers` | 200 OK |
| `https://modelcontextprotocol.io/docs/learn/architecture` | 200 OK |
| `https://modelcontextprotocol.io/specification` | 200 OK |
| `https://modelcontextprotocol.io/specification/2025-06-18/basic/security_best_practices` | 200 OK |
| `https://blog.modelcontextprotocol.io` | 200 OK |
| `https://github.com/modelcontextprotocol` | 200 OK |
| `https://mintcdn.com/mcp/4ZXF1PrDkEaJvXpn/images/mcp-simple-diagram.png` (×2 variants) | 200 OK |
| `https://mintcdn.com/mcp/4ZXF1PrDkEaJvXpn/logo/dark.svg` | 200 OK |
| `https://mintcdn.com/mcp/4ZXF1PrDkEaJvXpn/logo/light.svg` | 200 OK |
| `https://modelcontextprotocol.io/community/communication` | 200 OK |
| `https://modelcontextprotocol.io/docs/develop/build-client` | 200 OK |
| `https://modelcontextprotocol.io/docs/develop/build-server` | 200 OK |
| `https://modelcontextprotocol.io/docs/develop/connect-local-servers` | 200 OK |
| `https://modelcontextprotocol.io/docs/develop/connect-remote-servers` | 200 OK |
| `https://modelcontextprotocol.io/docs/getting-started/intro` | 200 OK |
| `https://modelcontextprotocol.io/docs/getting-started/intro#learn-more` | 200 OK |
| `https://modelcontextprotocol.io/docs/getting-started/intro#start-building` | 200 OK |
| `https://modelcontextprotocol.io/docs/getting-started/intro#what-can-mcp-enable%3F` | 200 OK |
| `https://modelcontextprotocol.io/docs/getting-started/intro#why-does-mcp-matter%3F` | 200 OK |
| `https://modelcontextprotocol.io/docs/learn/client-concepts` | 200 OK |
| `https://modelcontextprotocol.io/docs/learn/server-concepts` | 200 OK |
| `https://modelcontextprotocol.io/docs/sdk` | 200 OK |
| `https://modelcontextprotocol.io/legacy/tools/inspector` | 200 OK |
| `https://modelcontextprotocol.io/specification/2025-06-18` | 200 OK |
| `https://modelcontextprotocol.io/specification/versioning` | 200 OK |

</details>

---

## Recommendations

1. **Fix 3 real broken links** immediately — especially `spec.modelcontextprotocol.io` in `demos/04-query-tabular-data/README.md`, which is a student-facing file.
2. **Fix 4 malformed URLs** with trailing backticks in `SKILL.md` and `python_mcp_server.md` / `MCP_TECHNICAL_CHEATSHEET.md`.
3. **Annotate placeholder URLs** (example.com, api.example.com) with a comment like `# Replace with your actual API endpoint` so learners are not confused.
4. The overall link health is **good** — 84% of real (non-placeholder) links are working.
