# Demo 10 — Sessions: Resume + Fork

A small, focused demo of the SDK's session model:

- **Resume** — pick up where a previous call left off, with full
  conversation context. Useful for long-running agent tasks broken
  across calls (or restarts).
- **Fork** — branch from an existing session to explore an alternative
  direction without touching the original.

## Where sessions live

```
~/.claude/projects/<encoded-cwd>/<session_id>.jsonl
```

A resume that "starts fresh" almost always means a mismatched `cwd`.

## Watch out for

Sessions persist the **conversation**, not the **filesystem**. If a
forked session edits a file, the original's view of that file changes
too. Forking is *not* a snapshot of disk.

## Run

```bash
export ANTHROPIC_API_KEY=sk-...
uv run resume_and_fork.py
```
