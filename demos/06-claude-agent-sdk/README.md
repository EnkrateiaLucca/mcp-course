# Claude Agents SDK + MCP: Complete Course Materials

**Duration**: 2 Days (130 minutes total)
**Level**: Beginner to Intermediate
**Prerequisites**: Python 3.10+, Node.js, Anthropic API key

## 🎯 Course Overview

This module provides comprehensive hands-on training for building AI agents using the **Claude Agents SDK** combined with the **Model Context Protocol (MCP)**. You'll learn to create intelligent agents that can access tools, manage complex workflows, and automate sophisticated tasks.

### What You'll Learn

- 📚 **Claude Agents SDK Fundamentals**: Understand the core concepts and architecture
- 🔌 **MCP Integration**: Connect to both in-process and external MCP servers
- 🛠️ **Tool Creation**: Build custom tools with the `@tool` decorator
- 📁 **File Operations**: Access filesystems via MCP
- 🗄️ **Database Integration**: Create database-driven workflows
- 🤖 **Agent Development**: Build production-ready automation agents
- 🎣 **Hooks & Control**: Monitor and control agent behavior
- 🚀 **Production Patterns**: Error handling, validation, and deployment

## 📅 Course Schedule

### Day 1: Setup & First Working Agent (60 minutes + 10 min Q&A)

**Focus**: Introduction to Claude Agents SDK and building a file reader agent

- ✅ Install and configure Claude Agents SDK
- ✅ Understand streaming sessions
- ✅ Connect to MCP filesystem server
- ✅ List and invoke tools
- ✅ Build a complete file reader agent
- ✅ Use hooks for monitoring

**Materials**:
- 📓 Interactive Notebook: `day1-file-reader-agent/01-intro-claude-agents-sdk.ipynb`
- 🐍 Demo Script: `day1-file-reader-agent/file_reader_agent.py`
- 📖 Documentation: `day1-file-reader-agent/README.md`

### Day 2: Building an Automation Agent (60 minutes + 15 min recap)

**Focus**: Multi-server integration and automation script generation

- ✅ Create custom MCP database tools
- ✅ Integrate multiple MCP servers
- ✅ Generate automation scripts from requirements
- ✅ Manage complex multi-step workflows
- ✅ Track status via database
- ✅ Test and validate generated code

**Materials**:
- 📓 Interactive Notebook: `day2-automation-agent/02-building-automation-agent.ipynb`
- 🐍 Demo Script: `day2-automation-agent/automation_agent.py`
- 📖 Documentation: `day2-automation-agent/README.md`

## 🚀 Quick Start

### Prerequisites

```bash
# Required software
- Python 3.10 or higher
- Node.js 18+ (for MCP filesystem server)
- Anthropic API key

# Optional
- Jupyter (for notebooks)
- UV package manager (for faster setup)
```

### Installation

```bash
# Clone the repository (if not already done)
git clone https://github.com/EnkrateiaLucca/mcp-course.git
cd mcp-course/demos/06-claude-agent-sdk

# Install dependencies
pip install claude-agent-sdk anthropic python-dotenv jupyter

# Or use UV (recommended)
uv pip install claude-agent-sdk anthropic python-dotenv jupyter
```

### Set API Key

```bash
# Export environment variable
export ANTHROPIC_API_KEY="your-api-key-here"

# Or create .env file
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
```

### Run Day 1 Demo

```bash
cd day1-file-reader-agent

# With UV
uv run file_reader_agent.py

# Or traditional Python
python file_reader_agent.py

# Or use Jupyter notebook
jupyter notebook 01-intro-claude-agents-sdk.ipynb
```

### Run Day 2 Demo

```bash
cd day2-automation-agent

# With UV
uv run automation_agent.py

# Or traditional Python
python automation_agent.py

# Or use Jupyter notebook
jupyter notebook 02-building-automation-agent.ipynb
```

## 📁 Directory Structure

```
06-claude-agent-sdk/
├── README.md                          # This file
│
├── day1-file-reader-agent/            # Day 1: Introduction
│   ├── 01-intro-claude-agents-sdk.ipynb   # Interactive notebook
│   ├── file_reader_agent.py              # Standalone demo
│   └── README.md                         # Day 1 documentation
│
└── day2-automation-agent/             # Day 2: Automation
    ├── 02-building-automation-agent.ipynb # Interactive notebook
    ├── automation_agent.py               # Standalone demo
    └── README.md                         # Day 2 documentation
```

## 🎓 Learning Path

### Recommended Sequence

1. **Start with Day 1 Notebook**
   - Run `01-intro-claude-agents-sdk.ipynb`
   - Complete all cells interactively
   - Experiment with the examples

2. **Run Day 1 Demo Script**
   - Execute `file_reader_agent.py`
   - Observe the complete workflow
   - Review the generated files

3. **Move to Day 2 Notebook**
   - Run `02-building-automation-agent.ipynb`
   - Build the database-driven agent
   - Explore multi-server integration

4. **Run Day 2 Demo Script**
   - Execute `automation_agent.py`
   - Watch automation scripts being generated
   - Examine the results

5. **Experiment and Extend**
   - Modify the demos for your use cases
   - Add new tools and capabilities
   - Build your own agents

## 🔑 Key Concepts

### Claude Agents SDK

The Python library for building AI agents with Claude:

```python
from claude_agent_sdk import query, ClaudeSDKClient, ClaudeAgentOptions

# Simple query
async for message in query(prompt="Hello!"):
    print(message)

# Advanced agent
async with ClaudeSDKClient(options=options) as client:
    await client.query("Your task...")
    async for msg in client.receive_response():
        print(msg)
```

### MCP Integration: Two Approaches

#### 1. In-Process SDK Servers

Custom tools running in your Python process:

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("greet", "Greet someone", {"name": str})
async def greet(args):
    return {"content": [{"type": "text", "text": f"Hello, {args['name']}!"}]}

server = create_sdk_mcp_server(name="tools", version="1.0.0", tools=[greet])
```

**Benefits**: Fast, no subprocess overhead, type-safe

#### 2. External MCP Servers

Existing servers running as separate processes:

```python
options = ClaudeAgentOptions(
    mcp_servers={
        "filesystem": {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"]
        }
    }
)
```

**Benefits**: Reusable, language-agnostic, standard protocol

### Agent Configuration

```python
options = ClaudeAgentOptions(
    system_prompt="You are a helpful assistant...",
    mcp_servers={
        "internal": sdk_server,        # In-process
        "external": {...}              # External
    },
    allowed_tools=["mcp__internal__*"],
    max_turns=10,
    hooks={...}
)
```

## 🛠️ What You'll Build

### Day 1: File Reader Agent

A complete agent that:
- ✅ Connects to MCP filesystem server
- ✅ Lists available tools
- ✅ Reads multiple files
- ✅ Provides intelligent summaries
- ✅ Extracts action items
- ✅ Monitors tool usage with hooks

**Use Cases**:
- Document analysis
- Code review automation
- Log file examination
- Content extraction

### Day 2: Automation Agent

An advanced agent that:
- ✅ Reads requirements from SQLite database
- ✅ Generates production-ready Python scripts
- ✅ Saves scripts via MCP filesystem
- ✅ Tests generated code
- ✅ Updates database with results
- ✅ Handles complex multi-step workflows

**Use Cases**:
- DevOps script generation
- ETL pipeline creation
- Test automation
- Migration tools
- Documentation automation

## 📊 Comparison Table

| Feature | Day 1: File Reader | Day 2: Automation Agent |
|---------|-------------------|------------------------|
| **MCP Servers** | 1 (Filesystem) | 2 (Database + Filesystem) |
| **Tool Type** | External | Both (Custom + External) |
| **Complexity** | Simple | Advanced |
| **Workflow** | Single-step | Multi-step |
| **State Management** | None | Database-driven |
| **Code Generation** | No | Yes |
| **Testing** | No | Yes |
| **Production Ready** | Example | Yes |

## 🎯 Real-World Applications

### What You Can Build

1. **DevOps Automation**
   - Generate deployment scripts
   - Create infrastructure as code
   - Automate cloud operations

2. **Data Engineering**
   - Build ETL pipelines
   - Create data transformation scripts
   - Generate validation rules

3. **Test Automation**
   - Generate test cases from requirements
   - Create integration tests
   - Build test data generators

4. **Documentation**
   - Auto-generate API docs
   - Create user guides from code
   - Build knowledge bases

5. **Code Migration**
   - Generate migration scripts
   - Refactor legacy code
   - Convert between frameworks

## 🐛 Troubleshooting

### Common Issues

#### 1. API Key Not Found

```bash
# Error: ANTHROPIC_API_KEY not found
export ANTHROPIC_API_KEY="your-key-here"

# Or add to .env
echo "ANTHROPIC_API_KEY=your-key" > .env
```

#### 2. Node.js Not Found

```bash
# macOS
brew install node

# Ubuntu/Debian
sudo apt install nodejs npm

# Windows
# Download from https://nodejs.org
```

#### 3. Module Import Errors

```bash
# Reinstall dependencies
pip install --upgrade claude-agent-sdk anthropic

# Or with UV
uv pip install --upgrade claude-agent-sdk anthropic
```

#### 4. MCP Server Timeout

```python
# Increase max_turns in options
options = ClaudeAgentOptions(
    max_turns=30,  # Increase if needed
    # ...
)
```

#### 5. Database Locked (Day 2)

```python
# Add timeout to SQLite connection
conn = sqlite3.connect(db_path, timeout=10.0)
```

## 📚 Additional Resources

### Official Documentation

- [Claude Agents SDK Documentation](https://docs.claude.com/en/api/agent-sdk/overview)
- [MCP in the SDK](https://docs.claude.com/en/api/agent-sdk/mcp)
- [MCP Specification](https://modelcontextprotocol.io/specification/)
- [Claude API Reference](https://docs.anthropic.com/claude/reference/)

### GitHub Repositories

- [Claude Agents SDK Python](https://github.com/anthropics/claude-agent-sdk-python)
- [MCP Servers](https://github.com/modelcontextprotocol/servers)
- [MCP Examples](https://github.com/modelcontextprotocol/examples)

### Community Resources

- [Anthropic Discord](https://discord.gg/anthropic)
- [MCP Community](https://github.com/topics/mcp)
- [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers)

### Tutorials

- [Building Agents with Claude Code SDK](https://blog.promptlayer.com/building-agents-with-claude-codes-sdk/)
- [Claude Agent SDK Tutorial](https://www.datacamp.com/tutorial/how-to-use-claude-agent-sdk)
- [MCP Quickstart Guide](https://www.danliden.com/posts/20250412-mcp-quickstart.html)

## 🎯 Next Steps

After completing this course:

### Immediate Practice

1. **Modify the Demos**
   - Change the file reader to analyze code files
   - Add more automation tasks to the database
   - Create new custom tools

2. **Combine Concepts**
   - Build an agent that uses 3+ MCP servers
   - Create a workflow with validation hooks
   - Implement error recovery mechanisms

3. **Production Deployment**
   - Add authentication
   - Implement rate limiting
   - Create REST API wrapper
   - Add monitoring and logging

### Advanced Topics

1. **Multi-Agent Systems**
   - Create agents that work together
   - Implement agent communication
   - Build agent orchestration

2. **Advanced MCP**
   - Build custom MCP servers
   - Implement MCP resources and prompts
   - Create MCP server SDK

3. **Integration Patterns**
   - Connect to cloud services
   - Integrate with CI/CD pipelines
   - Build Slack/Discord bots

## 💡 Tips for Success

### Best Practices

1. **Start Simple**
   - Begin with basic examples
   - Add complexity gradually
   - Test each component

2. **Use Type Hints**
   - Makes code more maintainable
   - Helps catch errors early
   - Improves IDE support

3. **Error Handling**
   - Always wrap tool functions in try/except
   - Return meaningful error messages
   - Log errors for debugging

4. **Testing**
   - Test tools independently first
   - Verify MCP connections
   - Validate agent responses

5. **Documentation**
   - Document your tools clearly
   - Write detailed system prompts
   - Keep examples up to date

### Common Pitfalls

❌ **Avoid:**
- Using `eval()` in production code
- Ignoring error handling
- Hardcoding credentials
- Not validating inputs
- Infinite loops (set `max_turns`)

✅ **Do:**
- Use parameterized queries for SQL
- Implement comprehensive error handling
- Use environment variables for secrets
- Validate all user inputs
- Set reasonable iteration limits

## 🏆 Learning Objectives Checklist

By the end of this course, you should be able to:

### Day 1 Objectives

- [ ] Install and configure Claude Agents SDK
- [ ] Understand streaming vs. one-shot queries
- [ ] Create custom tools with `@tool` decorator
- [ ] Connect to external MCP servers
- [ ] List and invoke MCP tools
- [ ] Build a file analysis agent
- [ ] Implement hooks for monitoring

### Day 2 Objectives

- [ ] Create in-process MCP database tools
- [ ] Integrate multiple MCP servers
- [ ] Build complex multi-step workflows
- [ ] Generate code from requirements
- [ ] Manage state via database
- [ ] Test and validate outputs
- [ ] Deploy production-ready agents

### Overall Skills

- [ ] Design agent architectures
- [ ] Choose appropriate MCP server types
- [ ] Write effective system prompts
- [ ] Handle errors gracefully
- [ ] Monitor and debug agents
- [ ] Apply production best practices

## 🎓 Certificate of Completion

Upon finishing both days and exercises, you will have:

✅ Built two complete, working AI agents
✅ Mastered Claude Agents SDK fundamentals
✅ Learned MCP integration patterns
✅ Gained production deployment skills
✅ Created a portfolio of agent examples

## 📞 Support & Community

### Getting Help

- 📖 Check the README files in each day's folder
- 💬 Join [Anthropic Discord](https://discord.gg/anthropic)
- 🐛 Report issues on GitHub
- 📧 Contact instructor: lucasenkrateia@gmail.com

### Sharing Your Work

Built something cool? Share it!
- Tweet with #ClaudeAgentsSDK
- Post in Anthropic Discord
- Contribute to the course repo

---

## 🎉 Ready to Begin?

Start with **Day 1** and work your way through the materials at your own pace. The combination of notebooks and standalone scripts provides flexibility for different learning styles.

**Happy Learning!** 🚀

---

**Course Author**: Lucas Soares
**Platform**: O'Reilly Live Training
**Last Updated**: January 2025
**Version**: 1.0
