# Task Management MCP Server - Deployment Setup Guide

This guide will walk you through deploying an OpenAI agent with MCP server integration to Render.com.

## Overview

This example demonstrates:
- **MCP Server** with tools, resources, and prompts for task management
- **OpenAI Agent** that uses the MCP server for intelligent task operations
- **FastAPI wrapper** for web deployment and API access
- **Render deployment** for production hosting

## Prerequisites

### 1. Accounts & Services
- **OpenAI API Account** - Get your API key from [OpenAI Platform](https://platform.openai.com/)
- **GitHub Account** - For code repository and automatic deployments
- **Render Account** - Sign up at [Render.com](https://render.com/)

### 2. Local Development Tools
- Python 3.11+ installed
- Git installed
- Code editor (VS Code recommended)

## Quick Start Guide

### Step 1: Set Up Your Repository

1. **Fork or clone this repository:**
```bash
git clone <your-repo-url>
cd demos/07-deployment-example
```

2. **Set up local environment:**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

3. **Configure environment variables:**
Edit `.env` file:
```bash
OPENAI_API_KEY=sk-your-actual-openai-api-key
ENV=development
```

### Step 2: Test Locally

1. **Test the MCP server:**
```bash
# Run MCP server directly
python mcp_server.py

# In another terminal, test with MCP Inspector (if installed)
mcp dev ./mcp_server.py
```

2. **Test the OpenAI agent:**
```bash
# Set your OpenAI API key first
export OPENAI_API_KEY=sk-your-key-here

# Run the agent
python agent.py
```

3. **Test the web API:**
```bash
# Run the FastAPI server
python main.py

# Visit http://localhost:8000/docs for interactive API documentation
# Test health endpoint: http://localhost:8000/health
```

### Step 3: Deploy to Render

#### Option A: Deploy via GitHub (Recommended)

1. **Push your code to GitHub:**
```bash
git add .
git commit -m "Initial commit for MCP deployment"
git push origin main
```

2. **Create a new Web Service in Render:**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your repository and branch

3. **Configure deployment settings:**
   - **Name:** `task-mcp-server` (or your choice)
   - **Region:** Choose closest to your users
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`

4. **Set environment variables in Render:**
   - Go to your service → Environment tab
   - Add these variables:
     ```
     OPENAI_API_KEY=sk-your-actual-openai-api-key
     ENV=production
     PYTHON_VERSION=3.11.0
     ```

5. **Deploy:**
   - Click "Create Web Service"
   - Wait for deployment (usually 2-5 minutes)
   - Your service will be available at `https://your-service-name.onrender.com`

#### Option B: Deploy via Render Blueprint

1. **Use the render.yaml file:**
```bash
# Make sure render.yaml is in your repository
# It's already included in this example
```

2. **Deploy via Blueprint:**
   - In Render Dashboard, click "New +" → "Blueprint"
   - Connect your repository
   - Render will automatically read `render.yaml` and set up your service

### Step 4: Verify Deployment

1. **Check service health:**
   - Visit: `https://your-service-name.onrender.com/health`
   - Should return: `{"status": "healthy", "timestamp": "...", "service": "mcp-task-server"}`

2. **Explore the API:**
   - Visit: `https://your-service-name.onrender.com/docs`
   - Interactive API documentation with all available endpoints

3. **Test MCP functionality:**
   ```bash
   # Create a task via API
   curl -X POST "https://your-service-name.onrender.com/api/tasks/create" \
        -H "Content-Type: application/json" \
        -d '{
          "title": "Test deployment",
          "description": "Verify the MCP server is working",
          "priority": 4
        }'

   # List all tasks
   curl "https://your-service-name.onrender.com/api/mcp/resources/all-tasks"
   ```

## API Endpoints Reference

### Core Task Management
- `POST /api/tasks/create` - Create a new task
- `PUT /api/tasks/status` - Update task status
- `POST /api/tasks/list` - List tasks with filters
- `POST /api/tasks/search` - Search tasks
- `DELETE /api/tasks/{task_id}` - Delete a task

### MCP Resources
- `GET /api/mcp/resources/all-tasks` - All tasks resource
- `GET /api/mcp/resources/pending-tasks` - Pending tasks
- `GET /api/mcp/resources/high-priority` - High priority tasks

### MCP Prompts
- `GET /api/mcp/prompts/summary` - Task summary prompt
- `GET /api/mcp/prompts/standup` - Daily standup report
- `GET /api/mcp/prompts/prioritization` - Task prioritization guide

### Agent Integration
- `POST /api/agent/chat` - Natural language task management

## Local Agent Usage

Run the full OpenAI agent locally to see MCP integration:

```bash
# Ensure your OpenAI API key is set
export OPENAI_API_KEY=sk-your-key-here

# Run the agent
python agent.py

# Example interactions:
# > "Create a high priority task to review the deployment"
# > "Show me all pending tasks"
# > "Generate a task summary"
# > "What should I work on next?"
```

## Troubleshooting

### Common Issues

1. **Deployment fails with "Module not found":**
   - Check that all imports are correct in your Python files
   - Verify `requirements.txt` has all necessary dependencies

2. **OpenAI API errors:**
   - Verify your API key is correct and has credits
   - Check the environment variable name matches exactly

3. **MCP server not responding:**
   - Check the logs in Render dashboard
   - Verify the start command is correct: `python main.py`

4. **Health check failing:**
   - Ensure `/health` endpoint returns 200 status
   - Check if the service is listening on the correct port

### Render-Specific Issues

1. **Service keeps restarting:**
   - Check build and start commands
   - Review logs for Python errors
   - Ensure dependencies install successfully

2. **Environment variables not loading:**
   - Verify variables are set in Render dashboard
   - Check variable names match your code
   - Don't include quotes around values in Render UI

3. **Slow cold starts:**
   - Normal for free tier (services sleep after 15 min inactive)
   - Consider upgrading to paid plan for production
   - Implement keep-alive pings if needed

## Production Considerations

### Security
- Use environment variables for all secrets
- Enable HTTPS (automatic with Render)
- Consider adding authentication for production use
- Validate all inputs and sanitize outputs

### Monitoring
- Set up log aggregation
- Monitor API response times
- Set up alerts for service failures
- Track OpenAI API usage and costs

### Scaling
- Start with free tier for testing
- Monitor resource usage in Render dashboard
- Upgrade to paid plans for production workloads
- Consider adding database persistence for larger datasets

### Database Integration (Optional)
To add persistent storage:

1. **Uncomment database section in `render.yaml`**
2. **Update code to use PostgreSQL instead of in-memory storage:**
```python
# Add to requirements.txt
# sqlalchemy==2.0.25
# asyncpg==0.29.0

# Update mcp_server.py to use database
import sqlalchemy
# ... database connection code
```

## Next Steps

1. **Customize for your use case:**
   - Modify task fields and validation
   - Add new MCP tools for your specific needs
   - Enhance the agent with domain-specific knowledge

2. **Add more features:**
   - User authentication
   - Task notifications
   - Integration with other services (Slack, email, etc.)
   - Advanced reporting and analytics

3. **Scale the system:**
   - Add database persistence
   - Implement caching
   - Add rate limiting
   - Set up monitoring and alerting

## Support

If you run into issues:
1. Check the [Render documentation](https://render.com/docs)
2. Review [OpenAI Agents SDK docs](https://openai.github.io/openai-agents-python/)
3. Check [MCP documentation](https://modelcontextprotocol.io/)
4. Open an issue in the course repository

## Architecture Summary

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI Web  │    │   OpenAI Agent   │    │   MCP Server    │
│      API        │    │  (Natural Lang)  │    │ (Tools/Resources│
│                 │    │                  │    │   /Prompts)     │
├─────────────────┤    ├──────────────────┤    ├─────────────────┤
│ • REST API      │◄──►│ • GPT-4 powered  │◄──►│ • Task CRUD     │
│ • Health checks │    │ • MCP client     │    │ • Search tools  │
│ • CORS enabled  │    │ • Intent recog   │    │ • Status updates│
│ • Auto-deploy   │    │ • Action exec    │    │ • Resources     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
   ┌──────────────────────────────────────────────────────────────┐
   │                    Render Cloud Platform                     │
   │ • Automatic HTTPS  • Health monitoring  • Log aggregation   │
   │ • GitHub deploys   • Environment vars   • Horizontal scale  │
   └──────────────────────────────────────────────────────────────┘
```

This architecture provides a production-ready foundation for building and deploying AI agents with MCP server integration.