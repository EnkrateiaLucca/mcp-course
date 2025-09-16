#!/usr/bin/env python3
"""
Setup example Google Sheet with sample automation configurations
"""
import json
from datetime import datetime
from google_sheets_mcp_server import GoogleSheetsClient
from config import Config

def create_sample_automations():
    """Create sample automation configurations"""
    return [
        {
            "automation_name": "Daily File Processor",
            "automation_type": "file_processor",
            "configuration": {
                "type": "file_processor",
                "source_directory": "/tmp/input",
                "file_patterns": ["*.csv", "*.json"],
                "actions": ["validate", "transform", "archive"],
                "schedule": "0 2 * * *",
                "output_directory": "/tmp/processed"
            },
            "status": "pending",
            "created_date": datetime.now().isoformat(),
            "last_updated": "",
            "error_message": ""
        },
        {
            "automation_name": "API Health Monitor",
            "automation_type": "api_monitor",
            "configuration": {
                "type": "api_monitor",
                "endpoint": "https://httpbin.org/status/200",
                "check_interval": 60,
                "trigger_conditions": ["status_code != 200"],
                "actions": ["send_alert", "log_incident"],
                "notification_channels": ["email"]
            },
            "status": "pending",
            "created_date": datetime.now().isoformat(),
            "last_updated": "",
            "error_message": ""
        },
        {
            "automation_name": "User Data Sync",
            "automation_type": "data_sync",
            "configuration": {
                "type": "data_sync",
                "source": {"type": "api", "endpoint": "https://jsonplaceholder.typicode.com/users"},
                "destination": {"type": "api", "endpoint": "https://httpbin.org/post"},
                "schedule": "0 6 * * *",
                "mapping": {"id": "user_id", "name": "username", "email": "user_email"},
                "batch_size": 50
            },
            "status": "pending",
            "created_date": datetime.now().isoformat(),
            "last_updated": "",
            "error_message": ""
        },
        {
            "automation_name": "Error Alert System",
            "automation_type": "notification_sender",
            "configuration": {
                "type": "notification_sender",
                "trigger_conditions": ["error_count > 10", "response_time > 2000"],
                "notification_channels": ["email", "slack"],
                "message_template": "ALERT: {condition} detected at {timestamp}"
            },
            "status": "pending",
            "created_date": datetime.now().isoformat(),
            "last_updated": "",
            "error_message": ""
        },
        {
            "automation_name": "Daily Summary Report",
            "automation_type": "report_generator",
            "configuration": {
                "type": "report_generator",
                "report_type": "daily_summary",
                "schedule": "0 9 * * *",
                "recipients": ["admin@example.com"],
                "format": "html"
            },
            "status": "pending",
            "created_date": datetime.now().isoformat(),
            "last_updated": "",
            "error_message": ""
        }
    ]

def setup_sheet_headers(client: GoogleSheetsClient):
    """Setup sheet headers"""
    headers = [
        "Automation Name",
        "Automation Type",
        "Configuration",
        "Status",
        "Created Date",
        "Last Updated",
        "Error Message"
    ]

    client.update_row(1, headers)
    print("Headers created successfully")

def populate_sample_data(client: GoogleSheetsClient):
    """Populate sheet with sample automation data"""
    sample_automations = create_sample_automations()

    for i, automation in enumerate(sample_automations, start=2):
        row_data = [
            automation["automation_name"],
            automation["automation_type"],
            json.dumps(automation["configuration"]),
            automation["status"],
            automation["created_date"],
            automation["last_updated"],
            automation["error_message"]
        ]

        client.update_row(i, row_data)
        print(f"Created automation: {automation['automation_name']}")

def main():
    """Main setup function"""
    print("Setting up example Google Sheet for Automation Agent...")

    # Validate configuration
    config_errors = Config.validate_config()
    if config_errors:
        print("Configuration errors:")
        for error in config_errors:
            print(f"  - {error}")
        return

    try:
        # Initialize client
        client = GoogleSheetsClient()

        # Setup headers
        setup_sheet_headers(client)

        # Populate sample data
        populate_sample_data(client)

        print("\n✅ Example sheet setup completed successfully!")
        print(f"Sheet ID: {Config.GOOGLE_SHEETS_ID}")
        print("\nSample automations created:")

        sample_automations = create_sample_automations()
        for automation in sample_automations:
            print(f"  - {automation['automation_name']} ({automation['automation_type']})")

        print("\nYou can now run the automation agent to process these automations.")

    except Exception as e:
        print(f"❌ Error setting up example sheet: {e}")

if __name__ == "__main__":
    main()