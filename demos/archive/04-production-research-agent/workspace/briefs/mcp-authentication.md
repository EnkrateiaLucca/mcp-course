# MCP Authentication

## Findings

### Overview
- MCP authentication is **optional** but strongly recommended for remote (HTTP) servers; local `stdio` servers should retrieve credentials from the environment instead ([MCP Spec](https://modelcontextprotocol.io/specification/draft/basic/authorization)).
- The official standard for securing remote MCP servers is **OAuth 2.1** (IETF draft-ietf-oauth-v2-1-13), adopted as of the March 2025 specification update.
- For `stdio` transport: **no OAuth required** — credentials (e.g. API keys, env vars) are passed through the process environment.
- For HTTP-based transports (`streamable-http`, SSE): OAuth 2.1 authorization code flow is the required path.

---

### Three Roles
- **MCP Client** — acts as an OAuth 2.1 client (e.g. Claude Desktop, Cursor, a custom agent). Makes protected resource requests on behalf of the user.
- **MCP Server** — acts as an OAuth 2.1 **resource server** only. Validates tokens; does not issue them. Separation from the auth server is mandatory per the June 2025 spec revision.
- **Authorization Server** — external identity provider (e.g. Auth0, Okta, Descope) that authenticates users and issues access tokens.

---

### The OAuth 2.1 Authorization Code Flow (step by step)
1. Client makes an unauthenticated request to the MCP server.
2. Server returns **HTTP 401** with a `WWW-Authenticate` header containing the Protected Resource Metadata URL (RFC 9728).
3. Client discovers the authorization server via that metadata endpoint (RFC 8414).
4. Client registers itself — via **Dynamic Client Registration** (RFC 7591), pre-registration, or Client ID Metadata Documents (CIMD).
5. Client initiates the authorization code flow using **PKCE** (Proof Key for Code Exchange), which is mandatory for all public clients.
6. User authenticates and grants consent for the requested scopes.
7. Auth server issues a short-lived **access token** (and optional refresh token).
8. Client includes the token in every subsequent request as a **Bearer token** in the `Authorization` header.
9. MCP server validates the token — checking issuer, audience, expiry, and scopes — and allows or denies the request.

---

### PKCE (Proof Key for Code Exchange)
- Required for **all** authorization code flows, not just public clients (as of the November 2025 spec revision).
- Prevents authorization code interception attacks — critical because MCP clients (agents, CLIs, serverless) often cannot safely store client secrets.
- Replaces the now-dropped implicit grant and removes the need for client secrets in public clients.

---

### Discovery Mechanism
- Servers advertise their authorization server via `WWW-Authenticate` headers on `401` responses.
- Clients read the **Protected Resource Metadata** document (RFC 9728) to find the authorization server URL.
- Authorization server capabilities are then fetched from `/.well-known/oauth-authorization-server` (RFC 8414).
- This replaces older hardcoded fallback endpoint patterns.

---

### Bearer Token Validation
- Every HTTP request from the MCP client includes: `Authorization: Bearer <access_token>`
- The MCP server validates: **issuer**, **audience**, **expiry**, and **scopes**.
- Insufficient scope → server responds with HTTP **403 Forbidden** + `WWW-Authenticate: error="insufficient_scope"`.
- Step-up authorization (v2025-11-25): on a 403, clients can request elevated scopes and re-initiate the flow.

---

### Token Security Rules
- Access tokens must **never** appear as URL parameters — header only.
- Tokens must be short-lived to limit theft risk; refresh tokens enable silent renewal.
- **Token passthrough is prohibited**: MCP servers must not forward a client's token to upstream/backend APIs (confused deputy vulnerability). Use RFC 8693 Token Exchange instead.

---

### Simple Bearer Auth (minimal / demo pattern)
- For internal or demo use, a **static shared secret** (bearer token) can be used without full OAuth.
- Client sets `Authorization: Bearer <token>`, server validates it matches the expected value.
- This is what demo 04 of this course uses (`MCP_AUTH_TOKEN` env var) — **not for production**.

---

### Transport-Specific Summary

| Transport | Auth Approach |
|-----------|--------------|
| `stdio` | Env vars / API keys passed in process environment |
| `streamable-http` (remote) | OAuth 2.1 + PKCE + Bearer tokens |
| Simple HTTP (internal/demo) | Static Bearer token shared secret |

---

### Open / Evolving Areas (as of 2026)
- Client trust establishment between clients and servers
- Scope discovery aligned with agent UX
- DCR security hardening (concern: anonymous client registration)
- Universal JWT validation conventions
- Server-to-server (agent-to-agent) uses emerging client credentials grant extensions

---

## Sources

- [Authorization — Model Context Protocol (official spec)](https://modelcontextprotocol.io/specification/draft/basic/authorization)
- [Is that allowed? Authentication and authorization in MCP — Stack Overflow Blog](https://stackoverflow.blog/2026/01/21/is-that-allowed-authentication-and-authorization-in-model-context-protocol/)
- [Diving Into the MCP Authorization Specification — Descope](https://www.descope.com/blog/post/mcp-auth-spec)
- [MCP, OAuth 2.1, PKCE, and the Future of AI Authorization — Aembit](https://aembit.io/blog/mcp-oauth-2-1-pkce-and-the-future-of-ai-authorization/)
- [Configure Bearer auth in MCP server — mcp-auth.dev](https://mcp-auth.dev/docs/configure-server/bearer-auth)
