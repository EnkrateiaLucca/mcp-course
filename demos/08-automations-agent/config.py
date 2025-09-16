"""
Configuration settings for the Automation Agent system
"""
import os
from pathlib import Path
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class with all system settings"""

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

    # Google Sheets Configuration
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    GOOGLE_SHEETS_ID = os.getenv('GOOGLE_SHEETS_ID')
    GOOGLE_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    # MCP Server Configuration
    MCP_SERVER_HOST = os.getenv('MCP_SERVER_HOST', 'localhost')
    MCP_SERVER_PORT = int(os.getenv('MCP_SERVER_PORT', '5000'))
    MCP_SERVER_PATH = os.getenv('MCP_SERVER_PATH', './google_sheets_mcp_server.py')

    # Deployment Configuration
    AUTOMATION_DEPLOY_PATH = os.getenv('AUTOMATION_DEPLOY_PATH', '/tmp/automations')
    AUTOMATION_LOG_PATH = os.getenv('AUTOMATION_LOG_PATH', '/tmp/logs/automations')

    # Security Settings
    ENABLE_SCRIPT_SANDBOXING = os.getenv('ENABLE_SCRIPT_SANDBOXING', 'true').lower() == 'true'
    MAX_CONCURRENT_AUTOMATIONS = int(os.getenv('MAX_CONCURRENT_AUTOMATIONS', '10'))
    SCRIPT_TIMEOUT_SECONDS = int(os.getenv('SCRIPT_TIMEOUT_SECONDS', '300'))
    ALLOWED_AUTOMATION_TYPES = [
        'file_processor',
        'api_monitor',
        'data_sync',
        'notification_sender',
        'report_generator'
    ]

    # Monitoring Configuration
    PROMETHEUS_PORT = int(os.getenv('PROMETHEUS_PORT', '9090'))
    ENABLE_METRICS = os.getenv('ENABLE_METRICS', 'true').lower() == 'true'
    MONITORING_INTERVAL = int(os.getenv('MONITORING_INTERVAL', '30'))

    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ENABLE_FILE_LOGGING = os.getenv('ENABLE_FILE_LOGGING', 'true').lower() == 'true'

    # Sheet Structure Configuration
    SHEET_COLUMNS = {
        'automation_name': 0,   # Column A
        'automation_type': 1,   # Column B
        'configuration': 2,     # Column C
        'status': 3,            # Column D
        'created_date': 4,      # Column E
        'last_updated': 5,      # Column F
        'error_message': 6      # Column G
    }

    # Status Values
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_DEPLOYED = 'deployed'
    STATUS_FAILED = 'failed'
    STATUS_COMPLETED = 'completed'

    # Validation Rules
    VALIDATION_RULES = {
        'file_processor': {
            'required_fields': ['source_directory', 'actions'],
            'optional_fields': ['file_patterns', 'output_directory', 'schedule']
        },
        'api_monitor': {
            'required_fields': ['endpoint'],
            'optional_fields': ['check_interval', 'trigger_conditions', 'actions', 'notification_channels']
        },
        'data_sync': {
            'required_fields': ['source', 'destination'],
            'optional_fields': ['schedule', 'mapping', 'batch_size']
        },
        'notification_sender': {
            'required_fields': ['trigger_conditions', 'notification_channels'],
            'optional_fields': ['message_template', 'retry_policy']
        },
        'report_generator': {
            'required_fields': ['report_type'],
            'optional_fields': ['schedule', 'recipients', 'format']
        }
    }

    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        directories = [
            cls.AUTOMATION_DEPLOY_PATH,
            cls.AUTOMATION_LOG_PATH,
            f"{cls.AUTOMATION_DEPLOY_PATH}/reports",
            f"{cls.AUTOMATION_DEPLOY_PATH}/backups"
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate_config(cls) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []

        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required")

        if not cls.GOOGLE_APPLICATION_CREDENTIALS:
            errors.append("GOOGLE_APPLICATION_CREDENTIALS is required")
        elif not os.path.exists(cls.GOOGLE_APPLICATION_CREDENTIALS):
            errors.append(f"Credentials file not found: {cls.GOOGLE_APPLICATION_CREDENTIALS}")

        if not cls.GOOGLE_SHEETS_ID:
            errors.append("GOOGLE_SHEETS_ID is required")

        return errors

    @classmethod
    def get_example_configs(cls) -> Dict[str, Dict[str, Any]]:
        """Get example configurations for each automation type"""
        return {
            "file_processor": {
                "type": "file_processor",
                "source_directory": "/path/to/watch",
                "file_patterns": ["*.csv", "*.json"],
                "actions": ["validate", "transform", "archive"],
                "schedule": "*/5 * * * *",
                "output_directory": "/path/to/processed"
            },
            "api_monitor": {
                "type": "api_monitor",
                "endpoint": "https://api.example.com/status",
                "check_interval": 300,
                "trigger_conditions": ["status != 'healthy'"],
                "actions": ["send_alert", "log_incident"],
                "notification_channels": ["email", "slack"]
            },
            "data_sync": {
                "type": "data_sync",
                "source": {"type": "database", "connection": "postgresql://..."},
                "destination": {"type": "api", "endpoint": "https://api.target.com"},
                "schedule": "0 2 * * *",
                "mapping": {"source_field": "dest_field"},
                "batch_size": 1000
            },
            "notification_sender": {
                "type": "notification_sender",
                "trigger_conditions": ["error_count > 5", "response_time > 1000"],
                "notification_channels": ["email", "slack", "sms"],
                "message_template": "Alert: {condition} triggered at {timestamp}"
            },
            "report_generator": {
                "type": "report_generator",
                "report_type": "daily_summary",
                "schedule": "0 8 * * *",
                "recipients": ["team@example.com"],
                "format": "pdf"
            }
        }