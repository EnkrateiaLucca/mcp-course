# Quick Start Guide - Automation Agent

Get up and running with the Automation Agent in 5 minutes!

## ⚡ 3-Step Setup

### Step 1: Set API Key

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

**Need an API key?** Get one at [console.anthropic.com](https://console.anthropic.com/)

### Step 2: Navigate to Directory

```bash
cd demos/05-automations-agent
```

### Step 3: Run the Agent

```bash
uv run automation_agent.py
```

That's it! UV will handle all dependencies automatically.

## 💬 First Conversation

Try these example queries:

```
👤 You: What automations are available?
🤖 Agent: [Shows list of 7 available automations]

👤 You: Generate the file backup automation
🤖 Agent: [Creates backup_files.sh and explains how to use it]

👤 You: Show me python automations
🤖 Agent: [Lists all Python-based automations]
```

## 📝 Sample Queries

### Browse Automations
- "What automations are available?"
- "Show me the database statistics"
- "List file management automations"

### Search by Category
- "Show me system maintenance automations"
- "What database automations do you have?"
- "List all reporting scripts"

### Search by Language
- "Show me bash scripts"
- "What Python automations are available?"

### Generate Scripts
- "Generate the backup files automation"
- "Create the download organizer script"
- "I need the disk space monitor"
- "Generate automation ID 5"

### Get Help
- "How do I use the backup script?"
- "Explain the organize downloads automation"

## 🎯 What You'll See

### When Agent Creates a Script

```bash
🤖 Agent: I've created backup_files.sh for you!

This script backs up files from a source directory to a backup
location with a timestamp.

Usage:
  ./backup_files.sh <source_dir> <backup_dir>

Example:
  ./backup_files.sh ~/Documents ~/Backups

The script is located in: generated_scripts/backup_files.sh

It's already executable and ready to use!
```

### Generated Files Location

```
demos/05-automations-agent/
└── generated_scripts/
    ├── backup_files.sh         ← Generated here
    ├── organize_downloads.py   ← Generated here
    └── monitor_disk_space.py   ← Generated here
```

## 🔍 Testing the MCP Server Independently

Want to see how the MCP server works without the agent?

```bash
# Run MCP Inspector
mcp dev automation_mcp_server.py
```

This opens a web interface where you can:
- Test each tool directly
- See tool schemas
- Inspect responses
- Debug issues

## 🛠️ Architecture at a Glance

```
User Query
    ↓
Automation Agent (Claude Agent SDK)
    ↓
MCP Tools (via automation_mcp_server.py)
    ↓
Database Query (automations_database.csv)
    ↓
Return Template
    ↓
Agent Writes File (using Write tool)
    ↓
Agent Makes Executable (using Bash tool)
    ↓
Response to User
```

## 📚 Available Automations

The database includes 7 pre-configured automations:

| ID | Name | Category | Language |
|----|------|----------|----------|
| 1 | backup_files | File Management | bash |
| 2 | clean_temp_files | System Maintenance | bash |
| 3 | organize_downloads | File Management | python |
| 4 | database_backup | Database | bash |
| 5 | monitor_disk_space | System Monitoring | python |
| 6 | git_auto_commit | Version Control | bash |
| 7 | generate_report | Reporting | python |

## 🐛 Common Issues

### "ANTHROPIC_API_KEY not set"

```bash
export ANTHROPIC_API_KEY='sk-ant-...'
```

### "Permission denied"

Make sure you're in the right directory:
```bash
pwd  # Should show: .../demos/05-automations-agent
```

### Agent not responding

- Check your internet connection
- Verify API key is valid
- Try a simpler query: "hello"

## 🎓 Learning Path

1. **Start here** (Quick Start)
2. **Read the main README.md** for detailed explanations
3. **Explore automation_mcp_server.py** to see tool definitions
4. **Study automation_agent.py** to understand agent setup
5. **Modify automations_database.csv** to add your own scripts

## 💡 Tips

- **Be specific**: "Generate automation ID 3" is faster than browsing
- **Ask for categories**: Agent can filter and show relevant automations
- **Review scripts**: Always check generated scripts before running them
- **Test safely**: Try scripts with non-critical data first

## 🚀 Next Steps

Once comfortable with the basics:

1. **Add your own automation** to `automations_database.csv`
2. **Modify system instructions** in `automation_agent.py`
3. **Add new MCP tools** in `automation_mcp_server.py`
4. **Integrate with your workflow** using programmatic API

## 📖 More Information

- **Full README**: See `README.md` for complete documentation
- **MCP Docs**: [modelcontextprotocol.io](https://modelcontextprotocol.io/)
- **Agent SDK**: [github.com/anthropics/claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python)

---

**Ready to build?** Run `uv run automation_agent.py` and start exploring! 🎉
