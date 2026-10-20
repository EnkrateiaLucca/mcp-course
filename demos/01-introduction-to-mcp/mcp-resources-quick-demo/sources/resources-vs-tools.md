# Resources vs tools

A tool "read_file" makes the model spend a turn guessing which file matters.
A resource lets the *user* point at the file up front (Claude Code's `@file`,
Claude Desktop's attachment picker). Same bytes, different control plane:
resources = pull by the human, tools = pull by the model.
