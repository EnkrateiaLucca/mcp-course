#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "claude-agent-sdk>=0.1.0",
#     "gradio>=5.0.0,<6.0.0",
#     "pandas",
#     "matplotlib",
#     "seaborn",
#     "tabulate",
#     "python-dotenv",
# ]
# ///
"""
Demo 06 — Data Analysis Agent
Gradio chat UI backed by Claude Agent SDK with an in-process MCP server.

Run locally:  uv run main.py
Deploy:       vercel deploy
"""
from __future__ import annotations

import os
import tempfile
import uuid
from pathlib import Path
from typing import Any

import gradio as gr
import matplotlib

matplotlib.use("Agg")  # non-interactive backend — must be set before pyplot import
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from dotenv import load_dotenv

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
# Mirrors the main_financials table schema: revenue, EBITDA, EBIT, net profit,
# total assets, equity, employees, exports — grouped by sector and region.
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
    sector_codes = [sectors[i][0] for i in sector_idx]
    sector_names = [sectors[i][1] for i in sector_idx]

    return pd.DataFrame({
        "company_name":  [f"Company {i+1:03d} Lda" for i in range(n)],
        "region":        rng.choice(regions, n),
        "sector":        sector_names,
        "sector_code":   sector_codes,
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

_ARTIFACTS: list[dict[str, Any]] = []

ARTIFACT_DIR = Path(tempfile.gettempdir()) / "agent_chat_artifacts"
ARTIFACT_DIR.mkdir(exist_ok=True)


def _push_image(fig: plt.Figure, caption: str) -> str:
    path = ARTIFACT_DIR / f"plot_{uuid.uuid4().hex[:8]}.png"
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)
    _ARTIFACTS.append({"type": "image", "path": str(path), "caption": caption})
    return str(path)


def _drain_artifacts() -> list[dict[str, Any]]:
    out = _ARTIFACTS.copy()
    _ARTIFACTS.clear()
    return out


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------

@tool(
    "describe_data",
    "Return summary statistics (pandas describe) for the preloaded dataset.",
    {},
)
async def describe_data(args: dict[str, Any]) -> dict[str, Any]:
    numeric = DATA.select_dtypes(include="number")
    categorical = DATA.select_dtypes(exclude="number")

    parts = [f"**Shape:** {DATA.shape[0]} rows × {DATA.shape[1]} columns\n"]

    if not numeric.empty:
        num_desc = numeric.describe().round(2)
        parts.append(f"**Numeric columns:**\n\n{num_desc.to_markdown()}")

    if not categorical.empty:
        cat_desc = categorical.describe()
        parts.append(f"**Categorical columns:**\n\n{cat_desc.to_markdown()}")

    return {"content": [{"type": "text", "text": "\n\n".join(parts)}]}


@tool(
    "show_head",
    "Show the first N rows of the dataset (N defaults to 5).",
    {"n": int},
)
async def show_head(args: dict[str, Any]) -> dict[str, Any]:
    n = int(args.get("n") or 5)
    md = DATA.head(n).to_markdown(index=False)
    return {"content": [{"type": "text", "text": f"First {n} rows:\n\n{md}"}]}


@tool(
    "column_info",
    "List columns with their dtypes, non-null counts, and unique-value counts.",
    {},
)
async def column_info(args: dict[str, Any]) -> dict[str, Any]:
    info = pd.DataFrame(
        {
            "dtype": DATA.dtypes.astype(str),
            "non_null": DATA.notna().sum(),
            "unique": DATA.nunique(),
        }
    )
    return {"content": [{"type": "text", "text": f"Columns:\n\n{info.to_markdown()}"}]}


@tool(
    "group_aggregate",
    (
        "Group the dataset by a column and aggregate a numeric column. "
        "Supported ops: mean, sum, count, median, min, max, std."
    ),
    {"group_by": str, "value_col": str, "op": str},
)
async def group_aggregate(args: dict[str, Any]) -> dict[str, Any]:
    group_by = args.get("group_by", "")
    value_col = args.get("value_col", "")
    op = (args.get("op") or "mean").lower()

    allowed_ops = {"mean", "sum", "count", "median", "min", "max", "std"}
    if op not in allowed_ops:
        return {
            "content": [
                {"type": "text", "text": f"Unsupported op '{op}'. Allowed: {sorted(allowed_ops)}"}
            ]
        }
    if group_by not in DATA.columns:
        return {
            "content": [
                {"type": "text", "text": f"Unknown group column '{group_by}'. Available: {list(DATA.columns)}"}
            ]
        }
    if value_col not in DATA.columns:
        return {
            "content": [
                {"type": "text", "text": f"Unknown value column '{value_col}'. Available: {list(DATA.columns)}"}
            ]
        }

    result = (
        DATA.groupby(group_by)[value_col]
        .agg(op)
        .reset_index()
        .rename(columns={value_col: f"{op}_{value_col}"})
    )
    return {
        "content": [
            {
                "type": "text",
                "text": f"{op}({value_col}) by {group_by}:\n\n{result.to_markdown(index=False)}",
            }
        ]
    }


@tool(
    "correlation_matrix",
    "Compute and plot the correlation matrix of all numeric columns.",
    {},
)
async def correlation_matrix(args: dict[str, Any]) -> dict[str, Any]:
    corr = DATA.select_dtypes(include="number").corr()
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax, fmt=".2f", vmin=-1, vmax=1)
    ax.set_title("Correlation matrix (numeric columns)")
    _push_image(fig, "Correlation matrix")
    return {
        "content": [
            {"type": "text", "text": f"Correlation matrix:\n\n{corr.round(3).to_markdown()}"}
        ]
    }


@tool(
    "plot_data",
    (
        "Create a visualization of the dataset. "
        "kind must be one of: bar, line, scatter, hist, box. "
        "x is the primary column. y is required for bar/line/scatter/box."
    ),
    {"kind": str, "x": str, "y": str},
)
async def plot_data(args: dict[str, Any]) -> dict[str, Any]:
    kind = (args.get("kind") or "").lower()
    x = args.get("x") or ""
    y = args.get("y") or None

    valid_kinds = {"bar", "line", "scatter", "hist", "box"}

    # Validate kind first
    if kind not in valid_kinds:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Unsupported plot kind '{kind}'. Try one of: {sorted(valid_kinds)}",
                }
            ]
        }

    # Validate columns
    if not x or x not in DATA.columns:
        return {
            "content": [
                {"type": "text", "text": f"Unknown column '{x}'. Available: {list(DATA.columns)}"}
            ]
        }
    if y and y not in DATA.columns:
        return {
            "content": [
                {"type": "text", "text": f"Unknown column '{y}'. Available: {list(DATA.columns)}"}
            ]
        }

    # Check y requirement
    needs_y = {"line", "scatter", "box"}
    if kind in needs_y and not y:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Plot kind '{kind}' requires both x and y columns. Please specify y.",
                }
            ]
        }

    fig, ax = plt.subplots(figsize=(8, 5))
    try:
        if kind == "hist":
            # Only use hue for categorical columns — numeric hue creates one
            # legend entry per unique float value (hundreds of entries).
            is_categorical = y and DATA[y].dtype in ("object", "category")
            sns.histplot(data=DATA, x=x, hue=y if is_categorical else None, bins=20, ax=ax)
        elif kind == "bar":
            if y:
                DATA.groupby(x)[y].mean().plot(kind="bar", ax=ax)
                ax.set_ylabel(f"mean({y})")
            else:
                DATA[x].value_counts().plot(kind="bar", ax=ax)
                ax.set_ylabel("count")
        elif kind == "scatter":
            sns.scatterplot(data=DATA, x=x, y=y, ax=ax, alpha=0.7)
        elif kind == "line":
            DATA.sort_values(x).plot(kind="line", x=x, y=y, ax=ax)
        elif kind == "box":
            sns.boxplot(data=DATA, x=x, y=y, ax=ax)
    except Exception as exc:
        plt.close(fig)
        return {"content": [{"type": "text", "text": f"Plot failed: {exc}"}]}

    caption = f"{kind} of {x}" + (f" vs {y}" if y else "")
    ax.set_title(caption)
    _push_image(fig, caption)
    return {"content": [{"type": "text", "text": f"Generated: {caption}."}]}


# ---------------------------------------------------------------------------
# In-process MCP server + agent configuration
# ---------------------------------------------------------------------------

analysis_server = create_sdk_mcp_server(
    name="analysis",
    version="1.0.0",
    tools=[
        describe_data,
        show_head,
        column_info,
        group_aggregate,
        correlation_matrix,
        plot_data,
    ],
)

ALLOWED_TOOLS = [
    "mcp__analysis__describe_data",
    "mcp__analysis__show_head",
    "mcp__analysis__column_info",
    "mcp__analysis__group_aggregate",
    "mcp__analysis__correlation_matrix",
    "mcp__analysis__plot_data",
]

SYSTEM_PROMPT = f"""You are a financial data analysis assistant embedded in a Gradio chat UI.

CRITICAL OUTPUT RULES — follow these exactly:
- NEVER use any special formatting modes, headers like "PAI", "NATIVE MODE", emoji mode names, or internal system formats.
- NEVER summarize or paraphrase tool output — always reproduce the full table or result returned by the tool verbatim in your response, formatted as markdown.
- When a tool returns a markdown table, paste the entire table into your reply unchanged.
- After the table, you may add 1-3 short bullet observations — but the table must come first and be complete.
- Do not truncate, abbreviate, or describe the table instead of showing it.

You have access to tools that operate on a dataset of {DATA.shape[0]} Portuguese companies
(synthetic data based on the sabi_hubspot schema — main_financials table).

Schema:
{DATA.dtypes.to_string()}

Columns: {list(DATA.columns)}

Column meanings:
- revenue, ebitda, ebit, net_profit, total_assets, equity, exports: financial figures in EUR
- employees: headcount
- sector / sector_code: industry classification (CAE)
- region: Portuguese district (Lisboa, Porto, etc.)
- size: micro / small / medium / large
- status: Active or Inactive

Tool usage guidelines:
- Always call the appropriate tool — never answer from training data.
- Use plot_data or correlation_matrix whenever a visualization would help.
- If the request is ambiguous, make a reasonable assumption and proceed.
"""


# ---------------------------------------------------------------------------
# Gradio chat bridge
# ---------------------------------------------------------------------------

def _artifact_to_message(art: dict[str, Any]) -> dict[str, Any]:
    if art["type"] == "image":
        return {
            "role": "assistant",
            "content": gr.Image(value=art["path"], label=art.get("caption"), show_label=True),
        }
    return {"role": "assistant", "content": str(art)}


_TOOL_LABELS = {
    "mcp__analysis__describe_data":     ("📊", "describe_data",      "Summarising dataset statistics"),
    "mcp__analysis__show_head":         ("👀", "show_head",          "Fetching first rows"),
    "mcp__analysis__column_info":       ("🗂️",  "column_info",        "Inspecting column types"),
    "mcp__analysis__group_aggregate":   ("🧮", "group_aggregate",    "Grouping and aggregating"),
    "mcp__analysis__correlation_matrix":("🔗", "correlation_matrix", "Computing correlations"),
    "mcp__analysis__plot_data":         ("📈", "plot_data",          "Generating plot"),
}

def _tool_call_message(block: ToolUseBlock) -> dict[str, Any]:
    icon, short, label = _TOOL_LABELS.get(block.name, ("🔧", block.name, "Calling tool"))
    # Show key input args so the user understands what the agent decided
    args = getattr(block, "input", {}) or {}
    args_str = ", ".join(f"`{k}={v}`" for k, v in args.items() if v) if args else ""
    detail = f" — {args_str}" if args_str else ""
    return {
        "role": "assistant",
        "content": f"{icon} **{label}** `{short}`{detail}",
    }


async def chat_fn(message: str, history: list[dict[str, Any]]):
    """Async generator — streams agent reply + chart artifacts to Gradio."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        yield [
            {
                "role": "assistant",
                "content": (
                    "❌ **ANTHROPIC_API_KEY not set.**\n\n"
                    "Add it to a `.env` file in this directory:\n```\nANTHROPIC_API_KEY=sk-ant-...\n```\n"
                    "Then restart the server."
                ),
            }
        ]
        return

    options = ClaudeAgentOptions(
        mcp_servers={"analysis": analysis_server},
        allowed_tools=ALLOWED_TOOLS,
        system_prompt=SYSTEM_PROMPT,
    )

    emitted: list[dict[str, Any]] = []
    buffer = ""

    async with ClaudeSDKClient(options=options) as client:
        await client.query(message)
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock) and block.text:
                        buffer += block.text
                        yield emitted + [{"role": "assistant", "content": buffer}]
                    elif isinstance(block, ToolUseBlock):
                        # Commit any text buffered before this tool call
                        if buffer.strip():
                            emitted.append({"role": "assistant", "content": buffer})
                            buffer = ""
                        # Show which tool the agent is calling
                        emitted.append(_tool_call_message(block))
                        yield emitted

                # Commit buffered text, then flush any artifacts produced by tool calls
                if buffer.strip():
                    emitted.append({"role": "assistant", "content": buffer})
                    buffer = ""
                for art in _drain_artifacts():
                    emitted.append(_artifact_to_message(art))
                    yield emitted

            elif isinstance(msg, ResultMessage):
                break

    # Final flush
    if buffer.strip():
        emitted.append({"role": "assistant", "content": buffer})
    for art in _drain_artifacts():
        emitted.append(_artifact_to_message(art))
    yield emitted


# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

CUSTOM_CSS = """
.gradio-container {
    max-width: 960px !important;
    margin: 0 auto !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}

/* Header card */
#header-md {
    background: linear-gradient(135deg, #0f2f5e 0%, #1565a8 100%);
    border-radius: 14px;
    padding: 28px 32px;
    margin-bottom: 4px;
    color: white !important;
}
#header-md h1, #header-md p, #header-md code {
    color: white !important;
}
#header-md code {
    background: rgba(255,255,255,0.15);
    border-radius: 4px;
    padding: 1px 6px;
}

/* Chat bubbles */
.message.bot, .message.assistant {
    border-radius: 12px !important;
}

/* Markdown tables inside chat messages — dark-theme safe */
.message table {
    border-collapse: collapse;
    width: 100%;
    font-size: 13px;
    margin: 8px 0;
}
.message th, .message td {
    border: 1px solid rgba(255,255,255,0.12);
    padding: 6px 10px;
    text-align: left;
}
.message th {
    background: rgba(255,255,255,0.08);
    font-weight: 600;
}
.message tr:nth-child(even) td {
    background: rgba(255,255,255,0.04);
}

/* Example prompt pills */
.examples-holder button {
    border-radius: 20px !important;
    font-size: 12px !important;
    padding: 4px 14px !important;
}

/* Input textarea — taller, no scrollbar */
textarea[placeholder="Type a message..."],
div.input-container textarea {
    min-height: 80px !important;
    max-height: 200px !important;
    height: 80px !important;
    overflow-y: hidden !important;
    resize: none !important;
    line-height: 1.6 !important;
    padding: 12px 14px !important;
    font-size: 14px !important;
}
div.input-container {
    min-height: 80px !important;
}
"""


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------

with gr.Blocks(
    title="Data Analysis Agent",
    theme=gr.themes.Soft(primary_hue="blue", secondary_hue="indigo", neutral_hue="slate"),
    css=CUSTOM_CSS,
) as demo:

    gr.Markdown(
        f"""
        # 📊 Company Financial Analysis Agent
        **Claude Agent SDK** + **MCP** + **Vercel** &nbsp;|&nbsp;
        Dataset: **Portuguese companies** &nbsp;`{DATA.shape[0]} rows × {DATA.shape[1]} cols`
        Columns: `{" · ".join(DATA.columns)}`
        Ask about revenue, EBITDA, employees, sectors, regions — the agent picks the right tool.
        """,
        elem_id="header-md",
    )

    gr.ChatInterface(
        fn=chat_fn,
        type="messages",
        examples=[
            "Describe the dataset",
            "Show me the first 10 companies",
            "What is the average EBITDA by sector?",
            "Plot a histogram of revenue",
            "Scatter plot of revenue vs net_profit",
            "Which region has the highest average revenue?",
            "Show the correlation matrix",
            "Box plot of ebitda by size",
        ],
        cache_examples=False,
    )


# ---------------------------------------------------------------------------
# Vercel ASGI export
# ---------------------------------------------------------------------------

# Vercel's @vercel/python runtime picks up `app` as the ASGI handler.
app = demo.app


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", "7860")),
        share=False,
    )
