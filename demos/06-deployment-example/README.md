# Task Management MCP Server - Deployment Example

A complete example of building and deploying an OpenAI agent with MCP (Model Context Protocol) server integration to Render.com.

## What This Example Demonstrates

🤖 **OpenAI Agent Integration** - Intelligent task management with natural language processing
🔧 **MCP Server Tools** - CRUD operations for tasks (create, read, update, delete)
📊 **MCP Resources** - Structured data access (all tasks, pending tasks, high priority)
💬 **MCP Prompts** - AI-generated summaries and reports (task summary, daily standup)
🌐 **Web API Deployment** - FastAPI wrapper for production hosting
☁️ **Cloud Deployment** - Ready-to-deploy on Render.com

## Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd demos/07-deployment-example

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your OpenAI API key

# Test locally
python main.py  # Web API on http://localhost:8000
python agent.py # Interactive agent CLI
```

## File Structure

```
demos/07-deployment-example/
├── mcp_server.py      # MCP server with tools, resources, prompts
├── agent.py           # OpenAI agent with MCP integration
├── main.py            # FastAPI web wrapper for deployment
├── requirements.txt   # Python dependencies
├── render.yaml        # Render deployment configuration
├── .env.example       # Environment variables template
├── .gitignore         # Git ignore patterns
├── setup.md           # Detailed setup instructions
└── README.md          # This file
```

## Core Components

### 1. MCP Server (`mcp_server.py`)
- **Tools**: `create_task`, `update_task_status`, `list_tasks`, `search_tasks`, `delete_task`
- **Resources**: All tasks, pending tasks, high priority tasks
- **Prompts**: Task summary, daily standup, prioritization guide

### 2. OpenAI Agent (`agent.py`)
- Natural language task management interface
- Intelligent intent recognition and action execution
- Real-time MCP server communication

### 3. Web API (`main.py`)
- RESTful API endpoints for all MCP functionality
- Health checks and error handling
- CORS enabled for web frontend integration
- Production-ready with proper error handling

## API Endpoints

### Task Management
- `POST /api/tasks/create` - Create new task
- `PUT /api/tasks/status` - Update task status
- `POST /api/tasks/list` - List tasks with filters
- `POST /api/tasks/search` - Search tasks
- `DELETE /api/tasks/{task_id}` - Delete task

### MCP Integration
- `GET /api/mcp/tools` - List available MCP tools
- `GET /api/mcp/resources` - List available MCP resources
- `GET /api/mcp/prompts` - List available MCP prompts
- `POST /api/agent/chat` - Natural language interface

### Health & Status
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation

## Deployment to Render

### Prerequisites
1. [OpenAI API key](https://platform.openai.com/)
2. [GitHub account](https://github.com/)
3. [Render account](https://render.com/)

### One-Click Deploy
1. Fork this repository
2. Connect to Render.com
3. Set `OPENAI_API_KEY` environment variable
4. Deploy automatically with `render.yaml`

### Manual Setup
See [setup.md](setup.md) for detailed instructions.

## Example Usage

### Interactive Agent
```bash
python agent.py

> "Create a high priority task to deploy the application"
✅ Task created: 'Deploy the application' (ID: task_20241201123456)

> "Show me all pending tasks"
📋 Found 3 task(s):
⏳ [5⭐] Deploy the application
⏳ [3⭐] Write documentation
⏳ [4⭐] Test integration
```

### Web API
```bash
# Create a task
curl -X POST "http://localhost:8000/api/tasks/create" \
     -H "Content-Type: application/json" \
     -d '{"title": "Review code", "priority": 4}'

# Get task summary
curl "http://localhost:8000/api/mcp/prompts/summary"
```

## Features

### Task Management
- ✅ Create, read, update, delete tasks
- 📊 Priority levels (1-5 stars)
- 🏷️ Status tracking (pending, in_progress, completed)
- 🏷️ Tags and assignee support
- 📅 Due dates and timestamps
- 🔍 Full-text search capabilities

### AI Integration
- 🤖 Natural language task creation
- 🎯 Intelligent prioritization suggestions
- 📈 Automated status updates
- 📋 Dynamic report generation
- 💬 Context-aware responses

### Production Features
- 🚀 Auto-deployment with Render
- ⚡ Fast API with async support
- 🔒 Environment variable security
- 📝 Comprehensive error handling
- 📊 Health monitoring endpoints
- 📖 Interactive API documentation

## Architecture

```
User Input → OpenAI Agent → MCP Client → MCP Server → Task Storage
                ↓              ↓          ↓
           Web Interface → FastAPI → MCP Tools/Resources
```

## Technology Stack

- **Python 3.11+** - Core runtime
- **FastMCP** - MCP server framework
- **OpenAI Agents SDK** - AI agent framework
- **FastAPI** - Web framework
- **Render.com** - Cloud deployment platform
- **Uvicorn** - ASGI server

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## License

This example is provided as educational material for the O'Reilly Live Training on Model Context Protocol.

## Support

- 📚 [Setup Guide](setup.md) - Detailed deployment instructions
- 🔗 [Render Docs](https://render.com/docs) - Platform documentation
- 🤖 [OpenAI Agents](https://openai.github.io/openai-agents-python/) - Agent framework
- 🔧 [MCP Documentation](https://modelcontextprotocol.io/) - Protocol specification

---

**Built for O'Reilly Live Training: Model Context Protocol Course**