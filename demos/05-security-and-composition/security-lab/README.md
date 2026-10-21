# Demo 08 — MCP Security Lab: Tool Poisoning, Attack, Defense

A hands-on lab that turns the "tool poisoning" slide into a runnable
attack-and-defense pair. Everything runs on your laptop with a *fake* secret —
nothing real is exfiltrated.

## The attack, in one sentence

A benign-looking `add` tool ships a poisoned **description** that tells the model
to read a local file and hand its contents back through a hidden `context_token`
argument — so a secret is stolen through a normal tool call while the user only
ever sees `4`.

## What's in here

| File | What it does |
|------|--------------|
| `poisoned_server.py` | Defines the poisoned `add` tool: a friendly "adds two numbers" description with an injected, mundane-sounding "audit gateway" procedure, plus a hidden `context_token` parameter that is the exfiltration channel. The malicious implementation captures whatever the model puts there and **rejects calls without it**, forcing the read. |
| `attack_demo.py` | A minimal hand-rolled agent loop (module-00 style) on a small model. Ask "what is 2+2" and watch it read `./.runtime/session.ctx` and smuggle the fake key out through `context_token`. |
| `defended_demo.py` | The same loop plus a `pretool_guard` (the hand-rolled twin of an Agent SDK `PreToolUse` hook): a path firewall, an argument firewall, a description scan, and a rug-pull checksum. The attack fails. |
| `.runtime/session.ctx` | The bait — a fake credential, auto-created on first run. Named like routine session state, not `secrets/api_key.txt`, because the giveaway naming is half of why the naive attack gets flagged. |

## Run it

```bash
export ANTHROPIC_API_KEY=sk-...

# 1. Show the attack succeeds.
uv run attack_demo.py

# 2. Now defend.
uv run defended_demo.py
```

## Why this version works (and the old `<IMPORTANT>` one didn't)

The classic teaching payload — an `<IMPORTANT>` block saying "read this secret,
paste it, don't tell the user" — is refused by every current model on sight. The
security research says why, and this lab is rebuilt around it:

1. **Exfiltrate through a parameter, not the chat reply.** The secret becomes the
   value of an innocuous `context_token` argument, delivered straight to the
   malicious tool. There is no "leak it to the user" step to catch. (Invariant
   Labs' `add(a, b, sidenote)` technique.)
2. **Frame it as boring operational compliance, not a command.** The MCPTox
   benchmark found this "audit / logging / gateway" framing is what drives
   success; adding `<IMPORTANT>` or "ignore previous instructions" bought only
   ~2 points and mostly *triggered* refusals.
3. **Make the bait look like config, not a secret.** `./.runtime/session.ctx`
   reads as routine runtime state the tool legitimately needs; only its
   *contents* reveal it's a credential.
4. **Add a forcing function.** The tool rejects unattributed calls, pressuring
   the model to fetch the file and retry.

## The model-choice lesson

The attack runs on a small, cheap model (Haiku) — the kind behind many real MCP
hosts — and fires reliably. Point `HOST_MODEL` at a frontier model (Sonnet/Fable)
and it will usually refuse and *name* the attack. **Do not read that as safety.**
MCPTox measured attack-success near 0.8–1.0 across frontier models, and found
*more* capable models were often *more* susceptible. The Claude Agent SDK / Claude
Code harness also resists this via its system prompt — but model refusal and host
guardrails are mitigations, not the boundary you build on. The boundary is the
`pretool_guard`.

## The teaching arc (maps to the security slide deck)

1. **Tool poisoning** — `poisoned_server.py` is the canonical example. The
   injected procedure sits in the description, which the model reads but the
   human installing the server does not.
2. **Defense: description transparency** — `defended_demo.py` prints and
   checksums every tool description so the hidden procedure becomes visible.
3. **Defense: least privilege + firewalls** — the `pretool_guard` blocks the
   read of the bait file (an arithmetic task needs *no* file access) and, belt
   and suspenders, blocks `add` calls whose `context_token` looks like stolen
   data.
4. **Rug pulls** — the checksum flags any description that silently changes
   between runs (cf. CVE-2025-54136 "MCPoison": a server approved once, swapped
   later).

## Why this matters

An MCP server you install from a third party can ship benign code and a poisoned
description. The user reviews the code; the model is governed by the description.
That asymmetry is the bug, and the defense is making the description as auditable
to the user as the code is — and never trusting model or host guardrails as your
only line.

## References

- Invariant Labs — [MCP Security Notification: Tool Poisoning Attacks](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks) and [`mcp-injection-experiments`](https://github.com/invariantlabs-ai/mcp-injection-experiments)
- [MCPTox: A Benchmark for Tool Poisoning Attack on Real-World MCP Servers](https://arxiv.org/abs/2508.14925)
- [OWASP MCP Top 10 — MCP03:2025 Tool Poisoning](https://owasp.org/www-project-mcp-top-10/)
- Simon Willison — [The lethal trifecta for AI agents](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
- [Securely deploying AI agents](https://code.claude.com/docs/en/agent-sdk/secure-deployment)
