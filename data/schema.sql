CREATE TABLE IF NOT EXISTS deals (
  deal_id TEXT PRIMARY KEY,
  date_funded DATE,
  lender TEXT,
  borrower_zip TEXT,
  fico_band TEXT,
  vehicle_year INTEGER,
  vehicle_make TEXT,
  vehicle_model TEXT,
  retail_price REAL,
  sale_price REAL,
  down_payment REAL,
  amount_financed REAL,
  apr REAL,
  term_months INTEGER,
  payment_monthly REAL,
  dti_ratio REAL,
  ltv_ratio REAL,
  approval_status TEXT,
  callbacks INTEGER,
  delinquent_30d INTEGER
);
CREATE INDEX IF NOT EXISTS idx_deals_date ON deals(date_funded);
CREATE INDEX IF NOT EXISTS idx_deals_lender ON deals(lender);
CREATE INDEX IF NOT EXISTS idx_deals_fico ON deals(fico_band);
