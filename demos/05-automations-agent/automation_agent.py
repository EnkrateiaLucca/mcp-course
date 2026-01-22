# /// script
# requires-python = ">=3.12"
# dependencies = ["claude-agent-sdk>=0.1.21"]
# ///

import asyncio
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    model="claude-sonnet-4-5",
    system_prompt="""
    You are an automation script generator assistant.
    You help users discover and generate automation scripts from a database.

    When asked about automations:
    1. Use list_automations to show available scripts
    2. Use get_automation with the ID to retrieve the full template
    3. Save scripts to the generated_scripts/ folder with descriptive names
    4. Explain what each script does and how to use it
    """,
    mcp_servers={
        "automation-db": {
            "type": "stdio",
            "command": "uv",
            "args": ["run", "automation_mcp_server.py"]
        }
    },
    permission_mode="bypassPermissions",
)

async def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║           Automation Generator - Claude Agent + MCP          ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")
    print("Ask me about available automations or request to generate one!\n")
    print("Examples:")
    print("  - What automations are available?")
    print("  - Generate the backup files automation")
    print("  - Show me file management scripts\n")
    print("Type 'quit' to exit\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        print()
        async for message in query(prompt=user_input, options=options):
            print(message, end="", flush=True)
        print("\n")

if __name__ == "__main__":
    asyncio.run(main())
