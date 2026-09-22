# Claude Agent SDK: Top 3 Use Cases

The Claude Agent SDK exposes the same agent loop, tools (file read/edit, shell, web), context management, hooks, and subagent orchestration that power Claude Code, programmable in Python and TypeScript. Anthropic frames it as "giving Claude a computer": the agent works in a real environment with files, scripts, and MCP-connected apps.

## 1. Autonomous coding agents

- The SDK's origin. Claude Code itself runs on it, and coding remains the most mature agent category.
- Typical flow: take a ticket ("add rate limiting to our API"), read the codebase, plan multi-file changes, write code, run tests, fix failures, open a PR.
- Built-in tools cover the full loop out of the box: file system, terminal, search, git. No custom tool scaffolding needed for the common path.
- Fits CI pipelines, code review bots, migration/refactor jobs, and asynchronous "assign and walk away" tasks (Claude Code on the Web is the reference deployment).
- Hooks (`PreToolUse` / `PostToolUse`) and permission callbacks let teams gate destructive commands in unattended runs.

## 2. Deep research and knowledge-work agents

- Anthropic explicitly lists "deep research agents" and "personal assistant agents" as first-class targets.
- Pattern: search the web or internal sources, read many documents, synthesize a briefing, and write it to disk or a connected system. The file system serves as working memory across long tasks.
- Anthropic's own `claude-agent-sdk-demos` repo ships an IMAP email agent that displays the inbox, runs agentic search over mail, and turns research findings into executive-ready briefings.
- Subagents run in parallel to fan out across sources, then a lead agent consolidates results. Sessions can be resumed or forked for follow-up questions.
- MCP servers plug in domain data (Notion, Drive, databases) without custom integration code.

## 3. Vertical business operations agents (finance, support, back office)

- Anthropic names finance agents and customer support agents alongside coding and research as core SDK use cases.
- Flagship production example: OffDeal, an AI-native investment bank, consolidated nearly all AI workloads into "Archie," one general-purpose agent built on the SDK. Archie connects to 20+ data sources and works every phase of an M&A deal: sourcing sellers, finding buyers, drafting investment memoranda, running diligence. OffDeal reports eval accuracy rising from 25% to 85% and $91M in deals closed with a four-banker team.
- The pattern generalizes: one agent, many MCP-connected systems, evals to measure task correctness, hooks for audit logging and compliance gates.
- Anthropic's platform docs publish production guides for adjacent workloads: ticket routing, customer support, content moderation, legal summarization, commerce agents.

## Why the SDK over a raw API loop

- Agent loop, context compaction, tool execution, and permissions come pre-built and battle-tested in Claude Code.
- MCP host support means tools are portable across agents and clients.
- Skills, subagents, sessions, and hooks give production controls without a framework rewrite.

## Sources

- Anthropic, "Building agents with the Claude Agent SDK" — https://claude.com/blog/building-agents-with-the-claude-agent-sdk
- Claude Code Docs, "Agent SDK overview" — https://code.claude.com/docs/en/agent-sdk/overview
- Claude Code Docs, "Agent SDK examples" — https://code.claude.com/docs/en/agent-sdk/examples
- anthropics/claude-agent-sdk-demos (email agent) — https://github.com/anthropics/claude-agent-sdk-demos
- OffDeal case study — https://claude.com/customers/offdeal
- The Applied, "How OffDeal uses Claude to close $91M in M&A deals" — https://theapplied.co/use-cases/how-offdeal-uses-claude-to-close-91m-in-ma-deals-with-a-team-of-four-bankers
- Claude Platform Docs, "Guides to common use cases" — https://platform.claude.com/docs/en/about-claude/use-case-guides/overview
- Anthropic, "Building Effective AI Agents" — https://www.anthropic.com/engineering/building-effective-agents
- Greendata, "Claude Code on the Web: asynchronous coding agents" — https://greendata.io/insights/claude-code-web-asynchronous-agents
- Jaro Education, "Agentic AI examples and use cases in 2026" — https://www.jaroeducation.com/blog/agentic-ai-examples-and-use-cases
