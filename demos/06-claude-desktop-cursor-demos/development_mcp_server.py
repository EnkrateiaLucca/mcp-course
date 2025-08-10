#!/usr/bin/env python3
"""
Development MCP Server for Claude Desktop & Cursor Integration

This MCP server provides development-focused tools that enhance coding workflows
when used with Claude Desktop or Cursor IDE.

Features:
- Code analysis and metrics
- Git operations and repository insights
- Project structure analysis
- Documentation generation
- Testing utilities
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the MCP server
app = Server("development-assistant")

def run_command(command: str, cwd: Optional[str] = None) -> Dict[str, Any]:
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=30
        )
        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command timed out after 30 seconds",
            "returncode": -1
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "returncode": -1
        }

def analyze_code_file(file_path: str) -> Dict[str, Any]:
    """Analyze a code file and return metrics."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Basic metrics
        total_lines = len(lines)
        non_empty_lines = len([line for line in lines if line.strip()])
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        
        # Language detection based on extension
        ext = Path(file_path).suffix.lower()
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.swift': 'Swift',
            '.kt': 'Kotlin'
        }
        
        return {
            "file_path": file_path,
            "language": language_map.get(ext, "Unknown"),
            "total_lines": total_lines,
            "code_lines": non_empty_lines - comment_lines,
            "comment_lines": comment_lines,
            "blank_lines": total_lines - non_empty_lines,
            "comment_ratio": comment_lines / non_empty_lines if non_empty_lines > 0 else 0,
            "file_size": len(content)
        }
    except Exception as e:
        return {"error": str(e)}

@app.list_tools()
async def list_tools() -> List[types.Tool]:
    """List all available development tools."""
    return [
        types.Tool(
            name="analyze_project_structure",
            description="Analyze the structure of a project directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to the project directory"
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "Maximum directory depth to analyze",
                        "default": 3
                    }
                },
                "required": ["project_path"]
            }
        ),
        types.Tool(
            name="git_status",
            description="Get git status and repository information",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to the git repository",
                        "default": "."
                    }
                }
            }
        ),
        types.Tool(
            name="code_analysis",
            description="Analyze code files for metrics and insights",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the code file to analyze"
                    }
                },
                "required": ["file_path"]
            }
        ),
        types.Tool(
            name="find_files",
            description="Find files in a directory with optional pattern matching",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory to search in"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "File pattern to match (e.g., '*.py', '*.js')",
                        "default": "*"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Search recursively in subdirectories",
                        "default": True
                    }
                },
                "required": ["directory"]
            }
        ),
        types.Tool(
            name="generate_readme",
            description="Generate a README.md template for a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to the project directory"
                    },
                    "project_name": {
                        "type": "string",
                        "description": "Name of the project"
                    },
                    "description": {
                        "type": "string",
                        "description": "Project description"
                    }
                },
                "required": ["project_path", "project_name"]
            }
        ),
        types.Tool(
            name="run_tests",
            description="Run tests for a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to the project directory"
                    },
                    "test_command": {
                        "type": "string",
                        "description": "Test command to run (e.g., 'pytest', 'npm test')",
                        "default": "pytest"
                    }
                },
                "required": ["project_path"]
            }
        ),
        types.Tool(
            name="create_gitignore",
            description="Create a .gitignore file for a specific language/framework",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to the project directory"
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language or framework",
                        "enum": ["python", "javascript", "java", "go", "rust", "react", "vue", "angular"]
                    }
                },
                "required": ["project_path", "language"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls."""
    logger.info(f"Development tool called: {name} with arguments: {arguments}")
    
    if name == "analyze_project_structure":
        project_path = arguments.get("project_path", ".")
        max_depth = arguments.get("max_depth", 3)
        
        try:
            project_path = Path(project_path).resolve()
            if not project_path.exists():
                return [types.TextContent(
                    type="text",
                    text=f"❌ Project path does not exist: {project_path}"
                )]
            
            structure = {"directories": 0, "files": 0, "total_size": 0, "languages": {}}
            
            def analyze_directory(path: Path, current_depth: int = 0):
                if current_depth > max_depth:
                    return
                
                for item in path.iterdir():
                    if item.is_dir() and not item.name.startswith('.'):
                        structure["directories"] += 1
                        analyze_directory(item, current_depth + 1)
                    elif item.is_file():
                        structure["files"] += 1
                        try:
                            size = item.stat().st_size
                            structure["total_size"] += size
                            
                            # Count by file extension
                            ext = item.suffix.lower()
                            if ext:
                                structure["languages"][ext] = structure["languages"].get(ext, 0) + 1
                        except OSError:
                            pass
            
            analyze_directory(project_path)
            
            result = f"📁 **Project Structure Analysis: {project_path.name}**\n\n"
            result += f"**Overview:**\n"
            result += f"- Directories: {structure['directories']}\n"
            result += f"- Files: {structure['files']}\n"
            result += f"- Total Size: {structure['total_size'] / 1024:.1f} KB\n\n"
            
            if structure["languages"]:
                result += f"**File Types:**\n"
                sorted_langs = sorted(structure["languages"].items(), key=lambda x: x[1], reverse=True)
                for ext, count in sorted_langs[:10]:  # Top 10
                    result += f"- {ext}: {count} files\n"
            
            return [types.TextContent(type="text", text=result)]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Error analyzing project structure: {str(e)}"
            )]
    
    elif name == "git_status":
        repo_path = arguments.get("repo_path", ".")
        
        # Get git status
        status_result = run_command("git status --porcelain", cwd=repo_path)
        branch_result = run_command("git branch --show-current", cwd=repo_path)
        log_result = run_command("git log --oneline -5", cwd=repo_path)
        
        if not status_result["success"]:
            return [types.TextContent(
                type="text",
                text=f"❌ Not a git repository or git error: {status_result.get('error', 'Unknown error')}"
            )]
        
        current_branch = branch_result["stdout"].strip() if branch_result["success"] else "unknown"
        
        result = f"🔧 **Git Repository Status**\n\n"
        result += f"**Current Branch:** {current_branch}\n\n"
        
        if status_result["stdout"].strip():
            result += f"**Changes:**\n"
            for line in status_result["stdout"].strip().split('\n'):
                if line.strip():
                    status = line[:2]
                    filename = line[3:]
                    if status == "??":
                        result += f"- 🆕 {filename} (untracked)\n"
                    elif status[0] == "M":
                        result += f"- ✏️ {filename} (modified)\n"
                    elif status[0] == "A":
                        result += f"- ➕ {filename} (added)\n"
                    elif status[0] == "D":
                        result += f"- ❌ {filename} (deleted)\n"
                    else:
                        result += f"- 📝 {filename} ({status.strip()})\n"
        else:
            result += f"**Status:** ✅ Working directory clean\n"
        
        if log_result["success"] and log_result["stdout"].strip():
            result += f"\n**Recent Commits:**\n"
            for line in log_result["stdout"].strip().split('\n')[:3]:
                result += f"- {line}\n"
        
        return [types.TextContent(type="text", text=result)]
    
    elif name == "code_analysis":
        file_path = arguments.get("file_path", "")
        
        if not os.path.exists(file_path):
            return [types.TextContent(
                type="text",
                text=f"❌ File does not exist: {file_path}"
            )]
        
        analysis = analyze_code_file(file_path)
        
        if "error" in analysis:
            return [types.TextContent(
                type="text",
                text=f"❌ Error analyzing file: {analysis['error']}"
            )]
        
        result = f"📊 **Code Analysis: {Path(file_path).name}**\n\n"
        result += f"**Language:** {analysis['language']}\n"
        result += f"**Lines of Code:** {analysis['code_lines']}\n"
        result += f"**Comments:** {analysis['comment_lines']}\n"
        result += f"**Blank Lines:** {analysis['blank_lines']}\n"
        result += f"**Total Lines:** {analysis['total_lines']}\n"
        result += f"**Comment Ratio:** {analysis['comment_ratio']:.1%}\n"
        result += f"**File Size:** {analysis['file_size']} bytes\n\n"
        
        # Code quality insights
        if analysis['comment_ratio'] < 0.1:
            result += "💡 **Suggestion:** Consider adding more comments for better code documentation\n"
        elif analysis['comment_ratio'] > 0.3:
            result += "✅ **Good:** Well-documented code with adequate comments\n"
        
        return [types.TextContent(type="text", text=result)]
    
    elif name == "find_files":
        directory = arguments.get("directory", ".")
        pattern = arguments.get("pattern", "*")
        recursive = arguments.get("recursive", True)
        
        try:
            directory_path = Path(directory).resolve()
            if not directory_path.exists():
                return [types.TextContent(
                    type="text",
                    text=f"❌ Directory does not exist: {directory}"
                )]
            
            if recursive:
                files = list(directory_path.rglob(pattern))
            else:
                files = list(directory_path.glob(pattern))
            
            # Filter out directories
            files = [f for f in files if f.is_file()]
            
            result = f"🔍 **Found {len(files)} files matching '{pattern}' in {directory}**\n\n"
            
            if files:
                # Group by directory for better organization
                by_dir = {}
                for file in files[:50]:  # Limit to 50 files
                    parent = str(file.parent.relative_to(directory_path))
                    if parent not in by_dir:
                        by_dir[parent] = []
                    by_dir[parent].append(file.name)
                
                for dir_name, filenames in sorted(by_dir.items()):
                    if dir_name == ".":
                        result += f"**Root directory:**\n"
                    else:
                        result += f"**{dir_name}/**\n"
                    
                    for filename in sorted(filenames):
                        result += f"- {filename}\n"
                    result += "\n"
                
                if len(files) > 50:
                    result += f"... and {len(files) - 50} more files\n"
            else:
                result += "No files found matching the pattern.\n"
            
            return [types.TextContent(type="text", text=result)]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Error finding files: {str(e)}"
            )]
    
    elif name == "generate_readme":
        project_path = arguments.get("project_path", ".")
        project_name = arguments.get("project_name", "My Project")
        description = arguments.get("description", "A brief description of the project")
        
        try:
            readme_content = f"""# {project_name}

{description}

## Getting Started

### Prerequisites

List any prerequisites needed to run this project.

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd {Path(project_path).name}
```

2. Install dependencies
```bash
# Add installation commands here
```

### Usage

Provide examples of how to use the project.

```bash
# Add usage examples here
```

## Features

- Feature 1
- Feature 2
- Feature 3

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Hat tip to anyone whose code was used
- Inspiration
- etc.

---

*Generated on {datetime.now().strftime('%Y-%m-%d')} using MCP Development Assistant*
"""
            
            readme_path = Path(project_path) / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            result = f"📝 **README.md Generated Successfully!**\n\n"
            result += f"**Location:** {readme_path}\n"
            result += f"**Project:** {project_name}\n\n"
            result += "The README includes sections for:\n"
            result += "- Project description\n"
            result += "- Installation instructions\n"
            result += "- Usage examples\n"
            result += "- Contributing guidelines\n"
            result += "- License information\n\n"
            result += "💡 Remember to customize the content for your specific project!"
            
            return [types.TextContent(type="text", text=result)]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Error generating README: {str(e)}"
            )]
    
    elif name == "run_tests":
        project_path = arguments.get("project_path", ".")
        test_command = arguments.get("test_command", "pytest")
        
        result_cmd = run_command(test_command, cwd=project_path)
        
        result = f"🧪 **Test Results**\n\n"
        result += f"**Command:** {test_command}\n"
        result += f"**Directory:** {project_path}\n"
        result += f"**Return Code:** {result_cmd['returncode']}\n\n"
        
        if result_cmd["success"]:
            result += f"**Output:**\n```\n{result_cmd['stdout']}\n```\n"
            if result_cmd["stderr"]:
                result += f"\n**Warnings/Errors:**\n```\n{result_cmd['stderr']}\n```\n"
        else:
            result += f"❌ **Error:** {result_cmd.get('error', 'Unknown error')}\n"
            if result_cmd.get("stderr"):
                result += f"**Error Output:**\n```\n{result_cmd['stderr']}\n```\n"
        
        return [types.TextContent(type="text", text=result)]
    
    elif name == "create_gitignore":
        project_path = arguments.get("project_path", ".")
        language = arguments.get("language", "python")
        
        gitignore_templates = {
            "python": """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json
""",
            "javascript": """# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Directory for instrumented libs generated by jscoverage/JSCover
lib-cov

# Coverage directory used by tools like istanbul
coverage

# nyc test coverage
.nyc_output

# Grunt intermediate storage (https://gruntjs.com/creating-plugins#storing-task-files)
.grunt

# Bower dependency directory (https://bower.io/)
bower_components

# node-waf configuration
.lock-wscript

# Compiled binary addons (https://nodejs.org/api/addons.html)
build/Release

# Dependency directories
node_modules/
jspm_packages/

# TypeScript v1 declaration files
typings/

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variables file
.env

# next.js build output
.next

# nuxt.js build output
.nuxt

# vuepress build output
.vuepress/dist

# Serverless directories
.serverless
""",
            "java": """*.class

# Log file
*.log

# BlueJ files
*.ctxt

# Mobile Tools for Java (J2ME)
.mtj.tmp/

# Package Files #
*.jar
*.war
*.nar
*.ear
*.zip
*.tar.gz
*.rar

# virtual machine crash logs, see http://www.java.com/en/download/help/error_hotspot.xml
hs_err_pid*

# IDE
.idea/
*.iml
.vscode/

# Maven
target/
pom.xml.tag
pom.xml.releaseBackup
pom.xml.versionsBackup
pom.xml.next
release.properties
dependency-reduced-pom.xml
buildNumber.properties
.mvn/timing.properties

# Gradle
.gradle
build/
!gradle/wrapper/gradle-wrapper.jar
!**/src/main/**/build/
!**/src/test/**/build/
""",
            "go": """# Binaries for programs and plugins
*.exe
*.exe~
*.dll
*.so
*.dylib

# Test binary, built with `go test -c`
*.test

# Output of the go coverage tool, specifically when used with LiteIDE
*.out

# Dependency directories (remove the comment below to include it)
# vendor/

# Go workspace file
go.work
""",
            "rust": """# Generated by Cargo
# will have compiled files and executables
/target/

# Remove Cargo.lock from gitignore if creating an executable, leave it for libraries
# More information here https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html
Cargo.lock

# These are backup files generated by rustfmt
**/*.rs.bk
""",
            "react": """# Dependencies
node_modules/
/.pnp
.pnp.js

# Testing
/coverage

# Production
/build

# Misc
.DS_Store
.env.local
.env.development.local
.env.test.local
.env.production.local

npm-debug.log*
yarn-debug.log*
yarn-error.log*
""",
            "vue": """node_modules/
/dist/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Editor directories and files
.idea
.vscode
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?
""",
            "angular": """# See http://help.github.com/ignore-files/ for more about ignoring files.

# compiled output
/dist
/tmp
/out-tsc

# dependencies
/node_modules

# IDEs and editors
/.idea
.project
.classpath
.c9/
*.launch
.settings/
*.sublime-workspace

# IDE - VSCode
.vscode/*
!.vscode/settings.json
!.vscode/tasks.json
!.vscode/launch.json
!.vscode/extensions.json

# misc
/.sass-cache
/connect.lock
/coverage
/libpeerconnection.log
npm-debug.log
yarn-error.log
testem.log
/typings

# System Files
.DS_Store
Thumbs.db
"""
        }
        
        try:
            gitignore_content = gitignore_templates.get(language, gitignore_templates["python"])
            gitignore_path = Path(project_path) / ".gitignore"
            
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(gitignore_content)
            
            result = f"🙈 **.gitignore Created Successfully!**\n\n"
            result += f"**Location:** {gitignore_path}\n"
            result += f"**Language:** {language.title()}\n\n"
            result += "The .gitignore file includes patterns for:\n"
            result += "- Compiled files and build artifacts\n"
            result += "- Dependencies and package directories\n"
            result += "- IDE and editor files\n"
            result += "- Logs and temporary files\n"
            result += "- Environment and configuration files\n\n"
            result += "💡 Review and customize the file for your specific project needs!"
            
            return [types.TextContent(type="text", text=result)]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Error creating .gitignore: {str(e)}"
            )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the development MCP server."""
    logger.info("Starting Development Assistant MCP Server...")
    logger.info("Available tools:")
    logger.info("- analyze_project_structure: Analyze project directory structure")
    logger.info("- git_status: Get git repository status and information")
    logger.info("- code_analysis: Analyze code files for metrics")
    logger.info("- find_files: Find files with pattern matching")
    logger.info("- generate_readme: Generate README.md template")
    logger.info("- run_tests: Execute test commands")
    logger.info("- create_gitignore: Create .gitignore for specific languages")
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
