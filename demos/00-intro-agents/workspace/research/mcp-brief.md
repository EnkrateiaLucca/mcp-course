# Model Context Protocol (MCP) — Brief

## Overview
- **MCP** is an open standard and open-source framework introduced by **Anthropic in November 2024**.
- Its goal is to standardize how AI systems (especially large language models) **integrate and share data with external tools and services**.
- Often described as a universal "plugin interface" or "USB-C port" for AI — one protocol to connect any model to any data source or tool.

## The Problem It Solves
- Before MCP, connecting an LLM to external systems required **bespoke, fragmented integrations** for each tool or data source.
- MCP replaces this patchwork with a **single, consistent protocol**, reducing engineering overhead and improving reliability.

## How It Works
- Follows a **client–server architecture**:
  - **MCP Hosts** — AI applications (e.g., Claude, IDEs) that want to access external context.
  - **MCP Clients** — Components inside the host that initiate connections.
  - **MCP Servers** — Lightweight services that expose data, tools, or APIs using the MCP standard.
- Communication is **bidirectional and secure**, allowing models to both read context and take actions.
- Servers can expose three primitives: **Resources** (data/context), **Tools** (callable functions), and **Prompts** (reusable templates).

## Key Features
- **Open standard** — freely available and not vendor-locked.
- **Language/framework agnostic** — any LLM or application can implement it.
- **Security-conscious** — designed with controlled, permissioned access to external systems.
- **Composable** — a single AI host can connect to multiple MCP servers simultaneously.

## Adoption & Ecosystem
- Rapidly gained traction; by **March 2025** it had become one of the hottest topics in the AI developer space.
- Supported by major platforms including **Anthropic (Claude), Google Cloud, Vercel, IBM**, and many open-source projects.
- Used across domains: coding assistants, FinOps, business automation, development environments, and more.

## Common Use Cases
- Connecting AI assistants to **databases, file systems, and code repositories**.
- Enabling **automated cost analysis** and business intelligence queries.
- Powering **agentic workflows** where an LLM takes multi-step actions across services.
- Integrating AI into **IDEs and development environments** for real-time context.

---

## Sources
1. Anthropic — *Introducing the Model Context Protocol* (Nov 2024): https://www.anthropic.com/news/model-context-protocol
2. Wikipedia — *Model Context Protocol*: https://en.wikipedia.org/wiki/Model_Context_Protocol
3. Vercel Blog — *Model Context Protocol (MCP) explained: An FAQ*: https://vercel.com/blog/model-context-protocol-mcp-explained
4. IBM Think — *What is Model Context Protocol (MCP)?*: https://www.ibm.com/think/topics/model-context-protocol
5. Google Cloud — *What is Model Context Protocol (MCP)? A guide*: https://cloud.google.com/discover/what-is-model-context-protocol
6. Composio — *What is Model Context Protocol (MCP): Explained*: https://composio.dev/content/what-is-model-context-protocol-mcp-explained
