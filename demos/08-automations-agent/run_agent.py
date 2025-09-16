#!/usr/bin/env python3
"""
Main entry point for running the Automation Agent system
"""
import asyncio
import argparse
import sys
from pathlib import Path
from loguru import logger

from automation_agent import AutomationAgent
from config import Config

def setup_logging():
    """Setup logging configuration"""
    logger.remove()  # Remove default handler

    # Console logging
    logger.add(
        sys.stderr,
        level=Config.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    # File logging if enabled
    if Config.ENABLE_FILE_LOGGING:
        log_file = Path(Config.AUTOMATION_LOG_PATH) / "automation_agent.log"
        logger.add(
            log_file,
            level=Config.LOG_LEVEL,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="10 MB",
            retention="7 days"
        )

async def run_setup_mode():
    """Run in setup mode to initialize the system"""
    print("🚀 Setting up Automation Agent system...")

    # Validate configuration
    config_errors = Config.validate_config()
    if config_errors:
        print("❌ Configuration errors found:")
        for error in config_errors:
            print(f"   - {error}")
        print("\nPlease check your .env file and fix the configuration issues.")
        return False

    # Ensure directories exist
    Config.ensure_directories()
    print("✅ Created necessary directories")

    # Check if Google Sheets is accessible
    try:
        from google_sheets_mcp_server import GoogleSheetsClient
        client = GoogleSheetsClient()
        data = client.read_data("A1:A1")  # Test read
        print("✅ Google Sheets connection successful")
    except Exception as e:
        print(f"❌ Google Sheets connection failed: {e}")
        return False

    print("\n🎉 Setup completed successfully!")
    print("Run with --mode monitor to start processing automations")
    return True

async def run_monitor_mode():
    """Run in monitoring mode (continuous processing)"""
    logger.info("Starting Automation Agent in monitoring mode")

    agent = AutomationAgent()
    try:
        await agent.run_monitoring_loop()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    finally:
        await agent.mcp_client.stop_server()
        logger.info("Automation Agent stopped")

async def run_interactive_mode():
    """Run in interactive chat mode"""
    logger.info("Starting Automation Agent in interactive mode")

    agent = AutomationAgent()
    try:
        await agent.run_interactive()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    finally:
        await agent.mcp_client.stop_server()

async def run_task_mode(task: str):
    """Run a single task"""
    logger.info(f"Running single task: {task}")

    agent = AutomationAgent()
    try:
        result = await agent.run_single_task(task)
        print("\n" + "="*50)
        print("TASK RESULT:")
        print("="*50)
        print(result.final_output)
    finally:
        await agent.mcp_client.stop_server()

async def run_test_mode():
    """Run in test mode to validate system components"""
    print("🧪 Running system tests...")

    # Test 1: Configuration validation
    print("Testing configuration...")
    config_errors = Config.validate_config()
    if config_errors:
        print(f"❌ Configuration test failed: {config_errors}")
        return False
    print("✅ Configuration test passed")

    # Test 2: Google Sheets connectivity
    print("Testing Google Sheets connectivity...")
    try:
        from google_sheets_mcp_server import GoogleSheetsClient
        client = GoogleSheetsClient()
        data = client.read_data("A1:G1")
        print("✅ Google Sheets connectivity test passed")
    except Exception as e:
        print(f"❌ Google Sheets connectivity test failed: {e}")
        return False

    # Test 3: MCP server
    print("Testing MCP server...")
    try:
        agent = AutomationAgent()
        await agent.mcp_client.start_server()
        await asyncio.sleep(1)  # Give server time to start
        await agent.mcp_client.stop_server()
        print("✅ MCP server test passed")
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        return False

    print("\n🎉 All tests passed! System is ready to use.")
    return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Automation Agent with OpenAI Agents SDK + MCP",
        epilog="""
Examples:
  python run_agent.py --mode setup          # Setup and validate system
  python run_agent.py --mode monitor        # Continuous monitoring mode
  python run_agent.py --mode interactive    # Interactive chat mode
  python run_agent.py --mode task --task "Get all pending automations"
  python run_agent.py --mode test           # Run system tests
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--mode",
        choices=["setup", "monitor", "interactive", "task", "test"],
        default="monitor",
        help="Run mode (default: monitor)"
    )

    parser.add_argument(
        "--task",
        help="Single task to run (required for task mode)"
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )

    args = parser.parse_args()

    # Update log level if specified
    Config.LOG_LEVEL = args.log_level

    # Setup logging
    setup_logging()

    # Ensure directories exist
    Config.ensure_directories()

    try:
        if args.mode == "setup":
            success = asyncio.run(run_setup_mode())
            sys.exit(0 if success else 1)

        elif args.mode == "monitor":
            asyncio.run(run_monitor_mode())

        elif args.mode == "interactive":
            asyncio.run(run_interactive_mode())

        elif args.mode == "task":
            if not args.task:
                print("❌ Task mode requires --task argument")
                sys.exit(1)
            asyncio.run(run_task_mode(args.task))

        elif args.mode == "test":
            success = asyncio.run(run_test_mode())
            sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()