#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp[cli]>=1.12,<2", "pyyaml"]
# ///
"""Serve Agent Skills over MCP with the Skills extension (SEP-2640).

Every folder under ./skills that holds a SKILL.md is one skill. Each file in
it becomes an ordinary MCP resource at skill://<skill-name>/<file-path>. The
extension adds two methods on top of plain resources: skills/list and
skills/get. Section names in comments refer to the spec:
https://github.com/modelcontextprotocol/ext-skills/blob/main/specification/stable/skills.mdx

    uv run skills_server.py              # stdio
    SKILLS_DIR=/some/dir uv run skills_server.py
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Literal

import anyio
import yaml
from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.lowlevel import server as lowlevel_server
from mcp.server.lowlevel.helper_types import ReadResourceContents
from mcp.server.session import ServerSession
from mcp.server.stdio import stdio_server
from mcp.shared.exceptions import McpError

SKILLS_DIR = Path(os.environ.get("SKILLS_DIR", Path(__file__).parent / "skills")).resolve()
EXTENSION = "io.modelcontextprotocol/skills"


# ── Skill folders on disk -> skill:// resources (§Resource Mapping) ──────────
# Everything is read from disk on each request, so an edited file shows up
# with a new digest immediately.

def skill_dirs() -> list[Path]:
    return sorted(p.parent for p in SKILLS_DIR.glob("*/SKILL.md"))


def skill_files(skill_dir: Path) -> dict[str, Path]:
    """URI -> path for every file of one skill (dotfiles like .DS_Store excluded)."""
    return {
        f"skill://{skill_dir.name}/{p.relative_to(skill_dir).as_posix()}": p
        for p in sorted(skill_dir.rglob("*"))
        if p.is_file() and not p.name.startswith(".")
    }


def all_files() -> dict[str, Path]:
    return {uri: p for d in skill_dirs() for uri, p in skill_files(d).items()}


def frontmatter(skill_md: Path) -> dict:
    """SKILL.md's YAML frontmatter, every field, as a JSON object (§Frontmatter)."""
    _, block, _ = skill_md.read_text(encoding="utf-8").split("---", 2)
    return yaml.safe_load(block)


def skill_entry(skill_dir: Path) -> dict:
    """A Skill entry: verbatim frontmatter + a complete per-file manifest (§Skill Entries).

    The folder name is the skill name (Agent Skills rule), so the URI's last
    path segment equals frontmatter.name, as §Resource Mapping requires.
    """
    manifest = []
    for uri, path in skill_files(skill_dir).items():
        data = path.read_bytes()  # the digest covers the raw bytes
        manifest.append({"uri": uri, "digest": f"sha256:{hashlib.sha256(data).hexdigest()}", "size": len(data)})
    return {
        "uri": f"skill://{skill_dir.name}/SKILL.md",
        "frontmatter": frontmatter(skill_dir / "SKILL.md"),
        "resources": manifest,  # a generated skill would send the string "dynamic" instead
    }


# ── Two new JSON-RPC methods (§Listing Skills, §Getting a Skill) ─────────────

class ListSkillsRequest(types.PaginatedRequest[Literal["skills/list"]]):
    method: Literal["skills/list"] = "skills/list"


class GetSkillParams(types.RequestParams):
    uri: str


class GetSkillRequest(types.Request[GetSkillParams, Literal["skills/get"]]):
    method: Literal["skills/get"] = "skills/get"
    params: GetSkillParams


# The v1 SDK validates every incoming request against a closed union of
# spec-defined methods, so "skills/list" would be rejected before reaching any
# handler. Widen that union by our two methods. This is the whole SDK
# workaround; native support is pending (python-sdk PR #3485).
class ClientRequestWithSkills(types.ClientRequest):
    root: types.ClientRequestType | ListSkillsRequest | GetSkillRequest


class SkillsSession(ServerSession):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._receive_request_type = ClientRequestWithSkills


lowlevel_server.ServerSession = SkillsSession  # Server.run() builds its session from this name


# ── The server ────────────────────────────────────────────────────────────────

server = Server("skills-over-mcp")
CACHE_HINT = {"ttlMs": 0, "cacheScope": "public"}  # CacheableResult: files are live on disk, so don't cache


async def list_skills(req: ListSkillsRequest) -> types.Result:
    # One page holds the whole catalog, so no nextCursor.
    skills = [skill_entry(d) for d in skill_dirs()]
    return types.Result.model_validate({"resultType": "complete", "skills": skills, **CACHE_HINT})


async def get_skill(req: GetSkillRequest) -> types.Result:
    for d in skill_dirs():
        if f"skill://{d.name}/SKILL.md" == req.params.uri:
            return types.Result.model_validate({"resultType": "complete", "skill": skill_entry(d), **CACHE_HINT})
    raise McpError(types.ErrorData(code=types.INVALID_PARAMS, message=f"No skill is served at {req.params.uri}"))


server.request_handlers[ListSkillsRequest] = list_skills
server.request_handlers[GetSkillRequest] = get_skill


# Skill files are plain resources, read with the standard resources/read
# (§Reading Skill Content). Reading SKILL.md this way does not "activate" it.
@server.list_resources()
async def list_resources() -> list[types.Resource]:
    return [
        types.Resource(uri=uri, name=p.relative_to(SKILLS_DIR).as_posix(),
                       mimeType="text/markdown" if p.suffix == ".md" else "text/plain")
        for uri, p in all_files().items()
    ]


@server.read_resource()
async def read_resource(uri) -> list[ReadResourceContents]:
    path = all_files().get(str(uri))  # only URIs we enumerated: no path traversal
    if path is None:
        raise McpError(types.ErrorData(code=types.INVALID_PARAMS, message=f"Unknown resource {uri}"))
    # ponytail: text files only (instructor-style skills); serve bytes as a blob if you add images.
    mime = "text/markdown" if path.suffix == ".md" else "text/plain"
    # read_bytes().decode() keeps the bytes exact (read_text would rewrite \r\n).
    return [ReadResourceContents(content=path.read_bytes().decode("utf-8"), mime_type=mime)]


async def main() -> None:
    options = server.create_initialization_options()
    # §Capability Negotiation: declare the extension next to `resources`.
    # `{}` = supported, no optional features (we skip directoryRead).
    options.capabilities.extensions = {EXTENSION: {}}
    async with stdio_server() as (read, write):
        await server.run(read, write, options)


if __name__ == "__main__":
    anyio.run(main)
