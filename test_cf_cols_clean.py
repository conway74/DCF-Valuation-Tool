import yfinance as yf
tk = yf.Ticker("KO")
cf = tk.cashflow
with open("yf_cols.txt", "w") as f:
    f.write(str(cf.columns))
    f.write("\n")
    if "Operating Cash Flow" in cf.index:
        f.write("Operating Cash Flow row:\n")
        f.write(str(cf.loc["Operating Cash Flow"]))
