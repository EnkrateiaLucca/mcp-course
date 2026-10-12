"""Protocol test for the module-03 Skills-over-MCP server (SEP-2640).

Starts demos/03-skills-and-mcp/skills-over-mcp/skills_server.py over stdio
(via `uv run`, so the server gets its own inline deps) and checks that
skills/list and skills/get return a complete manifest whose digests match the
bytes on disk and the bytes resources/read serves.
"""
from __future__ import annotations

import asyncio
import hashlib
from pathlib import Path
from typing import Any

import pytest
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from mcp.shared.exceptions import McpError
from pydantic import AnyUrl

DEMO = Path(__file__).resolve().parent.parent / "demos" / "03-skills-and-mcp" / "skills-over-mcp"
SKILL_DIR = DEMO / "skills" / "mcp-builder"
SKILL_URI = "skill://mcp-builder/SKILL.md"
SERVER = StdioServerParameters(command="uv", args=["run", "--quiet", str(DEMO / "skills_server.py")])


async def call(session: ClientSession, method: str, **params: Any) -> dict:
    request = types.Request[dict[str, Any] | None, str](method=method, params=params or None)
    return (await session.send_request(request, types.Result)).model_dump(exclude_none=True)  # type: ignore[arg-type]


def run_with_session(check):
    async def main():
        async with stdio_client(SERVER) as (r, w), ClientSession(r, w) as session:
            init = await session.initialize()
            return await check(session, init)

    return asyncio.run(main())


def test_list_get_and_digests():
    disk = {
        f"skill://mcp-builder/{p.relative_to(SKILL_DIR).as_posix()}": p.read_bytes()
        for p in SKILL_DIR.rglob("*")
        if p.is_file() and not p.name.startswith(".")
    }

    async def check(session: ClientSession, init: types.InitializeResult):
        caps = init.capabilities
        assert caps.resources is not None
        assert "io.modelcontextprotocol/skills" in caps.model_extra["extensions"]

        listing = await call(session, "skills/list")
        assert listing["resultType"] == "complete" and "ttlMs" in listing and "cacheScope" in listing
        (entry,) = listing["skills"]
        assert entry["uri"] == SKILL_URI
        assert entry["frontmatter"]["name"] == "mcp-builder"  # == last URI path segment

        # Complete manifest: every file on disk, each once, digests of the raw bytes.
        manifest = {f["uri"]: f for f in entry["resources"]}
        assert len(manifest) == len(entry["resources"]) and set(manifest) == set(disk)
        for uri, data in disk.items():
            assert manifest[uri]["digest"] == "sha256:" + hashlib.sha256(data).hexdigest()
            assert manifest[uri]["size"] == len(data)
        assert not any("/scripts/" in uri for uri in manifest)  # instructor-style: no helper scripts

        assert (await call(session, "skills/get", uri=SKILL_URI))["skill"] == entry

        served = await session.read_resource(AnyUrl("skill://mcp-builder/reference/python_mcp_server.md"))
        assert served.contents[0].text.encode() == disk["skill://mcp-builder/reference/python_mcp_server.md"]

    run_with_session(check)


def test_unknown_skill_is_invalid_params():
    async def check(session: ClientSession, _init):
        with pytest.raises(McpError) as err:
            await call(session, "skills/get", uri="skill://nope/SKILL.md")
        assert err.value.error.code == types.INVALID_PARAMS  # -32602, per spec §Error Handling

        with pytest.raises(McpError) as err:
            await session.read_resource(AnyUrl("skill://mcp-builder/../../etc/passwd"))
        assert err.value.error.code == types.INVALID_PARAMS

    run_with_session(check)
