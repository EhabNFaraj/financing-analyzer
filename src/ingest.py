import pandas as pd
from .config import RAW_DIR, INTERIM_DIR

# Map raw export headers to normalized names (adjust as needed)
COLUMN_MAP = {
    "Deal ID": "deal_id",
    "Funded Date": "date_funded",
    "Lender": "lender",
    "ZIP": "borrower_zip",
    "FICO": "fico_band",
    "Year": "vehicle_year",
    "Make": "vehicle_make",
    "Model": "vehicle_model",
    "Retail": "retail_price",
    "Sale": "sale_price",
    "Down": "down_payment",
    "Amt Financed": "amount_financed",
    "APR": "apr",
    "Term": "term_months",
    "Pmt": "payment_monthly",
    "DTI": "dti_ratio",
    "LTV": "ltv_ratio",
    "Status": "approval_status",
    "Callbacks": "callbacks",
}

def load_raw(pattern="*.csv"):
    frames = []
    for p in RAW_DIR.glob(pattern):
        df = pd.read_csv(p)
        df = df.rename(columns=COLUMN_MAP)
        frames.append(df)
    if not frames:
        raise FileNotFoundError("No raw files found in data/raw")
    out = pd.concat(frames, ignore_index=True)
    out.to_csv(INTERIM_DIR / "deals_clean.csv", index=False)
    return out
