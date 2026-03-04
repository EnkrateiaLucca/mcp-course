# /// script
# requires-python = ">=3.12"
# dependencies = ["anthropic"]
# ///

import os
from anthropic import Anthropic
from datetime import datetime

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def get_current_time() -> str:
    return datetime.now().isoformat()

# Prepare the user message
messages = [
    {"role": "user", "content": "What is the current time?"}
]

# Ask Claude and explicitly provide max_tokens as required by API
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=256,
    messages=messages,
    tools=[
        {
            "name": "get_current_time",
            "description": "Get the current time",
            "input_schema": {
                "type": "object",
                "properties": {},
            },
        }
    ]
)

print(response)