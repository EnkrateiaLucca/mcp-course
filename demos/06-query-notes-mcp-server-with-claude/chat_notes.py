from webbrowser import get
from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerStdio
import asyncio


async def run_notes_agent(mcp_server: MCPServer):
    agent = Agent(
        name="Notes Agent",
        model="gpt-5-mini",
        instructions="""
        You are a helpful assistant that can answer questions.
        You can also create notes and list the available notes
        from my obsidian vault.
        """,
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
        name="obsidian-vault",
        params={
            "command": "uv",
            "args": ["run", "./obsidian_vault_server.py"],
        },
        
    ) as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="Notes Agent", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run_notes_agent(server)


if __name__ == "__main__":
    asyncio.run(main())