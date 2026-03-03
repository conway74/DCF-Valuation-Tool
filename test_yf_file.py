import yfinance as yf
tk = yf.Ticker("KO")
cf = tk.cashflow
with open("yf_output.txt", "w") as f:
    f.write(f"Operating CF: {cf.loc['Operating Cash Flow'].iloc[0]}\n")
    f.write(f"Capex: {cf.loc['Capital Expenditure'].iloc[0]}\n")
    if "Free Cash Flow" in cf.index:
        f.write(f"Free CF: {cf.loc['Free Cash Flow'].iloc[0]}\n")
    f.write(f"Info operatingCF: {tk.info.get('operatingCashflow')}\n")
    f.write(f"Info freeCF: {tk.info.get('freeCashflow')}\n")
    f.write(f"Info shares: {tk.info.get('sharesOutstanding')}\n")
    f.write(f"Info debt: {tk.info.get('totalDebt')}\n")
    f.write(f"Info cash: {tk.info.get('totalCash')}\n")
