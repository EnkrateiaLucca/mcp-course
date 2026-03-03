#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "mcp[cli]==1.9.3",
#     "anthropic",
#     "python-dotenv",
#     "rich"
# ]
# ///

# The HOST is the user-facing application.
# It imports and uses the MCP CLIENT, which handles protocol communication
# with the MCP SERVER.
#
# Architecture: Host (this file) -> Client (mcp_client.py) -> Server (mcp_server.py)

import asyncio
import sys
from mcp_client import SimpleMCPClient


async def interactive_mode(client: SimpleMCPClient):
    """Simple interactive loop to test the tools — this is our 'Host' UI."""
    print("\n🤖 Interactive Mode - Type 'help' for commands or 'quit' to exit")

    while True:
        try:
            command = input("\n> ").strip().lower()

            if command == "quit":
                break
            elif command == "help":
                print(
                    """
Available commands:
  time          - Get current time
  add X Y       - Add two numbers
  write F C     - Write to file C content F
  read_resource - Read the documents resource
  help          - Show this help
  quit          - Exit
                    """
                )
            elif command == "time":
                result = await client.call_tool("get_current_time", {})
                print(f"Current time: {result.content}")
            elif command.startswith("add "):
                parts = command.split()
                if len(parts) == 3:
                    a, b = float(parts[1]), float(parts[2])
                    result = await client.call_tool("add_numbers", {"a": a, "b": b})
                    print(f"Result: {result.content}")
                else:
                    print("Usage: add <number1> <number2>")
            elif command.startswith("write "):
                parts = command.split(maxsplit=2)
                if len(parts) == 3:
                    filename = parts[1]
                    content = parts[2]
                    result = await client.call_tool(
                        "write_file",
                        {"file_name": filename, "file_content": content},
                    )
                    print(f"File written: {result.content}")
                else:
                    print("Usage: write <filename> <content>")
            elif command == "read_resource":
                result = await client.read_resource("docs://documents.txt")
                print(f"Document content:\n{result if result else 'No content'}")
            else:
                print("Unknown command. Type 'help' for available commands.")

        except Exception as e:
            print(f"Error: {e}")


async def main():
    if len(sys.argv) < 2:
        print("Usage: python mcp_host.py <path_to_server.py>")
        print("Example: python mcp_host.py ./mcp_server.py")
        sys.exit(1)

    server_path = sys.argv[1]
    client = SimpleMCPClient()

    try:
        await client.connect_to_server(server_path)
        await interactive_mode(client)
    finally:
        await client.cleanup()
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())
