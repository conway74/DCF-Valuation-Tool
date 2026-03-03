import warnings
warnings.filterwarnings('ignore')

from src.app import fetch_company_data
data = fetch_company_data("KO")
for k, v in data.items():
    print(f"{k}: {v}")

print("========================")
rev_b = data["revenue"] / 1e9
fcf_b = data["free_cash_flow"] / 1e9

default_fcf_margin = (fcf_b / rev_b * 100) if rev_b > 0 else 20.0
default_fcf_margin = round(max(5.0, min(50.0, default_fcf_margin)) * 2) / 2  # snap to 0.5 steps

info_growth = data.get("revenue_growth")
if info_growth and info_growth > 0:
    default_growth = round(min(30.0, info_growth * 100) * 2) / 2
elif rev_b > 0:
    default_growth = 5.0  # conservative fallback
else:
    default_growth = 10.0

beta_val = data.get("beta", 1.0) or 1.0
default_wacc = round((4.5 + beta_val * 5.5) * 10) / 10  # snap to 0.1 steps
default_wacc = max(5.0, min(20.0, default_wacc))

print(f"FCF Margin: {default_fcf_margin}")
print(f"Growth: {default_growth}")
print(f"WACC: {default_wacc}")
