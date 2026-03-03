import yfinance as yf
tk = yf.Ticker("KO")
cf = tk.cashflow
print(cf.columns)
