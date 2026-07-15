# /// script
# requires-python = ">=3.12"
# dependencies = ["duckdb>=1.1.0", "faker>=30.0.0", "numpy>=2.0.0"]
# ///
"""
Generate a synthetic `sabi_synth.duckdb` with English-language column and table
names (trimmed to the teaching-relevant subset of the original SABI schema).
Deterministic under a fixed seed so the committed .duckdb file stays
reproducible.

Run:
    uv run scripts/generate_dataset.py
"""

from __future__ import annotations

import os
import random
from dataclasses import dataclass
from pathlib import Path

import duckdb
import numpy as np
from faker import Faker

SEED = 20260422
N_COMPANIES = 150
YEARS = 5  # columns _0.._4 ; _0 is most recent (2025)
LATEST_YEAR = 2025

OUT = Path(__file__).resolve().parent.parent / "data" / "sabi_synth.duckdb"

# Trimmed CAE-style sectors with typical EBITDA margin ranges. One sector
# (food retail) is intentionally put into decline so the agent can discover it.
SECTORS = [
    # (code, label, revenue_mu_log, ebitda_lo, ebitda_hi, yoy_mu, yoy_sigma, decline)
    ("47110", "Food retail",              14.5, 0.03, 0.07, -0.04, 0.05, True),
    ("62010", "Software development",     14.0, 0.15, 0.28,  0.08, 0.06, False),
    ("41200", "Building construction",    15.0, 0.06, 0.12,  0.02, 0.10, False),
    ("10110", "Meat processing",          13.8, 0.04, 0.08,  0.01, 0.04, False),
    ("56100", "Restaurants",              13.2, 0.05, 0.10,  0.03, 0.07, False),
    ("71120", "Engineering & consulting", 13.9, 0.10, 0.20,  0.05, 0.05, False),
    ("86220", "Hospital activities",      14.6, 0.08, 0.15,  0.04, 0.03, False),
    ("49410", "Road transport",           14.1, 0.04, 0.09,  0.02, 0.06, False),
]

# Proper-noun place names are kept in Portuguese — they refer to real locations.
DISTRICTS = [
    ("Lisboa",   0.35),
    ("Porto",    0.25),
    ("Braga",    0.08),
    ("Aveiro",   0.07),
    ("Coimbra",  0.05),
    ("Setúbal",  0.05),
    ("Faro",     0.05),
    ("Leiria",   0.04),
    ("Évora",    0.03),
    ("Viseu",    0.03),
]

EXPENSE_CATEGORIES = [
    "subcontracting", "advertising", "professional_fees", "energy",
    "rent", "insurance", "maintenance", "specialized_services",
]

PIPELINE_STAGES = [
    "appointmentscheduled", "qualifiedtobuy", "presentationscheduled",
    "decisionmakerboughtin", "contractsent", "closedwon", "closedlost",
]


@dataclass
class Company:
    tax_id: str
    name: str
    district: str
    municipality: str
    sector_code: str
    sector_label: str
    revenue_mu: float
    ebitda_margin: float
    yoy_mu: float
    yoy_sigma: float
    headcount_0: int
    export_share: float


def _rnd_tax_id(fake: Faker, used: set[str]) -> str:
    while True:
        tax_id = str(random.randint(500_000_000, 599_999_999))
        if tax_id not in used:
            used.add(tax_id)
            return tax_id


def _municipality(district: str) -> str:
    table = {
        "Lisboa":  ["Lisboa", "Sintra", "Cascais", "Oeiras", "Loures", "Amadora"],
        "Porto":   ["Porto", "Vila Nova de Gaia", "Matosinhos", "Gondomar", "Maia"],
        "Braga":   ["Braga", "Guimarães", "Vila Nova de Famalicão"],
        "Aveiro":  ["Aveiro", "Santa Maria da Feira", "Ovar"],
        "Coimbra": ["Coimbra", "Figueira da Foz"],
        "Setúbal": ["Setúbal", "Almada", "Seixal", "Barreiro"],
        "Faro":    ["Faro", "Loulé", "Portimão"],
        "Leiria":  ["Leiria", "Marinha Grande", "Pombal"],
        "Évora":   ["Évora", "Montemor-o-Novo"],
        "Viseu":   ["Viseu", "Tondela"],
    }
    return random.choice(table.get(district, ["Unknown"]))


def generate_companies(fake: Faker) -> list[Company]:
    used: set[str] = set()
    companies: list[Company] = []
    districts_weighted = random.choices(
        [d for d, _ in DISTRICTS],
        weights=[w for _, w in DISTRICTS],
        k=N_COMPANIES,
    )
    for i in range(N_COMPANIES):
        sector = random.choice(SECTORS)
        code, label, rev_mu, ebi_lo, ebi_hi, yoy_mu, yoy_sigma, decline = sector
        district = districts_weighted[i]
        companies.append(
            Company(
                tax_id=_rnd_tax_id(fake, used),
                name=fake.company().replace(",", ""),
                district=district,
                municipality=_municipality(district),
                sector_code=code,
                sector_label=label,
                revenue_mu=np.random.normal(rev_mu, 0.6),
                ebitda_margin=np.random.uniform(ebi_lo, ebi_hi),
                yoy_mu=yoy_mu,
                yoy_sigma=yoy_sigma,
                headcount_0=max(3, int(np.random.lognormal(2.8, 0.8))),
                export_share=np.random.beta(1.5, 6.0),
            )
        )
    # Inject one high-debt company + a few with recent revenue jumps — findable anomalies
    companies[0].name = "Leverage Example SA"
    companies[1].name = "Iberian Exporter Lda"
    return companies


def _yoy_series(base_latest: float, yoy_mu: float, yoy_sigma: float) -> list[float]:
    """Return [year_0, year_1, ..., year_4] with year_0 = most recent."""
    series = [base_latest]
    val = base_latest
    for _ in range(YEARS - 1):
        step = np.random.normal(yoy_mu, yoy_sigma)
        val = val / (1.0 + step)  # walking backwards in time
        series.append(max(val, 1.0))
    return series


def build_main_financials(companies: list[Company]) -> list[dict]:
    rows: list[dict] = []
    for c in companies:
        revenue_0 = float(np.exp(c.revenue_mu))
        revenue = _yoy_series(revenue_0, c.yoy_mu, c.yoy_sigma)

        ebitda = [r * c.ebitda_margin * np.random.uniform(0.9, 1.1) for r in revenue]
        gross_margin = [r * np.random.uniform(0.35, 0.55) for r in revenue]
        net_income = [e * np.random.uniform(0.5, 0.8) - r * 0.02 for e, r in zip(ebitda, revenue)]
        headcount = [max(1, int(c.headcount_0 * (1.0 + np.random.normal(0, 0.05) * k))) for k in range(YEARS)]
        exports = [r * c.export_share * np.random.uniform(0.8, 1.2) for r in revenue]

        # Balance sheet (simple — teaching signal, not IFRS-accurate)
        total_assets = [r * np.random.uniform(0.7, 1.4) for r in revenue]
        equity = [a * np.random.uniform(0.2, 0.6) for a in total_assets]
        # Special case: company 0 is intentionally over-leveraged
        if c.name == "Leverage Example SA":
            equity = [a * np.random.uniform(0.03, 0.08) for a in total_assets]
        liabilities = [a - e for a, e in zip(total_assets, equity)]

        row = {
            "tax_id": c.tax_id,
            "name": c.name,
            "latest_year": LATEST_YEAR,
            "district": c.district,
            "municipality": c.municipality,
            "sector_code": c.sector_code,
            "sector_label": c.sector_label,
        }
        for k in range(YEARS):
            row[f"revenue_{k}"] = round(revenue[k], 2)
            row[f"gross_margin_{k}"] = round(gross_margin[k], 2)
            row[f"ebitda_{k}"] = round(ebitda[k], 2)
            row[f"net_income_{k}"] = round(net_income[k], 2)
            row[f"employees_{k}"] = headcount[k]
            row[f"exports_{k}"] = round(exports[k], 2)
            row[f"total_assets_{k}"] = round(total_assets[k], 2)
            row[f"equity_{k}"] = round(equity[k], 2)
            row[f"total_liabilities_{k}"] = round(liabilities[k], 2)
        rows.append(row)
    return rows


def build_operating_expenses(companies: list[Company], mf_rows: list[dict]) -> list[dict]:
    by_tax_id = {r["tax_id"]: r for r in mf_rows}
    out: list[dict] = []
    for c in companies:
        revenues = [by_tax_id[c.tax_id][f"revenue_{k}"] for k in range(YEARS)]
        # Operating expenses are typically 10–25% of revenue; split across categories
        total_opex = [r * np.random.uniform(0.10, 0.25) for r in revenues]
        weights = np.random.dirichlet(np.ones(len(EXPENSE_CATEGORIES)) * 2.0)
        row: dict = {
            "tax_id": c.tax_id,
            "name": c.name,
            "latest_year": LATEST_YEAR,
        }
        for cat_idx, cat in enumerate(EXPENSE_CATEGORIES):
            for k in range(YEARS):
                row[f"{cat}_{k}"] = round(total_opex[k] * weights[cat_idx], 2)
        out.append(row)
    return out


def build_ownership(companies: list[Company], fake: Faker) -> list[dict]:
    rows: list[dict] = []
    for c in companies:
        n_shareholders = random.choice([1, 2, 3, 4])
        remaining = 100.0
        for i in range(n_shareholders):
            pct = round(remaining if i == n_shareholders - 1
                       else min(remaining - 1, random.uniform(5, 70)), 2)
            remaining = round(remaining - pct, 2)
            rows.append({
                "tax_id": c.tax_id,
                "name": c.name,
                "latest_year": LATEST_YEAR,
                "shareholder_name": fake.name() if random.random() < 0.6 else fake.company(),
                "direct_ownership_pct": pct,
            })
    return rows


def build_subsidiaries(companies: list[Company]) -> list[dict]:
    rows: list[dict] = []
    # ~30% of companies own another
    parents = random.sample(companies, k=int(0.3 * len(companies)))
    for parent in parents:
        n_subs = random.choice([1, 2])
        subs = random.sample([c for c in companies if c.tax_id != parent.tax_id], k=n_subs)
        for sub in subs:
            rows.append({
                "tax_id": parent.tax_id,
                "name": parent.name,
                "latest_year": LATEST_YEAR,
                "subsidiary_name": sub.name,
                "ownership_pct": round(random.uniform(20, 100), 2),
            })
    return rows


def build_hubspot(companies: list[Company], fake: Faker) -> list[dict]:
    rows: list[dict] = []
    # 60% of companies have 1–3 deals
    for c in companies:
        if random.random() > 0.6:
            continue
        n_deals = random.choice([1, 1, 2, 3])
        for _ in range(n_deals):
            stage = random.choice(PIPELINE_STAGES)
            amount = np.random.lognormal(mean=10.5, sigma=1.1)
            rows.append({
                "record_id": str(random.randint(10**9, 10**10)),
                "deal_name": f"{c.name} — {fake.bs().title()}",
                "tax_id": c.tax_id,
                "pipeline_stage": stage,
                "amount": round(float(amount), 2),
                "close_date": fake.date_between(start_date="-18M", end_date="+6M").isoformat(),
                "updated_at": fake.date_time_this_year().isoformat(timespec="seconds"),
            })
    return rows


def _sql_type(value: object) -> str:
    if isinstance(value, bool):
        return "BOOLEAN"
    if isinstance(value, int):
        return "BIGINT"
    if isinstance(value, float):
        return "DOUBLE"
    return "VARCHAR"


def _insert(con: duckdb.DuckDBPyConnection, table: str, rows: list[dict]) -> None:
    """Recreate table from rows. Schema inferred from the first row's types."""
    if not rows:
        return
    columns = list(rows[0].keys())
    types = {c: _sql_type(rows[0][c]) for c in columns}
    # Promote to VARCHAR if any row has a non-numeric for a numeric col
    for r in rows:
        for c in columns:
            v = r.get(c)
            if v is None:
                continue
            if types[c] in ("BIGINT", "DOUBLE") and not isinstance(v, (int, float, bool)):
                types[c] = "VARCHAR"
    cols_ddl = ", ".join(f'"{c}" {types[c]}' for c in columns)
    con.execute(f"CREATE OR REPLACE TABLE {table} ({cols_ddl})")
    col_list = ", ".join(f'"{c}"' for c in columns)
    placeholders = ", ".join("?" for _ in columns)
    con.executemany(
        f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})",
        [tuple(r.get(c) for c in columns) for r in rows],
    )


def main() -> None:
    random.seed(SEED)
    np.random.seed(SEED)
    fake = Faker("pt_PT")
    Faker.seed(SEED)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        os.remove(OUT)

    companies = generate_companies(fake)

    print(f"Generating {len(companies)} companies...")
    companies_rows = [
        {
            "tax_id": c.tax_id,
            "name": c.name,
            "latest_year": LATEST_YEAR,
            "district": c.district,
            "municipality": c.municipality,
            "sector_code": c.sector_code,
            "sector_label": c.sector_label,
        }
        for c in companies
    ]
    mf_rows = build_main_financials(companies)
    opex_rows = build_operating_expenses(companies, mf_rows)
    own_rows = build_ownership(companies, fake)
    sub_rows = build_subsidiaries(companies)
    hub_rows = build_hubspot(companies, fake)

    con = duckdb.connect(str(OUT))
    _insert(con, "companies", companies_rows)
    _insert(con, "main_financials", mf_rows)
    _insert(con, "operating_expenses", opex_rows)
    _insert(con, "ownership", own_rows)
    _insert(con, "subsidiaries", sub_rows)
    _insert(con, "hubspot", hub_rows)

    print("Table row counts:")
    for t in ["companies", "main_financials", "operating_expenses",
              "ownership", "subsidiaries", "hubspot"]:
        n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t:<20} {n}")
    con.close()
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
