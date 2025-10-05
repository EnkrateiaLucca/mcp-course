# Resolved Questions from MCP Course

This document provides comprehensive answers to key questions from the previous Model Context Protocol (MCP) course, with references to authoritative sources.

---

## 1. What is the Difference Between Using Tools to Query Data and MCP Resources?

### Key Distinctions

**MCP Tools** and **Resources** serve fundamentally different purposes in the Model Context Protocol ecosystem:

#### Tools (Model-Controlled)
- **Purpose**: Enable AI models to take actions and perform operations
- **Control**: Model-controlled - the LLM decides when to invoke them (with user approval)
- **Characteristics**:
  - Perform computations and have side effects
  - Can modify state or interact with external systems
  - Dynamic operations (e.g., querying databases, calling APIs)
  - Require tool calls to execute
  - Designed for agentic, autonomous behavior

#### Resources (Application-Controlled)
- **Purpose**: Provide context and data to AI models
- **Control**: Application-controlled - the client explicitly manages data fetching
- **Characteristics**:
  - Read-only data sources (similar to GET endpoints in REST API)
  - No side effects or significant computation
  - Can be directly included in prompts without tool calls
  - More efficient for providing context to models
  - Ideal for managing extensive reference data

### When to Use Each

| Use Case | Recommended Approach |
|----------|---------------------|
| Model needs to reason and act autonomously | **Tools** |
| Providing scoped, structured data | **Resources** |
| Dynamic automated agentic systems | **Tools** |
| Managing extensive reference documentation | **Resources** |
| Reducing context overload | **Resources** |
| Performing actions with side effects | **Tools** |

### Efficiency Considerations

Resources offer a significant efficiency advantage: they allow information to be directly placed into prompts without requiring tool calls. This makes context provision more streamlined and reduces the overhead of tool invocation when the goal is simply to provide data rather than execute actions[1][2].

---

## 2. What Does the `@mcp.tool()` Decorator Do Behind the Hood?

### Core Mechanism

The `@mcp.tool()` decorator transforms standard Python functions into AI-executable tools through several automated processes:

#### 1. Function Registration
- Converts regular Python functions into MCP tools that LLMs can discover and invoke
- Captures the function at decoration time
- Creates a Tool object (not a regular callable function)
- Registers the tool with the MCP framework for protocol compliance

#### 2. Automatic Schema Generation
The decorator automatically generates JSON Schema for input validation based on function type hints:

```python
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers and return the result."""
    return a + b
```

**What happens automatically:**
- Function name → Tool identifier in MCP protocol
- Type hints → JSON Schema for parameter types
- Docstring → Tool description for AI systems
- Return type annotation → Output schema

#### 3. Structured Output Handling
- Automatically validates and returns structured results
- Supports various return types:
  - Pydantic models
  - TypedDicts
  - Dataclasses
  - Primitive types (strings, numbers, lists)
  - Binary media (images, files)
- Validates output against generated schema

#### 4. Context Injection
Tools can optionally receive a `Context` object for advanced capabilities:
- Progress reporting
- Logging
- Access to MCP framework features
- Automatically injected by FastMCP framework

#### 5. Technical Implementation Details

**Schema Generation Process:**
1. Extracts type hints from function signature
2. Converts Python types to JSON Schema types
3. Includes validation rules, default values, and type constraints
4. Ensures MCP protocol compliance
5. Makes the schema available to AI systems for proper request formatting

**Key Features:**
- No manual JSON schema writing required
- Leverages Python's native type system
- Automatic validation of inputs and outputs
- Support for both sync and async functions
- Optional parameters with default values supported[3][4][5]

---

## 3. LLM-Assisted MCP Development: Best Practices and Workflows

### Development Workflow

Building MCP servers with LLM assistance (using Claude Code, Cursor, or similar tools) follows a structured approach:

#### Phase 1: Preparation
1. **Gather Documentation**
   - Collect full MCP documentation
   - Include relevant SDK README files
   - Provide comprehensive context to the LLM

2. **Define Requirements**
   - Clearly specify server requirements
   - Identify resources to expose
   - List tools to provide
   - Define desired prompts
   - Map external system interactions

#### Phase 2: Development with LLM
1. **Iterative Development**
   - Start with core functionality
   - Add features incrementally
   - Request code explanations from LLM
   - Test and refine each component
   - Break complex servers into smaller pieces

2. **LLM Collaboration Points**
   - Code generation
   - Implementation explanation
   - Troubleshooting
   - Iterative improvements
   - Security review

#### Phase 3: Testing and Debugging

**MCP Inspector** is the essential tool for testing MCP servers:

- **What it is**: Interactive, browser-based developer tool (like Postman for MCP)
- **Architecture**:
  - MCP Inspector Client (MCPI): React-based web UI
  - MCP Proxy (MCPP): Node.js protocol bridge

**Usage Modes:**

1. **UI Mode** (Interactive Testing):
```bash
npx @modelcontextprotocol/inspector node build/index.js
```
Opens at `http://localhost:6274` with visual interface for testing

2. **CLI Mode** (Automation):
Enables programmatic interaction for scripting and integration

**Key Testing Features:**
- Test server functions directly from UI
- View request/response details
- Explore available tools and resources
- Real-time log panel showing all messages
- Debug protocol compliance
- Test remote servers and containers[6][7][8]

#### Phase 4: Configuration Across Platforms

**Claude Code:**
```bash
npm install -g @anthropic-ai/claude-code
```

**Cursor:**
- Global configuration: `~/.cursor/mcp.json`
- Project-specific: `.cursor/mcp.json`

**Visual Studio Code:**
Follow MCP configuration guides for VSCode extensions

### Security Best Practices for Deployment (2025)

#### 1. Authentication & Authorization
- ✅ Implement OAuth Resource Server patterns
- ✅ Use Resource Indicators (RFC 8707) to prevent token theft
- ✅ Enable mutual authentication (mTLS)
- ✅ Implement multi-factor authentication
- ✅ Issue temporary scoped tokens
- ✅ Rotate keys regularly
- ⚠️ **Critical**: Every MCP interface needs real security controls, even "local" or "testing" environments

#### 2. Network Security & Isolation
- ✅ Segregate MCP servers by VPC subnets or VLANs
- ✅ Deploy service meshes for identity-related traffic
- ✅ Implement mTLS encryption
- ✅ Apply WAFs and API gateways for deep packet inspection
- ❌ **Avoid**: Binding to `0.0.0.0` without authentication
- ✅ Implement origin and CSRF protection

#### 3. Secrets Management
- ✅ Use environment variables or vaults for credentials
- ✅ Pull secrets at runtime from secrets managers
- ✅ Use temporary tokens during testing
- ❌ **Never**: Check keys into Git
- ❌ **Never**: Store credentials in code or config files

#### 4. Least Privilege & Permissions
- Define minimum required permissions for MCP servers
- Restrict access to only necessary resources/services
- Implement proper isolation for multi-tenant deployments
- Use data partitions and isolated auth tokens

#### 5. Supply Chain Security
- Implement SAST (Static Application Security Testing) in pipelines
- Use SCA (Software Composition Analysis) for dependency vulnerabilities
- Fix known security vulnerabilities before deployment
- Review and dismiss false positives

#### 6. Containerization & Sandboxing
- Use image signing for containers
- Implement SBOM (Software Bill of Materials)
- Continuous security scanning
- Isolate from host to minimize blast radius

#### 7. Testing Strategy
- **Local Tests**: Fast iteration and development
- **Network-based Tests**: Mirror real-world deployment scenarios
- **MCP Inspector**: Interactive testing, schema inspection, log review
- Test with security controls enabled from the start[9][10][11]

### Common Security Pitfalls (2025 Reality Check)
⚠️ **Current State**: Most MCP servers are deployed without:
- Basic authentication
- Input validation
- Proper token management

**Active Threats**:
- Prompt injection attacks
- Tool poisoning
- Token theft
- Multi-tenant access control failures

**Recommendation**: Treat security as a first-class concern from day one, not as an afterthought[11][12].

---

## References

1. **MCP Resources vs Tools - Practical Guide**
   https://ramwert.medium.com/mcp-demystifying-mcp-resources-vs-tools-a-practical-guide-for-agentic-automation-cb07fcb82241

2. **The Full MCP Blueprint: Tools, Resources, and Prompts**
   https://www.dailydoseofds.com/model-context-protocol-crash-course-part-4/

3. **GitHub - Model Context Protocol Python SDK**
   https://github.com/modelcontextprotocol/python-sdk

4. **How to Build an MCP Server in Python: Complete Guide**
   https://scrapfly.io/blog/posts/how-to-build-an-mcp-server-in-python-a-complete-guide

5. **FastMCP - Tools Documentation**
   https://gofastmcp.com/servers/tools

6. **MCP Inspector - GitHub Repository**
   https://github.com/modelcontextprotocol/inspector

7. **MCP Inspector: Debugging Made Easy**
   https://bootcamptoprod.com/mcp-inspector-guide/

8. **MCP Inspector Setup Guide**
   https://mcpcat.io/guides/setting-up-mcp-inspector-server-testing/

9. **Building MCP with LLMs - Official Tutorial**
   https://modelcontextprotocol.io/tutorials/building-mcp-with-llms

10. **The MCP Security Survival Guide**
    https://towardsdatascience.com/the-mcp-security-survival-guide-best-practices-pitfalls-and-real-world-lessons/

11. **7 MCP Server Best Practices for Scalable AI Integrations in 2025**
    https://www.marktechpost.com/2025/07/23/7-mcp-server-best-practices-for-scalable-ai-integrations-in-2025/

12. **MCP Security: Key Risks, Controls & Best Practices**
    https://www.reco.ai/learn/mcp-security

13. **Configure MCP Servers on VSCode, Cursor & Claude Desktop**
    https://spknowledge.com/2025/06/06/configure-mcp-servers-on-vscode-cursor-claude-desktop/

14. **Understanding MCP Security Risks and Controls**
    https://www.redhat.com/en/blog/model-context-protocol-mcp-understanding-security-risks-and-controls

---

*Last Updated: October 2025*
