---
title: 12 Factors for Building Agents - Compressed
created: 2025-08-11 15:11:20
modified: 2025-08-11 15:11:20
type: reference
tags: #agents #12-factors #reference #compressed
---

# 12 Factors for Building Agents - Compressed

# 12 Factors for Building Agents - Compressed

Production-ready AI agent methodology for building modular, observable, and controllable systems:

**Language & Structure (1-4):**
1. **Natural Language → Tool Calls** - Convert language to structured JSON actions
2. **Own Your Prompts** - Full control over what the model sees
3. **Own Your Context Window** - Efficient history/state management  
4. **Tools = Structured Outputs** - JSON payloads your code interprets

**State & Flow (5-8):**
5. **Unify Execution & Business State** - LLM history as source of truth
6. **Launch/Pause/Resume APIs** - Event-driven agent control
7. **Human Contact via Tool Calls** - Structured human intervention
8. **Own Your Control Flow** - No blind loops, use rules for flow

**Reliability & Scale (9-12):**
9. **Compact Errors into Context** - Let models fix their mistakes
10. **Small, Focused Agents** - Short tasks, lower error rates
11. **Trigger from Anywhere** - Slack, cron, webhooks integration
12. **Stateless Reducer** - Input + history = next action

**+1 Bonus:**
13. **Pre-Fetch Context** - Include anticipated info upfront

*Core principle: Clean separation between language understanding and code execution with robust state management and human oversight.*

---
*Created via MCP Server on 2025-08-11 at 15:11:20*
