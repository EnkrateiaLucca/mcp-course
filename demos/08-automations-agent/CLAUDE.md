# Automation Agent with OpenAI Agents SDK + MCP Prompt

This prompt is designed to build a complete automation system that reads Google Sheets entries and automatically generates and deploys automation scripts using OpenAI Agents SDK with MCP integration.

## Complete System Prompt

```
Build a comprehensive automation agent system using OpenAI Agents SDK + MCP that automates the creation of automation scripts based on Google Sheets configurations. This system should consist of two main components:

## Component 1: Google Sheets MCP Server

**Server Purpose:**
- Connect to Google Sheets API using service account authentication
- Read automation configuration data from specified spreadsheets
- Provide structured access to automation definitions and parameters
- Support real-time monitoring of sheet changes

**Required Tools:**
- read_sheet_data: Read automation configurations from {GOOGLE_SHEETS_ID}
- validate_automation_config: Validate automation parameters and requirements
- update_execution_status: Update the status column when automations are created/deployed
- list_available_automations: Get all pending automation requests from the sheet

**Required Resources:**
- automation_configs: Current automation configurations from the sheet
- execution_logs: Historical execution data and status updates
- template_definitions: Available automation script templates

**Sheet Structure Expected:**
- Column A: Automation Name
- Column B: Automation Type (file_processor, api_monitor, data_sync, etc.)
- Column C: Configuration JSON (parameters, schedules, targets)
- Column D: Status (pending, processing, deployed, failed)
- Column E: Created Date
- Column F: Last Updated
- Column G: Error Messages (if any)

**Authentication Requirements:**
- Google Service Account JSON key file
- Appropriate Google Sheets API permissions
- OAuth 2.0 scope: https://www.googleapis.com/auth/spreadsheets

## Component 2: OpenAI Agents SDK Integration

**Agent Purpose:**
- Monitor the Google Sheets MCP server for new automation requests
- Generate appropriate automation scripts based on configuration
- Deploy and test the generated automations
- Update status back to Google Sheets

**Agent Capabilities:**
- script_generator: Generate Python/bash scripts based on automation type
- deployment_manager: Deploy scripts to appropriate environments
- testing_framework: Run basic tests on generated automations
- error_handler: Handle failures and update status with meaningful messages

**Supported Automation Types:**
1. **file_processor**: Monitor directories, process files based on rules
2. **api_monitor**: Monitor APIs and trigger actions on changes
3. **data_sync**: Synchronize data between systems on schedules
4. **notification_sender**: Send notifications based on triggers
5. **report_generator**: Generate and distribute reports automatically

## Implementation Structure

### 1. MCP Server (google_sheets_mcp_server.py)

```python
# Expected structure - implement this:

from fastmcp import FastMCP
import asyncio
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

mcp = FastMCP("google-sheets-automation")

@mcp.tool()
async def read_sheet_data(sheet_id: str, range_name: str = "A:G") -> dict:
    """Read automation configurations from Google Sheets"""
    # Implementation here
    pass

@mcp.tool()
async def update_execution_status(sheet_id: str, row: int, status: str, error_msg: str = "") -> bool:
    """Update the execution status in the sheet"""
    # Implementation here
    pass

@mcp.resource("uri://automation-configs")
async def get_automation_configs() -> str:
    """Get current automation configurations"""
    # Implementation here
    pass

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### 2. OpenAI Agent (automation_agent.py)

```python
# Expected structure - implement this:

from agents import Agent
from mcp.client import ClientSession
import asyncio
import json

class AutomationAgent(Agent):
    def __init__(self):
        super().__init__(name="automation-agent")
        # MCP client setup
        # Agent tools registration

    async def process_automation_request(self, config: dict) -> dict:
        """Process a single automation request"""
        # Implementation here
        pass

    async def generate_script(self, automation_type: str, config: dict) -> str:
        """Generate automation script based on type and config"""
        # Implementation here
        pass

    async def deploy_automation(self, script: str, config: dict) -> bool:
        """Deploy the generated automation"""
        # Implementation here
        pass

if __name__ == "__main__":
    agent = AutomationAgent()
    asyncio.run(agent.run())
```

## Documentation Context Needed

{INSERT_OPENAI_AGENTS_SDK_DOCS}
{INSERT_MCP_PYTHON_SDK_DOCS}
{INSERT_GOOGLE_SHEETS_API_DOCS}
{INSERT_GOOGLE_AUTH_LIBRARY_DOCS}

## Configuration Requirements

### Environment Variables:
```bash
export OPENAI_API_KEY="your-openai-api-key"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
export GOOGLE_SHEETS_ID="your-google-sheets-id"
export AUTOMATION_DEPLOY_PATH="/path/to/automation-scripts"
```

### Google Sheets Setup:
- Create a Google Sheet with the expected column structure
- Share the sheet with your service account email
- Populate with sample automation requests for testing

### Sample Automation Configurations:

```json
// File Processor Example
{
  "type": "file_processor",
  "source_directory": "/path/to/watch",
  "file_patterns": ["*.csv", "*.json"],
  "actions": ["validate", "transform", "archive"],
  "schedule": "*/5 * * * *",
  "output_directory": "/path/to/processed"
}

// API Monitor Example
{
  "type": "api_monitor",
  "endpoint": "https://api.example.com/status",
  "check_interval": 300,
  "trigger_conditions": ["status != 'healthy'"],
  "actions": ["send_alert", "log_incident"],
  "notification_channels": ["email", "slack"]
}

// Data Sync Example
{
  "type": "data_sync",
  "source": {"type": "database", "connection": "postgresql://..."},
  "destination": {"type": "api", "endpoint": "https://api.target.com"},
  "schedule": "0 2 * * *",
  "mapping": {"source_field": "dest_field"},
  "batch_size": 1000
}
```

## Testing Strategy

1. **Unit Tests**: Test each MCP tool individually
2. **Integration Tests**: Test agent + MCP server communication
3. **End-to-End Tests**: Full workflow from sheet entry to deployed automation
4. **Error Handling Tests**: Various failure scenarios and recovery

## Security Considerations

- Validate all automation configurations before execution
- Sandbox script execution environments
- Limit file system access for generated scripts
- Audit log all automation deployments
- Encrypt sensitive configuration data

## Success Criteria

- Agent successfully reads new entries from Google Sheets
- Generates appropriate automation scripts based on configuration
- Deploys scripts to designated environments
- Updates sheet status with success/failure information
- Handles errors gracefully with meaningful error messages
- Supports all defined automation types
- Scales to handle multiple concurrent automation requests

## Implementation Steps

1. **Phase 1**: Build basic Google Sheets MCP server with read/write capabilities
2. **Phase 2**: Create OpenAI agent with MCP client integration
3. **Phase 3**: Implement script generation for each automation type
4. **Phase 4**: Add deployment and testing capabilities
5. **Phase 5**: Integrate error handling and status updates
6. **Phase 6**: Add monitoring and logging
7. **Phase 7**: Performance optimization and scaling

Please implement this system incrementally, starting with the Google Sheets MCP server, then building the OpenAI agent integration, and finally adding the automation script generation and deployment capabilities. Include comprehensive error handling, logging, and testing at each phase.
```

## Usage Instructions

1. Replace `{INSERT_*_DOCS}` sections with relevant documentation
2. Set up Google Sheets with the specified column structure
3. Configure Google Service Account with appropriate permissions
4. Provide the complete prompt to Claude Code
5. Test each component thoroughly before integration
6. Deploy in a controlled environment with proper monitoring

## Expected Deliverables

- Fully functional Google Sheets MCP server
- OpenAI Agents SDK integration with MCP client
- Script generation templates for each automation type
- Deployment and testing framework
- Comprehensive error handling and logging
- Documentation and usage examples