import yfinance as yf
tk = yf.Ticker("KO")
cf = tk.cashflow
print("Operating CF:", cf.loc["Operating Cash Flow"].iloc[0])
print("Capex:", cf.loc["Capital Expenditure"].iloc[0])
print("Free CF:", cf.loc["Free Cash Flow"].iloc[0] if "Free Cash Flow" in cf.index else "N/A")
print("Info operatingCF:", tk.info.get("operatingCashflow"))
print("Info freeCF:", tk.info.get("freeCashflow"))
print("Info shares:", tk.info.get("sharesOutstanding"))
print("Info debt:", tk.info.get("totalDebt"))
print("Info cash:", tk.info.get("totalCash"))
