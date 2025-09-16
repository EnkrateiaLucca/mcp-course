#!/usr/bin/env python3
"""
OpenAI Automation Agent with MCP Integration
Monitors Google Sheets for new automation requests and generates/deploys automation scripts
"""

import os
import json
import asyncio
import subprocess
import tempfile
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from agents import Agent, function_tool, Runner, run_demo_loop
from dotenv import load_dotenv
from loguru import logger
import httpx

# Load environment variables
load_dotenv()

# Configuration
DEPLOY_PATH = os.getenv('AUTOMATION_DEPLOY_PATH', '/tmp/automations')
LOG_PATH = os.getenv('AUTOMATION_LOG_PATH', '/var/log/automations')
MAX_CONCURRENT = int(os.getenv('MAX_CONCURRENT_AUTOMATIONS', '10'))
SCRIPT_TIMEOUT = int(os.getenv('SCRIPT_TIMEOUT_SECONDS', '300'))
ENABLE_SANDBOXING = os.getenv('ENABLE_SCRIPT_SANDBOXING', 'true').lower() == 'true'

class MCPClient:
    """Client for communicating with Google Sheets MCP server"""

    def __init__(self, server_path: str = "./google_sheets_mcp_server.py"):
        self.server_path = server_path
        self.process = None

    async def start_server(self):
        """Start the MCP server process"""
        try:
            self.process = await asyncio.create_subprocess_exec(
                'python', self.server_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            logger.info("MCP server started successfully")
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            raise

    async def send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a JSON-RPC request to the MCP server"""
        if not self.process:
            await self.start_server()

        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }

        try:
            request_data = json.dumps(request).encode() + b'\n'
            self.process.stdin.write(request_data)
            await self.process.stdin.drain()

            # Read response
            response_line = await self.process.stdout.readline()
            response = json.loads(response_line.decode())

            if "error" in response:
                logger.error(f"MCP server error: {response['error']}")
                return {"success": False, "error": response["error"]}

            return response.get("result", {})

        except Exception as e:
            logger.error(f"Error communicating with MCP server: {e}")
            return {"success": False, "error": str(e)}

    async def stop_server(self):
        """Stop the MCP server process"""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            self.process = None

class AutomationScriptGenerator:
    """Generates automation scripts based on configuration"""

    SCRIPT_TEMPLATES = {
        'file_processor': '''#!/usr/bin/env python3
"""
File Processing Automation
Generated automatically by Automation Agent
"""
import os
import glob
import shutil
import json
from pathlib import Path
from datetime import datetime
import logging

# Configuration
CONFIG = {config_json}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{LOG_PATH}/{automation_name}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def process_file(file_path: str):
    """Process a single file based on configuration"""
    logger.info(f"Processing file: {{file_path}}")

    try:
        # Implement processing logic based on actions
        for action in CONFIG.get('actions', []):
            if action == 'validate':
                # Add validation logic
                logger.info(f"Validating {{file_path}}")
            elif action == 'transform':
                # Add transformation logic
                logger.info(f"Transforming {{file_path}}")
            elif action == 'archive':
                # Archive the file
                archive_dir = Path(CONFIG.get('output_directory', '/tmp/archived'))
                archive_dir.mkdir(exist_ok=True)
                shutil.move(file_path, archive_dir / Path(file_path).name)
                logger.info(f"Archived {{file_path}}")

        return True
    except Exception as e:
        logger.error(f"Error processing {{file_path}}: {{e}}")
        return False

def main():
    """Main processing loop"""
    source_dir = CONFIG.get('source_directory', '/tmp/input')
    file_patterns = CONFIG.get('file_patterns', ['*'])

    logger.info(f"Starting file processor for {{source_dir}}")

    processed_count = 0
    error_count = 0

    for pattern in file_patterns:
        files = glob.glob(os.path.join(source_dir, pattern))
        for file_path in files:
            if os.path.isfile(file_path):
                if process_file(file_path):
                    processed_count += 1
                else:
                    error_count += 1

    logger.info(f"Processing complete. Processed: {{processed_count}}, Errors: {{error_count}}")
    return processed_count, error_count

if __name__ == "__main__":
    main()
''',

        'api_monitor': '''#!/usr/bin/env python3
"""
API Monitoring Automation
Generated automatically by Automation Agent
"""
import asyncio
import aiohttp
import json
import logging
from datetime import datetime
from typing import Dict, Any

# Configuration
CONFIG = {config_json}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{LOG_PATH}/{automation_name}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def check_endpoint() -> Dict[str, Any]:
    """Check the configured endpoint"""
    endpoint = CONFIG.get('endpoint')

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint, timeout=30) as response:
                data = await response.json()
                return {{
                    'status_code': response.status,
                    'data': data,
                    'timestamp': datetime.now().isoformat(),
                    'healthy': response.status == 200
                }}
    except Exception as e:
        logger.error(f"Error checking endpoint: {{e}}")
        return {{
            'status_code': 0,
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'healthy': False
        }}

def evaluate_trigger_conditions(response_data: Dict[str, Any]) -> bool:
    """Evaluate if trigger conditions are met"""
    conditions = CONFIG.get('trigger_conditions', [])

    for condition in conditions:
        # Simple condition evaluation (in production, use a proper expression evaluator)
        if "status != 'healthy'" in condition and not response_data.get('healthy'):
            return True
        if "status_code != 200" in condition and response_data.get('status_code') != 200:
            return True

    return False

async def perform_actions():
    """Perform configured actions when conditions are met"""
    actions = CONFIG.get('actions', [])

    for action in actions:
        if action == 'send_alert':
            logger.warning("ALERT: Trigger conditions met!")
        elif action == 'log_incident':
            logger.error("INCIDENT: API monitoring detected an issue")
        # Add more action implementations as needed

async def main():
    """Main monitoring loop"""
    check_interval = CONFIG.get('check_interval', 300)
    endpoint = CONFIG.get('endpoint')

    logger.info(f"Starting API monitor for {{endpoint}} (interval: {{check_interval}}s)")

    while True:
        response_data = await check_endpoint()
        logger.info(f"API check result: {{response_data}}")

        if evaluate_trigger_conditions(response_data):
            logger.warning("Trigger conditions met, performing actions...")
            await perform_actions()

        await asyncio.sleep(check_interval)

if __name__ == "__main__":
    asyncio.run(main())
''',

        'data_sync': '''#!/usr/bin/env python3
"""
Data Synchronization Automation
Generated automatically by Automation Agent
"""
import asyncio
import aiohttp
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

# Configuration
CONFIG = {config_json}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{LOG_PATH}/{automation_name}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def fetch_source_data() -> List[Dict[str, Any]]:
    """Fetch data from the configured source"""
    source = CONFIG.get('source', {{}})
    source_type = source.get('type')

    if source_type == 'api':
        endpoint = source.get('endpoint')
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint) as response:
                    data = await response.json()
                    logger.info(f"Fetched {{len(data)}} records from source API")
                    return data
        except Exception as e:
            logger.error(f"Error fetching from source API: {{e}}")
            return []

    elif source_type == 'database':
        # Implement database connection logic
        logger.warning("Database source not implemented yet")
        return []

    else:
        logger.error(f"Unknown source type: {{source_type}}")
        return []

async def transform_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Transform data according to mapping configuration"""
    mapping = CONFIG.get('mapping', {{}})
    transformed = []

    for record in data:
        transformed_record = {{}}
        for source_field, dest_field in mapping.items():
            if source_field in record:
                transformed_record[dest_field] = record[source_field]
        transformed.append(transformed_record)

    logger.info(f"Transformed {{len(transformed)}} records")
    return transformed

async def sync_to_destination(data: List[Dict[str, Any]]):
    """Sync data to the configured destination"""
    destination = CONFIG.get('destination', {{}})
    dest_type = destination.get('type')
    batch_size = CONFIG.get('batch_size', 1000)

    if dest_type == 'api':
        endpoint = destination.get('endpoint')

        # Process in batches
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(endpoint, json=batch) as response:
                        if response.status == 200:
                            logger.info(f"Successfully synced batch {{i//batch_size + 1}} ({{len(batch)}} records)")
                        else:
                            logger.error(f"Failed to sync batch {{i//batch_size + 1}}: {{response.status}}")
            except Exception as e:
                logger.error(f"Error syncing batch {{i//batch_size + 1}}: {{e}}")

    else:
        logger.error(f"Unknown destination type: {{dest_type}}")

async def main():
    """Main synchronization process"""
    logger.info("Starting data synchronization")

    try:
        # Fetch data
        source_data = await fetch_source_data()
        if not source_data:
            logger.warning("No data to sync")
            return

        # Transform data
        transformed_data = await transform_data(source_data)

        # Sync to destination
        await sync_to_destination(transformed_data)

        logger.info("Data synchronization completed successfully")

    except Exception as e:
        logger.error(f"Data synchronization failed: {{e}}")

if __name__ == "__main__":
    asyncio.run(main())
''',

        'notification_sender': '''#!/usr/bin/env python3
"""
Notification Sender Automation
Generated automatically by Automation Agent
"""
import smtplib
import json
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any

# Configuration
CONFIG = {config_json}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{LOG_PATH}/{automation_name}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def send_email_notification(message: str):
    """Send notification via email"""
    try:
        # This is a simplified email implementation
        # In production, configure proper SMTP settings
        logger.info(f"EMAIL NOTIFICATION: {{message}}")
    except Exception as e:
        logger.error(f"Error sending email: {{e}}")

def send_slack_notification(message: str):
    """Send notification via Slack"""
    try:
        # This is a simplified Slack implementation
        # In production, use proper Slack webhook or API
        logger.info(f"SLACK NOTIFICATION: {{message}}")
    except Exception as e:
        logger.error(f"Error sending Slack notification: {{e}}")

def send_sms_notification(message: str):
    """Send notification via SMS"""
    try:
        # This is a simplified SMS implementation
        # In production, use a service like Twilio
        logger.info(f"SMS NOTIFICATION: {{message}}")
    except Exception as e:
        logger.error(f"Error sending SMS: {{e}}")

def evaluate_trigger_conditions() -> bool:
    """Evaluate if trigger conditions are met"""
    # This is a simplified implementation
    # In production, implement proper condition evaluation
    conditions = CONFIG.get('trigger_conditions', [])

    # For demo purposes, always return True
    # In reality, you would check actual system metrics
    return len(conditions) > 0

def send_notifications():
    """Send notifications via configured channels"""
    channels = CONFIG.get('notification_channels', [])
    message_template = CONFIG.get('message_template', 'Alert triggered at {{timestamp}}')

    message = message_template.format(
        timestamp=datetime.now().isoformat(),
        condition="demo condition"
    )

    for channel in channels:
        if channel == 'email':
            send_email_notification(message)
        elif channel == 'slack':
            send_slack_notification(message)
        elif channel == 'sms':
            send_sms_notification(message)
        else:
            logger.warning(f"Unknown notification channel: {{channel}}")

def main():
    """Main notification process"""
    logger.info("Starting notification sender")

    try:
        if evaluate_trigger_conditions():
            logger.info("Trigger conditions met, sending notifications...")
            send_notifications()
        else:
            logger.info("Trigger conditions not met")

    except Exception as e:
        logger.error(f"Notification sender failed: {{e}}")

if __name__ == "__main__":
    main()
''',

        'report_generator': '''#!/usr/bin/env python3
"""
Report Generator Automation
Generated automatically by Automation Agent
"""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any

# Configuration
CONFIG = {config_json}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{LOG_PATH}/{automation_name}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def collect_report_data() -> Dict[str, Any]:
    """Collect data for the report"""
    report_type = CONFIG.get('report_type')

    # This is a simplified implementation
    # In production, collect actual data based on report type
    mock_data = {{
        'report_type': report_type,
        'generated_at': datetime.now().isoformat(),
        'period': 'last_24_hours',
        'metrics': {{
            'total_events': 150,
            'success_rate': 95.5,
            'error_count': 7,
            'average_response_time': 245
        }}
    }}

    logger.info(f"Collected data for {{report_type}} report")
    return mock_data

def generate_report_content(data: Dict[str, Any]) -> str:
    """Generate report content based on data"""
    report_format = CONFIG.get('format', 'text')

    if report_format == 'json':
        return json.dumps(data, indent=2)

    elif report_format == 'html':
        html_content = f"""
        <html>
        <head><title>{{data['report_type']}} Report</title></head>
        <body>
            <h1>{{data['report_type'].replace('_', ' ').title()}} Report</h1>
            <p>Generated at: {{data['generated_at']}}</p>
            <h2>Metrics</h2>
            <ul>
                <li>Total Events: {{data['metrics']['total_events']}}</li>
                <li>Success Rate: {{data['metrics']['success_rate']}}%</li>
                <li>Error Count: {{data['metrics']['error_count']}}</li>
                <li>Average Response Time: {{data['metrics']['average_response_time']}}ms</li>
            </ul>
        </body>
        </html>
        """
        return html_content

    else:  # text format
        text_content = f"""
{{data['report_type'].replace('_', ' ').title()}} Report
Generated at: {{data['generated_at']}}

Metrics:
- Total Events: {{data['metrics']['total_events']}}
- Success Rate: {{data['metrics']['success_rate']}}%
- Error Count: {{data['metrics']['error_count']}}
- Average Response Time: {{data['metrics']['average_response_time']}}ms
        """
        return text_content.strip()

def save_report(content: str) -> str:
    """Save report to file"""
    report_type = CONFIG.get('report_type')
    format_ext = CONFIG.get('format', 'txt')

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{{report_type}}_{{timestamp}}.{{format_ext}}"

    report_path = Path(DEPLOY_PATH) / 'reports'
    report_path.mkdir(exist_ok=True)

    file_path = report_path / filename
    with open(file_path, 'w') as f:
        f.write(content)

    logger.info(f"Report saved to {{file_path}}")
    return str(file_path)

def distribute_report(file_path: str):
    """Distribute report to configured recipients"""
    recipients = CONFIG.get('recipients', [])

    for recipient in recipients:
        # This is a simplified implementation
        # In production, implement actual distribution (email, upload, etc.)
        logger.info(f"Distributing report to {{recipient}}: {{file_path}}")

def main():
    """Main report generation process"""
    logger.info("Starting report generation")

    try:
        # Collect data
        data = collect_report_data()

        # Generate report content
        content = generate_report_content(data)

        # Save report
        file_path = save_report(content)

        # Distribute report
        distribute_report(file_path)

        logger.info("Report generation completed successfully")

    except Exception as e:
        logger.error(f"Report generation failed: {{e}}")

if __name__ == "__main__":
    main()
'''
    }

    def generate_script(self, automation_name: str, automation_type: str, config: Dict[str, Any]) -> str:
        """Generate automation script based on type and configuration"""
        template = self.SCRIPT_TEMPLATES.get(automation_type)
        if not template:
            raise ValueError(f"Unknown automation type: {automation_type}")

        # Format template with configuration
        script_content = template.format(
            config_json=json.dumps(config, indent=2),
            automation_name=automation_name,
            LOG_PATH=LOG_PATH
        )

        return script_content

class AutomationAgent:
    """Main automation agent class"""

    def __init__(self):
        self.mcp_client = MCPClient()
        self.script_generator = AutomationScriptGenerator()
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the OpenAI agent with tools"""
        return Agent(
            name="AutomationAgent",
            instructions="""
            You are an advanced automation agent that monitors Google Sheets for automation requests
            and generates appropriate automation scripts. Your responsibilities include:

            1. Monitor Google Sheets for new automation entries with 'pending' status
            2. Validate automation configurations against requirements
            3. Generate appropriate automation scripts based on the automation type
            4. Deploy scripts to the configured environment
            5. Update the Google Sheets with execution status and any errors
            6. Provide detailed feedback on automation deployment success/failure

            When processing automation requests:
            - Always validate the configuration first
            - Generate appropriate scripts for the automation type
            - Test the generated script if possible
            - Update the sheet status immediately after each step
            - Provide clear error messages if something fails

            Supported automation types:
            - file_processor: Monitor directories and process files based on rules
            - api_monitor: Monitor APIs and trigger actions on changes
            - data_sync: Synchronize data between systems on schedules
            - notification_sender: Send notifications based on triggers
            - report_generator: Generate and distribute reports automatically
            """,
            model="gpt-4o-mini",
            tools=[
                self.get_pending_automations,
                self.validate_automation,
                self.generate_automation_script,
                self.deploy_automation_script,
                self.update_automation_status,
                self.test_automation_script
            ]
        )

    @function_tool
    async def get_pending_automations(self) -> str:
        """Get all pending automation requests from Google Sheets"""
        try:
            result = await self.mcp_client.send_request(
                "list_available_automations",
                {"filter_status": "pending"}
            )

            if result.get("success"):
                automations = result.get("automations", [])
                logger.info(f"Found {len(automations)} pending automations")
                return json.dumps({
                    "success": True,
                    "count": len(automations),
                    "automations": automations
                }, indent=2)
            else:
                return json.dumps({
                    "success": False,
                    "error": result.get("message", "Unknown error")
                })

        except Exception as e:
            logger.error(f"Error getting pending automations: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    @function_tool
    async def validate_automation(self, automation_config: str) -> str:
        """Validate an automation configuration"""
        try:
            config = json.loads(automation_config)
            result = await self.mcp_client.send_request(
                "validate_automation_config",
                {"config": config}
            )

            logger.info(f"Validation result: {result}")
            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error validating automation: {e}")
            return json.dumps({
                "valid": False,
                "errors": [str(e)],
                "warnings": []
            })

    @function_tool
    async def generate_automation_script(
        self,
        automation_name: str,
        automation_type: str,
        configuration: str
    ) -> str:
        """Generate automation script based on configuration"""
        try:
            config = json.loads(configuration)

            # Generate script content
            script_content = self.script_generator.generate_script(
                automation_name, automation_type, config
            )

            logger.info(f"Generated script for {automation_name} ({automation_type})")
            return json.dumps({
                "success": True,
                "script_content": script_content,
                "automation_name": automation_name,
                "automation_type": automation_type
            }, indent=2)

        except Exception as e:
            logger.error(f"Error generating script: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    @function_tool
    async def deploy_automation_script(
        self,
        automation_name: str,
        script_content: str,
        make_executable: bool = True
    ) -> str:
        """Deploy automation script to the configured path"""
        try:
            # Ensure deploy directory exists
            deploy_dir = Path(DEPLOY_PATH)
            deploy_dir.mkdir(exist_ok=True)

            # Create script file
            script_path = deploy_dir / f"{automation_name}.py"

            with open(script_path, 'w') as f:
                f.write(script_content)

            # Make executable if requested
            if make_executable:
                os.chmod(script_path, 0o755)

            logger.info(f"Deployed script to {script_path}")
            return json.dumps({
                "success": True,
                "script_path": str(script_path),
                "message": f"Script deployed successfully to {script_path}"
            })

        except Exception as e:
            logger.error(f"Error deploying script: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    @function_tool
    async def update_automation_status(
        self,
        row_number: int,
        status: str,
        error_message: str = ""
    ) -> str:
        """Update automation status in Google Sheets"""
        try:
            result = await self.mcp_client.send_request(
                "update_execution_status",
                {
                    "row": row_number,
                    "status": status,
                    "error_msg": error_message
                }
            )

            logger.info(f"Updated row {row_number} status to {status}")
            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error updating status: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    @function_tool
    async def test_automation_script(
        self,
        script_path: str,
        test_mode: bool = True
    ) -> str:
        """Test the deployed automation script"""
        try:
            if not os.path.exists(script_path):
                return json.dumps({
                    "success": False,
                    "error": f"Script not found: {script_path}"
                })

            # Run syntax check
            result = subprocess.run(
                ['python', '-m', 'py_compile', script_path],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                logger.info(f"Script {script_path} passed syntax check")
                return json.dumps({
                    "success": True,
                    "message": "Script passed syntax validation",
                    "script_path": script_path
                })
            else:
                logger.error(f"Script {script_path} failed syntax check: {result.stderr}")
                return json.dumps({
                    "success": False,
                    "error": f"Syntax check failed: {result.stderr}"
                })

        except Exception as e:
            logger.error(f"Error testing script: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    async def process_automation_request(self, automation: Dict[str, Any]) -> bool:
        """Process a single automation request"""
        try:
            row_number = automation['row_number']
            automation_name = automation['automation_name']
            automation_type = automation['automation_type']
            configuration = automation['configuration']

            logger.info(f"Processing automation: {automation_name} (type: {automation_type})")

            # Update status to processing
            await self.update_automation_status(row_number, "processing")

            # Validate configuration
            validation_result = await self.validate_automation(json.dumps(configuration))
            validation_data = json.loads(validation_result)

            if not validation_data.get('valid', False):
                error_msg = f"Configuration validation failed: {validation_data.get('errors', [])}"
                await self.update_automation_status(row_number, "failed", error_msg)
                return False

            # Generate script
            script_result = await self.generate_automation_script(
                automation_name, automation_type, json.dumps(configuration)
            )
            script_data = json.loads(script_result)

            if not script_data.get('success', False):
                error_msg = f"Script generation failed: {script_data.get('error')}"
                await self.update_automation_status(row_number, "failed", error_msg)
                return False

            # Deploy script
            deploy_result = await self.deploy_automation_script(
                automation_name, script_data['script_content']
            )
            deploy_data = json.loads(deploy_result)

            if not deploy_data.get('success', False):
                error_msg = f"Script deployment failed: {deploy_data.get('error')}"
                await self.update_automation_status(row_number, "failed", error_msg)
                return False

            # Test script
            test_result = await self.test_automation_script(deploy_data['script_path'])
            test_data = json.loads(test_result)

            if not test_data.get('success', False):
                error_msg = f"Script testing failed: {test_data.get('error')}"
                await self.update_automation_status(row_number, "failed", error_msg)
                return False

            # Update status to deployed
            await self.update_automation_status(row_number, "deployed")
            logger.info(f"Successfully processed automation: {automation_name}")
            return True

        except Exception as e:
            logger.error(f"Error processing automation request: {e}")
            if 'row_number' in locals():
                await self.update_automation_status(row_number, "failed", str(e))
            return False

    async def run_monitoring_loop(self):
        """Main monitoring loop for processing automations"""
        logger.info("Starting automation monitoring loop")

        while True:
            try:
                # Get pending automations
                pending_result = await self.get_pending_automations()
                pending_data = json.loads(pending_result)

                if pending_data.get('success') and pending_data.get('count', 0) > 0:
                    automations = pending_data['automations']
                    logger.info(f"Processing {len(automations)} pending automations")

                    # Process each automation
                    for automation in automations:
                        await self.process_automation_request(automation)
                        # Small delay between processing
                        await asyncio.sleep(1)

                # Wait before next check
                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error

    async def run_interactive(self):
        """Run the agent in interactive mode"""
        logger.info("Starting automation agent in interactive mode")
        await run_demo_loop(self.agent)

    async def run_single_task(self, task: str):
        """Run a single task with the agent"""
        logger.info(f"Running single task: {task}")
        result = await Runner.run(self.agent, task)
        print(result.final_output)
        return result

async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Automation Agent with OpenAI Agents SDK + MCP")
    parser.add_argument("--mode", choices=["monitor", "interactive", "task"], default="monitor",
                       help="Run mode: monitor (continuous), interactive (chat), or task (single)")
    parser.add_argument("--task", help="Single task to run (required for task mode)")

    args = parser.parse_args()

    # Setup directories
    Path(DEPLOY_PATH).mkdir(exist_ok=True)
    Path(LOG_PATH).mkdir(exist_ok=True)

    agent = AutomationAgent()

    try:
        if args.mode == "monitor":
            await agent.run_monitoring_loop()
        elif args.mode == "interactive":
            await agent.run_interactive()
        elif args.mode == "task":
            if not args.task:
                print("Task mode requires --task argument")
                return
            await agent.run_single_task(args.task)

    finally:
        # Cleanup MCP client
        await agent.mcp_client.stop_server()

if __name__ == "__main__":
    asyncio.run(main())