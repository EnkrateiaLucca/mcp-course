# MCP resources quick demo

Chat agent where `@name` attaches an MCP **resource** to your message.

```bash
uv run chat.py        # needs ANTHROPIC_API_KEY
mcp dev server.py     # inspect resources + tools
```

```
you > compare @mcp-primitives with @resources-vs-tools, then save_note a summary
```

Type `@` + TAB to complete resources, `/` + TAB to list prompts (`/summarize <name>`, `/compare <a> <b>`). The host discovers the `source://{name}` template via `resources/templates/list`,
completes `@` via `completion/complete`, reads each mention via `resources/read`, and prepends the content as
`<source>` blocks before the Agent SDK sees the message.

| | Who decides | Wire call |
|---|---|---|
| Resource (`@name`) | the user / host | `resources/read` |
| Prompt (`/compare a b`) | the user | `prompts/get` |
| Tool (`search_sources`, `save_note`) | the model | `tools/call` |

Drop any `.md` into `sources/` and it is immediately available as `@<stem>` via the `source://{name}` template.
