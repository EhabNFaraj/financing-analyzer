from pathlib import Path
RAW_DIR = Path("data/raw")
INTERIM_DIR = Path("data/interim")
PROCESSED_DIR = Path("data/processed")
REPORT_DIR = Path("reports")
CHART_DIR = REPORT_DIR / "charts"

# Risk thresholds
RISK_DTI = 0.40
RISK_LTV = 1.10
