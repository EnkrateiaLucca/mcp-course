#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp[cli]>=1.9.3"]
# ///
"""Knowledge-base MCP server — RESOURCES demo.

Resources are read-only context the host can pull into the LLM prompt
(think: files, docs, DB rows). Tools, by contrast, are *actions* the
model can invoke. This server exposes resources only.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("acme-knowledge-base")

DOCS = {
    "company-faq": """# Acme Corp FAQ
Q: What does Acme do?
A: We build rocket-powered roller skates and anvil delivery systems.

Q: Where are you based?
A: Albuquerque, New Mexico.

Q: What are your hours?
A: 24/7 — coyotes never sleep.
""",
    "product-specs": """# Rocket Skate Model RS-9
- Top speed: 320 km/h
- Battery: 12 minutes of thrust
- Weight: 4.2 kg per skate
- Warranty: 30 days (excludes cliff falls)
- Color options: Red, Roadrunner Blue, Desert Tan
""",
    "pricing": """# Pricing
- RS-9 Rocket Skates: $499 / pair
- Anvil (standard, 50 kg): $89
- Anvil (giant, 250 kg): $249
- Bulk discount: 15% off orders of 10+ units
- Free shipping over $500
""",
    "support-policy": """# Support Policy
- Email: support@acme.example
- Response SLA: 1 business day
- Refunds: within 14 days of purchase, unused product only
- No refunds on items damaged by gravity-related incidents
""",
}


@mcp.resource("docs://company-faq", name="Company FAQ",
              description="Frequently asked questions about Acme Corp.")
def company_faq() -> str:
    return DOCS["company-faq"]


@mcp.resource("docs://product-specs", name="Product Specs",
              description="Technical specs for the RS-9 rocket skates.")
def product_specs() -> str:
    return DOCS["product-specs"]


@mcp.resource("docs://pricing", name="Pricing",
              description="Current product pricing and bulk discounts.")
def pricing() -> str:
    return DOCS["pricing"]


@mcp.resource("docs://support-policy", name="Support Policy",
              description="Customer support, SLA, and refund policy.")
def support_policy() -> str:
    return DOCS["support-policy"]


if __name__ == "__main__":
    mcp.run(transport="stdio")
