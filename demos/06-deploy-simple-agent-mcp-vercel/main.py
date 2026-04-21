#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "claude-agent-sdk>=0.1.0",
#     "fastapi>=0.100.0",
#     "uvicorn>=0.20.0",
#     "pandas>=2.0.0",
#     "numpy>=1.26.0",
#     "matplotlib>=3.8.0",
#     "tabulate>=0.9.0",
#     "python-dotenv>=1.0.0",
# ]
# ///
"""
Demo 06 — Data Analysis Agent
FastAPI + SSE chat UI backed by Claude Agent SDK with an in-process MCP server.

Run locally:  uv run main.py
Deploy:       vercel --prod
"""
from __future__ import annotations

import base64
import io
import json
import os
from typing import Any, AsyncGenerator

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    create_sdk_mcp_server,
    tool,
)

load_dotenv()

# ---------------------------------------------------------------------------
# Dataset — synthetic Portuguese company financials (blueprint: sabi_hubspot)
# ---------------------------------------------------------------------------

def _generate_company_data() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    n = 250

    sectors = [
        ("G47", "Retail trade"),
        ("G46", "Wholesale trade"),
        ("C25", "Metal products manufacturing"),
        ("C10", "Food manufacturing"),
        ("F41", "Building construction"),
        ("M69", "Legal and accounting"),
        ("M70", "Management consulting"),
        ("I56", "Restaurants and food service"),
        ("J62", "Software and IT services"),
        ("H49", "Land transport"),
        ("K64", "Financial services"),
        ("C22", "Rubber and plastics"),
    ]

    regions = [
        "Lisboa", "Porto", "Setúbal", "Braga", "Aveiro",
        "Coimbra", "Leiria", "Faro", "Évora", "Santarém",
    ]

    sizes = rng.choice(["micro", "small", "medium", "large"], n, p=[0.45, 0.35, 0.15, 0.05])
    revenue_ranges = {
        "micro":  (50_000,     500_000),
        "small":  (500_000,  5_000_000),
        "medium": (5_000_000, 50_000_000),
        "large":  (50_000_000, 500_000_000),
    }
    revenues = np.array([rng.uniform(*revenue_ranges[s]) for s in sizes])

    ebitda_margin = rng.uniform(0.03, 0.28, n)
    ebitda = revenues * ebitda_margin
    loss_mask = rng.random(n) < 0.12
    ebitda[loss_mask] *= -rng.uniform(0.1, 1.0, loss_mask.sum())

    da = revenues * rng.uniform(0.02, 0.07, n)
    ebit = ebitda - da
    net_profit = ebit * rng.uniform(0.50, 0.85, n)

    total_assets = revenues * rng.uniform(0.5, 2.5, n)
    equity = total_assets * rng.uniform(0.2, 0.7, n)

    employees = np.maximum(1, (revenues / rng.uniform(30_000, 150_000, n)).astype(int))

    export_mask = rng.random(n) < 0.40
    exports = np.where(export_mask, revenues * rng.uniform(0.05, 0.6, n), 0)

    sector_idx = rng.integers(0, len(sectors), n)

    return pd.DataFrame({
        "company_name":  [f"Company {i+1:03d} Lda" for i in range(n)],
        "region":        rng.choice(regions, n),
        "sector":        [sectors[i][1] for i in sector_idx],
        "sector_code":   [sectors[i][0] for i in sector_idx],
        "size":          sizes,
        "status":        rng.choice(["Active", "Inactive"], n, p=[0.92, 0.08]),
        "revenue":       revenues.round(0).astype(int),
        "ebitda":        ebitda.round(0).astype(int),
        "ebit":          ebit.round(0).astype(int),
        "net_profit":    net_profit.round(0).astype(int),
        "total_assets":  total_assets.round(0).astype(int),
        "equity":        equity.round(0).astype(int),
        "employees":     employees,
        "exports":       exports.round(0).astype(int),
    })


DATA: pd.DataFrame = _generate_company_data()

# Module-level artifact queue (single-user demo assumption)
_ARTIFACTS: list[dict[str, Any]] = []


def _push_image(fig: plt.Figure, caption: str) -> None:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110, bbox_inches="tight")
    plt.close(fig)
    b64 = base64.b64encode(buf.getvalue()).decode()
    _ARTIFACTS.append({"type": "image", "content": f"data:image/png;base64,{b64}", "caption": caption})


def _drain_artifacts() -> list[dict[str, Any]]:
    out = _ARTIFACTS.copy()
    _ARTIFACTS.clear()
    return out


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------

@tool("describe_data", "Return summary statistics (pandas describe) for the preloaded dataset.", {})
async def describe_data(args: dict[str, Any]) -> dict[str, Any]:
    numeric = DATA.select_dtypes(include="number")
    categorical = DATA.select_dtypes(exclude="number")
    parts = [f"**Shape:** {DATA.shape[0]} rows × {DATA.shape[1]} columns\n"]
    if not numeric.empty:
        parts.append(f"**Numeric columns:**\n\n{numeric.describe().round(2).to_markdown()}")
    if not categorical.empty:
        parts.append(f"**Categorical columns:**\n\n{categorical.describe().to_markdown()}")
    return {"content": [{"type": "text", "text": "\n\n".join(parts)}]}


@tool("show_head", "Show the first N rows of the dataset (N defaults to 5).", {"n": int})
async def show_head(args: dict[str, Any]) -> dict[str, Any]:
    n = int(args.get("n") or 5)
    return {"content": [{"type": "text", "text": f"First {n} rows:\n\n{DATA.head(n).to_markdown(index=False)}"}]}


@tool("column_info", "List columns with their dtypes, non-null counts, and unique-value counts.", {})
async def column_info(args: dict[str, Any]) -> dict[str, Any]:
    info = pd.DataFrame({"dtype": DATA.dtypes.astype(str), "non_null": DATA.notna().sum(), "unique": DATA.nunique()})
    return {"content": [{"type": "text", "text": f"Columns:\n\n{info.to_markdown()}"}]}


@tool(
    "group_aggregate",
    "Group the dataset by a column and aggregate a numeric column. Supported ops: mean, sum, count, median, min, max, std.",
    {"group_by": str, "value_col": str, "op": str},
)
async def group_aggregate(args: dict[str, Any]) -> dict[str, Any]:
    group_by = args.get("group_by", "")
    value_col = args.get("value_col", "")
    op = (args.get("op") or "mean").lower()
    allowed_ops = {"mean", "sum", "count", "median", "min", "max", "std"}
    if op not in allowed_ops:
        return {"content": [{"type": "text", "text": f"Unsupported op '{op}'. Allowed: {sorted(allowed_ops)}"}]}
    if group_by not in DATA.columns:
        return {"content": [{"type": "text", "text": f"Unknown group column '{group_by}'. Available: {list(DATA.columns)}"}]}
    if value_col not in DATA.columns:
        return {"content": [{"type": "text", "text": f"Unknown value column '{value_col}'. Available: {list(DATA.columns)}"}]}
    result = DATA.groupby(group_by)[value_col].agg(op).reset_index().rename(columns={value_col: f"{op}_{value_col}"})
    return {"content": [{"type": "text", "text": f"{op}({value_col}) by {group_by}:\n\n{result.to_markdown(index=False)}"}]}


@tool("correlation_matrix", "Compute and plot the correlation matrix of all numeric columns.", {})
async def correlation_matrix(args: dict[str, Any]) -> dict[str, Any]:
    corr = DATA.select_dtypes(include="number").corr()
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(corr.values, cmap="coolwarm", vmin=-1, vmax=1, aspect="auto")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    labels = corr.columns.tolist()
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=7)
    ax.set_yticklabels(labels, fontsize=7)
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=6)
    ax.set_title("Correlation matrix (numeric columns)")
    fig.tight_layout()
    _push_image(fig, "Correlation matrix")
    return {"content": [{"type": "text", "text": f"Correlation matrix:\n\n{corr.round(3).to_markdown()}"}]}


@tool(
    "plot_data",
    "Create a visualization. kind: bar | line | scatter | hist | box. x is the primary column; y required for bar/line/scatter/box.",
    {"kind": str, "x": str, "y": str},
)
async def plot_data(args: dict[str, Any]) -> dict[str, Any]:
    kind = (args.get("kind") or "").lower()
    x = args.get("x") or ""
    y = args.get("y") or None
    valid_kinds = {"bar", "line", "scatter", "hist", "box"}

    if kind not in valid_kinds:
        return {"content": [{"type": "text", "text": f"Unsupported plot kind '{kind}'. Try: {sorted(valid_kinds)}"}]}
    if not x or x not in DATA.columns:
        return {"content": [{"type": "text", "text": f"Unknown column '{x}'. Available: {list(DATA.columns)}"}]}
    if y and y not in DATA.columns:
        return {"content": [{"type": "text", "text": f"Unknown column '{y}'. Available: {list(DATA.columns)}"}]}
    if kind in {"line", "scatter", "box"} and not y:
        return {"content": [{"type": "text", "text": f"Plot kind '{kind}' requires both x and y. Please specify y."}]}

    fig, ax = plt.subplots(figsize=(8, 5))
    try:
        if kind == "hist":
            is_categorical = y and DATA[y].dtype in ("object", "category")
            if is_categorical:
                for cat in DATA[y].dropna().unique():
                    ax.hist(DATA.loc[DATA[y] == cat, x].dropna(), bins=20, alpha=0.6, label=str(cat))
                ax.legend(title=y)
            else:
                ax.hist(DATA[x].dropna(), bins=20)
            ax.set_xlabel(x)
            ax.set_ylabel("Count")
        elif kind == "bar":
            if y:
                DATA.groupby(x)[y].mean().plot(kind="bar", ax=ax)
                ax.set_ylabel(f"mean({y})")
            else:
                DATA[x].value_counts().plot(kind="bar", ax=ax)
                ax.set_ylabel("count")
        elif kind == "scatter":
            ax.scatter(DATA[x], DATA[y], alpha=0.6)
            ax.set_xlabel(x)
            ax.set_ylabel(y)
        elif kind == "line":
            DATA.sort_values(x).plot(kind="line", x=x, y=y, ax=ax)
        elif kind == "box":
            groups = [grp[y].dropna().values for _, grp in DATA.groupby(x)]
            group_labels = [str(k) for k, _ in DATA.groupby(x)]
            ax.boxplot(groups, labels=group_labels)
            ax.set_xlabel(x)
            ax.set_ylabel(y)
            ax.tick_params(axis="x", rotation=45)
    except Exception as exc:
        plt.close(fig)
        return {"content": [{"type": "text", "text": f"Plot failed: {exc}"}]}

    caption = f"{kind} of {x}" + (f" vs {y}" if y else "")
    ax.set_title(caption)
    fig.tight_layout()
    _push_image(fig, caption)
    return {"content": [{"type": "text", "text": f"Generated: {caption}."}]}


# ---------------------------------------------------------------------------
# In-process MCP server + agent configuration
# ---------------------------------------------------------------------------

analysis_server = create_sdk_mcp_server(
    name="analysis",
    version="1.0.0",
    tools=[describe_data, show_head, column_info, group_aggregate, correlation_matrix, plot_data],
)

ALLOWED_TOOLS = [
    "mcp__analysis__describe_data",
    "mcp__analysis__show_head",
    "mcp__analysis__column_info",
    "mcp__analysis__group_aggregate",
    "mcp__analysis__correlation_matrix",
    "mcp__analysis__plot_data",
]

SYSTEM_PROMPT = f"""You are a financial data analysis assistant.

CRITICAL OUTPUT RULES:
- NEVER use PAI, NATIVE MODE, or any internal system format headers.
- NEVER summarize tool output — reproduce the full table verbatim as markdown.
- When a tool returns a markdown table, paste it entirely into your reply.
- After the table you may add 1-3 short observations, but the table comes first.

Dataset: {DATA.shape[0]} Portuguese companies (synthetic, sabi_hubspot schema).
Columns: {list(DATA.columns)}
Column meanings: revenue/ebitda/ebit/net_profit/total_assets/equity/exports are EUR figures;
employees is headcount; sector/sector_code is CAE industry; region is Portuguese district;
size is micro/small/medium/large; status is Active or Inactive.

Always call the appropriate tool — never answer from training data.
"""

# ---------------------------------------------------------------------------
# SSE agent stream
# ---------------------------------------------------------------------------

_TOOL_LABELS: dict[str, tuple[str, str, str]] = {
    "mcp__analysis__describe_data":      ("📊", "describe_data",       "Summarising dataset statistics"),
    "mcp__analysis__show_head":          ("👀", "show_head",           "Fetching first rows"),
    "mcp__analysis__column_info":        ("🗂️",  "column_info",         "Inspecting column types"),
    "mcp__analysis__group_aggregate":    ("🧮", "group_aggregate",     "Grouping and aggregating"),
    "mcp__analysis__correlation_matrix": ("🔗", "correlation_matrix",  "Computing correlations"),
    "mcp__analysis__plot_data":          ("📈", "plot_data",           "Generating plot"),
}


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


async def _agent_stream(message: str) -> AsyncGenerator[str, None]:
    if not os.getenv("ANTHROPIC_API_KEY"):
        yield _sse({"type": "error", "content": "ANTHROPIC_API_KEY not set — add it to .env and restart."})
        yield _sse({"type": "done"})
        return

    options = ClaudeAgentOptions(
        mcp_servers={"analysis": analysis_server},
        allowed_tools=ALLOWED_TOOLS,
        system_prompt=SYSTEM_PROMPT,
    )

    # Yield status immediately so the browser shows feedback before the LLM call
    yield _sse({"type": "status", "content": "Initializing agent…"})

    max_attempts = 2
    for attempt in range(max_attempts):
        try:
            async with ClaudeSDKClient(options=options) as client:
                yield _sse({"type": "status", "content": "Calling Claude…"})
                await client.query(message)
                async for msg in client.receive_response():
                    if isinstance(msg, AssistantMessage):
                        for block in msg.content:
                            if isinstance(block, TextBlock) and block.text:
                                yield _sse({"type": "text", "content": block.text})
                            elif isinstance(block, ToolUseBlock):
                                icon, short, label = _TOOL_LABELS.get(block.name, ("🔧", block.name, "Calling tool"))
                                args = getattr(block, "input", {}) or {}
                                args_str = ", ".join(f"{k}={v}" for k, v in args.items() if v)
                                detail = f" — {args_str}" if args_str else ""
                                yield _sse({"type": "tool_call", "content": f"{icon} {label} `{short}`{detail}"})
                        for art in _drain_artifacts():
                            yield _sse(art)
                    elif isinstance(msg, ResultMessage):
                        break
            break  # success — exit retry loop
        except Exception as exc:
            err = str(exc)
            is_timeout = "timeout" in err.lower() or "initialize" in err.lower()
            if is_timeout and attempt < max_attempts - 1:
                yield _sse({"type": "status", "content": f"Cold start detected — retrying… (attempt {attempt + 2}/{max_attempts})"})
                continue
            # Friendlier message for the known Vercel cold-start timeout
            if is_timeout:
                err = (
                    "Agent timed out during initialization. "
                    "This happens on Vercel's hobby plan (10 s limit) during cold starts. "
                    "Please try again — warm instances respond in time. "
                    "For reliable use, upgrade to Vercel Pro (60 s timeout)."
                )
            yield _sse({"type": "error", "content": err})

    for art in _drain_artifacts():
        yield _sse(art)
    yield _sse({"type": "done"})


# ---------------------------------------------------------------------------
# Embedded HTML frontend
# ---------------------------------------------------------------------------

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Data Analysis Agent</title>
<script src="https://cdn.jsdelivr.net/npm/marked@14/marked.min.js"></script>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: system-ui, -apple-system, sans-serif;
    background: #0f172a; color: #e2e8f0;
    display: flex; flex-direction: column; align-items: center;
    min-height: 100vh;
  }
  #app {
    width: 100%; max-width: 860px;
    display: flex; flex-direction: column;
    height: 100vh; padding: 0 16px;
  }
  header { padding: 20px 0 10px; border-bottom: 1px solid #1e293b; }
  header h1 { font-size: 1.3rem; font-weight: 700; color: #60a5fa; }
  header p  { font-size: 0.78rem; color: #64748b; margin-top: 3px; }
  #examples {
    display: flex; flex-wrap: wrap; gap: 6px;
    padding: 10px 0 6px;
  }
  .ex {
    background: #1e3a5f; border: 1px solid #2563eb33;
    color: #93c5fd; border-radius: 999px;
    padding: 3px 12px; font-size: 12px; cursor: pointer;
    transition: background .15s;
  }
  .ex:hover { background: #1e40af; }
  #messages {
    flex: 1; overflow-y: auto;
    display: flex; flex-direction: column; gap: 10px;
    padding: 10px 0;
  }
  .msg {
    max-width: 88%; padding: 10px 14px;
    border-radius: 14px; line-height: 1.65;
    word-break: break-word; font-size: 14px;
  }
  .msg.user {
    align-self: flex-end;
    background: #1d4ed8; color: #fff;
    border-bottom-right-radius: 4px;
  }
  .msg.assistant {
    align-self: flex-start;
    background: #1e293b; color: #e2e8f0;
    border: 1px solid #334155;
    border-bottom-left-radius: 4px;
  }
  .msg.tool {
    align-self: flex-start;
    background: #0c1f36; color: #7dd3fc;
    border: 1px solid #1e3a5f;
    border-radius: 8px; font-size: 13px;
    padding: 5px 12px; font-family: monospace;
  }
  .msg.err { background: #3b0f0f; border: 1px solid #7f1d1d; color: #fca5a5; }
  .msg table { border-collapse: collapse; width: 100%; font-size: 12px; margin: 8px 0; }
  .msg th, .msg td { border: 1px solid #334155; padding: 5px 8px; text-align: left; }
  .msg th { background: rgba(255,255,255,0.06); font-weight: 600; }
  .msg tr:nth-child(even) td { background: rgba(255,255,255,0.03); }
  .msg code { background: rgba(255,255,255,0.08); border-radius: 4px; padding: 1px 5px; font-size: 12px; }
  .msg pre { background: rgba(0,0,0,0.3); border-radius: 8px; padding: 10px; overflow-x: auto; }
  .msg pre code { background: none; padding: 0; }
  .msg img { max-width: 100%; border-radius: 10px; margin-top: 6px; display: block; }
  .caption { font-size: 11px; color: #475569; text-align: center; margin-top: 4px; }
  #input-row {
    display: flex; gap: 8px;
    padding: 10px 0 18px; align-items: flex-end;
  }
  textarea {
    flex: 1; background: #1e293b;
    border: 1px solid #334155; color: #e2e8f0;
    border-radius: 12px; padding: 10px 14px;
    font-size: 14px; font-family: inherit;
    resize: none; min-height: 44px; max-height: 140px;
    line-height: 1.5;
  }
  textarea:focus { outline: none; border-color: #3b82f6; }
  button#send {
    background: #2563eb; color: #fff;
    border: none; border-radius: 12px;
    padding: 0 22px; height: 44px;
    font-size: 14px; font-weight: 600; cursor: pointer;
    transition: background .15s;
  }
  button#send:hover:not(:disabled) { background: #1d4ed8; }
  button#send:disabled { background: #1e3a5f; color: #475569; cursor: not-allowed; }
  #status-bar {
    display: none; align-items: center; gap: 8px;
    padding: 6px 12px; margin-bottom: 4px;
    background: #0c1f36; border: 1px solid #1e3a5f;
    border-radius: 8px; font-size: 13px; color: #7dd3fc;
  }
  #status-bar.visible { display: flex; }
  .spinner {
    width: 14px; height: 14px; border-radius: 50%;
    border: 2px solid #1e3a5f; border-top-color: #60a5fa;
    animation: spin .7s linear infinite; flex-shrink: 0;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  #timer { color: #475569; font-variant-numeric: tabular-nums; }
</style>
</head>
<body>
<div id="app">
  <header>
    <h1>📊 Company Financial Analysis Agent</h1>
    <p>Claude Agent SDK &nbsp;·&nbsp; MCP &nbsp;·&nbsp; FastAPI &nbsp;·&nbsp; Vercel &nbsp;|&nbsp; 250 Portuguese companies &nbsp;·&nbsp; 14 financial columns</p>
  </header>
  <div id="examples">
    <span class="ex" onclick="submit('Describe the dataset')">Describe the dataset</span>
    <span class="ex" onclick="submit('Show me the first 10 companies')">First 10 companies</span>
    <span class="ex" onclick="submit('Average EBITDA by sector')">EBITDA by sector</span>
    <span class="ex" onclick="submit('Plot histogram of revenue')">Histogram of revenue</span>
    <span class="ex" onclick="submit('Scatter plot of revenue vs net_profit')">Revenue vs net profit</span>
    <span class="ex" onclick="submit('Show the correlation matrix')">Correlation matrix</span>
    <span class="ex" onclick="submit('Box plot of ebitda by size')">EBITDA by size</span>
    <span class="ex" onclick="submit('Which region has highest average revenue?')">Revenue by region</span>
  </div>
  <div id="messages"></div>
  <div id="status-bar">
    <div class="spinner"></div>
    <span id="status-text">Processing…</span>
    <span id="timer"></span>
  </div>
  <div id="input-row">
    <textarea id="txt" placeholder="Ask about the company data…" rows="1"></textarea>
    <button id="send" onclick="handleSend()">Send</button>
  </div>
</div>
<script>
  marked.setOptions({ breaks: true, gfm: true });

  const msgBox    = document.getElementById('messages');
  const txt       = document.getElementById('txt');
  const btn       = document.getElementById('send');
  const statusBar = document.getElementById('status-bar');
  const statusTxt = document.getElementById('status-text');
  const timerEl   = document.getElementById('timer');

  let timerInterval = null;

  function startTimer() {
    const t0 = Date.now();
    timerInterval = setInterval(() => {
      timerEl.textContent = '(' + Math.floor((Date.now() - t0) / 1000) + 's)';
    }, 1000);
    timerEl.textContent = '(0s)';
    statusBar.classList.add('visible');
  }

  function stopTimer() {
    clearInterval(timerInterval);
    timerInterval = null;
    statusBar.classList.remove('visible');
    timerEl.textContent = '';
  }

  function setStatus(text) {
    statusTxt.textContent = text;
  }

  txt.addEventListener('input', () => {
    txt.style.height = 'auto';
    txt.style.height = Math.min(txt.scrollHeight, 140) + 'px';
  });
  txt.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  });

  function scrollEnd() { msgBox.scrollTop = msgBox.scrollHeight; }

  function addMsg(cls, html) {
    const d = document.createElement('div');
    d.className = 'msg ' + cls;
    d.innerHTML = html;
    msgBox.appendChild(d);
    scrollEnd();
    return d;
  }

  function esc(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  function submit(text) { txt.value = text; handleSend(); }

  async function handleSend() {
    const text = txt.value.trim();
    if (!text || btn.disabled) return;
    txt.value = ''; txt.style.height = 'auto';
    btn.disabled = true;

    addMsg('user', esc(text));
    startTimer();
    setStatus('Connecting…');

    let bubble = null;
    let bufText = '';

    try {
      const resp = await fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: text})
      });

      if (!resp.ok) { addMsg('err', 'Server error: ' + resp.status); return; }

      const reader = resp.body.getReader();
      const dec = new TextDecoder();
      let buf = '';

      while (true) {
        const {done, value} = await reader.read();
        if (done) break;
        buf += dec.decode(value, {stream: true});
        const parts = buf.split('\\n\\n');
        buf = parts.pop();
        for (const part of parts) {
          if (!part.startsWith('data: ')) continue;
          let evt;
          try { evt = JSON.parse(part.slice(6)); } catch { continue; }

          if (evt.type === 'status') {
            setStatus(evt.content);
          } else if (evt.type === 'text') {
            bufText += evt.content;
            if (!bubble) bubble = addMsg('assistant', marked.parse(bufText));
            else { bubble.innerHTML = marked.parse(bufText); scrollEnd(); }
          } else if (evt.type === 'tool_call') {
            bubble = null; bufText = '';
            addMsg('tool', esc(evt.content));
          } else if (evt.type === 'image') {
            bubble = null; bufText = '';
            const cap = evt.caption ? `<div class="caption">${esc(evt.caption)}</div>` : '';
            addMsg('assistant', `<img src="${evt.content}" alt="${esc(evt.caption||'plot')}">` + cap);
          } else if (evt.type === 'error') {
            addMsg('err', '⚠️ ' + esc(evt.content));
          } else if (evt.type === 'done') {
            stopTimer();
          }
        }
      }
    } finally {
      stopTimer();
      btn.disabled = false;
      txt.focus();
    }
  }
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(title="Data Analysis Agent")


class ChatRequest(BaseModel):
    message: str


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML


@app.post("/chat")
async def chat(req: ChatRequest):
    return StreamingResponse(
        _agent_stream(req.message),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------------------------------------------------------------------------
# Local entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
