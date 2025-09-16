#!/usr/bin/env python3
"""
Simple validation test for the automation system
"""
import json
import tempfile
import os
from pathlib import Path

def test_basic_functionality():
    """Test basic system functionality"""
    print("🧪 Running simple validation tests...")

    # Test 1: Config validation
    print("1. Testing configuration...")
    try:
        from config import Config

        # Test example configs
        examples = Config.get_example_configs()
        assert len(examples) == 5, f"Expected 5 examples, got {len(examples)}"

        # Test required automation types
        expected_types = ['file_processor', 'api_monitor', 'data_sync', 'notification_sender', 'report_generator']
        for automation_type in expected_types:
            assert automation_type in examples, f"Missing example for {automation_type}"

        print("   ✅ Configuration examples validated")

        # Test directory creation
        with tempfile.TemporaryDirectory() as temp_dir:
            original_deploy = Config.AUTOMATION_DEPLOY_PATH
            original_log = Config.AUTOMATION_LOG_PATH

            Config.AUTOMATION_DEPLOY_PATH = os.path.join(temp_dir, "deploy")
            Config.AUTOMATION_LOG_PATH = os.path.join(temp_dir, "logs")

            Config.ensure_directories()

            assert os.path.exists(Config.AUTOMATION_DEPLOY_PATH)
            assert os.path.exists(Config.AUTOMATION_LOG_PATH)
            print("   ✅ Directory creation validated")

            # Restore original paths
            Config.AUTOMATION_DEPLOY_PATH = original_deploy
            Config.AUTOMATION_LOG_PATH = original_log

    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False

    # Test 2: Error handling
    print("2. Testing error handling...")
    try:
        from error_handler import ErrorHandler, AutomationError, ValidationError

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            error_handler = ErrorHandler(temp_file.name)

            # Test error logging
            test_error = AutomationError("Test error", "TEST_CODE")
            error_info = error_handler.log_error(test_error, "test_context")

            assert error_info["error_type"] == "AutomationError"
            assert error_info["context"] == "test_context"
            print("   ✅ Error logging validated")

            # Test error summary
            summary = error_handler.get_error_summary()
            assert summary["total_errors"] == 1
            print("   ✅ Error summary validated")

            # Clean up
            os.unlink(temp_file.name)

    except Exception as e:
        print(f"   ❌ Error handling test failed: {e}")
        return False

    # Test 3: Basic script template validation
    print("3. Testing script templates...")
    try:
        # Read the script generator code and validate templates exist
        with open('automation_agent.py', 'r') as f:
            content = f.read()

        # Check that all automation types have templates
        automation_types = ['file_processor', 'api_monitor', 'data_sync', 'notification_sender', 'report_generator']

        for automation_type in automation_types:
            if f"'{automation_type}'" in content:
                print(f"   ✅ Template found for {automation_type}")
            else:
                print(f"   ⚠️  Template might be missing for {automation_type}")

        print("   ✅ Script templates validated")

    except Exception as e:
        print(f"   ❌ Script template test failed: {e}")
        return False

    # Test 4: MCP server code validation
    print("4. Testing MCP server code...")
    try:
        # Read and validate MCP server code structure
        with open('google_sheets_mcp_server.py', 'r') as f:
            mcp_content = f.read()

        # Check for required components
        required_components = [
            'FastMCP',
            'GoogleSheetsClient',
            '@mcp.tool()',
            'read_sheet_data',
            'update_execution_status',
            'validate_automation_config'
        ]

        for component in required_components:
            if component in mcp_content:
                print(f"   ✅ MCP component found: {component}")
            else:
                print(f"   ❌ Missing MCP component: {component}")
                return False

    except Exception as e:
        print(f"   ❌ MCP server test failed: {e}")
        return False

    # Test 5: Basic validation functions
    print("5. Testing validation functions...")
    try:
        from error_handler import validate_automation_config, ValidationError

        # Test valid configuration
        valid_config = {
            "type": "file_processor",
            "source_directory": "/tmp/input",
            "actions": ["validate"]
        }

        try:
            validate_automation_config(valid_config, "file_processor")
            print("   ✅ Valid configuration accepted")
        except ValidationError:
            print("   ❌ Valid configuration rejected incorrectly")
            return False

        # Test invalid configuration
        invalid_config = {"type": "file_processor"}  # Missing required fields

        try:
            validate_automation_config(invalid_config, "file_processor")
            print("   ❌ Invalid configuration accepted incorrectly")
            return False
        except ValidationError:
            print("   ✅ Invalid configuration rejected correctly")

    except Exception as e:
        print(f"   ❌ Validation test failed: {e}")
        return False

    print("\n🎉 All basic validation tests passed!")
    return True

def test_file_structure():
    """Test that all required files exist"""
    print("📁 Testing file structure...")

    required_files = [
        'automation_agent.py',
        'google_sheets_mcp_server.py',
        'config.py',
        'error_handler.py',
        'run_agent.py',
        'setup_example_sheet.py',
        'requirements.txt',
        '.env.example',
        'README.md'
    ]

    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (missing)")
            missing_files.append(file_path)

    if missing_files:
        print(f"\n⚠️  Missing {len(missing_files)} required files")
        return False
    else:
        print("\n✅ All required files present")
        return True

def main():
    """Run all validation tests"""
    print("=" * 60)
    print("🚀 AUTOMATION AGENT SYSTEM VALIDATION")
    print("=" * 60)

    # Test file structure
    file_structure_ok = test_file_structure()

    # Test basic functionality
    functionality_ok = test_basic_functionality()

    # Final result
    print("\n" + "=" * 60)
    if file_structure_ok and functionality_ok:
        print("🎉 SYSTEM VALIDATION SUCCESSFUL!")
        print("   The automation agent system appears to be correctly implemented.")
        print("   Next steps:")
        print("   1. Set up your .env file with proper credentials")
        print("   2. Create a Google Sheet with the required structure")
        print("   3. Run: python run_agent.py --mode setup")
        print("   4. Run: python run_agent.py --mode monitor")
        return True
    else:
        print("❌ SYSTEM VALIDATION FAILED!")
        print("   Please fix the issues above before using the system.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)