# Skills over MCP (SEP-2640)

An MCP server that serves an Agent Skill through the official **Skills
extension** (`io.modelcontextprotocol/skills`), plus two ways to verify it:
the MCP Inspector CLI and a small Python client.

## What SEP-2640 is

Earlier in this module a skill was a folder on your disk. [SEP-2640](https://modelcontextprotocol.io/seps/2640-skills-extension)
lets an MCP server ship skills too, so the know-how travels with the access.

- Every file of a skill is an ordinary MCP resource at `skill://<skill-name>/<file-path>`, read with the standard `resources/read`.
- The server declares the extension in its capabilities and answers two new methods: `skills/list` (the catalog) and `skills/get` (one skill by URI). A third method, `resources/directory/read`, is optional behind a `directoryRead` flag. This demo skips it.
- Each skill entry carries the `SKILL.md` frontmatter verbatim and a manifest of every file with its SHA-256 digest and size.
- The skill format stays with [agentskills.io](https://agentskills.io). The extension only defines the transport.

## Four things to notice

1. **Resources, no new primitive.** Skill files ride on the Resources primitive you already know. A client that ignores the extension sees plain resources. See `list_resources` and `read_resource` in `skills_server.py`.
2. **Per-file digests bind the approval.** A host's approval covers the whole set of `(uri, digest)` pairs. A change to any file, even a reference doc, revokes it. `verify_skills.py --tamper` shows this.
3. **Progressive disclosure is mandatory.** Hosts MUST NOT fetch skill files on connect, on listing, or at approval. `SKILL.md` loads when the skill activates. A supporting file loads when the model reads it. Our verifier reads every file on purpose because checking them is its job. A host must not do that.
4. **Security and identity rules.** Hosts treat MCP-served skills as a higher-risk surface than tool calls. A skill's identity is the pair (server, URI), and its name is only a label. An MCP skill must never silently shadow a local skill with the same name. Hosts ignore `allowed-tools` unless the user approves that grant for that skill, and any code execution the skill asks for needs explicit per-skill approval.

## Which skill, and why no `scripts/`

`skills/mcp-builder/` is this module's mcp-builder skill (Apache-2.0, `LICENSE.txt` included) without its `scripts/` folder.
The working group scoped MCP-served skills to the *instructor* format: markdown the model reads ([decision log, 2026-02-14](https://github.com/modelcontextprotocol/ext-skills/blob/main/docs/decisions.md)).
Helper scripts that run on your machine are out of scope.
`reference/evaluation.md` still tells the agent to run `scripts/evaluation.py`. Over MCP, a host must put that kind of instruction behind explicit user approval.

## Run it

```bash
cd demos/03-skills-and-mcp/skills-over-mcp

# 1. The server (stdio). It waits for a client; Ctrl-C to stop.
uv run skills_server.py

# 2. MCP Inspector CLI (needs 2.6.0+; tested with 2.10.1)
npx -y @modelcontextprotocol/inspector --cli uv run skills_server.py --method skills/list
npx -y @modelcontextprotocol/inspector --cli uv run skills_server.py --method skills/list --verify
npx -y @modelcontextprotocol/inspector --cli uv run skills_server.py \
  --method skills/get --uri skill://mcp-builder/SKILL.md --verify
npx -y @modelcontextprotocol/inspector --cli uv run skills_server.py \
  --method resources/read --uri skill://mcp-builder/reference/python_mcp_server.md

# 3. The Python verifier, then the tamper demo (edits a temp copy only)
uv run verify_skills.py
uv run verify_skills.py --tamper

# 4. The test (from the repo root)
make test
```

The Inspector has no `skill-verify` subcommand. Skill verification is the
`--verify` flag on `--method skills/list` or `--method skills/get`. It checks
conformance, every digest and size, and the served frontmatter against the
listed one. Exit codes: `0` verified, `7` failed, `8` incomplete, `9` for a
`"dynamic"` skill when you pass `--require-digests`.

## Expected output

Inspector `--verify` (one NDJSON report per skill, trimmed here):

```text
{"uri":"skill://mcp-builder/SKILL.md","name":"mcp-builder","conformance":[],"frontmatter":[],
 "files":[{"uri":"skill://mcp-builder/LICENSE.txt","status":"verified", ...}, ...],"ok":true,"outcome":"verified"}
Verified 1 skill and 6 files: no conformance errors.
```

`uv run verify_skills.py`:

```text
server declares io.modelcontextprotocol/skills = {}

(course-skills, skill://mcp-builder/SKILL.md): 6 files in the manifest
  PASS  skill://mcp-builder/LICENSE.txt  (11357 bytes, sha256:58d1e17ffe51...)
  PASS  skill://mcp-builder/SKILL.md  (13552 bytes, sha256:b1010e90adcb...)
  PASS  skill://mcp-builder/reference/evaluation.md  (21663 bytes, sha256:8c99479f8a2d...)
  ...
  PASS  SKILL.md frontmatter matches the entry

ALL PASS
```

`uv run verify_skills.py --tamper`:

```text
1. User approves (course-skills, skill://mcp-builder/SKILL.md).
   The approval binds to all 6 (uri, digest) pairs, not just SKILL.md.

2. The server's copy of reference/mcp_best_practices.md changes after approval.

3. The host reads that file and checks it against the entry it holds:
  FAIL  skill://mcp-builder/reference/mcp_best_practices.md  (28973 bytes, sha256:92e086f7a51b...)

4. The host refreshes the entry with skills/get and compares it to the approval:
   skill://mcp-builder/reference/mcp_best_practices.md
     approved sha256:3bdf013379bd...  now sha256:92e086f7a51b...
   -> APPROVAL REVOKED: re-prompt the user before loading
```

Digests change if you edit the skill files. The PASS/FAIL pattern stays the same.

## How the server works

- `skill_entry()` hashes every file from disk on each request, so an edit shows up with a new digest right away.
- `skills/list` and `skills/get` are registered with the v2 SDK's `Server.add_request_handler`, so no SDK workaround is needed.
- Add a skill by dropping another folder with a `SKILL.md` into `skills/`. The folder name must equal the `name` in its frontmatter.

## Current status (October 2026)

- **Spec:** Final since 2026-09-13, written against base protocol `2026-07-28`. The server runs on SDK v2 (`mcp>=2.3,<3`), which advertises extensions only in the `2026-07-28` `server/discover` result: a client using the older `initialize` handshake still gets the `skill://` resources, but not the extension capability. `verify_skills.py` connects with `discover()` for that reason. The server still sends the newer `resultType`, `ttlMs` and `cacheScope` fields.
- **SDKs:** native Skills types in the Python, TypeScript, Go and C# SDKs are still in open PRs (Python: [python-sdk#3485](https://github.com/modelcontextprotocol/python-sdk/pull/3485)), so both sides send the two methods as plain JSON-RPC.
- **Hosts:** the official [client matrix](https://modelcontextprotocol.io/extensions/client-matrix) lists Skills support for mcpc, plus partial support in ChatGPT, fast-agent and MCP Inspector. Claude Code is not listed, and Claude web and Desktop show no Skills support. Claude Code connected to this server sees the `skill://` files as plain resources.
- **Digests are unsigned.** The same server supplies the content and the digests. A match proves the two agree. Digests catch drift and changes after approval. They cannot protect you from a malicious server or from a gateway that rewrites both.

Sources: [spec](https://github.com/modelcontextprotocol/ext-skills/blob/main/specification/stable/skills.mdx) ·
[rationale](https://github.com/modelcontextprotocol/ext-skills/blob/main/docs/rationale.md) ·
[implementations](https://github.com/modelcontextprotocol/ext-skills/blob/main/docs/implementations.md) ·
[Inspector CLI skill verification](https://github.com/modelcontextprotocol/inspector/blob/main/clients/cli/README.md#skill-verification---verify)
