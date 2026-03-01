# /// script
# requires-python = ">=3.11"
# dependencies = ["google-genai"]
# ///
"""Generate 4 MCP integration diagram images using Gemini image generation."""

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
Warm gray for disabled/secondary: #DDD9D2. Dark gray for text: #2A2825.
Typography: Clean sans-serif for labels, monospace for code snippets.
High contrast, print-ready, WCAG AA accessible. 16:9 aspect ratio.
DO NOT use: rounded corners, gradients, 3D effects, photorealistic elements, pure white backgrounds, cool grays, decorative swooshes, emoji, cartoon characters.
This must look like a clean whiteboard/notebook diagram with precise technical annotation.
"""

OUTPUT_DIR = Path("/Users/greatmaster/Desktop/projects/oreilly-live-trainings/mcp-course/workspace/slides")

PROMPTS = {
    "diagram-mcp-basic.png": """
Generate a clean technical diagram for a presentation slide on warm cream (#F5F3EB) background.

This diagram shows the basic concept of MCP (Model Context Protocol):

Layout (centered on slide, horizontal flow left to right):
- Inside a light gray bordered container:
  - Left: A rectangle with sharp corners and black 2px border labeled "LLM" in bold black text
  - Above the LLM box: Small red/coral (#E86B5A) italic text: "ChatGPT / Claude / Gemini"
  - Arrow pointing right from LLM to the middle box
  - Middle: A rectangle with sharp corners, black 2px border, and GOLDEN/YELLOW (#F5C542) background fill labeled "MCP" in bold black text
  - Above the MCP box: Small red/coral (#E86B5A) italic text: "Tools / Resources / Prompts"
  - Arrow pointing right from MCP to the right box
  - Right: A rectangle with sharp corners and black 2px border labeled "Context" in bold black text

- The arrows should be clean straight horizontal arrows with proper arrowheads
- The three boxes should be roughly equal size, arranged in a clear horizontal row
- Keep it simple and minimal — just these three boxes connected by arrows
- The MCP box should stand out with its yellow/golden background
- The whole diagram should be inside a subtle light gray bordered frame
""",

    "diagram-mcp-mn-problem.png": """
Generate a clean technical diagram for a presentation slide on warm cream (#F5F3EB) background.

This diagram shows the M×N integration problem (WITHOUT MCP):

Layout:
- Title at top center in bold black text with a RED X mark: "M × N integrations" (with a red coral #E86B5A "✗" or "×" symbol to indicate this is problematic)
- Two columns of boxes with crossing arrows between them:

LEFT COLUMN (labeled "M" in small text above):
  - Three rectangles stacked vertically, each with sharp corners, black 2px border, and GOLDEN/YELLOW (#F5C542) background:
    - "LLM1" (top)
    - "LLM2" (middle)
    - "LLM3" (bottom)

RIGHT COLUMN (labeled "N" in small text above):
  - Three rectangles stacked vertically, each with sharp corners, black 2px border:
    - "Resources" with PINK/CORAL LIGHT (#FBEAE7) background (top)
    - "Tools" with SAGE GREEN LIGHT (#EEF5EC) background (middle)
    - "Prompts" with SKY BLUE LIGHT (#E8F1F9) background (bottom)

ARROWS:
  - Every LLM connects to every item on the right (9 arrows total)
  - LLM1 → Resources, LLM1 → Tools, LLM1 → Prompts
  - LLM2 → Resources, LLM2 → Tools, LLM2 → Prompts
  - LLM3 → Resources, LLM3 → Tools, LLM3 → Prompts
  - The arrows should cross in the middle, creating a messy web of connections
  - This visually communicates the complexity of the M×N problem

- All boxes have sharp corners, no rounded edges
- The crossing arrows should feel deliberately messy/complex to show the problem
""",

    "diagram-mcp-mn-lines.png": """
Generate a clean technical diagram for a presentation slide on warm cream (#F5F3EB) background.

This diagram shows the M×N integration problem with emphasis on each line being a separate integration:

Layout:
- Title at top center in bold black text: "M × N integrations"
- Small annotation text near the arrows: "each line is an integration" in gray (#5C5750) italic

LEFT COLUMN:
  - Three rectangles stacked vertically with GOLDEN/YELLOW (#F5C542) background, sharp corners, black 2px border:
    - "LLM1" (top)
    - "LLM2" (middle)
    - "LLM3" (bottom)

RIGHT COLUMN:
  - Three rectangles stacked vertically, sharp corners, black 2px border:
    - "Resources" with PINK/CORAL LIGHT (#FBEAE7) background (top)
    - "Tools" with SAGE GREEN LIGHT (#EEF5EC) background (middle)
    - "Prompts" with SKY BLUE LIGHT (#E8F1F9) background (bottom)

ARROWS:
  - Every LLM connects to every item on the right (9 arrows total)
  - Each arrow represents one integration
  - The arrows cross in the middle creating a complex web
  - Arrows should be clearly visible individual lines (not merged)

- Clean technical style, all sharp corners
- The purpose is to show that without MCP, you need M×N separate integrations
""",

    "diagram-mcp-mn-solution.png": """
Generate a clean technical diagram for a presentation slide on warm cream (#F5F3EB) background.

This diagram shows the MCP solution: M+N integrations instead of M×N:

Layout:
- Title at top center in bold black text: "M + N integrations"

LEFT COLUMN:
  - Three rectangles stacked vertically with GOLDEN/YELLOW (#F5C542) background, sharp corners, black 2px border:
    - "LLM1" (top)
    - "LLM2" (middle)
    - "LLM3" (bottom)

CENTER:
  - A larger rectangle with sharp corners, GRAY (#DDD9D2) background, and black 2px border labeled "MCP" in bold black text
  - This box is positioned between the two columns

RIGHT COLUMN:
  - Three rectangles stacked vertically, sharp corners, black 2px border:
    - "Resources" with PINK/CORAL LIGHT (#FBEAE7) background (top)
    - "Tools" with SAGE GREEN LIGHT (#EEF5EC) background (middle)
    - "Prompts" with SKY BLUE LIGHT (#E8F1F9) background (bottom)

ARROWS (KEY DIFFERENCE - much simpler!):
  - LEFT SIDE: Only 3 arrows (one from each LLM to the MCP box)
    - LLM1 → MCP
    - LLM2 → MCP
    - LLM3 → MCP
  - RIGHT SIDE: Only 3 arrows (one from MCP to each resource type)
    - MCP → Resources
    - MCP → Tools
    - MCP → Prompts

- Below left column: Red/coral (#E86B5A) italic text: "M = number of Models"
- Below right column: Red/coral (#E86B5A) italic text: "N = number of Integrations"

- This shows the elegant simplification: instead of 9 arrows (M×N), only 6 arrows (M+N)
- The MCP box acts as a hub/intermediary
- All sharp corners, clean technical style
- The contrast with the previous messy diagram should be visually striking
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
