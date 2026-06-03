# Model Context Protocol (MCP) — Research Brief

## TL;DR
MCP (Model Context Protocol) is Anthropic's open standard (Nov 2024) that acts as a **universal connector** between AI models and external tools/data sources. It replaces brittle, one-off integrations with a single client-server protocol built on three primitives — **Tools**, **Resources**, and **Prompts** — slashing the N×M integration problem down to N+M. Widely adopted by early 2025; spec lives at modelcontextprotocol.io.

## What Is It?
- **MCP** is an **open standard and open-source framework** introduced by **Anthropic in November 2024**.
- It standardizes how AI systems (particularly large language models) **integrate and share data with external tools, systems, and data sources**.
- Often described as a **"universal connector"** for AI applications — analogous to USB-C for devices.

## The Problem It Solves
- Before MCP, developers had to build **custom, one-off connectors** for every tool or data source an AI needed to access.
- This created an **"N×M" integration problem**: N models × M tools = an explosion of bespoke connectors.
- Earlier partial solutions (e.g., OpenAI's 2023 function-calling API, ChatGPT plugins) helped but remained **vendor-specific**.

## How It Works
- MCP defines a **client-server architecture**:
  - **MCP Servers** expose tools, data resources, and preset prompts.
  - **MCP Clients** (AI applications / LLMs) connect to those servers to retrieve context or invoke actions.
- Communication is built around three core **primitives**:
  - **Tools** — callable functions/actions (similar to function calling).
  - **Resources** — structured data or documents the model can read.
  - **Prompts** — reusable, preset prompt templates.
- Uses a **JSON-RPC**-based transport layer, making it language- and platform-agnostic.

## Key Features & Benefits
- **Standardization** — one protocol works across models, frameworks, and vendors.
- **Composability** — multiple MCP servers can be combined in a single AI workflow.
- **Reduced complexity** — developers write one integration per tool, not one per (tool × model).
- **Multi-step workflows** — enables richer AI agents that chain context across actions (e.g., reading a calendar, booking a flight, drafting an email).

## Common Use Cases
- AI-powered IDEs and coding assistants accessing file systems and APIs.
- Chatbots that can read/write documents, calendars, and emails.
- Trip/vacation planning agents combining calendar, email, and booking services.
- Custom enterprise AI workflows connecting internal data sources.

## Ecosystem & Adoption
- Rapidly gained momentum, becoming one of the **hottest topics in AI by early 2025**.
- Supported by a growing library of community and vendor-built MCP servers.
- Specification is maintained at **modelcontextprotocol.io**.

---

## Sources
1. Wikipedia — *Model Context Protocol* — https://en.wikipedia.org/wiki/Model_Context_Protocol
2. Composio — *What is Model Context Protocol (MCP): Explained* — https://composio.dev/content/what-is-model-context-protocol-mcp-explained
3. Weights & Biases — *The Model Context Protocol by Anthropic: Origins, functionality, and impact* — https://wandb.ai/onlineinference/mcp/reports/The-Model-Context-Protocol-MCP-by-Anthropic-Origins-functionality-and-impact--VmlldzoxMTY5NDI4MQ
4. MCP Official Specification — https://modelcontextprotocol.io/specification/2025-11-25
5. Anthropic Engineering Blog — *Code execution with MCP* — https://www.anthropic.com/engineering/code-execution-with-mcp
6. Moveworks Blog — *Simplifying AI Connections: Understanding the Power of MCP* — https://www.moveworks.com/us/en/resources/blog/model-context-protocol-mcp-explained
