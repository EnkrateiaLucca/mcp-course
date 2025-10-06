# MCP Resources vs Tools: A Clear Explanation

## The Core Difference

The key distinction between **Resources** and **Tools** in MCP comes down to **who controls when they're used** and **what they do**:

| Aspect | Tools | Resources |
|--------|-------|-----------|
| **Purpose** | Execute actions & perform operations | Provide read-only data access |
| **Control** | Model-controlled (AI decides when to call) | Application-controlled (host decides when to read) |
| **Usage** | `session.call_tool(name, arguments)` | `session.read_resource(uri)` |
| **Decorator** | `@mcp.tool()` | `@mcp.resource("uri://...")` |
| **Identifier** | Function name | URI (e.g., `docs://file.txt`) |
| **Can modify state?** | Yes - can write files, update databases, etc. | No - read-only data sources |

## What Are Resources?

**Resources are data sources that provide context to the AI.** Think of them as read-only files or data endpoints that the AI application can access to understand your environment.

Resources expose data through **URIs** (Uniform Resource Identifiers). When an MCP client (like Claude Desktop) connects to your server, it can:
1. List available resources
2. Read their contents to provide context
3. Subscribe to updates when resources change

### Resource Examples from Your Course

From `demos/01-introduction-to-mcp/mcp_server.py`:
```python
@mcp.resource("docs://documents.txt")
def get_docs() -> str:
    """Expose a text file as a resource"""
    with open("./documents.txt", "r") as f:
        return f.read()
```

From `demos/05-deployment-example/mcp_server.py`:
```python
@mcp.resource("uri://tasks/all")
async def get_all_tasks() -> str:
    """Get all tasks as a resource"""
    all_tasks = [serialize_task(task) for task in tasks_db.values()]
    return json.dumps({
        "total_tasks": len(all_tasks),
        "tasks": all_tasks,
        "last_updated": datetime.now().isoformat()
    }, indent=2)

@mcp.resource("uri://tasks/pending")
async def get_pending_tasks() -> str:
    """Get all pending tasks as a resource"""
    pending_tasks = [
        serialize_task(task)
        for task in tasks_db.values()
        if task.status == "pending"
    ]
    return json.dumps({"pending_count": len(pending_tasks), ...})
```

**How clients access resources:**
```python
# From demos/01-introduction-to-mcp/mcp_client.py
result = await client.read_resource('docs://documents.txt')
print(result.contents[0].text)
```

### When to Use Resources

Use resources when you want to:
- ✅ Expose documentation or reference material
- ✅ Provide read-only access to data (configs, databases, files)
- ✅ Give AI context about your system's current state
- ✅ Let applications browse available data before deciding what to process
- ✅ Enable subscriptions to data updates

## What Are Tools?

**Tools are functions that the AI can execute to perform actions.** They are capabilities that allow the AI to interact with your system, modify state, or compute results.

The AI model analyzes the conversation and **autonomously decides** when to call tools based on what the user asks for.

### Tool Examples from Your Course

From `demos/02-study-case-anthropic-tools-resources-prompts-chat-app/mcp_server.py`:
```python
@mcp.tool(
    name="read_doc",
    description="Function to read documents"
)
def read_doc(filepath: str) -> str:
    """Read the contents of a file at the specified filepath."""
    with open(filepath, "r") as f:
        return f.read()

@mcp.tool(
    name='write_file',
    description='Function that writes to file'
)
def write_file(filepath: str, contents: str) -> str:
    """Write contents to a file at the specified filepath."""
    with open(filepath, "w") as f:
        f.write(contents)
    return f"File written successfully to: {filepath}"
```

From `demos/05-deployment-example/mcp_server.py`:
```python
@mcp.tool()
async def create_task(
    title: str,
    description: str,
    priority: int = 3,
    due_date: Optional[str] = None,
    assignee: Optional[str] = None,
    tags: List[str] = []
) -> dict:
    """Create a new task with the given details."""
    task_id = generate_task_id()
    task = Task(id=task_id, title=title, ...)
    tasks_db[task_id] = task
    save_task_to_db(task)
    return {"success": True, "task": serialize_task(task), ...}
```

**How clients call tools:**
```python
# From demos/01-introduction-to-mcp/mcp_client.py
result = await client.call_tool('add_numbers', {'a': 5, 'b': 3})
result = await client.call_tool('write_file', {
    'file_name': 'output.txt',
    'file_content': 'Hello World'
})
```

### When to Use Tools

Use tools when you want the AI to:
- ✅ Execute calculations or transformations
- ✅ Write to files or databases
- ✅ Call external APIs
- ✅ Perform actions (create, update, delete operations)
- ✅ Run commands or scripts

## A Practical Analogy

Think of an MCP server like a **smart library with a librarian**:

- **Resources** = Books on shelves
  - The librarian (host application) can browse and read them
  - They contain information but don't do anything
  - You can check what books are available without opening them
  - Example: "Here's the current inventory of all books"

- **Tools** = Services the librarian can perform
  - The librarian decides when to use them based on requests
  - They perform actions: "check out a book", "add new book", "send overdue notices"
  - They change the state of the library
  - Example: "Create a new book record" or "Calculate late fees"

## Real-World Example: Task Management System

From `demos/05-deployment-example/mcp_server.py`, the server provides **both**:

### Resources (Data to Read)
```python
@mcp.resource("uri://tasks/all")          # Read: All tasks
@mcp.resource("uri://tasks/pending")      # Read: Just pending tasks
@mcp.resource("uri://tasks/high-priority") # Read: High priority tasks
```

**Use case**: Claude Desktop reads these resources to understand the current state before making decisions.

### Tools (Actions to Execute)
```python
@mcp.tool() async def create_task(...)      # Action: Create new task
@mcp.tool() async def update_task_status(...) # Action: Change task status
@mcp.tool() async def delete_task(...)      # Action: Remove task
@mcp.tool() async def search_tasks(...)     # Action: Find tasks
```

**Use case**: The AI calls these tools when the user says "Create a task for deploying the server" or "Mark task #123 as completed".

## Key Architectural Insight

From your course cheatsheet (`demos/assets-resources/MCP_TECHNICAL_CHEATSHEET.md`):

> **Resources (Application-Controlled)**
> Data the host application can access
>
> **Tools (Model-Controlled)**
> Functions the AI can execute

This control distinction is **critical**:
- **Resources**: The application (Claude Desktop, IDE) proactively loads them to provide context
- **Tools**: The AI model analyzes the conversation and decides when to call them

## References

- **Your Course Materials**:
  - `demos/assets-resources/MCP_TECHNICAL_CHEATSHEET.md` - Lines 141-149
  - `demos/01-introduction-to-mcp/mcp_server.py` - Lines 28-31 (resource example)
  - `demos/05-deployment-example/mcp_server.py` - Lines 324-361 (resource examples), Lines 180-322 (tool examples)
  - `demos/01-introduction-to-mcp/mcp_client.py` - Lines 83-90 (`read_resource`), Lines 74-81 (`call_tool`)

- **Official MCP Documentation**:
  - MCP Specification: https://modelcontextprotocol.io/specification
  - Architecture Guide: https://modelcontextprotocol.io/docs/learn/architecture
  - Building Servers: https://modelcontextprotocol.io/docs/develop/build-server

## Common Student Questions

**Q: Can a resource execute code?**
A: Yes, the Python function runs when accessed, but conceptually it should return data, not perform side effects. Resources are meant to be read-only views of your data.

**Q: Why not just make everything a tool?**
A: Resources allow the host application to proactively load context without the AI having to "think" about calling tools. They're more efficient for providing background information.

**Q: Can resources have parameters?**
A: Resources are identified by URIs, and in the newer MCP spec, resources can support URI templates with parameters. In FastMCP, the basic `@mcp.resource()` decorator doesn't take runtime parameters - the URI is fixed.

**Q: What's the difference between calling a tool that returns data vs reading a resource?**
A: Conceptually, resources are meant for passive data access (like browsing), while tools are for active operations. The AI decides when to call tools based on user intent, but the application can load resources proactively to provide context before the AI even processes a request.

---

**Summary**: Resources are **what you have** (data/context), Tools are **what you can do** (actions/operations). Resources provide context, tools enable agency.
