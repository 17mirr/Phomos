# PHOMOS — PE Growth Engine v4.4

> **Portfolio Hedge & Optimized Momentum Oscillation Screener**  
> Multi-market stock screener built with Python, FastAPI, and vanilla JS.

---

## What It Does

PHOMOS screens stocks across 5 markets (US, UK, Germany, France, Poland) using a private equity-style methodology: identifying companies capturing market share from sector rivals through superior revenue growth. The screener computes a **Share Gain score** — the difference between a company's revenue growth and its sector median — and ranks stocks accordingly.

### Core Signal Logic

```
Share Gain = Company Revenue Growth − Sector Median Revenue Growth

Strong Buy  → Rev Growth ≥ 30% AND Share Gain ≥ 15pp
Watch       → Rev Growth ≥ 12% AND Share Gain ≥ 4pp
Pass        → Everything else
```

---

## Features

### Screener
- **83 stocks** across US (NYSE/NASDAQ), UK (LSE), Germany (XETRA), France (Euronext), Poland (GPW)
- Live price data with intraday % change
- Sector share gain ranking vs. sector median
- Signal distribution chart (Strong Buy / Watch / Pass)
- Sortable table with P/E, P/B, market cap, buzz score
- Filters: market, signal, sector, min revenue growth, min share gain

![PHOMOS Screener](screenshots/Screenshot%20phomos%20screener.png)

---

### Stock Detail Modal
- Full valuation metrics (P/E trailing & forward, P/B, P/S, Beta, 52W high/low)
- Growth & profitability (revenue growth, earnings growth, gross/net/operating margin, ROE, ROA)
- Balance sheet: net cash position, total debt, free cash flow
- Quarterly earnings history chart (last 6 quarters, revenue + net income)
- Company description

![Stock Detail](screenshots/Screenshot%20company.png)

---

### AI Analysis ⚡
- Claude-powered analysis for **Strong Buy** stocks only
- Explains why the stock qualifies: revenue growth drivers, key risks, valuation
- Server-side cache (1 hour) to minimize API costs
- Triggered on demand — one click per stock

![AI Analysis](screenshots/Screenshot%20ai%20analysis.png)

---

### Watchlist
- Save any stock to a persistent watchlist (localStorage)
- Card view with key metrics per position

![Watchlist](screenshots/Screenshot%20watchlist.png)

---

### Portfolio Sync (Trading212)
- Connects to Trading212 live account via API
- Displays portfolio as an interactive **donut chart**
- Shows total value, P&L, return %, position weights
- Highlights portfolio holdings in the screener with ★
- Credentials stored in `.env`, never exposed

![Portfolio](screenshots/Screenshot%20portfolio.png)

---

### News Tab 📰
- Market news powered by **Alpha Vantage**
- Ticker-specific news — click any stock from your watchlist or portfolio
- Sentiment indicator per article
- Auto-populates ticker buttons from your watchlist and portfolio

![News](screenshots/Screenshot%20news.png)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, yfinance, pandas |
| Frontend | Vanilla JS, Chart.js, CSS custom properties |
| Data | Yahoo Finance (fundamentals + live prices) |
| News | Alpha Vantage News Sentiment API |
| AI | Anthropic Claude API (claude-sonnet-4) |
| Portfolio | Trading212 Public API v0 |
| Config | python-dotenv |

---

## Setup

```bash
# 1. Clone
git clone https://github.com/17mirr/Phomos
cd Phomos/backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
# T212_KEY=your_trading212_api_key
# T212_SECRET=your_trading212_api_secret
# ANTHROPIC_KEY=your_anthropic_api_key
# NEWS_KEY=your_alphavantage_api_key

# 4. Run
python -m uvicorn main:app --reload

# 5. Open
# http://localhost:8000
```

---

## Markets Covered

| Market | Exchange | Coverage |
|--------|----------|----------|
| 🇺🇸 US | NYSE / NASDAQ | Large cap + high-growth small/mid cap |
| 🇬🇧 UK | London Stock Exchange | FTSE large cap |
| 🇩🇪 Germany | XETRA | DAX constituents |
| 🇫🇷 France | Euronext Paris | CAC 40 constituents |
| 🇵🇱 Poland | GPW Warsaw | WIG20 + growth stocks |

---

## Methodology

The Share Gain metric is inspired by private equity market share capture analysis. Rather than comparing absolute revenue growth figures, PHOMOS normalizes growth against the sector median — isolating companies that are genuinely outperforming peers, not just riding sector tailwinds.

---

## Related Research

This project accompanies original macro research on the **Liquidity Absorption Ratio (LAR)** — a novel market valuation indicator measuring the proportion of global M2 money supply absorbed by US equity market capitalisation, with historical convergence observed at five major crisis inflection points (1929, 1932, 2000, 2008, 2019).

---

*Built by Emir — Warsaw, 2026*
