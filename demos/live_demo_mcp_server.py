#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp[cli]>=2.3,<3", "matplotlib", "numpy"]
# ///

import json
import logging
from pathlib import Path
import argparse, base64, io, webbrowser
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
import matplotlib
matplotlib.use("Agg")  # headless: Claude Desktop has no GUI
import matplotlib.pyplot as plt
import numpy as np

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("notes-heatmap", dependencies=["mcp[cli]>=2.3,<3"])


@mcp.tool()
def vault_heatmap(vault: str = "~/lucas-notes", glob: str = "**/*.md", grep: str | None = None, days: int = 365, out: str = "vault_heatmap") -> dict:
    """Count notes per creation day, save <out>.png and <out>.html, return both paths."""
    vault = Path(vault).expanduser()
    counts = Counter()
    for p in vault.glob(glob):
        if any(part.startswith(".") for part in p.relative_to(vault).parts):
            continue
        if grep and grep not in p.read_text(errors="ignore"):
            continue
        st = p.stat()
        counts[date.fromtimestamp(getattr(st, "st_birthtime", st.st_mtime))] += 1

    end = date.today()
    start = end - timedelta(days=days - 1)
    start -= timedelta(days=start.weekday())  # align to Monday
    weeks = (end - start).days // 7 + 1
    grid = np.full((7, weeks), np.nan)
    d = start
    while d <= end:
        grid[d.weekday(), (d - start).days // 7] = counts.get(d, 0)
        d += timedelta(days=1)

    total = int(np.nansum(grid))
    fig, ax = plt.subplots(figsize=(max(8, weeks * 0.22), 2.6))
    cmap = plt.get_cmap("Greens").copy()
    cmap.set_bad("white")
    im = ax.imshow(grid, cmap=cmap, aspect="equal", vmin=0, vmax=max(1, np.nanpercentile(grid, 98)))
    ax.set_yticks(range(7), ["Mon", "", "Wed", "", "Fri", "", "Sun"], fontsize=8)
    months = [(w, start + timedelta(weeks=w)) for w in range(weeks)]
    ticks = [(w, m.strftime("%b")) for i, (w, m) in enumerate(months) if i == 0 or m.month != months[i - 1][1].month]
    ax.set_xticks([w for w, _ in ticks], [l for _, l in ticks], fontsize=8)
    ax.set_xticks(np.arange(-0.5, weeks), minor=True)
    ax.set_yticks(np.arange(-0.5, 7), minor=True)
    ax.grid(which="minor", color="white", linewidth=2)
    ax.tick_params(which="both", length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title(f"{total} notes created · {vault.name}/{glob}{f' · grep {grep!r}' if grep else ''}", fontsize=10, loc="left")
    fig.colorbar(im, ax=ax, fraction=0.015, pad=0.01)
    fig.tight_layout()

    png, html = (Path(__file__).parent / f"{out}.png").resolve(), (Path(__file__).parent / f"{out}.html").resolve()
    fig.savefig(png, dpi=150)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    b64 = base64.b64encode(buf.getvalue()).decode()
    busiest = "".join(f"<li>{d}: {n}</li>" for d, n in counts.most_common(10) if d >= start)
    html.write_text(
        f"<!doctype html><meta charset=utf-8><title>Vault Heatmap</title>"
        f"<body style='font-family:system-ui;margin:24px'><h2>Obsidian vault activity</h2>"
        f"<img src='data:image/png;base64,{b64}' style='max-width:100%'>"
        f"<h3>Busiest days</h3><ol>{busiest}</ol></body>"
    )
    return {"png": str(png), "html": str(html)}

if __name__ == "__main__":
    mcp.run(transport="stdio")  # or "websocket" for a websocket server