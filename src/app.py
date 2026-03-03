import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# --- PAGE CONFIG & STYLING ---
st.set_page_config(
    page_title="DCF Valuation Tool",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        font-size: 2.4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1a73e8, #8e24aa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280;
        margin-top: 0.25rem;
        margin-bottom: 1.5rem;
    }
    .valuation-card {
        background: linear-gradient(135deg, #f0f4ff, #e8f0fe);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #c2d5f7;
    }
    .snapshot-metric {
        background: #f8f9fa;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        border-left: 4px solid #1a73e8;
        margin-bottom: 0.5rem;
    }
    div[data-testid="stMetric"] {
        background: #f8f9fa;
        padding: 0.75rem 1rem;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================
st.markdown('<div class="main-header">📈 DCF Valuation Tool</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Discounted Cash Flow analysis for any public company — adjust assumptions, explore scenarios, and learn the math.</div>', unsafe_allow_html=True)


# ============================================================
# SIDEBAR — INPUTS
# ============================================================
st.sidebar.header("🔧 Company & Assumptions")

ticker_symbol = st.sidebar.text_input(
    "Stock Ticker",
    "KO",
    help="Enter any public company ticker symbol (e.g., KO, AAPL, MSFT, JNJ, GOOG).",
).upper().strip()

# ============================================================
# DATA RETRIEVAL
# ============================================================
@st.cache_data(ttl=300, show_spinner="Fetching financial data…")
def fetch_company_data(symbol: str) -> dict:
    """Retrieve financial data for a given ticker from Yahoo Finance."""
    tk = yf.Ticker(symbol)
    info = tk.info

    def _safe(df, key, fallback=0):
        """Safely get a value from a DataFrame row, returning fallback if NaN or missing."""
        try:
            if key in df.index:
                val = df.loc[key].iloc[0]
                if pd.notna(val):
                    return float(val)
        except Exception:
            pass
        return fallback

    def _nz(val, fallback=0):
        """Return fallback if val is None or NaN."""
        if val is None:
            return fallback
        try:
            if pd.isna(val):
                return fallback
        except (TypeError, ValueError):
            pass
        return float(val)

    # --- Quote-level data ---
    company_name = info.get("shortName", symbol)
    current_price = _nz(info.get("currentPrice")) or _nz(info.get("previousClose"), 0)
    market_cap = _nz(info.get("marketCap"), 0)
    shares_outstanding = _nz(info.get("sharesOutstanding"), 1)
    beta = _nz(info.get("beta"), 1.0)
    sector = info.get("sector", "N/A")
    industry = info.get("industry", "N/A")

    # --- Income Statement (try DataFrame first, fall back to info) ---
    try:
        financials = tk.financials
    except Exception:
        financials = pd.DataFrame()

    last_revenue = _safe(financials, "Total Revenue", _nz(info.get("totalRevenue"), 0))
    ebitda = _safe(financials, "EBITDA", _nz(info.get("ebitda"), 0))

    # If revenue is still 0, try income_stmt as alternative
    if last_revenue == 0:
        try:
            inc = tk.income_stmt
            last_revenue = _safe(inc, "Total Revenue", 0)
            if ebitda == 0:
                ebitda = _safe(inc, "EBITDA", 0)
        except Exception:
            pass

    # --- Cash Flow Statement ---
    try:
        cf = tk.cashflow
    except Exception:
        cf = pd.DataFrame()

    operating_cf = _safe(cf, "Operating Cash Flow", _nz(info.get("operatingCashflow"), 0))
    capex = _safe(cf, "Capital Expenditure", 0)
    free_cash_flow = operating_cf + capex  # capex is negative in yfinance
    if free_cash_flow == 0:
        free_cash_flow = _nz(info.get("freeCashflow"), 0)

    # --- Balance Sheet ---
    try:
        bs = tk.balance_sheet
    except Exception:
        bs = pd.DataFrame()

    total_debt = _safe(bs, "Total Debt", _nz(info.get("totalDebt"), 0))
    cash = _safe(bs, "Cash And Cash Equivalents", _nz(info.get("totalCash"), 0))

    net_debt = total_debt - cash

    return {
        "company_name": company_name,
        "current_price": current_price,
        "market_cap": market_cap,
        "shares_outstanding": shares_outstanding,
        "beta": beta,
        "sector": sector,
        "industry": industry,
        "revenue": last_revenue,
        "ebitda": ebitda,
        "operating_cf": operating_cf,
        "capex": capex,
        "free_cash_flow": free_cash_flow,
        "total_debt": total_debt,
        "cash": cash,
        "net_debt": net_debt,
        "revenue_growth": _nz(info.get("revenueGrowth"), 0),
    }


# ============================================================
# MAIN FLOW
# ============================================================
try:
    data = fetch_company_data(ticker_symbol)

    # ----- Convenience (all in $B) -----
    rev_b = data["revenue"] / 1e9
    ebitda_b = data["ebitda"] / 1e9
    opcf_b = data["operating_cf"] / 1e9
    capex_b = data["capex"] / 1e9
    fcf_b = data["free_cash_flow"] / 1e9
    debt_b = data["total_debt"] / 1e9
    cash_b = data["cash"] / 1e9
    net_debt_b = data["net_debt"] / 1e9
    current_price = data["current_price"]
    shares = data["shares_outstanding"]

    # ----- Sidebar: current price + info -----
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**{data['company_name']}** ({ticker_symbol})")
    st.sidebar.metric("Current Price", f"${current_price:,.2f}")
    st.sidebar.caption(f"{data['sector']}  ·  {data['industry']}")

    # ---- Sidebar: Adjustable Assumptions ----
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Key Assumptions")

    # ---- Compute smart defaults from actual data ----
    # FCF Margin: actual FCF / Revenue (clamped to slider range)
    default_fcf_margin = (fcf_b / rev_b * 100) if rev_b > 0 else 20.0
    default_fcf_margin = round(max(5.0, min(50.0, default_fcf_margin)) * 2) / 2  # snap to 0.5 steps

    # Growth rate: use info revenueGrowth if available, else conservative estimate
    info_growth = data.get("revenue_growth")
    if info_growth and info_growth > 0:
        default_growth = round(min(30.0, info_growth * 100) * 2) / 2
    elif rev_b > 0:
        default_growth = 5.0  # conservative fallback
    else:
        default_growth = 10.0

    # WACC: simple CAPM estimate → risk-free(4.5%) + beta × equity premium(5.5%)
    beta_val = data.get("beta", 1.0) or 1.0
    default_wacc = round((4.5 + beta_val * 5.5) * 10) / 10  # snap to 0.1 steps
    default_wacc = max(5.0, min(20.0, default_wacc))

    growth_rate = st.sidebar.slider(
        "Revenue Growth Rate (%)",
        min_value=0.0, max_value=30.0, value=default_growth, step=0.5,
        help="Annualized revenue growth rate applied over the projection period.",
    ) / 100.0

    fcf_margin = st.sidebar.slider(
        "FCF Margin (%)",
        min_value=5.0, max_value=50.0, value=default_fcf_margin, step=0.5,
        help="Free Cash Flow as a percentage of Revenue. Represents profitability after all capital spending.",
    ) / 100.0

    wacc = st.sidebar.slider(
        "WACC — Discount Rate (%)",
        min_value=5.0, max_value=20.0, value=default_wacc, step=0.1,
        help="Weighted Average Cost of Capital — the minimum return investors require. Higher risk → higher WACC → lower valuation.",
    ) / 100.0

    st.sidebar.markdown("---")
    st.sidebar.subheader("📐 Terminal Value")

    tv_method = st.sidebar.radio(
        "Terminal Value Method",
        ["Gordon Growth (Perpetuity)", "Exit Multiple (EV/EBITDA)"],
        help="Choose how to estimate the company's value beyond the projection period.",
    )

    if tv_method == "Gordon Growth (Perpetuity)":
        terminal_growth = st.sidebar.slider(
            "Terminal Growth Rate (%)",
            min_value=1.0, max_value=5.0, value=2.5, step=0.1,
            help="Long-term perpetual growth rate — typically 2-3% to match GDP/inflation.",
        ) / 100.0
        exit_multiple = None
    else:
        exit_multiple = st.sidebar.slider(
            "Exit EV/EBITDA Multiple",
            min_value=5.0, max_value=30.0, value=12.0, step=0.5,
            help="Multiple applied to terminal-year EBITDA to estimate terminal enterprise value.",
        )
        terminal_growth = None

    st.sidebar.markdown("---")
    st.sidebar.subheader("🏦 Equity Bridge")

    net_debt_input = st.sidebar.number_input(
        "Net Debt Override ($B)",
        value=round(net_debt_b, 2),
        help="Total Debt minus Cash. Auto-populated from the balance sheet — override if needed.",
    )

    # ============================================================
    # COMPANY SNAPSHOT — shows retrieved financial data
    # ============================================================
    st.markdown("### 🏢 Company Snapshot — Retrieved Financial Data")
    snap1, snap2, snap3, snap4 = st.columns(4)

    with snap1:
        st.metric("Revenue", f"${rev_b:,.2f}B")
        st.metric("EBITDA", f"${ebitda_b:,.2f}B")
    with snap2:
        st.metric("Operating Cash Flow", f"${opcf_b:,.2f}B")
        st.metric("Free Cash Flow", f"${fcf_b:,.2f}B")
    with snap3:
        st.metric("Total Debt", f"${debt_b:,.2f}B")
        st.metric("Cash & Equivalents", f"${cash_b:,.2f}B")
    with snap4:
        st.metric("Net Debt", f"${net_debt_b:,.2f}B")
        st.metric("Shares Outstanding", f"{shares / 1e9:,.2f}B")

    st.caption("_Data retrieved automatically from Yahoo Finance (income statement, cash flow statement, and balance sheet)._")

    # ============================================================
    # CORE DCF MODEL
    # ============================================================
    years = 5
    future_fcf = []
    pv_fcf = []
    revenues = []
    ebitda_proj = []
    projection_data = []

    for i in range(1, years + 1):
        rev = rev_b * ((1 + growth_rate) ** i)
        fcf = rev * fcf_margin
        ebitda_yr = rev * (ebitda_b / rev_b if rev_b != 0 else 0.15)  # maintain EBITDA margin
        df = (1 + wacc) ** i
        pv = fcf / df

        revenues.append(rev)
        future_fcf.append(fcf)
        ebitda_proj.append(ebitda_yr)
        pv_fcf.append(pv)

        projection_data.append({
            "Year": f"Year {i}",
            "Revenue ($B)": f"{rev:,.2f}",
            "EBITDA ($B)": f"{ebitda_yr:,.2f}",
            "FCF ($B)": f"{fcf:,.2f}",
            "Discount Factor": f"{1/df:.4f}",
            "PV of FCF ($B)": f"{pv:,.2f}",
        })

    # Terminal Value
    if tv_method == "Gordon Growth (Perpetuity)":
        terminal_value = (future_fcf[-1] * (1 + terminal_growth)) / (wacc - terminal_growth)
    else:
        terminal_value = ebitda_proj[-1] * exit_multiple

    pv_terminal = terminal_value / ((1 + wacc) ** years)

    # Valuation waterfall
    sum_pv_fcf = sum(pv_fcf)
    enterprise_value = sum_pv_fcf + pv_terminal
    equity_value = enterprise_value - net_debt_input
    implied_share_price = (equity_value * 1e9) / shares if shares else 0
    upside = (implied_share_price - current_price) / current_price if current_price else 0

    # ============================================================
    # VALUATION RESULTS
    # ============================================================
    st.markdown("---")
    st.markdown("### 🎯 Valuation Results")

    res1, res2, res3, res4 = st.columns(4)
    with res1:
        st.metric("Enterprise Value", f"${enterprise_value:,.2f}B", help="PV(Future Cash Flows) + PV(Terminal Value)")
    with res2:
        st.metric("Equity Value", f"${equity_value:,.2f}B", help="Enterprise Value minus Net Debt")
    with res3:
        st.metric(
            "Implied Share Price",
            f"${implied_share_price:,.2f}",
            f"{upside:+.1%} vs market",
            delta_color="normal",
        )
    with res4:
        st.metric("Current Market Price", f"${current_price:,.2f}")

    # Comparison note (neutral — not a recommendation)
    diff_pct = abs(upside)
    if implied_share_price > current_price:
        st.info(
            f"📊 The DCF model implies a value **{diff_pct:.1%} above** the current market price "
            f"(${implied_share_price:,.2f} vs ${current_price:,.2f}). "
            f"Adjust the assumptions in the sidebar to explore different scenarios."
        )
    elif implied_share_price < current_price:
        st.info(
            f"📊 The DCF model implies a value **{diff_pct:.1%} below** the current market price "
            f"(${implied_share_price:,.2f} vs ${current_price:,.2f}). "
            f"This may reflect that the market prices in intangibles (brand, moat) not captured by a simple DCF. "
            f"Try adjusting growth or WACC to test scenarios."
        )
    else:
        st.info("📊 The implied price closely matches the current market price.")

    # Waterfall breakdown
    wf1, wf2, wf3 = st.columns(3)
    wf1.metric("PV of 5-Year Cash Flows", f"${sum_pv_fcf:,.2f}B")
    wf2.metric("PV of Terminal Value", f"${pv_terminal:,.2f}B")
    tv_pct = (pv_terminal / enterprise_value * 100) if enterprise_value else 0
    wf3.metric("Terminal Value % of EV", f"{tv_pct:.1f}%", help="How much of total value comes from beyond Year 5")

    # ============================================================
    # TABS
    # ============================================================
    tab1, tab2, tab3 = st.tabs(["📊 Projections", "⚡ Sensitivity Analysis", "📚 Learn the Math"])

    # ---------- TAB 1: PROJECTIONS ----------
    with tab1:
        st.markdown("#### Projected Free Cash Flow & Revenue")

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[f"Year {i}" for i in range(1, 6)],
            y=future_fcf,
            name="Projected FCF ($B)",
            marker_color="#4CAF50",
            marker_line_width=0,
        ))
        fig.add_trace(go.Scatter(
            x=[f"Year {i}" for i in range(1, 6)],
            y=revenues,
            name="Revenue ($B)",
            yaxis="y2",
            line=dict(color="#1565C0", width=3),
            mode="lines+markers",
        ))
        fig.update_layout(
            yaxis=dict(title="FCF ($B)"),
            yaxis2=dict(title="Revenue ($B)", overlaying="y", side="right"),
            legend=dict(x=0, y=1.0, bgcolor="rgba(255,255,255,0.8)"),
            height=420,
            margin=dict(l=20, r=20, t=30, b=20),
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

        # Projection data table
        st.markdown("#### Detailed Projections")
        proj_df = pd.DataFrame(projection_data)
        st.dataframe(proj_df, use_container_width=True, hide_index=True)

    # ---------- TAB 2: SENSITIVITY ANALYSIS ----------
    with tab2:
        st.markdown("#### Sensitivity Analysis — Implied Share Price")
        st.write("See how the implied share price changes across different **Growth Rate** and **WACC** assumptions:")

        # 5×5 grid — growth vs. WACC
        growth_steps = [growth_rate + (g - 2) * 0.01 for g in range(5)]
        wacc_steps = [wacc + (w - 2) * 0.01 for w in range(5)]

        # Filter out invalid combinations
        growth_steps = [max(g, 0.0) for g in growth_steps]
        wacc_steps = [max(w, 0.01) for w in wacc_steps]

        sensitivity_matrix = []
        for g in growth_steps:
            row = []
            for w in wacc_steps:
                s_pv = 0
                s_last_fcf = 0
                s_last_ebitda = 0
                for i in range(1, years + 1):
                    r = rev_b * ((1 + g) ** i)
                    f = r * fcf_margin
                    eb = r * (ebitda_b / rev_b if rev_b != 0 else 0.15)
                    d = (1 + w) ** i
                    s_pv += f / d
                    s_last_fcf = f
                    s_last_ebitda = eb

                if tv_method == "Gordon Growth (Perpetuity)":
                    tg = terminal_growth if terminal_growth else 0.025
                    if w <= tg:
                        s_tv = s_last_fcf * 20  # fallback cap
                    else:
                        s_tv = (s_last_fcf * (1 + tg)) / (w - tg)
                else:
                    s_tv = s_last_ebitda * (exit_multiple if exit_multiple else 12)

                s_pv_tv = s_tv / ((1 + w) ** years)
                s_ev = s_pv + s_pv_tv
                s_eq = s_ev - net_debt_input
                s_price = (s_eq * 1e9) / shares if shares else 0
                row.append(round(s_price, 2))
            sensitivity_matrix.append(row)

        sens_df = pd.DataFrame(
            sensitivity_matrix,
            index=[f"Growth: {g:.1%}" for g in growth_steps],
            columns=[f"WACC: {w:.1%}" for w in wacc_steps],
        )

        # Color-coded dataframe
        def color_cell(val):
            if val > current_price * 1.1:
                return "background-color: #c8e6c9; color: #1b5e20; font-weight: 600"
            elif val < current_price * 0.9:
                return "background-color: #ffcdd2; color: #b71c1c; font-weight: 600"
            else:
                return "background-color: #fff9c4; color: #f57f17; font-weight: 600"

        styled = sens_df.style.format("${:,.2f}").applymap(color_cell)
        st.dataframe(styled, use_container_width=True)

        st.caption(
            f"🟢 Green = >10% above current price (${current_price:,.2f})  ·  "
            f"🔴 Red = >10% below  ·  🟡 Yellow = within 10%"
        )

        # Heatmap chart
        st.markdown("#### Heatmap View")
        fig_heat = go.Figure(data=go.Heatmap(
            z=sensitivity_matrix,
            x=[f"WACC: {w:.1%}" for w in wacc_steps],
            y=[f"Growth: {g:.1%}" for g in growth_steps],
            colorscale="RdYlGn",
            text=[[f"${v:,.0f}" for v in row] for row in sensitivity_matrix],
            texttemplate="%{text}",
            textfont={"size": 12},
            colorbar=dict(title="Share Price ($)"),
        ))
        fig_heat.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis_title="WACC",
            yaxis_title="Growth Rate",
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    # ---------- TAB 3: LEARN THE MATH ----------
    with tab3:
        st.markdown("### 🎓 The DCF Formula — Step by Step")

        with st.expander("1. Free Cash Flow (FCF)", expanded=True):
            st.markdown("""
            **Cash is King.** We model the actual cash the business generates — not accounting profit.

            $$FCF = Revenue \\times \\text{FCF Margin}$$

            The FCF Margin captures: operating profits minus taxes minus capital expenditures.
            """)

        with st.expander("2. WACC (Discount Rate)"):
            st.markdown("""
            **Time Value of Money.** A dollar today is worth more than a dollar tomorrow.

            We *discount* future cash flows by the **Weighted Average Cost of Capital** (WACC)
            to find what they're worth *today*.

            $$PV = \\frac{FCF_t}{(1 + WACC)^t}$$

            Higher risk companies → higher WACC → lower present value.
            """)

        with st.expander("3. Terminal Value"):
            st.markdown("""
            **The "Forever" Value.** We can't forecast year-by-year indefinitely.
            After the projection period (5 years), we estimate a terminal value:

            - **Gordon Growth Model**: $TV = \\frac{FCF_5 \\times (1 + g)}{WACC - g}$
            - **Exit Multiple**: $TV = EBITDA_5 \\times \\text{Multiple}$
            """)

        with st.expander("4. Putting It All Together"):
            st.code("""
    Enterprise Value = Σ PV(FCF₁…FCF₅) + PV(Terminal Value)
    Equity Value     = Enterprise Value − Net Debt
    Share Price      = Equity Value ÷ Shares Outstanding
            """, language="text")

        st.info("💡 **Tip:** Go back to the sidebar and change an assumption — watch how the valuation moves in real time!")

except Exception as e:
    st.error(f"⚠️ Could not retrieve data for **{ticker_symbol}**.")
    st.write(f"Error details: `{e}`")
    st.write("Please try a valid ticker like **AAPL**, **MSFT**, **GOOG**, or **JNJ**.")
