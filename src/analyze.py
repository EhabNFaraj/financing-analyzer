import pandas as pd
from .config import INTERIM_DIR, REPORT_DIR, RISK_DTI, RISK_LTV

def _load_clean():
    return pd.read_csv(INTERIM_DIR / "deals_clean.csv", parse_dates=["date_funded"])

def kpis():
    df = _load_clean()
    df["approval_status"] = df["approval_status"].astype(str).str.lower()
    df["risky"] = (df["dti_ratio"] > RISK_DTI) | (df["ltv_ratio"] > RISK_LTV)
    approved = df[df["approval_status"].eq("approved")]

    out = {}
    out["overall_approval_rate"] = (df["approval_status"].eq("approved")).mean()
    if not approved.empty:
        out["apr_by_lender"] = approved.groupby("lender")["apr"].mean().sort_values()
    else:
        out["apr_by_lender"] = pd.Series(dtype=float)
    out["approval_by_fico"] = (
        df.assign(is_approved=df["approval_status"].eq("approved"))
          .groupby("fico_band")["is_approved"].mean().sort_values()
    )
    out["risky_share_overall"] = df["risky"].mean()
    out["risky_by_month"] = (
        df.set_index("date_funded").resample("MS")["risky"].mean()
    )
    return out

def save_excel_summary(kpi_dict, fname="weekly_summary.xlsx"):
    path = REPORT_DIR / fname
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path, engine="xlsxwriter") as xw:
        pd.DataFrame({"overall_approval_rate":[kpi_dict["overall_approval_rate"]]}).to_excel(xw, sheet_name="Summary", index=False)
        if not kpi_dict["apr_by_lender"].empty:
            kpi_dict["apr_by_lender"].reset_index(name="avg_apr").to_excel(xw, sheet_name="APR by Lender", index=False)
        kpi_dict["approval_by_fico"].reset_index(name="approval_rate").to_excel(xw, sheet_name="Approval by FICO", index=False)
        kpi_dict["risky_by_month"].rename("risky_share").to_frame().to_excel(xw, sheet_name="Risk Trend")
    return path
