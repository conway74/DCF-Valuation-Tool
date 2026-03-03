import yfinance as yf
tk = yf.Ticker("KO")
print("CASHFLOW:")
print(tk.cashflow.loc[["Operating Cash Flow", "Capital Expenditure", "Free Cash Flow"]])
print("----------")
print(tk.info.get("operatingCashflow"))
print(tk.info.get("freeCashflow"))
