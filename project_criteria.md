# Detailed Project Requirements and Rubrics

## Project 1: Corporate Valuation Application (200 points)

**What You Build:** A DCF-based valuation tool that accepts any stock ticker, allows adjustment of key assumptions, and includes sensitivity analysis.

## Required App Functionality

Your application must:
1. Accept a stock ticker as input (e.g., AAPL, MSFT, JNJ)
2. Retrieve financial data automatically (revenue, EBITDA, cash flows, etc.)
3. Calculate a DCF-based intrinsic value
4. Display key valuation outputs: Enterprise Value, Equity Value, Per-Share Value
5. Allow user to adjust key assumptions (WACC, growth rate, terminal growth/multiple, etc.)
6. Produce sensitivity analysis showing how valuation changes across assumption ranges

**Why Adjustable Inputs Matter:** A valuation tool that only runs once with fixed assumptions is not useful. Real analysts need to test scenarios: "What if growth is 3% instead of 5%?" "What if WACC is 12% instead of 10%?" Your tool must support this.

## AI-Graded Checklist (60% = 120 points)

### Working Application (40% = 80 points):

- [ ] App runs without crashing
- [ ] Accepts ticker input
- [ ] Retrieves financial data for the ticker
- [ ] Outputs Enterprise Value, Equity Value, or Per-Share Value
- [ ] User can adjust WACC assumption
- [ ] User can adjust growth rate assumption
- [ ] Displays sensitivity table or chart (valuation across range of assumptions)
