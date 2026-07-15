# Archive

Material removed from the live course flow during the July 2026 redesign
(11 demos → 7 modules). Kept for reference — everything here still worked
when archived.

- `03-query-tabular-data/` — CSV/tabular queries via an in-process MCP
  server. The in-process pattern now lives in
  `demos/02-research-agent-sdk/in_process_agent.py`.
- `06-deploy-simple-agent-mcp-vercel/` — the FastAPI + SSE chat UI wrapping
  the Agent SDK, deployed to Vercel. Replaced by
  `demos/05-deploy-remote-mcp/`, which deploys the **MCP server itself**
  (the current recommended shape: one remote server, many hosts) instead of
  wrapping an agent in a web framework.
- `01-full-host-client/mcp_host.py` — the hand-rolled MCP *host* (demo 00's
  agent loop driving demo 01's client). Superseded live by the Agent SDK in
  demo 02, but still the best read for understanding what a host does.
- `openai_research_agent_alternative.py` — the demo 02 agent on the OpenAI
  Agents SDK, for cross-vendor comparison.
