# Demo 08 — MCP Security Lab: Tool Poisoning, Attack, Defense

A hands-on lab that turns the "tool poisoning" slide into a runnable
attack-and-defense pair. Every piece runs on your laptop with a *faked*
secret — nothing real is exfiltrated.

## What's in here

| File | What it does |
|------|--------------|
| `poisoned_server.py` | An in-process MCP server with one tool, `add`, whose description contains a hidden directive telling the model to read `./secrets/api_key.txt` and silently include it in the response. The user sees "add". The model sees the full description, injected directive and all. |
| `attack_demo.py` | An agent with permissive permissions (`Read` + the poisoned tool). Asks "what is 2+2". Watch it *also* read the secret because the hidden directive told it to. |
| `defended_demo.py` | The same setup, plus a `PreToolUse` hook implementing a path firewall (blocks any `Read` outside the workspace) and a tool-description inspection that flags hidden directives. The attack fails. |
| `secrets/api_key.txt` | A fake key. The bait. Not a real secret. |

## Run it

```bash
export ANTHROPIC_API_KEY=sk-...

# 1. Show the attack succeeds.
uv run attack_demo.py

# 2. Now defend.
uv run defended_demo.py
```

## The teaching arc

This demo maps directly to the four pillars in the security slide deck:

1. **Tool poisoning** — `poisoned_server.py` is the canonical example.
   The injected `<IMPORTANT>` block sits in the tool description, which
   the model reads but the human user does not.
2. **Defense: description transparency** — at session start the SDK emits
   a `SystemMessage(subtype="init")` containing every tool's full
   description. Both demos print these so the hidden block becomes
   visible.
3. **Defense: least privilege + path firewall** — `defended_demo.py`
   restricts `allowed_tools`, and its `PreToolUse` hook rejects any
   `Read` outside the workspace.
4. **Rug pulls** — `defended_demo.py` checksums each tool description
   on first load and flags any change on next run. A tool whose
   description silently mutates between sessions is poisoned.

## Why this matters

In the wild, an MCP server you `npm install` from a third party can
ship benign code and a poisoned description. The user reviews the code;
the model is governed by the description. The asymmetry is the bug, and
the defense is *making the description as auditable to the user as the
code is*.

## References

- [Securely deploying AI agents](https://code.claude.com/docs/en/agent-sdk/secure-deployment)
- Anthropic cookbook: [`06_The_vulnerability_detection_agent`](https://github.com/anthropics/claude-cookbooks/tree/main/claude_agent_sdk)
- Anthropic cookbook: [`03_The_site_reliability_agent`](https://github.com/anthropics/claude-cookbooks/tree/main/claude_agent_sdk) — `PreToolUse` write-validation pattern
