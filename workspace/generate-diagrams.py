# /// script
# requires-python = ">=3.11"
# dependencies = ["google-genai"]
# ///
"""Generate all 6 agent-basics diagram images using Gemini image generation."""

import os
import sys
from pathlib import Path
from google import genai
from google.genai import types

BRAND_STYLE = """
Style: Clean educational technical diagram combining precision with warm approachability.
Background: Warm Cream (#F5F3EB). Primary linework: Ink Black (#000000), 2px solid borders.
Sharp corners (0px border radius) on ALL rectangular shapes — no rounded corners whatsoever.
Accent colors: Coral (#E86B5A), Golden (#F5C542), Sage (#7CB56B), Sky (#5B9BD5).
Warm gray for disabled text: #DDD9D2.
Typography: Clean sans-serif for labels, monospace for code snippets.
High contrast, print-ready, WCAG AA accessible. 16:9 aspect ratio.
DO NOT use: rounded corners, gradients, 3D effects, photorealistic elements, pure white backgrounds, cool grays, decorative swooshes, emoji, cartoon characters.
This must look like a clean whiteboard/notebook diagram with precise technical annotation.
"""

OUTPUT_DIR = Path("/Users/greatmaster/Desktop/projects/oreilly-live-trainings/mcp-course/workspace/slides")

PROMPTS = {
    "diagram-user-llm.png": """
Generate a clean technical diagram for a presentation slide. The diagram should be on a warm cream (#F5F3EB) background.

The diagram shows the basic interaction between a user and an LLM:

Layout:
- Title text at the top center in large bold black font: "ChatGPT / Claude / Gemini"
- Below the title, centered on the slide:
  - A rectangle with sharp corners and black 2px border labeled "USER" in bold black text (on the left side)
  - A rectangle with sharp corners and black 2px border labeled "LLM" in bold black text (on the right side)
  - A straight horizontal arrow pointing from USER to LLM, with the word "text" written above the arrow in smaller font
  - A straight horizontal arrow pointing from LLM back to USER (below the first arrow), with the word "text" written below this arrow in smaller font
- The arrows should be clean with proper arrowheads
- Keep it simple and minimal — just these two boxes with bidirectional arrows labeled "text"
- The style should feel like a clean hand-drawn whiteboard diagram but with precise lines
""",

    "diagram-tool-use.png": """
Generate a clean technical diagram for a presentation slide showing how LLMs use tools. Warm cream (#F5F3EB) background.

Layout from top to bottom:
- At the very top, red/coral (#E86B5A) text: "(requires current knowledge)"
- Below that, black bold text: "What were the latest AI news in January of 2026?"
- Then the main diagram showing a flow with three boxes in a row:
  - Left box: "USER" (sharp corners, black border)
  - Middle box: "LLM" (sharp corners, black border)
  - Right box: "web search tool" (sharp corners, black border, slightly different background like light cream)

- Top arrows (left to right flow):
  - Arrow from USER to LLM with label "text" above it
  - Arrow from LLM to web search tool with label "tool call" above it

- Bottom arrows (right to left return flow):
  - Arrow from web search tool back toward LLM with label "search output" below it
  - Arrow from LLM back to USER with label "text + results from search" below it

- The return arrows should be below the forward arrows, creating a clear bidirectional flow
- Clean technical diagram style, black ink lines, sharp corners on all boxes
- A small paper/document icon could appear near the "web search tool" box to indicate external knowledge
""",

    "diagram-agent-step1.png": """
Generate a clean technical diagram for a presentation slide showing AI Agent architecture — Step 1 focusing on LLM API Access.

Warm cream (#F5F3EB) background.

Layout:
- At the very top, huge bold black text: "AGENT" (very large, display-size font, centered)
- Below that, smaller gray (#5C5750) text: "Intro Agents"
- Below that, a large rectangular container with a thin gray border containing the main diagram:

Inside the container:
- TOP FLOW (horizontal row of 4 boxes connected by arrows, left to right):
  - "USER" box (sharp corners, black border, bold text)
  - Arrow pointing right →
  - "LLM" box (sharp corners, RED/coral #E86B5A border to highlight it, bold text) with small text "LLM 2? LLM 3?" above it in gray
  - Arrow pointing right →
  - "Action" box (sharp corners, black border) with a small checkmark icon above it
  - Arrow pointing right →
  - "Observation" box (sharp corners, black border) with a small lightbulb/eye icon above it

- ABOVE THE FLOW: A curved arrow going from the LLM area back to the USER, labeled "Final output" in red/coral (#E86B5A) italic text. This represents the output being returned.

- BOTTOM LEFT of the container: Text block reading:
  "Writing Code for:"  (black, bold)
  "1. LLM API access"  (RED/coral #E86B5A, bold — this is the active/highlighted item)
  "2. Connection to Tools/Resources"  (light gray #DDD9D2 — grayed out, not yet revealed)
  "3. The Agent Logic"  (light gray #DDD9D2 — grayed out, not yet revealed)

The overall style should be a clean technical architecture diagram with sharp corners everywhere.
""",

    "diagram-agent-step2.png": """
Generate a clean technical diagram for a presentation slide showing AI Agent architecture — Step 2 focusing on Tools/Resources connection.

Warm cream (#F5F3EB) background.

Layout:
- At the very top, huge bold black text: "AGENT" (very large, display-size font, centered)
- Below that, smaller gray (#5C5750) text: "Intro Agents"
- Below that, a large rectangular container with a thin gray border containing the main diagram:

Inside the container:
- TOP FLOW (horizontal row of 4 boxes connected by arrows, left to right):
  - "USER" box (sharp corners, black border, bold text)
  - Arrow pointing right →
  - "LLM" box (sharp corners, RED/coral #E86B5A border, bold text) with small text "LLM 2? LLM 3?" above it in gray
  - Arrow pointing right →
  - "Action" box (sharp corners, black border) with a small checkmark icon above it
  - Arrow pointing right →
  - "Observation" box (sharp corners, black border) with a small lightbulb/eye icon above it

- ABOVE THE FLOW: A curved arrow from LLM back to USER, labeled "Final output" in coral red italic.

- TOOLS AREA (NEW in this step): Below and to the right of the flow, a bordered box with sage green (#7CB56B) border containing:
  - Three circular icons in a row: a magnifying glass search icon, a "W" (Wikipedia) icon, and "arXiv" text
  - Below the icons: a dark/black code bar showing: "function_response = function_to_call(**function_args)" in green monospace text
  - Below the code: small sage green italic text: "python functions and tool/function schemas"
  - An arrow/connection from the LLM box down to this tools area

- BOTTOM LEFT text block:
  "Writing Code for:"  (black, bold)
  "1. LLM API access"  (RED/coral #E86B5A, bold)
  "2. Connection to Tools/Resources"  (SAGE GREEN #7CB56B, bold — NOW highlighted/active)
  "3. The Agent Logic"  (light gray #DDD9D2 — still grayed out)

Clean technical architecture diagram, sharp corners everywhere, no rounded shapes.
""",

    "diagram-agent-step3.png": """
Generate a clean technical diagram for a presentation slide showing AI Agent architecture — Step 3 focusing on the Agent Logic loop.

Warm cream (#F5F3EB) background.

Layout:
- At the very top, huge bold black text: "AGENT" (very large, display-size font, centered)
- Below that, smaller gray (#5C5750) text: "Intro Agents"
- Below that, a large rectangular container with a thin gray border containing the main diagram:

Inside the container:
- TOP FLOW (horizontal row of 4 boxes connected by arrows):
  - "USER" box → "LLM" box (red/coral border) → "Action" box → "Observation" box
  - "LLM 2? LLM 3?" text above LLM box in gray
  - Checkmark icon above Action, lightbulb icon above Observation

- ABOVE THE FLOW: Curved "Final output" arrow (coral red) from LLM back to USER

- TOOLS AREA: Below the flow, box with sage green border containing:
  - Search, Wikipedia "W", arXiv icons in circles
  - Dark code bar: "function_response = function_to_call(**function_args)"
  - Green italic label: "python functions and tool/function schemas"

- THE AGENT LOOP (NEW in this step): A prominent golden/orange (#F5C542) curved arrow that goes from the Observation box, down through the tools area, and loops back up to the LLM box, representing the iterative agent loop. This arrow should be thick and clearly visible.

- At the bottom center: Bold golden text: "Loop until final output is reached"

- BOTTOM LEFT text block:
  "Writing Code for:"  (black, bold)
  "1. LLM API access"  (RED/coral #E86B5A, bold)
  "2. Connection to Tools/Resources"  (SAGE GREEN #7CB56B, bold)
  "3. The Agent Logic"  (GOLDEN #F5C542, bold — NOW highlighted/active)

Clean technical architecture diagram, sharp corners, no rounded shapes.
""",

    "diagram-agent-complete.png": """
Generate a clean technical diagram for a presentation slide showing the COMPLETE AI Agent architecture with all components highlighted.

Warm cream (#F5F3EB) background.

Layout:
- At the very top, huge bold black text: "AGENT" (very large, display-size font, centered)
- Below that, smaller gray (#5C5750) text: "Complete Architecture"
- Below that, a large rectangular container with a thick black border (slightly thicker than previous slides, 3px) containing the complete diagram:

Inside the container — ALL elements fully visible and emphasized:
- TOP FLOW (horizontal row of 4 boxes connected by arrows):
  - "USER" box (sharp corners, bold black border)
  - Arrow →
  - "LLM" box (sharp corners, RED/coral #E86B5A thick border, bold text) with "LLM 2? LLM 3?" in gray above
  - Arrow →
  - "Action" box (sharp corners, golden #F5C542 border) with checkmark icon
  - Arrow →
  - "Observation" box (sharp corners, golden #F5C542 border) with lightbulb icon

- ABOVE THE FLOW: Curved "Final output" arrow (coral red #E86B5A) from LLM back to USER

- TOOLS AREA: Box with sage green (#7CB56B) border containing:
  - Search magnifying glass, Wikipedia "W", arXiv icons in circles
  - Dark code bar: "function_response = function_to_call(**function_args)" in green monospace
  - Sage green italic: "python functions and tool/function schemas"

- THE AGENT LOOP: Thick golden (#F5C542) curved arrow looping from Observation through tools back to LLM

- Bottom center: Bold golden text: "Loop until final output is reached"

- BOTTOM LEFT text block (ALL items now in their colors):
  "Writing Code for:"  (black, bold)
  "1. LLM API access"  (RED/coral #E86B5A, bold)
  "2. Connection to Tools/Resources"  (SAGE GREEN #7CB56B, bold)
  "3. The Agent Logic"  (GOLDEN #F5C542, bold)

This is the COMPLETE, polished version. All elements should feel cohesive and the color coding should clearly distinguish the three coding areas. Sharp corners on every rectangle. Clean technical style.
"""
}


def generate_image(client, prompt, output_path):
    full_prompt = f"{prompt}\n\n{BRAND_STYLE}"
    try:
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
                image_config=types.ImageConfig(aspect_ratio="16:9")
            )
        )
        image_parts = [p for p in response.candidates[0].content.parts if p.inline_data]
        if image_parts:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            image_parts[0].as_image().save(str(output_path))
            return True
        print(f"  No image generated for: {output_path.name}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"  Error generating {output_path.name}: {e}", file=sys.stderr)
        return False


def main():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    ok, fail = 0, 0

    for filename, prompt in PROMPTS.items():
        output = OUTPUT_DIR / filename
        print(f"[{ok + fail + 1}/{len(PROMPTS)}] Generating: {filename}")
        if generate_image(client, prompt, output):
            print(f"  Saved: {output}")
            ok += 1
        else:
            fail += 1

    print(f"\nDone: {ok} generated, {fail} failed")
    sys.exit(0 if fail == 0 else 1)


if __name__ == "__main__":
    main()
