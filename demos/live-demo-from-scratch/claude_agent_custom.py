# /// script
# requires-python = ">=3.12"
# dependencies = ["claude-agent-sdk>=0.1.21"]
# ///

import asyncio
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    model="claude-sonnet-4-5",
    system_prompt="""
    You are a helpful assistant that can analyze pdf files.
    You answer questions about pdfs and that is it!
    If a question is about anything other than a pdf
    or if it does not contain a pdf name or file path
    just answer with: 'I can only answer questions about pdfs.'
    """,
    mcp_servers={
        "pdf-analysis": {
            "type": "stdio",
            "command": "uv",
            "args": ["run", "custom_mcp_server.py"]
        }
    },
    permission_mode="bypassPermissions",
)

# to download the pdf run this:
# wget -O paper.pdf https://arxiv.org/pdf/1301.3781
async def main():
    query_user_input = input("Enter your query and the pdf file path:")
    async for message in query(prompt=query_user_input, options=options):
        print(message)

if __name__ == "__main__":
    asyncio.run(main())