#!/usr/bin/env python3
"""
Test suite for the Automation Agent system
"""
import asyncio
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from config import Config
from error_handler import ErrorHandler, AutomationError, ValidationError
from automation_agent import AutomationAgent, AutomationScriptGenerator, MCPClient

class TestRunner:
    """Test runner for automation system"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def run_test(self, test_name: str, test_func):
        """Run a single test"""
        try:
            print(f"Running {test_name}...", end=" ")
            if asyncio.iscoroutinefunction(test_func):
                asyncio.run(test_func())
            else:
                test_func()
            print("✅ PASSED")
            self.passed += 1
        except Exception as e:
            print(f"❌ FAILED: {e}")
            self.failed += 1
            self.errors.append((test_name, str(e)))

    def print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        print(f"\n{'='*50}")
        print(f"TEST SUMMARY")
        print(f"{'='*50}")
        print(f"Total tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")

        if self.errors:
            print(f"\nFAILED TESTS:")
            for test_name, error in self.errors:
                print(f"  - {test_name}: {error}")

        if self.failed == 0:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n⚠️  {self.failed} tests failed")

        return self.failed == 0

def test_config_validation():
    """Test configuration validation"""
    # Test with missing required config
    original_key = os.getenv('OPENAI_API_KEY')
    if 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY']

    errors = Config.validate_config()
    assert len(errors) > 0, "Should have configuration errors"
    assert any('OPENAI_API_KEY' in error for error in errors), "Should mention missing API key"

    # Restore original key if it existed
    if original_key:
        os.environ['OPENAI_API_KEY'] = original_key

def test_script_generator():
    """Test automation script generator"""
    generator = AutomationScriptGenerator()

    # Test file processor script generation
    config = {
        "type": "file_processor",
        "source_directory": "/tmp/test",
        "actions": ["validate", "transform"]
    }

    script = generator.generate_script("test_automation", "file_processor", config)
    assert "file_processor" in script.lower(), "Script should contain automation type"
    assert "/tmp/test" in script, "Script should contain configuration values"
    assert "validate" in script, "Script should contain actions"

def test_error_handler():
    """Test error handling functionality"""
    with tempfile.TemporaryDirectory() as temp_dir:
        error_handler = ErrorHandler(log_path=os.path.join(temp_dir, "test_errors.log"))

        # Test error logging
        test_error = AutomationError("Test error", "TEST_ERROR")
        error_info = error_handler.log_error(
            test_error,
            context="test_context",
            automation_name="test_automation"
        )

        assert error_info["error_type"] == "AutomationError"
        assert error_info["context"] == "test_context"
        assert error_info["automation_name"] == "test_automation"

        # Test error summary
        summary = error_handler.get_error_summary()
        assert summary["total_errors"] == 1
        assert "AutomationError:test_context" in summary["error_counts"]

def test_validation_functions():
    """Test automation configuration validation"""
    from error_handler import validate_automation_config, ValidationError

    # Test valid file processor config
    valid_config = {
        "type": "file_processor",
        "source_directory": "/tmp/input",
        "actions": ["validate"]
    }

    try:
        validate_automation_config(valid_config, "file_processor")
    except ValidationError:
        raise AssertionError("Valid configuration should not raise ValidationError")

    # Test invalid config (missing required field)
    invalid_config = {
        "type": "file_processor"
        # Missing source_directory and actions
    }

    try:
        validate_automation_config(invalid_config, "file_processor")
        raise AssertionError("Invalid configuration should raise ValidationError")
    except ValidationError as e:
        assert len(e.validation_errors) > 0, "Should have validation errors"

async def test_mcp_client_mock():
    """Test MCP client functionality with mocking"""
    client = MCPClient()

    # Mock the subprocess creation
    with patch('asyncio.create_subprocess_exec') as mock_subprocess:
        mock_process = Mock()
        mock_process.stdin = Mock()
        mock_process.stdout = Mock()
        mock_process.stderr = Mock()

        # Mock successful response
        mock_process.stdout.readline.return_value = asyncio.coroutine(
            lambda: b'{"result": {"success": true, "message": "test"}}\n'
        )()

        mock_subprocess.return_value = mock_process
        client.process = mock_process

        result = await client.send_request("test_method", {"test": "param"})
        assert result.get("success") is True

def test_config_example_generation():
    """Test configuration example generation"""
    examples = Config.get_example_configs()

    assert "file_processor" in examples
    assert "api_monitor" in examples
    assert "data_sync" in examples
    assert "notification_sender" in examples
    assert "report_generator" in examples

    # Validate example structure
    file_processor_example = examples["file_processor"]
    assert file_processor_example["type"] == "file_processor"
    assert "source_directory" in file_processor_example
    assert "actions" in file_processor_example

def test_directory_creation():
    """Test directory creation functionality"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Temporarily change config paths
        original_deploy = Config.AUTOMATION_DEPLOY_PATH
        original_log = Config.AUTOMATION_LOG_PATH

        Config.AUTOMATION_DEPLOY_PATH = os.path.join(temp_dir, "deploy")
        Config.AUTOMATION_LOG_PATH = os.path.join(temp_dir, "logs")

        Config.ensure_directories()

        assert os.path.exists(Config.AUTOMATION_DEPLOY_PATH)
        assert os.path.exists(Config.AUTOMATION_LOG_PATH)
        assert os.path.exists(os.path.join(Config.AUTOMATION_DEPLOY_PATH, "reports"))
        assert os.path.exists(os.path.join(Config.AUTOMATION_DEPLOY_PATH, "backups"))

        # Restore original paths
        Config.AUTOMATION_DEPLOY_PATH = original_deploy
        Config.AUTOMATION_LOG_PATH = original_log

async def test_automation_agent_tools():
    """Test automation agent tool functionality"""
    agent = AutomationAgent()

    # Test get_pending_automations with mocked MCP client
    with patch.object(agent.mcp_client, 'send_request') as mock_send:
        mock_send.return_value = {
            "success": True,
            "automations": [
                {
                    "automation_name": "test_automation",
                    "automation_type": "file_processor",
                    "status": "pending"
                }
            ]
        }

        result = await agent.get_pending_automations()
        result_data = json.loads(result)
        assert result_data["success"] is True
        assert len(result_data["automations"]) == 1

def test_script_templates_completeness():
    """Test that all automation types have script templates"""
    generator = AutomationScriptGenerator()
    expected_types = Config.ALLOWED_AUTOMATION_TYPES

    for automation_type in expected_types:
        assert automation_type in generator.SCRIPT_TEMPLATES, \
            f"Missing script template for {automation_type}"

        # Test that each template can be formatted
        template = generator.SCRIPT_TEMPLATES[automation_type]
        test_config = {"type": automation_type}

        try:
            formatted_script = template.format(
                config_json=json.dumps(test_config),
                automation_name="test",
                LOG_PATH="/tmp/logs"
            )
            assert len(formatted_script) > 0, f"Template for {automation_type} produced empty script"
        except Exception as e:
            raise AssertionError(f"Template for {automation_type} failed to format: {e}")

def run_all_tests():
    """Run all tests"""
    runner = TestRunner()

    # Configuration tests
    runner.run_test("Config Validation", test_config_validation)
    runner.run_test("Directory Creation", test_directory_creation)
    runner.run_test("Config Examples", test_config_example_generation)

    # Script generation tests
    runner.run_test("Script Generator", test_script_generator)
    runner.run_test("Script Templates", test_script_templates_completeness)

    # Error handling tests
    runner.run_test("Error Handler", test_error_handler)
    runner.run_test("Validation Functions", test_validation_functions)

    # MCP and agent tests
    runner.run_test("MCP Client Mock", test_mcp_client_mock)
    runner.run_test("Agent Tools", test_automation_agent_tools)

    return runner.print_summary()

def main():
    """Main test entry point"""
    print("🧪 Running Automation Agent Test Suite")
    print("=" * 50)

    try:
        success = run_all_tests()
        exit_code = 0 if success else 1
    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")
        exit_code = 1

    exit(exit_code)

if __name__ == "__main__":
    main()