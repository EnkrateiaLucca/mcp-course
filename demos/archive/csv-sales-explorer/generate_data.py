#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Generate a realistic mock sales CSV for Voltaic Gear (consumer electronics).

Deterministic (seeded) so the numbers in the course materials stay stable.
Writes data/sales_data.csv: one row per order line, Jan 2025 - Jun 2026.

Realism baked in:
  - upward growth trend across the 18 months
  - seasonality (Q4 holiday spike, quiet January, soft summer)
  - Black Friday week 2025 promo (volume x2.5, deep discounts)
  - Spring Sale April 2026 (volume x1.4, moderate discounts)
  - weekends quieter than weekdays
  - distributor channel = big multi-unit orders with structural discounts
  - regions weighted (NA > EU > APAC > LATAM), reps tied to regions
"""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

OUT = Path(__file__).parent / "data" / "sales_data.csv"

# (product, category, unit_price)
PRODUCTS = [
    ("Pulse Wireless Earbuds", "Audio", 129.00),
    ("Resonance Over-Ear Headphones", "Audio", 249.00),
    ("BoomBar Bluetooth Speaker", "Audio", 89.00),
    ("Vitality Fitness Band", "Wearables", 79.00),
    ("Horizon Smartwatch", "Wearables", 299.00),
    ("Glow Smart Bulb 4-Pack", "Smart Home", 49.00),
    ("SentryCam Security Camera", "Smart Home", 139.00),
    ("ClimaSense Thermostat", "Smart Home", 179.00),
    ("VoltCharge 65W GaN Charger", "Accessories", 45.00),
    ("MagGrip Phone Stand", "Accessories", 25.00),
    ("TrailCase Rugged Sleeve", "Accessories", 35.00),
]
# popularity weights (cheap accessories move more units)
PRODUCT_WEIGHTS = [10, 6, 9, 8, 5, 9, 7, 4, 12, 14, 8]

REGIONS = ["North America", "Europe", "APAC", "Latin America"]
REGION_WEIGHTS = [40, 30, 20, 10]

REPS = {
    "North America": ["Maya Chen", "Derek Holt"],
    "Europe": ["Sofia Lindqvist", "Tomás Ribeiro"],
    "APAC": ["Priya Nair", "Kenji Watanabe"],
    "Latin America": ["Camila Torres", "Diego Fuentes"],
}

CHANNELS = ["Online", "Retail", "Distributor"]
CHANNEL_WEIGHTS = [55, 30, 15]

START, END = date(2025, 1, 1), date(2026, 6, 30)
BLACK_FRIDAY = (date(2025, 11, 24), date(2025, 11, 30))
SPRING_SALE = (date(2026, 4, 6), date(2026, 4, 19))

SEASON = {1: 0.80, 2: 0.85, 3: 0.95, 4: 1.00, 5: 1.00, 6: 0.95,
          7: 0.90, 8: 0.90, 9: 1.05, 10: 1.15, 11: 1.45, 12: 1.60}


def orders_for(day: date) -> int:
    months_in = (day.year - 2025) * 12 + day.month - 1
    base = 8 + months_in * 0.35                      # growth trend
    mult = SEASON[day.month]
    if day.weekday() >= 5:
        mult *= 0.75                                 # quieter weekends
    if BLACK_FRIDAY[0] <= day <= BLACK_FRIDAY[1]:
        mult *= 2.5
    elif SPRING_SALE[0] <= day <= SPRING_SALE[1]:
        mult *= 1.4
    return max(1, round(random.gauss(base * mult, base * 0.25)))


def make_row(day: date, order_id: int) -> list:
    product, category, price = random.choices(PRODUCTS, PRODUCT_WEIGHTS)[0]
    region = random.choices(REGIONS, REGION_WEIGHTS)[0]
    rep = random.choice(REPS[region])
    channel = random.choices(CHANNELS, CHANNEL_WEIGHTS)[0]

    if channel == "Distributor":
        units = random.randint(10, 50)
        discount = random.choice([20, 25, 30, 35])
    else:
        units = random.choices([1, 2, 3, 4, 5], [55, 25, 10, 6, 4])[0]
        if BLACK_FRIDAY[0] <= day <= BLACK_FRIDAY[1]:
            discount = random.choice([15, 20, 25])
        elif SPRING_SALE[0] <= day <= SPRING_SALE[1]:
            discount = random.choice([10, 15])
        else:
            discount = random.choices([0, 5, 10], [80, 12, 8])[0]

    revenue = round(units * price * (1 - discount / 100), 2)
    return [f"ORD-{order_id:06d}", day.isoformat(), product, category, region,
            channel, rep, units, f"{price:.2f}", discount, f"{revenue:.2f}"]


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows, order_id, day = [], 100001, START
    while day <= END:
        for _ in range(orders_for(day)):
            rows.append(make_row(day, order_id))
            order_id += 1
        day += timedelta(days=1)

    with OUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["order_id", "date", "product", "category", "region",
                    "channel", "sales_rep", "units", "unit_price",
                    "discount_pct", "revenue"])
        w.writerows(rows)

    total = sum(float(r[-1]) for r in rows)
    print(f"wrote {len(rows)} rows -> {OUT}")
    print(f"total revenue ${total:,.0f} across {START} .. {END}")


if __name__ == "__main__":
    main()
