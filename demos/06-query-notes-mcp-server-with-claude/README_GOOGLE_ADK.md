# Obsidian Notes Agent - Google ADK Version

This is a Google ADK implementation of the Obsidian Notes Agent that connects to the same MCP server (`obsidian_vault_server.py`) but uses Google's Agent Development Kit instead of the original agents library.

## Features

- 🤖 Powered by Google's Gemini models
- 📝 Full access to your Obsidian vault via MCP
- 🔧 Two implementations: Simple and Advanced
- 💬 Interactive CLI with session management

## Setup

1. **Install Dependencies**:
```bash
pip install -r requirements_adk.txt
```

2. **Configure Google AI API Key**:
```bash
export GOOGLE_API_KEY="your-api-key-here"
```

3. **(Optional) Set Obsidian Vault Path**:
```bash
export OBSIDIAN_VAULT_PATH="/path/to/your/obsidian/vault"
```

## Usage

### Simple Version
Basic implementation that closely mirrors the original:

```bash
python chat_notes_google_adk.py
```

### Advanced Version
Feature-rich implementation with commands and session management:

```bash
python chat_notes_adk_advanced.py
```

You can also specify the model:
```bash
python chat_notes_adk_advanced.py gemini-1.5-pro
```

## Available Commands (Advanced Version)

- `/help` - Show available commands
- `/summary` - Display session summary
- `/model` - Show current model info
- `/clear` - Clear the screen
- `exit` or `quit` - End the session

## Example Interactions

```
💬 You: List my notes

🤖 Assistant:
📚 Notes in your vault
Found 5 notes...
1. Daily Notes/2024-01-15.md
2. Projects/MCP Integration.md
...

💬 You: Read the MCP Integration note

🤖 Assistant:
📝 Note: Projects/MCP Integration.md
[Content of the note...]

💬 You: Create a new note about Google ADK

🤖 Assistant:
✅ Note Created Successfully!
📝 Title: Google ADK Overview
📁 Location: Projects/Google ADK Overview.md
...
```

## Key Differences from Original

1. **Framework**: Uses Google ADK instead of custom agents library
2. **Models**: Uses Gemini models (gemini-2.0-flash, gemini-1.5-pro)
3. **Execution**: Different async execution pattern
4. **Features**: Advanced version includes session management and CLI commands

## Troubleshooting

- Ensure `obsidian_vault_server.py` is in the same directory
- Verify Google API credentials are configured
- Check that all dependencies are installed
- The MCP server runs automatically via stdio connection

## Architecture

```
User Input → Google ADK Agent → MCPToolset → obsidian_vault_server.py → Obsidian Vault
```

The agent communicates with the MCP server through stdio, maintaining compatibility with the original server implementation.