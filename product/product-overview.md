# DCF Academy (Interactive Valuation Teacher)

## The Problem
Students and beginners find DCF valuation abstract. Spreadsheets are static and don't intuitively show how sensitive valuation is to small changes in assumptions (like WACC or Growth Rate).

## Success Looks Like
An interactive Streamlit app where a user can:
1. Search for a ticker (e.g., AAPL).
2. See the DCF model built **step-by-step** (Revenue -> FCF -> WACC -> Terminal Value).
3. Use **sliders** to adjust assumptions and see the "Fair Value" change instantly.
4. Read "Educational Tooltips" explaining each step.

## Building On (Existing Foundations)
- **yfinance** — For free, live market data and financial statements.
- **numpy-financial** — For core time-value-of-money calculations (NPV, etc).
- **Streamlit** — For the interactive "show don't tell" UI.

## The Unique Part
Focused on **teaching** the mechanics via interactivity. Unlike standard valuation tools, we prioritize exposing the *sensitivity* of the model to inputs, turning the valuation into a learning sandbox.

## Tech Stack
- **UI:** Streamlit
- **Backend:** Python (local calculation)
- **Key Libraries:** `yfinance`, `pandas`, `numpy-financial`, `plotly` (for sensitivity charts)

## Open Questions
- How deep to go on WACC calculation? (Start with simple CAPM or allow manual override? -> decision: Default to auto-calc but allow override).
