#!/usr/bin/env python3
"""
Google Sheets MCP Server for Automation Configuration
Provides tools and resources for reading/writing automation configs from Google Sheets
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP("google-sheets-automation")

# Google Sheets configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_ID')

# Column mapping for automation sheet
COLUMN_MAPPING = {
    'automation_name': 0,  # Column A
    'automation_type': 1,  # Column B
    'configuration': 2,    # Column C
    'status': 3,           # Column D
    'created_date': 4,     # Column E
    'last_updated': 5,     # Column F
    'error_message': 6     # Column G
}

class GoogleSheetsClient:
    """Client for interacting with Google Sheets API"""

    def __init__(self):
        self.service = None
        self.sheet = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Google Sheets API client"""
        try:
            if not CREDENTIALS_PATH or not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(f"Credentials file not found: {CREDENTIALS_PATH}")

            creds = service_account.Credentials.from_service_account_file(
                CREDENTIALS_PATH, scopes=SCOPES
            )
            self.service = build('sheets', 'v4', credentials=creds)
            self.sheet = self.service.spreadsheets()
            logger.info("Google Sheets client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets client: {e}")
            raise

    def read_data(self, range_name: str = 'A:G') -> List[List[str]]:
        """Read data from the spreadsheet"""
        try:
            result = self.sheet.values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=range_name
            ).execute()
            values = result.get('values', [])
            logger.debug(f"Read {len(values)} rows from sheet")
            return values
        except HttpError as e:
            logger.error(f"Error reading from sheet: {e}")
            raise

    def update_cell(self, row: int, column: str, value: str) -> bool:
        """Update a single cell in the spreadsheet"""
        try:
            range_name = f'{column}{row}'
            body = {'values': [[value]]}

            self.sheet.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()

            logger.debug(f"Updated cell {range_name} with value: {value}")
            return True
        except HttpError as e:
            logger.error(f"Error updating cell: {e}")
            return False

    def update_row(self, row: int, values: List[str]) -> bool:
        """Update an entire row in the spreadsheet"""
        try:
            range_name = f'A{row}:G{row}'
            body = {'values': [values]}

            self.sheet.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()

            logger.debug(f"Updated row {row}")
            return True
        except HttpError as e:
            logger.error(f"Error updating row: {e}")
            return False

    def append_row(self, values: List[str]) -> bool:
        """Append a new row to the spreadsheet"""
        try:
            body = {'values': [values]}

            self.sheet.values().append(
                spreadsheetId=SPREADSHEET_ID,
                range='A:G',
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()

            logger.debug(f"Appended new row to sheet")
            return True
        except HttpError as e:
            logger.error(f"Error appending row: {e}")
            return False

# Initialize client
sheets_client = GoogleSheetsClient()

@mcp.tool()
async def read_sheet_data(
    sheet_id: Optional[str] = None,
    range_name: str = "A:G"
) -> Dict[str, Any]:
    """
    Read automation configurations from Google Sheets

    Args:
        sheet_id: Optional sheet ID (uses env var if not provided)
        range_name: Range to read (default: A:G)

    Returns:
        Dictionary containing automation configurations
    """
    try:
        # Use provided sheet_id or default from env
        if sheet_id:
            global SPREADSHEET_ID
            SPREADSHEET_ID = sheet_id

        # Read data from sheet
        data = sheets_client.read_data(range_name)

        if not data:
            return {
                "success": False,
                "message": "No data found in sheet",
                "automations": []
            }

        # Parse data into structured format
        automations = []
        headers = data[0] if data else []

        for i, row in enumerate(data[1:], start=2):  # Start from row 2 (after headers)
            if len(row) >= 3:  # Minimum required columns
                automation = {
                    "row_number": i,
                    "automation_name": row[0] if len(row) > 0 else "",
                    "automation_type": row[1] if len(row) > 1 else "",
                    "configuration": json.loads(row[2]) if len(row) > 2 and row[2] else {},
                    "status": row[3] if len(row) > 3 else "pending",
                    "created_date": row[4] if len(row) > 4 else "",
                    "last_updated": row[5] if len(row) > 5 else "",
                    "error_message": row[6] if len(row) > 6 else ""
                }
                automations.append(automation)

        return {
            "success": True,
            "message": f"Read {len(automations)} automation configurations",
            "automations": automations
        }

    except Exception as e:
        logger.error(f"Error reading sheet data: {e}")
        return {
            "success": False,
            "message": str(e),
            "automations": []
        }

@mcp.tool()
async def validate_automation_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate automation parameters and requirements

    Args:
        config: Automation configuration to validate

    Returns:
        Validation result with any errors/warnings
    """
    errors = []
    warnings = []

    # Check required fields
    required_fields = ['type']
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field: {field}")

    # Validate automation type
    valid_types = ['file_processor', 'api_monitor', 'data_sync', 'notification_sender', 'report_generator']
    if config.get('type') and config['type'] not in valid_types:
        errors.append(f"Invalid automation type: {config['type']}. Must be one of {valid_types}")

    # Type-specific validation
    automation_type = config.get('type')

    if automation_type == 'file_processor':
        if not config.get('source_directory'):
            errors.append("file_processor requires 'source_directory'")
        if not config.get('file_patterns'):
            warnings.append("No file_patterns specified, will process all files")

    elif automation_type == 'api_monitor':
        if not config.get('endpoint'):
            errors.append("api_monitor requires 'endpoint'")
        if not config.get('check_interval'):
            warnings.append("No check_interval specified, defaulting to 300 seconds")

    elif automation_type == 'data_sync':
        if not config.get('source'):
            errors.append("data_sync requires 'source'")
        if not config.get('destination'):
            errors.append("data_sync requires 'destination'")
        if not config.get('schedule'):
            warnings.append("No schedule specified, will run on-demand only")

    elif automation_type == 'notification_sender':
        if not config.get('trigger_conditions'):
            errors.append("notification_sender requires 'trigger_conditions'")
        if not config.get('notification_channels'):
            errors.append("notification_sender requires 'notification_channels'")

    elif automation_type == 'report_generator':
        if not config.get('report_type'):
            errors.append("report_generator requires 'report_type'")
        if not config.get('schedule'):
            warnings.append("No schedule specified, will run on-demand only")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "config": config
    }

@mcp.tool()
async def update_execution_status(
    row: int,
    status: str,
    error_msg: str = ""
) -> Dict[str, Any]:
    """
    Update the execution status in the sheet

    Args:
        row: Row number to update
        status: New status (pending, processing, deployed, failed)
        error_msg: Optional error message

    Returns:
        Success status
    """
    try:
        # Update status column (D)
        sheets_client.update_cell(row, 'D', status)

        # Update last updated column (F) with current timestamp
        sheets_client.update_cell(row, 'F', datetime.now().isoformat())

        # Update error message column (G) if provided
        if error_msg:
            sheets_client.update_cell(row, 'G', error_msg)

        logger.info(f"Updated row {row} status to {status}")

        return {
            "success": True,
            "message": f"Updated row {row} status to {status}",
            "row": row,
            "status": status
        }

    except Exception as e:
        logger.error(f"Error updating execution status: {e}")
        return {
            "success": False,
            "message": str(e),
            "row": row,
            "status": status
        }

@mcp.tool()
async def list_available_automations(
    filter_status: Optional[str] = "pending"
) -> Dict[str, Any]:
    """
    Get all pending automation requests from the sheet

    Args:
        filter_status: Status to filter by (default: pending)

    Returns:
        List of automations matching the filter
    """
    try:
        # Read all data
        result = await read_sheet_data()

        if not result['success']:
            return result

        # Filter by status if specified
        automations = result['automations']
        if filter_status:
            automations = [a for a in automations if a.get('status') == filter_status]

        return {
            "success": True,
            "message": f"Found {len(automations)} automations with status '{filter_status}'",
            "automations": automations
        }

    except Exception as e:
        logger.error(f"Error listing automations: {e}")
        return {
            "success": False,
            "message": str(e),
            "automations": []
        }

@mcp.tool()
async def create_automation_entry(
    automation_name: str,
    automation_type: str,
    configuration: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a new automation entry in the sheet

    Args:
        automation_name: Name of the automation
        automation_type: Type of automation
        configuration: Configuration parameters as dict

    Returns:
        Success status with row number
    """
    try:
        # Validate configuration first
        validation = await validate_automation_config(configuration)
        if not validation['valid']:
            return {
                "success": False,
                "message": f"Invalid configuration: {validation['errors']}",
                "validation": validation
            }

        # Prepare row data
        row_data = [
            automation_name,
            automation_type,
            json.dumps(configuration),
            "pending",
            datetime.now().isoformat(),
            "",  # last_updated
            ""   # error_message
        ]

        # Append to sheet
        success = sheets_client.append_row(row_data)

        if success:
            return {
                "success": True,
                "message": f"Created automation entry: {automation_name}",
                "automation_name": automation_name
            }
        else:
            return {
                "success": False,
                "message": "Failed to create automation entry"
            }

    except Exception as e:
        logger.error(f"Error creating automation entry: {e}")
        return {
            "success": False,
            "message": str(e)
        }

# Resources
@mcp.resource("uri://automation-configs")
async def get_automation_configs() -> str:
    """Get current automation configurations"""
    result = await read_sheet_data()
    return json.dumps(result, indent=2)

@mcp.resource("uri://execution-logs")
async def get_execution_logs() -> str:
    """Get historical execution data and status updates"""
    result = await read_sheet_data()
    if result['success']:
        # Filter to only completed or failed automations
        logs = [a for a in result['automations']
                if a.get('status') in ['completed', 'deployed', 'failed']]
        return json.dumps({
            "success": True,
            "logs": logs
        }, indent=2)
    return json.dumps(result, indent=2)

@mcp.resource("uri://template-definitions")
async def get_template_definitions() -> str:
    """Get available automation script templates"""
    templates = {
        "file_processor": {
            "description": "Monitor directories and process files based on rules",
            "required_params": ["source_directory", "actions"],
            "optional_params": ["file_patterns", "output_directory", "schedule"],
            "example_config": {
                "type": "file_processor",
                "source_directory": "/path/to/watch",
                "file_patterns": ["*.csv", "*.json"],
                "actions": ["validate", "transform", "archive"],
                "schedule": "*/5 * * * *",
                "output_directory": "/path/to/processed"
            }
        },
        "api_monitor": {
            "description": "Monitor APIs and trigger actions on changes",
            "required_params": ["endpoint"],
            "optional_params": ["check_interval", "trigger_conditions", "actions", "notification_channels"],
            "example_config": {
                "type": "api_monitor",
                "endpoint": "https://api.example.com/status",
                "check_interval": 300,
                "trigger_conditions": ["status != 'healthy'"],
                "actions": ["send_alert", "log_incident"],
                "notification_channels": ["email", "slack"]
            }
        },
        "data_sync": {
            "description": "Synchronize data between systems on schedules",
            "required_params": ["source", "destination"],
            "optional_params": ["schedule", "mapping", "batch_size"],
            "example_config": {
                "type": "data_sync",
                "source": {"type": "database", "connection": "postgresql://..."},
                "destination": {"type": "api", "endpoint": "https://api.target.com"},
                "schedule": "0 2 * * *",
                "mapping": {"source_field": "dest_field"},
                "batch_size": 1000
            }
        },
        "notification_sender": {
            "description": "Send notifications based on triggers",
            "required_params": ["trigger_conditions", "notification_channels"],
            "optional_params": ["message_template", "retry_policy"],
            "example_config": {
                "type": "notification_sender",
                "trigger_conditions": ["error_count > 5", "response_time > 1000"],
                "notification_channels": ["email", "slack", "sms"],
                "message_template": "Alert: {condition} triggered at {timestamp}"
            }
        },
        "report_generator": {
            "description": "Generate and distribute reports automatically",
            "required_params": ["report_type"],
            "optional_params": ["schedule", "recipients", "format"],
            "example_config": {
                "type": "report_generator",
                "report_type": "daily_summary",
                "schedule": "0 8 * * *",
                "recipients": ["team@example.com"],
                "format": "pdf"
            }
        }
    }
    return json.dumps(templates, indent=2)

if __name__ == "__main__":
    logger.info("Starting Google Sheets MCP Server for Automation")
    mcp.run(transport="stdio")