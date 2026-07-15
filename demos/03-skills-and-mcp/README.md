# Demo 03 — Skills vs MCP (and agents that build MCP servers)

The question every 2026 audience asks: *"Do Agent Skills replace MCP?"*

**No — they're different layers of the same stack:**

| | MCP | Agent Skills |
|---|---|---|
| What it provides | **Access** — connections to external systems (tools, resources, auth, transport) | **Know-how** — procedural knowledge: instructions, scripts, references |
| Shape | A server process speaking JSON-RPC | A folder with a `SKILL.md` |
| Loaded | Tool schemas at connect time (or deferred via tool search) | Progressively: ~100-token metadata → body when triggered → bundled files only when used |
| Standard | modelcontextprotocol.io (Linux Foundation / AAIF) | agentskills.io (open standard, adopted by Gemini CLI, Codex, Copilot, Cursor, Goose…) |

Anthropic's one-liner: *skills complement MCP servers by teaching agents
more complex workflows* — and **plugins bundle both**. A skill often *uses*
MCP tools; an MCP server is often *built by* a skill. Which is exactly
what we do next.

## The demo: an agent that builds MCP servers

`mcp-builder-skill/` is a production-grade skill (tool design guidance,
FastMCP/TypeScript references, an eval harness) that teaches an agent how
to scaffold high-quality MCP servers. This mirrors the *official* workflow:
the MCP docs now recommend building servers with Anthropic's
`mcp-server-dev` plugin skills ([Build with Agent Skills](https://modelcontextprotocol.io/docs/develop/build-with-agent-skills)).

Two ways to run it:

**Via Claude Code** (fastest live demo):

```bash
cd demos/03-skills-and-mcp
mkdir -p .claude/skills && cp -r mcp-builder-skill .claude/skills/mcp-builder
claude   # then: "Use the mcp-builder skill to scaffold an MCP server for <your API>"
```

**Via the Agent SDK** — `skill_loader_demo.py`, which also documents the
gotchas that bite everyone:

- `setting_sources` must include `"project"` (and/or `"user"`) or
  `skills="all"` loads **nothing** (the default is `[]`).
- The `allowed-tools` frontmatter in SKILL.md is read by Claude Code only —
  the SDK ignores it; gate tools with the SDK's `allowed_tools` option.
- `cwd` decides which folder counts as "project" for discovery.

```bash
export ANTHROPIC_API_KEY=sk-...
uv run skill_loader_demo.py
```

## Also in this folder

- `hacks_tips.md` — ecosystem quick hits shown live (context7, gitingest,
  llms.txt, deepwiki).

## Takeaway for the day

You now have all four extension mechanisms in your head: **MCP servers**
(access), **skills** (know-how), **subagents** (delegation — demo 06),
**hooks** (control — demo 04). Plugins are the packaging format that ships
them together.
