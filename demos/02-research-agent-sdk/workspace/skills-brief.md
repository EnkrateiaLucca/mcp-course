# Agent Skills in the Claude Agent SDK

- Agent Skills are modular capability packs that extend what Claude can do for specific tasks.
- In Claude, a skill is typically a folder centered on a `SKILL.md` file with instructions; it can also include scripts and supporting resources.
- Claude scans available skills and loads only the ones that seem relevant to the current task, so skills are not all injected into context at once.
- When a skill is selected, Claude uses its instructions and resources to follow a specialized workflow and produce more consistent outputs.
- The Claude Agent SDK supports the same Agent Skills mechanism, so custom agents built with the SDK can discover and use skills programmatically.
- This makes skills useful for reusable workflows like file transformations, report generation, or domain-specific procedures.
- In practice, skills help separate general reasoning from task-specific operating procedures and assets.

## Sources

- https://claude.com/blog/skills
- https://docs.anthropic.com/en/docs/claude-code/skills
- https://docs.anthropic.com/en/docs/claude-code/sdk
