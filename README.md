# Toro Auto Financing & Payment Analyzer

A real‑world, portfolio‑ready project based on daily workflows at **Toro Auto**. It ingests deal/finance exports, cleans them, and produces insights: approval rates, APR trends, lender mix, and risk flags (DTI/LTV).

## Quickstart
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt

# First run (uses sample data already in data/raw)
python -m src.cli run-weekly
```

Outputs will appear in `reports/` (Excel summary + charts).

## Repo Structure
```
financing-analyzer/
├─ README.md
├─ requirements.txt
├─ .gitignore
├─ data/
│  ├─ raw/                 # CSV exports (sample included)
│  ├─ interim/             # cleaned CSV (after ingest)
│  ├─ processed/           # model-ready tables
│  └─ schema.sql
├─ src/
│  ├─ config.py
│  ├─ ingest.py
│  ├─ analyze.py
│  ├─ viz.py
│  └─ cli.py
├─ reports/
│  └─ charts/
├─ tests/
│  ├─ test_ingest.py
│  └─ test_analyze.py
└─ notebooks/
   └─ 01_eda.ipynb
```

## Data Privacy
- Do **not** commit PII. Keep only aggregate stats and fake/sample data.
