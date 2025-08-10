#!/usr/bin/env python3
"""
MCP Demo Workflow for Claude Desktop & Cursor
Demonstrates practical MCP usage patterns for development workflows
"""

import asyncio
import json
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

def create_demo_workflow_server():
    """Create a demo server that shows practical MCP workflows"""
    server = Server("demo-workflow-server")
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="demo_project_setup",
                description="Demonstrate setting up a new project with MCP tools",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_name": {
                            "type": "string",
                            "description": "Name of the project to set up"
                        },
                        "project_type": {
                            "type": "string",
                            "description": "Type of project (python, javascript, react, etc.)",
                            "enum": ["python", "javascript", "react", "vue", "java", "go"],
                            "default": "python"
                        }
                    },
                    "required": ["project_name"]
                }
            ),
            Tool(
                name="demo_code_review",
                description="Demonstrate using MCP for code review workflows",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string", 
                            "description": "Path to the file to review"
                        }
                    },
                    "required": ["file_path"]
                }
            ),
            Tool(
                name="demo_git_workflow",
                description="Demonstrate git operations using MCP",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "Git action to demonstrate",
                            "enum": ["status", "commit", "branch", "log"],
                            "default": "status"
                        }
                    }
                }
            ),
            Tool(
                name="demo_testing_workflow",
                description="Demonstrate testing workflows with MCP",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "test_type": {
                            "type": "string",
                            "description": "Type of testing to demonstrate",
                            "enum": ["unit", "integration", "coverage"],
                            "default": "unit"
                        }
                    }
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "demo_project_setup":
            project_name = arguments.get("project_name", "my-project")
            project_type = arguments.get("project_type", "python")
            
            workflow = f"""
# 🚀 Project Setup Workflow Demo

## Project: {project_name} ({project_type})

### Step 1: Project Structure
With MCP, Claude Desktop can:
- Analyze your current directory structure
- Suggest optimal project organization
- Create missing directories

**Example commands to use:**
1. "Analyze the current directory structure"
2. "Create a {project_type} project structure for {project_name}"

### Step 2: Configuration Files
MCP tools can generate:
- .gitignore for {project_type}
- README.md template
- Package configuration files

**Example commands:**
1. "Create a .gitignore file for {project_type}"
2. "Generate a README for {project_name}"

### Step 3: Git Initialization
Git operations through MCP:
- Initialize repository
- Set up initial commit
- Configure branches

**Example commands:**
1. "Initialize a git repository"
2. "Show me the current git status"

### Step 4: Dependencies & Environment
Language-specific setup:
- Package managers (pip, npm, cargo, etc.)
- Virtual environments
- Configuration files

**Try asking Claude:**
"Set up a complete {project_type} development environment for {project_name}"

### Benefits:
✅ Automated project setup
✅ Consistent file organization  
✅ Best practice configurations
✅ Integration with existing tools
"""
            
            return [TextContent(type="text", text=workflow)]
        
        elif name == "demo_code_review":
            file_path = arguments.get("file_path", "example.py")
            
            workflow = f"""
# 🔍 Code Review Workflow Demo

## File: {file_path}

### Step 1: Code Analysis
MCP enables Claude to:
- Read and analyze your code files
- Calculate code metrics (lines, complexity, etc.)
- Identify potential issues

**Example commands:**
1. "Analyze the code quality in {file_path}"
2. "Show me code metrics for this file"

### Step 2: Pattern Detection
Advanced analysis capabilities:
- Language-specific best practices
- Code style consistency
- Performance considerations

**Example commands:**
1. "Check if {file_path} follows Python best practices"
2. "Suggest improvements for this code"

### Step 3: Context Understanding
With filesystem access:
- Understand imports and dependencies
- Check for unused code
- Verify test coverage

**Example commands:**
1. "Find all files that import functions from {file_path}"
2. "Are there tests for the functions in {file_path}?"

### Step 4: Refactoring Suggestions
AI-powered recommendations:
- Extract common patterns
- Suggest architectural improvements
- Optimize performance bottlenecks

**Example workflow:**
1. "Review this code and suggest refactoring opportunities"
2. "Help me extract this into separate modules"
3. "Generate tests for the main functions"

### Benefits:
✅ Comprehensive code analysis
✅ Context-aware suggestions
✅ Integration with development workflow
✅ Automated quality checks
"""
            
            return [TextContent(type="text", text=workflow)]
        
        elif name == "demo_git_workflow":
            action = arguments.get("action", "status")
            
            workflow = f"""
# 🔄 Git Workflow Demo - {action.title()}

### Git Integration with MCP
Claude Desktop can perform git operations directly through MCP servers:

## Current Demo: {action.title()} Operation

### Available Git Operations:
1. **Status Checking**
   - View working directory status
   - See staged/unstaged changes
   - Track untracked files

2. **Commit Operations**
   - Review changes before commit
   - Generate commit messages
   - Create structured commits

3. **Branch Management**
   - List branches
   - Create feature branches
   - Switch between branches

4. **History Analysis**
   - View commit history
   - Analyze code changes
   - Track development progress

### Example Commands to Try:
**For Status:**
- "Show me the current git status"
- "What files have been modified?"

**For Commits:**
- "Help me write a good commit message for these changes"
- "Review my staged changes before committing"

**For Branches:**
- "List all branches in this repository"
- "Create a new feature branch for user authentication"

**For History:**
- "Show me the last 5 commits"
- "What changes were made in the last week?"

### Workflow Benefits:
✅ No need to switch between terminal and Claude
✅ AI-powered commit message generation
✅ Context-aware git operations
✅ Integration with code review workflow

### Security Note:
🔒 MCP git operations are read-only by default for safety. 
Write operations require explicit confirmation.
"""
            
            return [TextContent(type="text", text=workflow)]
        
        elif name == "demo_testing_workflow":
            test_type = arguments.get("test_type", "unit")
            
            workflow = f"""
# 🧪 Testing Workflow Demo - {test_type.title()} Tests

### Testing Integration with MCP
Claude can help with comprehensive testing workflows:

## Current Demo: {test_type.title()} Testing

### Step 1: Test Discovery
MCP enables Claude to:
- Find existing test files
- Analyze test coverage
- Identify untested code

**Example commands:**
1. "Find all test files in this project"
2. "What functions don't have tests yet?"

### Step 2: Test Generation
AI-powered test creation:
- Generate test cases for functions
- Create test data and fixtures
- Follow testing best practices

**Example commands:**
1. "Generate unit tests for the calculate_interest function"
2. "Create test data for the user authentication module"

### Step 3: Test Execution
Run and analyze tests:
- Execute test suites
- Analyze test results
- Identify failing tests

**Example commands:**
1. "Run all tests and show me the results"
2. "Why is the test_user_login test failing?"

### Step 4: Coverage Analysis
Comprehensive coverage reporting:
- Identify coverage gaps
- Suggest additional tests
- Track coverage trends

**Testing Workflow Examples:**

### Unit Testing:
- Test individual functions in isolation
- Mock external dependencies
- Verify edge cases and error conditions

### Integration Testing:
- Test component interactions
- Verify data flow between modules
- Test external API integrations

### Coverage Testing:
- Measure code coverage percentage
- Identify uncovered branches
- Set coverage targets and goals

### Example Commands to Try:
**For Unit Tests:**
- "Generate unit tests for the UserManager class"
- "Create tests that cover all edge cases for the validation function"

**For Integration Tests:**
- "Write integration tests for the payment processing workflow"
- "Test the database connection and query operations"

**For Coverage:**
- "Run tests with coverage analysis"
- "Which parts of the codebase need more test coverage?"

### Benefits:
✅ Automated test generation
✅ Intelligent test case suggestions
✅ Integration with CI/CD workflows
✅ Coverage tracking and improvement
"""
            
            return [TextContent(type="text", text=workflow)]
        
        return [TextContent(type="text", text=f"Unknown demo: {name}")]
    
    return server

async def main():
    """Run the demo workflow server"""
    server = create_demo_workflow_server()
    
    print("🎯 MCP Demo Workflow Server Starting...")
    print("This server demonstrates practical MCP usage patterns.")
    print("Configure it in Claude Desktop to see these workflows in action!")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

if __name__ == "__main__":
    asyncio.run(main())