# src/simulate.py
import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------
# Deterministic seeds so runs are reproducible
random.seed(42)
np.random.seed(42)

# ---------------------------------------------------------------------
# Inventory and lenders (your choices)
MAKES_MODELS = {
    "Toyota": ["Camry", "Corolla", "RAV4", "Highlander", "Tacoma"],
    "Honda": ["Civic", "Accord", "CR-V", "Pilot"],
    "Nissan": ["Altima", "Sentra", "Rogue"],
    "Ford": ["Focus", "Fusion", "Escape", "F-150"],
    "Hyundai": ["Elantra", "Sonata", "Tucson"],
    "Chevy": ["Cruze", "Malibu", "Equinox", "Silverado"],
    "Subaru": ["Impreza", "Legacy", "Outback", "Forester"],
    "Kia": ["Forte", "Optima", "Soul", "Sorento", "Sportage"],
    "BMW": ["3 Series", "5 Series", "X3", "X5"],
    "Mercedes-Benz": ["C-Class", "E-Class", "GLC", "GLE"],
    "Land Rover": ["Range Rover Evoque", "Range Rover Sport", "Discovery Sport"],
}

LENDERS = ["Westlake Financial", "Greenwood Credit", "United Auto Credit"]

# FICO bands we’ll sample from (no weights = uniform; simple & safe)
FICO_BANDS = ["300-579", "580-669", "670-739", "740-799", "800+"]

# APR ranges by FICO (hard capped at 18.9% per your note)
APR_CAP = 18.9
APR_BY_FICO = {
    "300-579": (15.0, 18.9),
    "580-669": (11.0, 16.5),
    "670-739": (7.0, 12.0),
    "740-799": (4.0, 8.0),
    "800+": (2.9, 5.5),
}

# ---------------------------------------------------------------------
# Helpers

def random_zip_state():
    """Return a (zip, state) from CT, MA, or NY."""
    state = random.choice(["CT", "MA", "NY"])
    if state == "CT":
        z = f"0{random.randint(600, 699):03d}"        # 06000–06999
    elif state == "MA":
        z = f"0{random.randint(100, 279):03d}"        # 01000–02799
    else:
        z = f"{random.randint(100,149):03d}{random.randint(0,99):02d}"  # 10001–14999-ish
    return z, state


def random_vehicle():
    make = random.choice(list(MAKES_MODELS.keys()))
    model = random.choice(MAKES_MODELS[make])
    year = random.randint(2012, 2022)
    return year, make, model


def price_from_year(year: int) -> int:
    base = 32000 - (datetime.now().year - year) * 1200
    return max(5500, int(np.random.normal(base, 3000)))


def monthly_payment(principal: float, apr: float, term_months: int) -> float:
    r = apr / 100.0 / 12.0
    if r <= 1e-12:
        return round(principal / term_months, 2)
    pmt = principal * (r * (1 + r) ** term_months) / ((1 + r) ** term_months - 1)
    return round(pmt, 2)


def decide_status(fico_band: str, down: float, sale: float, dti: float, ltv: float, pti: float) -> str:
    """
    Simple, robust, rule-based status:
    - Deep subprime needs >=50% down or it's declined.
    - Count risk flags (DTI>0.45, LTV>1.15, PTI>0.15).
    - Strong credit with <=1 flag -> approved.
    - 670–739 with <=1 flag -> approved.
    - 580–669 needs >=20% down and <=1 flag -> approved.
    - 1 flag -> conditional; 2+ flags -> declined; otherwise conditional.
    """
    if fico_band == "300-579" and down < 0.50 * sale:
        return "declined"

    risk_flags = int(dti > 0.45) + int(ltv > 1.15) + int(pti > 0.15)

    if fico_band in ("740-799", "800+") and risk_flags <= 1:
        return "approved"
    if fico_band == "670-739" and risk_flags <= 1:
        return "approved"
    if fico_band == "580-669" and down >= 0.20 * sale and risk_flags <= 1:
        return "approved"

    if risk_flags == 1:
        return "conditional"
    if risk_flags >= 2:
        return "declined"

    return "conditional"


# ---------------------------------------------------------------------
# Core generator

def simulate_rows(n: int = 900, days_back: int = 210) -> pd.DataFrame:
    rows = []
    start_date = datetime.now() - timedelta(days=days_back)

    for i in range(n):
        date_funded = start_date + timedelta(days=random.randint(0, days_back))
        lender = random.choice(LENDERS)
        fico_band = random.choice(FICO_BANDS)

        year, make, model = random_vehicle()
        retail = price_from_year(year)

        # Sale price ~ 85%..100% of retail
        sale = int(retail * random.uniform(0.85, 1.00))

        # Down payment:
        if fico_band == "300-579":
            # If they don't put >=50% down, our rule will decline anyway
            down = int(sale * random.uniform(0.10, 0.60))
        elif fico_band == "580-669":
            down = int(sale * random.uniform(0.10, 0.30))
        else:
            down = int(sale * random.uniform(0.05, 0.25))
        down = max(300, min(down, sale))
        amt_fin = max(0, sale - down)

        # APR & term
        lo, hi = APR_BY_FICO[fico_band]
        apr = round(min(APR_CAP, random.uniform(lo, hi)), 1)
        term = random.choice([36, 48, 60, 72])
        pmt = monthly_payment(amt_fin, apr, term)

        # Income & ratios
        # (very rough distribution that scales with credit band)
        income_map = {
            "300-579": (2600, 4200),
            "580-669": (3200, 5200),
            "670-739": (4200, 6800),
            "740-799": (5200, 8200),
            "800+":    (6200, 9800),
        }
        lo_i, hi_i = income_map[fico_band]
        income_monthly = float(random.randint(lo_i, hi_i))

        other_debt = float(np.clip(np.random.normal(0.10, 0.05), 0.0, 0.35) * income_monthly)
        pti = round(pmt / (income_monthly + 1e-9), 3)
        dti = round((pmt + other_debt) / (income_monthly + 1e-9), 3)

        # Book value & LTV
        book_value = round(sale / float(np.clip(np.random.normal(1.03, 0.08), 0.85, 1.25)), 2)
        ltv = round(amt_fin / max(1000.0, book_value), 3)

        # Status (no probability arrays)
        status = decide_status(fico_band, float(down), float(sale), float(dti), float(ltv), float(pti))

        # Callbacks: simple uniform 0–3 (no weights to avoid sum errors)
        callbacks = random.choice([0, 1, 2, 3])

        zip_code, state = random_zip_state()

        rows.append(
            {
                "Deal ID": f"SIM-{date_funded:%y%m%d}-{i:04d}",
                "Funded Date": f"{date_funded:%Y-%m-%d}",
                "Lender": lender,
                "ZIP": zip_code,
                "State": state,
                "FICO": fico_band,
                "Year": year,
                "Make": make,
                "Model": model,
                "Retail": retail,
                "Sale": sale,
                "Down": down,
                "Amt Financed": amt_fin,
                "APR": apr,
                "Term": term,
                "Pmt": pmt,
                "DTI": dti,
                "PTI": pti,
                "LTV": ltv,
                "Status": status,
                "Callbacks": callbacks,
                "Income Monthly": round(income_monthly, 2),
                "Book Value": book_value,
            }
        )

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------
# CLI

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=900)
    ap.add_argument("--days_back", type=int, default=210)
    ap.add_argument("--out", type=str, default="data/raw/simulated_toroauto.csv")
    args = ap.parse_args()

    df = simulate_rows(n=args.rows, days_back=args.days_back)
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"Wrote {args.out} with {len(df)} rows")


if __name__ == "__main__":
    main()
