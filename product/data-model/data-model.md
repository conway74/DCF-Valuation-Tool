# Data Model

## Entities

### Ticker
Represents the public company being analyzed (e.g., AAPL). Contains metadata like symbol, company name, sector, and currency.

### Financials
The raw historical financial data required for the model. Includes Revenue, EBITDA, Free Cash Flow (FCF), Net Debt, and Shares Outstanding. Sourced from yfinance.

### Assumptions
The user-defined inputs that drive the projection. Includes:
- Revenue Growth Rate
- Target Operating Margin
- Tax Rate
- WACC (Discount Rate)
- Terminal Growth Rate / Exit Multiple

### Valuation
The result of the DCF calculation. Contains:
- Enterprise Value
- Equity Value
- Implied Share Price
- Upside/Downside % vs Current Price

## Relationships

- A **Ticker** has one set of **Financials** (1:1).
- A **Valuation** is derived from ONE **Ticker**, ONE set of **Financials**, and ONE set of **Assumptions**.
