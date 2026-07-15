"""
Vercel Sandbox wrapper. Provides `run_in_sandbox(code, timeout_s)` which:

  - In production (when VERCEL_OIDC_TOKEN is present): spins up a Vercel
    Sandbox microVM via the @vercel/sandbox Python SDK, uploads the DuckDB
    file on first use per session, executes the supplied Python snippet,
    and returns `{stdout, stderr, error}`.

  - In local development (no OIDC token): falls back to running the code
    *in-process* via `exec()` against a temp file, mapping the sandbox path
    `/vercel/sandbox/data/sabi_synth.duckdb` to the local file. This is
    INSECURE and must never run in production — the module guards against
    that by only using the fallback when `ALLOW_INPROCESS_SANDBOX=1` is set.

Why the split:
  - Real sandbox adds ~500ms–1s boot cost per cold session, which makes
    iteration miserable. Students should be able to hack on tools without
    a Vercel OIDC token.
  - The in-process path uses a subprocess (not direct exec) to preserve
    the isolation invariant that `stdout` is the tool's return channel
    and nothing else.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

DATA_LOCAL = Path(__file__).resolve().parent.parent / "data" / "sabi_synth.duckdb"
SANDBOX_DATA = "/vercel/sandbox/data/sabi_synth.duckdb"

# Module-level cache of sandbox instances keyed by session id. Survives across
# warm invocations of the Vercel function. Lost on cold start → sandbox is
# recreated and data re-uploaded.
_SANDBOX_CACHE: dict[str, Any] = {}


def _has_vercel_token() -> bool:
    return bool(os.environ.get("VERCEL_OIDC_TOKEN"))


def _inprocess_allowed() -> bool:
    return os.environ.get("ALLOW_INPROCESS_SANDBOX") == "1"


async def run_in_sandbox(code: str, timeout_s: int = 30,
                        session_id: str = "default") -> dict[str, Any]:
    """Execute `code` (Python source) and return {stdout, stderr, error}."""
    if _has_vercel_token():
        return await _run_in_vercel_sandbox(code, timeout_s, session_id)
    if _inprocess_allowed():
        return await _run_inprocess(code, timeout_s)
    return {
        "stdout": "",
        "stderr": "",
        "error": (
            "No Vercel Sandbox available and in-process fallback is disabled. "
            "Set ALLOW_INPROCESS_SANDBOX=1 for local dev, or run under "
            "`vercel dev` with a linked project so VERCEL_OIDC_TOKEN is set."
        ),
    }


# ----------------------------------------------------------------------------
# Vercel Sandbox path
# ----------------------------------------------------------------------------


async def _run_in_vercel_sandbox(code: str, timeout_s: int,
                                 session_id: str) -> dict[str, Any]:
    try:
        from vercel_sandbox import Sandbox  # type: ignore
    except ImportError:
        return {"stdout": "", "stderr": "",
                "error": "vercel-sandbox package not installed."}

    sb = _SANDBOX_CACHE.get(session_id)
    if sb is None:
        sb = await Sandbox.create(
            runtime="python3.13",
            # pandas + plotly + duckdb installed once per sandbox lifetime.
            install_command="pip install --quiet duckdb pandas plotly",
            timeout_s=600,  # idle timeout
        )
        # Upload the dataset once.
        with DATA_LOCAL.open("rb") as f:
            await sb.upload_file(SANDBOX_DATA, f.read())
        _SANDBOX_CACHE[session_id] = sb

    # Write user code to the sandbox and execute.
    await sb.upload_file("/vercel/sandbox/user_code.py", code.encode("utf-8"))
    result = await sb.exec(
        ["python3", "/vercel/sandbox/user_code.py"],
        timeout_s=timeout_s,
    )
    return {
        "stdout": result.stdout or "",
        "stderr": result.stderr or "",
        "error": None if result.exit_code == 0 else
                 f"exit {result.exit_code}: {result.stderr[:500]}",
    }


async def cleanup_sandbox(session_id: str) -> None:
    sb = _SANDBOX_CACHE.pop(session_id, None)
    if sb is not None:
        try:
            await sb.stop()
        except Exception:
            pass


# ----------------------------------------------------------------------------
# In-process fallback (local dev only)
# ----------------------------------------------------------------------------


async def _run_inprocess(code: str, timeout_s: int) -> dict[str, Any]:
    """Run `code` as a subprocess using the current Python interpreter. Maps
    the sandbox DB path to the local file."""
    # Rewrite the sandbox path in the code to point at the local DB. A blunt
    # string replace is fine here — students see exactly what changed.
    local_code = code.replace(SANDBOX_DATA, str(DATA_LOCAL))

    proc = await asyncio.create_subprocess_exec(
        sys.executable, "-c", local_code,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout=timeout_s)
    except asyncio.TimeoutError:
        proc.kill()
        return {"stdout": "", "stderr": "", "error": f"Timeout after {timeout_s}s"}

    stdout = stdout_b.decode("utf-8", errors="replace")
    stderr = stderr_b.decode("utf-8", errors="replace")
    if proc.returncode != 0:
        return {"stdout": stdout, "stderr": stderr,
                "error": f"exit {proc.returncode}: {stderr[:500]}"}
    return {"stdout": stdout, "stderr": stderr, "error": None}
