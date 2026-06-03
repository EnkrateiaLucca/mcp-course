"""Pytest configuration: make demo packages importable without installing them."""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Make demo 04 importable as plain modules.
sys.path.insert(0, str(REPO_ROOT / "demos" / "04-production-research-agent"))

# research_server.py refuses to import without MCP_AUTH_TOKEN; tests don't
# need a real token — just satisfy the env-var guard.
os.environ.setdefault("MCP_AUTH_TOKEN", "test-token")
