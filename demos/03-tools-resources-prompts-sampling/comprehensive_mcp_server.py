#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "mcp>=1.0.0",
#     "asyncio-mqtt>=0.13.0"
# ]
# ///
"""
Comprehensive MCP Server demonstrating all four core capabilities:
- Tools: Model-controlled executable functions
- Resources: Application-controlled data access
- Prompts: User-controlled templates
- Sampling: Server-initiated LLM interactions

Based on MCP specification: https://modelcontextprotocol.io/specification/
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample data for resources
SAMPLE_DATA = {
    "documents": {
        "project_plan.md": {
            "content": "# Project Plan\n\n## Objectives\n- Implement MCP capabilities\n- Create comprehensive demos\n- Document best practices\n\n## Timeline\nWeek 1: Tools implementation\nWeek 2: Resources and Prompts\nWeek 3: Sampling integration",
            "metadata": {"created": "2024-12-01", "author": "Demo Team"}
        },
        "api_docs.md": {
            "content": "# API Documentation\n\n## Endpoints\n\n### GET /health\nReturns server health status\n\n### POST /data\nSubmits data for processing\n\n### GET /reports\nRetrives generated reports",
            "metadata": {"created": "2024-12-02", "author": "Engineering Team"}
        }
    },
    "database_records": [
        {"id": 1, "name": "Alice Johnson", "role": "Engineer", "department": "AI"},
        {"id": 2, "name": "Bob Smith", "role": "Designer", "department": "UX"},
        {"id": 3, "name": "Carol Davis", "role": "Manager", "department": "Product"}
    ]
}

# Available prompts
PROMPTS = {
    "code-review": types.Prompt(
        name="code-review",
        description="Generate a comprehensive code review checklist",
        arguments=[
            types.PromptArgument(
                name="language",
                description="Programming language (e.g., python, javascript)",
                required=True
            ),
            types.PromptArgument(
                name="complexity",
                description="Code complexity level (simple, medium, complex)",
                required=False
            )
        ]
    ),
    "project-planning": types.Prompt(
        name="project-planning",
        description="Create a project planning template",
        arguments=[
            types.PromptArgument(
                name="project_type",
                description="Type of project (web app, mobile app, ai system)",
                required=True
            ),
            types.PromptArgument(
                name="duration",
                description="Expected project duration in weeks",
                required=True
            )
        ]
    ),
    "data-analysis": types.Prompt(
        name="data-analysis",
        description="Analyze data and provide insights",
        arguments=[
            types.PromptArgument(
                name="data_type",
                description="Type of data to analyze",
                required=True
            )
        ]
    )
}

# Initialize the MCP server
app = Server("comprehensive-mcp-demo")

# TOOLS IMPLEMENTATION
# Tools are model-controlled functions that can have side effects

@app.list_tools()
async def list_tools() -> List[types.Tool]:
    """List all available tools."""
    return [
        types.Tool(
            name="send_notification",
            description="Send a notification message (simulated)",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The notification message to send"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Priority level of the notification"
                    },
                    "recipient": {
                        "type": "string",
                        "description": "Recipient email or username"
                    }
                },
                "required": ["message", "recipient"]
            }
        ),
        types.Tool(
            name="create_task",
            description="Create a new task in the project management system",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Task title"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed task description"
                    },
                    "assignee": {
                        "type": "string",
                        "description": "Person assigned to the task"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Due date in YYYY-MM-DD format"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                        "description": "Task priority"
                    }
                },
                "required": ["title", "assignee"]
            }
        ),
        types.Tool(
            name="analyze_performance",
            description="Analyze system performance and generate report",
            inputSchema={
                "type": "object",
                "properties": {
                    "time_period": {
                        "type": "string",
                        "description": "Time period to analyze (e.g., '7 days', '1 month')"
                    },
                    "metrics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific metrics to analyze"
                    }
                },
                "required": ["time_period"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls."""
    logger.info(f"Tool called: {name} with arguments: {arguments}")
    
    if name == "send_notification":
        message = arguments.get("message", "")
        priority = arguments.get("priority", "medium")
        recipient = arguments.get("recipient", "")
        
        # Simulate sending notification
        result = {
            "status": "sent",
            "notification_id": f"notif_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "message": message,
            "priority": priority,
            "recipient": recipient,
            "timestamp": datetime.now().isoformat()
        }
        
        return [types.TextContent(
            type="text",
            text=f"✅ Notification sent successfully!\n\nDetails:\n{json.dumps(result, indent=2)}"
        )]
    
    elif name == "create_task":
        title = arguments.get("title", "")
        description = arguments.get("description", "")
        assignee = arguments.get("assignee", "")
        due_date = arguments.get("due_date", "")
        priority = arguments.get("priority", "medium")
        
        # Simulate task creation
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        result = {
            "task_id": task_id,
            "title": title,
            "description": description,
            "assignee": assignee,
            "due_date": due_date,
            "priority": priority,
            "status": "created",
            "created_at": datetime.now().isoformat()
        }
        
        return [types.TextContent(
            type="text",
            text=f"✅ Task created successfully!\n\nTask Details:\n{json.dumps(result, indent=2)}"
        )]
    
    elif name == "analyze_performance":
        time_period = arguments.get("time_period", "7 days")
        metrics = arguments.get("metrics", ["cpu", "memory", "response_time"])
        
        # Simulate performance analysis
        analysis_result = {
            "analysis_id": f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "time_period": time_period,
            "metrics_analyzed": metrics,
            "summary": {
                "cpu_usage": "85% average, peak 98%",
                "memory_usage": "67% average, peak 89%",
                "response_time": "120ms average, 95th percentile 250ms"
            },
            "recommendations": [
                "Consider scaling up during peak hours",
                "Optimize memory-intensive processes",
                "Review slow API endpoints"
            ],
            "generated_at": datetime.now().isoformat()
        }
        
        return [types.TextContent(
            type="text",
            text=f"📊 Performance Analysis Complete!\n\nResults:\n{json.dumps(analysis_result, indent=2)}"
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

# RESOURCES IMPLEMENTATION
# Resources are application-controlled, read-only data

@app.list_resources()
async def list_resources() -> List[types.Resource]:
    """List all available resources."""
    resources = []
    
    # Document resources
    for doc_name in SAMPLE_DATA["documents"]:
        resources.append(types.Resource(
            uri=f"document://{doc_name}",
            name=f"Document: {doc_name}",
            description=f"Access to {doc_name} content and metadata"
        ))
    
    # Database resources
    resources.append(types.Resource(
        uri="database://employees",
        name="Employee Database",
        description="Employee records with roles and departments"
    ))
    
    # System resources
    resources.append(types.Resource(
        uri="system://status",
        name="System Status",
        description="Current system health and operational metrics"
    ))
    
    return resources

@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read resource content by URI."""
    logger.info(f"Reading resource: {uri}")
    
    if uri.startswith("document://"):
        doc_name = uri.replace("document://", "")
        if doc_name in SAMPLE_DATA["documents"]:
            doc = SAMPLE_DATA["documents"][doc_name]
            return json.dumps({
                "content": doc["content"],
                "metadata": doc["metadata"],
                "uri": uri,
                "type": "document"
            }, indent=2)
        else:
            raise ValueError(f"Document not found: {doc_name}")
    
    elif uri == "database://employees":
        return json.dumps({
            "data": SAMPLE_DATA["database_records"],
            "total_records": len(SAMPLE_DATA["database_records"]),
            "uri": uri,
            "type": "database",
            "last_updated": datetime.now().isoformat()
        }, indent=2)
    
    elif uri == "system://status":
        return json.dumps({
            "status": "healthy",
            "uptime": "72 hours",
            "cpu_usage": "45%",
            "memory_usage": "67%",
            "active_connections": 23,
            "last_check": datetime.now().isoformat(),
            "uri": uri,
            "type": "system"
        }, indent=2)
    
    else:
        raise ValueError(f"Unknown resource URI: {uri}")

# PROMPTS IMPLEMENTATION
# Prompts are user-controlled templates

@app.list_prompts()
async def list_prompts() -> List[types.Prompt]:
    """List all available prompts."""
    return list(PROMPTS.values())

@app.get_prompt()
async def get_prompt(name: str, arguments: Optional[Dict[str, str]] = None) -> types.GetPromptResult:
    """Get a specific prompt with arguments."""
    logger.info(f"Getting prompt: {name} with arguments: {arguments}")
    
    if name not in PROMPTS:
        raise ValueError(f"Prompt not found: {name}")
    
    arguments = arguments or {}
    
    if name == "code-review":
        language = arguments.get("language", "python")
        complexity = arguments.get("complexity", "medium")
        
        prompt_text = f"""# Code Review Checklist for {language.title()}

## Pre-Review Setup
- [ ] Ensure code follows {language} style guidelines
- [ ] Check that all tests pass
- [ ] Verify documentation is updated

## Code Quality ({complexity} complexity)
- [ ] **Readability**: Code is clear and well-commented
- [ ] **Structure**: Functions/classes have single responsibilities
- [ ] **Naming**: Variables and functions have descriptive names
- [ ] **Error Handling**: Appropriate error handling and logging

## {language.title()}-Specific Checks
"""
        
        if language.lower() == "python":
            prompt_text += """- [ ] **PEP 8**: Code follows Python style guidelines
- [ ] **Type Hints**: Functions have appropriate type annotations
- [ ] **Docstrings**: Functions have proper docstrings
- [ ] **Imports**: Imports are organized and necessary"""
        elif language.lower() == "javascript":
            prompt_text += """- [ ] **ESLint**: Code passes linting rules
- [ ] **ES6+**: Modern JavaScript features used appropriately
- [ ] **JSDoc**: Functions have proper documentation
- [ ] **Dependencies**: No unnecessary dependencies added"""
        
        prompt_text += f"""

## Security & Performance
- [ ] **Security**: No security vulnerabilities introduced
- [ ] **Performance**: Code is efficient for {complexity} complexity
- [ ] **Memory**: No memory leaks or excessive resource usage

## Testing
- [ ] **Unit Tests**: All new code has unit tests
- [ ] **Integration Tests**: Integration tests updated if needed
- [ ] **Edge Cases**: Edge cases are covered

## Final Check
- [ ] **Review Complete**: All items above have been reviewed
- [ ] **Approved**: Code is ready for merge

---
*Generated for {language} code with {complexity} complexity level*
"""
        
        return types.GetPromptResult(
            description=f"Code review checklist for {language} ({complexity} complexity)",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=prompt_text)
                )
            ]
        )
    
    elif name == "project-planning":
        project_type = arguments.get("project_type", "web app")
        duration = arguments.get("duration", "8")
        
        prompt_text = f"""# Project Planning Template: {project_type.title()}

## Project Overview
**Type**: {project_type}
**Duration**: {duration} weeks
**Planning Date**: {datetime.now().strftime('%Y-%m-%d')}

## Phase Breakdown

### Phase 1: Planning & Design ({int(int(duration) * 0.2)} weeks)
- [ ] Requirements gathering
- [ ] Technical specification
- [ ] Architecture design
- [ ] UI/UX design (if applicable)
- [ ] Team setup and resource allocation

### Phase 2: Development ({int(int(duration) * 0.6)} weeks)
- [ ] Core functionality implementation
- [ ] Integration development
- [ ] Testing framework setup
- [ ] Regular progress reviews

### Phase 3: Testing & Deployment ({int(int(duration) * 0.2)} weeks)
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] Documentation completion
- [ ] Deployment preparation
- [ ] Go-live planning

## Key Deliverables for {project_type}
"""
        
        if "web app" in project_type.lower():
            prompt_text += """- [ ] Frontend application
- [ ] Backend API
- [ ] Database schema
- [ ] Deployment configuration"""
        elif "mobile app" in project_type.lower():
            prompt_text += """- [ ] Mobile application (iOS/Android)
- [ ] Backend services
- [ ] App store submission
- [ ] User documentation"""
        elif "ai system" in project_type.lower():
            prompt_text += """- [ ] AI model development
- [ ] Training pipeline
- [ ] Inference API
- [ ] Model monitoring system"""
        
        prompt_text += f"""

## Risk Management
- [ ] Technical risks identified
- [ ] Resource constraints assessed
- [ ] Mitigation strategies defined
- [ ] Contingency plans prepared

## Success Metrics
- [ ] Performance benchmarks defined
- [ ] User acceptance criteria established
- [ ] Quality gates implemented
- [ ] Success measurement plan created

---
*{project_type.title()} project planned for {duration} weeks*
"""
        
        return types.GetPromptResult(
            description=f"Project planning template for {project_type} ({duration} weeks)",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=prompt_text)
                )
            ]
        )
    
    elif name == "data-analysis":
        data_type = arguments.get("data_type", "general")
        
        prompt_text = f"""# Data Analysis Guide: {data_type.title()}

## Analysis Objective
Analyze {data_type} data to extract meaningful insights and actionable recommendations.

## Data Exploration Steps

### 1. Data Understanding
- [ ] **Data Source**: Identify and document data sources
- [ ] **Data Volume**: Assess the size and scale of the dataset
- [ ] **Data Quality**: Check for completeness, accuracy, and consistency
- [ ] **Data Types**: Understand the structure and format of variables

### 2. Exploratory Data Analysis
- [ ] **Descriptive Statistics**: Calculate basic statistical measures
- [ ] **Distribution Analysis**: Examine data distributions and patterns
- [ ] **Correlation Analysis**: Identify relationships between variables
- [ ] **Outlier Detection**: Find and investigate anomalous data points

### 3. Data Preparation
- [ ] **Data Cleaning**: Handle missing values and inconsistencies
- [ ] **Feature Engineering**: Create new variables if needed
- [ ] **Data Transformation**: Apply necessary transformations
- [ ] **Data Validation**: Verify data integrity after processing

### 4. Analysis Techniques for {data_type.title()}
"""
        
        if data_type.lower() in ["sales", "revenue", "business"]:
            prompt_text += """- [ ] **Trend Analysis**: Identify sales patterns over time
- [ ] **Seasonal Analysis**: Detect seasonal variations
- [ ] **Customer Segmentation**: Group customers by behavior
- [ ] **Performance Metrics**: Calculate KPIs and benchmarks"""
        elif data_type.lower() in ["user", "customer", "behavioral"]:
            prompt_text += """- [ ] **Cohort Analysis**: Track user behavior over time
- [ ] **Funnel Analysis**: Analyze conversion pathways
- [ ] **Retention Analysis**: Measure user retention rates
- [ ] **A/B Testing**: Compare different user experiences"""
        else:
            prompt_text += """- [ ] **Pattern Recognition**: Identify recurring patterns
- [ ] **Comparative Analysis**: Compare across different segments
- [ ] **Predictive Modeling**: Build forecasting models
- [ ] **Root Cause Analysis**: Investigate underlying factors"""
        
        prompt_text += """

### 5. Insights & Recommendations
- [ ] **Key Findings**: Summarize the most important discoveries
- [ ] **Business Impact**: Quantify the potential impact of findings
- [ ] **Actionable Recommendations**: Provide specific next steps
- [ ] **Implementation Plan**: Outline how to act on insights

### 6. Reporting & Communication
- [ ] **Executive Summary**: Create high-level overview
- [ ] **Detailed Report**: Document methodology and findings
- [ ] **Visualizations**: Develop charts and graphs
- [ ] **Presentation**: Prepare stakeholder presentation

## Quality Assurance
- [ ] **Methodology Review**: Validate analytical approach
- [ ] **Results Verification**: Cross-check findings
- [ ] **Peer Review**: Get feedback from colleagues
- [ ] **Documentation**: Ensure reproducibility

---
*Data analysis framework for {data_type} data*
"""
        
        return types.GetPromptResult(
            description=f"Data analysis guide for {data_type} data",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=prompt_text)
                )
            ]
        )
    
    else:
        raise ValueError(f"Unknown prompt: {name}")

# SAMPLING IMPLEMENTATION
# Sampling allows the server to request LLM completions from the client

async def request_sampling(prompt: str, system_prompt: Optional[str] = None) -> str:
    """
    Request LLM sampling from the client.
    This is a simplified example - in practice, you'd use the MCP sampling protocol.
    """
    logger.info(f"Requesting sampling with prompt: {prompt[:100]}...")
    
    # In a real implementation, this would send a sampling request to the client
    # For demo purposes, we'll return a simulated response
    return f"""Based on the prompt: "{prompt[:50]}..."

This is a simulated LLM response. In a real MCP implementation, this would be:
1. A sampling request sent to the MCP client
2. The client would forward this to the LLM
3. The LLM response would be returned to the server
4. The server could then use this response for further processing

The sampling capability enables powerful agentic behaviors where the server can:
- Request analysis of complex data
- Generate dynamic responses based on context
- Perform multi-step reasoning workflows
- Adapt behavior based on LLM insights

Current timestamp: {datetime.now().isoformat()}
"""

# Additional tool that demonstrates sampling
@app.list_tools()
async def extended_tools() -> List[types.Tool]:
    """Additional tools that demonstrate sampling."""
    base_tools = await list_tools()
    
    sampling_tool = types.Tool(
        name="intelligent_summary",
        description="Generate an intelligent summary using LLM sampling",
        inputSchema={
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "Content to summarize"
                },
                "focus": {
                    "type": "string",
                    "description": "What to focus on in the summary"
                },
                "length": {
                    "type": "string",
                    "enum": ["brief", "detailed", "comprehensive"],
                    "description": "Length of the summary"
                }
            },
            "required": ["content"]
        }
    )
    
    base_tools.append(sampling_tool)
    return base_tools

@app.call_tool()
async def handle_sampling_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tools that use sampling."""
    if name == "intelligent_summary":
        content = arguments.get("content", "")
        focus = arguments.get("focus", "key points")
        length = arguments.get("length", "brief")
        
        # This would normally use the MCP sampling protocol
        sampling_prompt = f"""Please create a {length} summary of the following content, focusing on {focus}:

{content}

Make the summary engaging and highlight the most important information."""
        
        # Request sampling (simulated)
        llm_response = await request_sampling(sampling_prompt)
        
        return [types.TextContent(
            type="text",
            text=f"📝 Intelligent Summary Generated!\n\n{llm_response}"
        )]
    
    # Delegate to the original tool handler for other tools
    return await call_tool(name, arguments)

async def main():
    """Run the MCP server."""
    logger.info("Starting Comprehensive MCP Server...")
    logger.info("This server demonstrates all four MCP capabilities:")
    logger.info("- Tools: send_notification, create_task, analyze_performance, intelligent_summary")
    logger.info("- Resources: documents, database, system status")
    logger.info("- Prompts: code-review, project-planning, data-analysis")
    logger.info("- Sampling: Used in intelligent_summary tool")
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
