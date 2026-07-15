# Agent Skills + MCP in the Claude Agent SDK: Production Patterns

## What each layer does
- **MCP** = connectivity layer: standardized *how* an agent reaches external tools/data (servers, transports, auth).
- **Agent Skills** = capability layer: portable folders (SKILL.md + scripts/resources) defining *what* the agent knows how to do; discovered and loaded on demand (progressive disclosure — only name/description in context until invoked).
- They're complementary, not competing: skills steer workflows and procedures; MCP executes against live systems. Data shows MCP-only agents often ignore available tools without a skill to steer them.

## Skills in the Agent SDK
- Setting `skills` auto-adds the `Skill` tool to `allowedTools`; if you pass an explicit tools list, include `"Skill"` yourself.
- Filesystem-based skills require `setting_sources=["user","project"]` (SDK doesn't load settings by default); SKILL.md `allowed-tools` frontmatter is CLI-only — gate via SDK permissions instead.
- Skills are versionable, portable across Claude Code / API / claude.ai, and now an open standard (agentskills spec).

## MCP in the SDK (host patterns)
- SDK is a full MCP host: external servers (stdio / streamable HTTP + bearer/OAuth) or in-process via `create_sdk_mcp_server` (no subprocess, shared state).
- MCP tools are NOT auto-approved by permission modes — gate explicitly with `allowed_tools=["mcp__<server>__*"]`.
- Tool Search is on by default: MCP tool definitions are deferred/loaded on demand, avoiding context saturation from large tool sets.

## Production checklist (Anthropic guidance)
- **Tool design**: intent-grouped, workflow-shaped tools over 1:1 API mirrors; fewer, richer tools; descriptive docstrings (the LLM reads them); structured returns; build evals to measure tool quality.
- **Context efficiency**: code execution with MCP (agent writes code calling tools) cuts context overhead up to ~98.7%; tool search + skills' progressive disclosure attack the same token-saturation problem.
- **Security/defense in depth**: hooks (`PreToolUse` block, `PostToolUse` log) + `can_use_tool` permission callback; workspace/path sandboxing; least-privilege allowlists; OAuth/CIMD + secret vaults for remote servers.
- **Remote deployment**: stateless HTTP (`stateless_http=True`, `json_response=True`), pre-flight protocol tests, auth seam from day one.
- **Observability/eval**: OpenTelemetry tracing, layered eval datasets (protocol → tool → end-to-end correctness) before scaling.
- **Architecture rule of thumb**: skills for repeatable domain workflows; MCP for live external systems; direct API/CLI calls when a protocol layer adds no value; subagents for parallel/isolated context.

## Sources
- https://code.claude.com/docs/en/agent-sdk/skills
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- https://claude.com/blog/building-agents-that-reach-production-systems-with-mcp
- https://claude.com/blog/skills-explained
- https://www.anthropic.com/engineering/code-execution-with-mcp
- https://www.anthropic.com/engineering/writing-tools-for-agents
- https://aaif.io/blog/closing-the-context-gap-why-mcp-skills-works/
- https://www.damiangalarza.com/posts/2026-02-05-mcps-vs-agent-skills/
- https://inference.net/content/claude-agent-sdk-production-guide/
- https://ravichaganti.com/blog/agent-skills-vs-model-context-protocol-how-do-you-choose/
