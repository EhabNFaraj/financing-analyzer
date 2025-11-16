🚗 Toro Auto Financing & Payment Analyzer

A practical, portfolio-ready project based on real dealership workflows at Toro Auto.
This repository contains:

1️⃣ Automated Financing Data Pipeline (ETL + Analytics + Excel Reporting)

Ingests and cleans simulated financing data

Computes approval rates, lender mix, APR trends, and risk metrics (DTI/LTV)

Exports weekly Excel reports with tables and charts

Demonstrates strong Python, Pandas, and automation skills

2️⃣ Interactive Auto Financing Approval Simulator (run.py)

A command-line tool that estimates financing approval likelihood using realistic rules based on:

FICO score

Monthly income

Housing/other debt

Vehicle price

Down payment

Loan term + APR

Risk flags (open auto loan or repossession within the last 24 months)

The simulator applies rules similar to real lenders:
High credit → easier approvals & lower DP requirements
Low credit → larger down payments required
Recent repo → auto-deny unless FICO is 700+

🚀 Quickstart (Data Pipeline)
python -m venv .venv
source .venv/bin/activate    # macOS/Linux
# .venv\Scripts\activate     # Windows

pip install -r requirements.txt

python -m src.cli run-weekly


Your weekly Excel report will appear in:

reports/weekly_summary.xlsx

🧮 Run the Interactive Simulator
python run.py


You will be asked for:

Credit score (FICO)

Monthly income

Monthly housing payment

Other debt payments

Vehicle price

Down payment

Loan term

APR

Any open auto loans or repossessions in last 24 months

The simulator then calculates:

Monthly payment (based on APR + term)

Debt-to-Income ratio (DTI)

Loan-to-Value ratio (LTV)

Minimum required down payment

Approval status (Approved / Conditional / Denied)

Approval probability

Tips to improve approval odds

📂 Repository Structure
financing-analyzer/
├─ run.py                   # Interactive approval simulator
├─ README.md
├─ requirements.txt
├─ .gitignore
│
├─ data/
│  ├─ raw/                 # Input CSVs (sample included)
│  ├─ interim/             # Cleaned CSVs
│  ├─ processed/           # Model-ready tables
│  └─ schema.sql
│
├─ src/
│  ├─ config.py            # Global settings
│  ├─ ingest.py            # Data cleaning & normalization
│  ├─ analyze.py           # Risk metrics & lender analytics
│  ├─ viz.py               # Chart generation
│  └─ cli.py               # Command-line wrapper
│
├─ reports/
│  └─ charts/              # Rendered plots
│
└─ notebooks/
   └─ 01_eda.ipynb         # Exploratory data analysis

🔒 Data Privacy Notice

This project uses fake, synthetic, auto-generated sample data.
No real customer information is used or stored.
Do not upload real dealership data to this repository.

🎯 What This Project Demonstrates

Auto-finance data cleaning and ETL

Credit-based approval modeling

DTI/LTV risk assessment

Simulated dealership decision logic

Python scripting & automation

Pandas + NumPy data workflows

Excel report generation with visuals

Creating user-friendly interactive tools

Clean GitHub project structure & documentation
