"""Vercel entry point — exposes the MCP server as an ASGI app.

Vercel's Python runtime looks for an `app` variable in api/index.py.
Because the server is built with stateless_http=True + json_response=True,
it runs happily as a serverless function: no session affinity, no SSE.
"""

import sys
from pathlib import Path

# server.py lives one level up from api/
sys.path.insert(0, str(Path(__file__).parent.parent))

from server import app  # noqa: E402,F401  — Vercel picks this up
