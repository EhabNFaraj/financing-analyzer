# run.py  — interactive auto finance simulator with FICO + risk flags + min DP logic

def monthly_payment(principal: float, apr: float, term_months: int) -> float:
    r = apr / 12.0
    if term_months <= 0:
        return principal
    if r == 0:
        return principal / term_months
    return principal * r / (1 - (1 + r) ** (-term_months))

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def default_apr_from_fico(fico: int) -> float:
    # Rough defaults (annual % as decimal) to pre-fill for the user
    if fico >= 760: return 0.049
    if fico >= 720: return 0.059
    if fico >= 680: return 0.079
    if fico >= 640: return 0.119
    if fico >= 600: return 0.159
    return 0.219

def min_down_payment_pct_from_fico(fico: int) -> float:
    # Baseline minimum down payment expectation by FICO
    if fico >= 760: return 0.00   # strong prime: $0 down often possible
    if fico >= 720: return 0.05
    if fico >= 680: return 0.10
    if fico >= 640: return 0.15
    if fico >= 600: return 0.25
    return 0.35  # deep subprime

def score_components(fico, dti, ltv):
    # FICO 300..850 -> 0..1
    fico_s = clamp((fico - 300) / 550.0)

    # DTI scoring
    if dti <= 0.36: dti_s = 1.0
    elif dti <= 0.50: dti_s = 1.0 - (dti - 0.36) / 0.14 * 0.5
    elif dti <= 0.60: dti_s = 0.5 - (dti - 0.50) / 0.10 * 0.3
    else: dti_s = 0.1

    # LTV scoring
    if ltv <= 0.90: ltv_s = 1.0
    elif ltv <= 1.00: ltv_s = 1.0 - (ltv - 0.90) / 0.10 * 0.1
    elif ltv <= 1.20: ltv_s = 0.9 - (ltv - 1.00) / 0.20 * 0.6
    else: ltv_s = 0.2

    # Heavier weight on FICO as requested
    prob = clamp(0.6 * fico_s + 0.25 * dti_s + 0.15 * ltv_s)
    return prob

def decision_with_business_rules(fico, dti, ltv, dp_pct, risk_flag, min_dp_pct_base):
    """
    risk_flag = True if user has open auto loan or repo within 24 months.
    Returns label, probability, required_min_dp_pct (after bumps), reasons[]
    """
    reasons = []

    # If risk flag and weak credit -> auto deny
    if risk_flag and fico < 700:
        return "Denied", 0.0, max(min_dp_pct_base, 0.50), ["Recent auto risk + FICO < 700"]

    # Determine required down payment percentage
    req_dp_pct = min_dp_pct_base
    if risk_flag and fico >= 700:
        # Allow, but require ≥20% per your rule
        req_dp_pct = max(req_dp_pct, 0.20)

    # If still very weak credit, require even more
    if fico < 620:
        req_dp_pct = max(req_dp_pct, 0.40)

    # Cap at 50% as your upper bound
    req_dp_pct = min(req_dp_pct, 0.50)

    # Check if down payment meets requirement
    meets_dp = dp_pct + 1e-9 >= req_dp_pct
    if not meets_dp:
        reasons.append(f"Down payment below required minimum ({req_dp_pct:.0%}).")

    # Compute probability (FICO-weighted) and then bands
    prob = score_components(fico, dti, ltv)

    # Decision ladder with DP requirement considered
    if meets_dp and ((fico >= 720 and dti <= 0.45 and ltv <= 1.10) or prob >= 0.78):
        return "Approved", prob, req_dp_pct, reasons

    if meets_dp and ((fico >= 650 and dti <= 0.55 and ltv <= 1.20) or prob >= 0.58):
        return "Conditional Approval", prob, req_dp_pct, reasons

    # If DP doesn’t meet requirement, suggest conditional if they raise DP
    if not meets_dp and prob >= 0.50:
        return "Conditional Approval (needs higher down payment)", prob, req_dp_pct, reasons

    return "Denied", prob, req_dp_pct, reasons

def read_float(prompt, default=None, min_val=None, max_val=None):
    while True:
        raw = input(prompt).strip()
        if raw == "" and default is not None:
            return default
        try:
            val = float(raw)
            if min_val is not None and val < min_val:
                print(f"  Please enter ≥ {min_val}."); continue
            if max_val is not None and val > max_val:
                print(f"  Please enter ≤ {max_val}."); continue
            return val
        except ValueError:
            print("  Please enter a number (or press Enter for default).")

def read_yes_no(prompt, default="n"):
    d = default.lower() in ("y", "yes")
    while True:
        raw = input(prompt).strip().lower()
        if raw == "" and default is not None:
            return d
        if raw in ("y", "yes"): return True
        if raw in ("n", "no"): return False
        print("  Please answer y/n.")

def main():
    print("\n🔎  Welcome to the Auto Financing Approval Simulator\n")
    print("This tool estimates your approval probability based on your credit and finances.\n")

    # --- Inputs ---
    fico = int(read_float("Enter your credit score (FICO 300–850): ", min_val=300, max_val=850))
    income = read_float("Enter your monthly income (in $): ", min_val=0)
    housing = read_float("Enter your monthly rent/mortgage (in $): ", default=0, min_val=0)
    other_debt = read_float("Enter other monthly debt payments (credit cards, loans, etc) (in $): ", default=0, min_val=0)
    car_value = read_float("Enter the vehicle's price (in $): ", min_val=0)
    down_payment = read_float("Enter your available down payment (in $): ", default=0, min_val=0)
    risk_flag = read_yes_no("Any open auto loans OR a repossession within the past 24 months? (y/n): ", default="n")

    # Pre-fill APR by FICO, allow override
    apr_default = default_apr_from_fico(fico) * 100.0
    term_months = int(read_float("Enter loan term in months (default 60): ", default=60, min_val=12))
    apr_percent = read_float(f"Enter APR % (default {apr_default:.1f}): ", default=apr_default, min_val=0.0)
    apr = apr_percent / 100.0

    # --- Calculations ---
    principal = max(car_value - down_payment, 0.0)
    car_pmt = monthly_payment(principal, apr, term_months)
    total_debt = housing + other_debt + car_pmt
    dti = 0.0 if income <= 0 else total_debt / income
    ltv = 0.0 if car_value <= 0 else principal / car_value
    dp_pct = 0.0 if car_value <= 0 else down_payment / car_value

    base_min_dp = min_down_payment_pct_from_fico(fico)
    label, prob, req_dp_pct, reasons = decision_with_business_rules(
        fico=fico, dti=dti, ltv=ltv, dp_pct=dp_pct, risk_flag=risk_flag, min_dp_pct_base=base_min_dp
    )

    # --- Output ---
    print("\n📊 Results Summary")
    print("------------------")
    print(f"Vehicle Price: ${car_value:,.2f}")
    print(f"Down Payment: ${down_payment:,.2f}  ({dp_pct:.0%} of price)")
    print(f"Calculated Loan Amount: ${principal:,.2f}")
    print(f"Estimated Monthly Car Payment: ${car_pmt:,.2f}  (@ {apr_percent:.2f}% APR, {term_months} mo)")
    print(f"Debt-to-Income Ratio (DTI): {dti:.2f} → share of income going to debts.")
    print(f"Loan-to-Value Ratio (LTV): {ltv:.2f} → share of car financed by the loan.")
    if risk_flag:
        print("Risk Flag: Open auto loan or recent repo reported.")

    # Decision
    icon = "✅" if label == "Approved" else ("🟡" if "Conditional" in label else "❌")
    print(f"\n{icon} {label} (Estimated approval chance: {prob*100:.1f}%)")

    # Down payment requirements
    if dp_pct + 1e-9 < req_dp_pct:
        needed = max(0.0, req_dp_pct * car_value - down_payment)
        print(f"Minimum required down payment for this profile: {req_dp_pct:.0%} "
              f"→ ${req_dp_pct*car_value:,.0f} (you’re short by ${needed:,.0f}).")

    # Tips
    if dp_pct < req_dp_pct:
        print("💡 Tip: Increase your down payment to meet the required minimum for approval.")
    if dti > 0.45:
        print("💡 Tip: Lower monthly debts, increase term, or consider a cheaper car to reduce DTI.")
    if ltv > 1.0:
        print("💡 Tip: A larger down payment reduces LTV and improves approval odds.")
    if fico < 700:
        print("💡 Tip: Improving your FICO score can significantly boost approval odds and lower APR.")
    if risk_flag and fico < 700:
        print("💡 Note: With a recent repo or open auto loan and FICO < 700, most lenders will decline.")

    print("\nDisclaimer: This is a simplified demo model — not financial advice.\n")

if __name__ == "__main__":
    main()

