#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "openai-agents",
#     "mcp>=1.0.0"
# ]
# ///

import asyncio
import os
import shutil
from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerStdio

async def run(mcp_server: MCPServer):
    agent = Agent(
        name="Note Taker",
        model="gpt-5-mini",
        instructions="You are a note taker with access to a silly function to create a pancake recipe. You will be given a task and you will take notes on it.",
        mcp_servers=[mcp_server],
    )

    while True:
        message = input("Enter a message: ")
        if message == "exit" or message == "quit":
            break
        print(f"\n\nRunning: {message}")
        result = await Runner.run(starting_agent=agent, input=message)
        print(result.final_output)

async def main():
    async with MCPServerStdio(
        name="Note Taker Server",
        params={
            "command": "uv",
            "args": ["run", "mcp_server_for_openai_agent.py"],
        },
    ) as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="MCP Filesystem Example", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run(server)


if __name__ == "__main__":
    asyncio.run(main())