#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp[cli]>=2.3,<3"]
# ///
"""Tiny MCP server: one resource template over ./sources + two prompts + two tools.

Tools are model-controlled (the LLM calls them). Resources are
application-controlled (the host attaches them). chat.py shows the difference:
`@name` in the prompt reads a resource and injects it before the model runs.

    mcp dev server.py
"""

from pathlib import Path

from mcp.server.mcpserver import MCPServer
from mcp.types import Completion, ResourceTemplateReference

mcp = MCPServer("sources", dependencies=["mcp[cli]>=2.3,<3"])
SOURCES = Path(__file__).parent / "sources"
NOTES = Path(__file__).parent / "notes"

# ---- Resources: application-controlled, read-only, addressed by URI ----
# One URI template covers the whole ./sources folder. Hosts discover it via
# resources/templates/list, complete `{name}` via completion/complete, and
# fetch via resources/read. The model never decides to fetch; the user does.

def _source(name: str) -> Path:
    p = (SOURCES / f"{name}.md").resolve()
    if p.parent != SOURCES.resolve() or not p.is_file():   # no traversal, must exist
        raise ValueError(f"Resource not found: source://{name}")
    return p


@mcp.resource("source://{name}", name="source", title="Source document",
              mime_type="text/markdown")
def read_source(name: str) -> str:
    """A markdown document from the sources folder."""
    return _source(name).read_text()


@mcp.completion()
async def complete_source(ref, argument, context):
    """Autocomplete the {name} argument of source://{name}."""
    if isinstance(ref, ResourceTemplateReference) and argument.name == "name":
        names = sorted(p.stem for p in SOURCES.glob("*.md"))
        return Completion(values=[n for n in names if n.startswith(argument.value)])
    return None


# ---- Prompts: user-controlled templates, surfaced as slash commands ----
# Hosts discover them via prompts/list and expand via prompts/get.

@mcp.prompt(name="summarize", title="Summarize a source")
def summarize(name: str) -> str:
    """Three-bullet summary of one source document."""
    return f"Summarize @{name} in exactly three bullets, then name one open question."


@mcp.prompt(name="compare", title="Compare two sources")
def compare(a: str, b: str) -> str:
    """Compare two source documents and save the result as a note."""
    return (f"Compare @{a} and @{b}: what do they agree on, where do they differ? "
            f"Then call save_note with name '{a}-vs-{b}' containing your answer.")


# ---- Tools: model-controlled, may have side effects ----

@mcp.tool()
def search_sources(query: str) -> list[dict]:
    """Case-insensitive grep over all source documents. Returns matching lines."""
    hits = []
    for path in sorted(SOURCES.glob("*.md")):
        for n, line in enumerate(path.read_text().splitlines(), 1):
            if query.lower() in line.lower():
                hits.append({"source": path.stem, "line": n, "text": line.strip()})
    return hits


@mcp.tool()
def save_note(name: str, content: str) -> dict:
    """Save a markdown note under ./notes. `name` is a bare filename, no slashes."""
    if "/" in name or name.startswith("."):
        raise ValueError("name must be a plain filename")
    NOTES.mkdir(exist_ok=True)
    (NOTES / f"{name}.md").write_text(content)
    return {"saved": f"notes/{name}.md", "bytes": len(content)}


if __name__ == "__main__":
    mcp.run(transport="stdio")
