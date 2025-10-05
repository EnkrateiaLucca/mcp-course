# /// script
# requires-python = ">=3.12"
# dependencies = ["replicate", "mcp"]
# ///

import replicate
import os
from mcp.server.fastmcp import FastMCP
from datetime import datetime


# replicate_api_token = os.getenv("REPLICATE_API_TOKEN")
# if not replicate_api_token:
#     raise ValueError("REPLICATE_API_TOKEN is not set")

mcp = FastMCP("thumbnail-mcp")

@mcp.tool(name="Generate Thumbnail Reference Photo",
          description="Generate a thumbnail reference photo always containing the keyword 'Lucas TOK' for a YouTube thumbnail")
def generate_thumbnail_reference_photo(prompt: str) -> str:
    """
    Generate a thumbnail reference photo always containing the keyword 'Lucas TOK' for a YouTube thumbnail.
    """
    output = replicate.run(
        "enkrateialucca/automata-learning-lab-yt-thumbnails-3:666a9524ff9741fa38fef57cab09bb4e3072830103b447a2bbce3b5e1f6cd236",
        input={
            "model": "dev",
            "prompt": prompt,
            "go_fast": False,
            "lora_scale": 1,
            "megapixels": "1",
            "num_outputs": 2,
            "aspect_ratio": "16:9",
            "output_format": "webp",
            "guidance_scale": 3,
            "output_quality": 100,
            "prompt_strength": 0.8,
            "extra_lora_scale": 1,
            "num_inference_steps": 28
        }
    )

    # To access the file URL:
    
    # for item in output:
    #     print(item.url())
    # To write the file to disk:
    for i,item in enumerate(output):
        with open(f"ref-thumbnail-photo-{datetime.now().strftime('%Y%m%d%H%M%S')}-{i}.png", "wb") as file:
            file.write(item.read())

    return f"Successfully generated {len(output)} thumbnail reference photos"


if __name__ == "__main__":
    # prompt = """
    # A dramatic YouTube thumbnail featuring Lucas TOK — a bald, muscular lean man with glasses — holding a round white logo (modern tech logo with abstract curved lines) above three stylized 3D humanoid figures representing software tools. Lucas looks surprised, with wide expressive eyes. The scene has a clean, studio-style lighting setup with a dark gray background. Green dashed arrows point from the round logo to each of the three humanoid figures below: one metallic gray with a cube symbol, one orange with a sunburst icon, and one black with a purple crystal icon. Cinematic lighting, sharp contrast, 3D render style, hyper-realistic, YouTube thumbnail composition.
    # """
    # generate_thumbnail_reference_photo(prompt)
    print("Starting MCP server...")
    mcp.run(transport="stdio")