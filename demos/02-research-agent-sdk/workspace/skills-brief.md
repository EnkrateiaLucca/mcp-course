# Agent Skills in the Claude Agent SDK — Brief

## What Agent Skills Are
- Modular, packaged capabilities that extend Claude with domain-specific instructions, scripts, and resources.
- Each Skill is a **directory** containing a `SKILL.md` file (plus optional helper files: scripts, templates, reference docs).
- `SKILL.md` has YAML frontmatter (name, description, optional `allowed-tools`) followed by markdown instructions.
- Designed to be portable and shareable across Claude products (Claude Code, Claude apps, API) — the same Skill format works everywhere.

## How They Work in the Claude Agent SDK
- Skills are **filesystem artifacts**: discovered automatically from `.claude/skills/` directories (project, user, or plugin scope).
- Loading is governed by `settingSources` (TypeScript SDK) / `setting_sources` (Python SDK); once filesystem settings are enabled, Skills in those locations are auto-registered.
- The SDK exposes Skills to the model via a built-in `Skill` tool the agent can invoke when a task matches.
- No special API call is needed to "attach" a Skill — presence on disk + matching metadata is enough.
- Skills can ship alongside MCP servers, subagents, and slash commands as part of a plugin.

## Progressive Disclosure (Core Design Principle)
- **Tier 1 — Metadata only (~50 tokens/skill):** at session start the agent sees only each Skill's `name` + `description`. This lets you install hundreds of Skills without blowing the context window.
- **Tier 2 — Full SKILL.md:** when the agent decides a Skill is relevant, it loads the full body of `SKILL.md` (instructions, workflow, examples).
- **Tier 3 — Bundled resources:** the Skill's instructions can then point the agent at additional files in the Skill folder (scripts to execute, templates to fill, longer reference docs to read) on-demand.
- This tiered loading is what Anthropic calls *progressive disclosure*: capability is broad, context cost stays bounded.

## Typical Skill Folder Layout
```
.claude/skills/my-skill/
├── SKILL.md          # frontmatter + instructions (always-loaded once triggered)
├── scripts/          # executable helpers (Bash, Python, etc.)
├── templates/        # files the agent fills in
└── reference/        # deeper docs loaded only if needed
```

## Why It Matters
- Replaces ad-hoc "stuff everything in the system prompt" patterns with composable, versionable units.
- Skills are model-agnostic in spirit but tuned for agentic loops — they assume the model can read files, run code, and choose tools.
- Anthropic is positioning Skills as an open standard (similar to how it released MCP), so the same `SKILL.md` package can travel across agents and vendors.

## Sources
- https://code.claude.com/docs/en/agent-sdk/skills — Agent Skills in the SDK (official Claude Code docs)
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview — Agent Skills overview (Claude API docs)
- https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills — Anthropic launch post
- https://claude.com/blog/building-agents-with-skills-equipping-agents-for-specialized-work — Token economics + progressive disclosure
- https://www.newsletter.swirlai.com/p/agent-skills-progressive-disclosure — Progressive disclosure as system design pattern
- https://www.unite.ai/anthropic-opens-agent-skills-standard-continuing-its-pattern-of-building-industry-infrastructure/ — Skills as an open standard
- https://learn.deeplearning.ai/courses/agent-skills-with-anthropic/information — DeepLearning.AI course on Skills
- https://github.com/StrayDragon/my-claude-skills/blob/main/CLAUDE_CODE_SKILL_TUTORIAL.md — Community tutorial with examples
