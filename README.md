# PRIMESCREEN — PE Growth Engine

Private equity style stock screener. Finds small/mid cap companies taking market share from sector rivals across **US (NYSE/NASDAQ)** and **GPW Poland**.

## How it works
- Pulls **live data** from Yahoo Finance (free, no API key needed)
- Calculates **share gain** = company revenue growth YoY − sector median growth
- Signals: **STRONG BUY** (rev ≥30%, gain ≥15pp) · **WATCH** · **PASS**
- Filters: market, sector, min growth, min share gain, max market cap

## Run locally

```bash
bash start.sh
```

Then open → **http://localhost:8000**

## Manual setup (if needed)

```bash
cd backend
pip install -r requirements.txt
python main.py
```

## Stack
- **Backend**: Python · FastAPI · yfinance · pandas
- **Frontend**: Vanilla JS · Chart.js · Terminal dark UI

## Add more tickers
Edit the `UNIVERSE` list in `backend/main.py`. GPW tickers use `.WA` suffix (e.g. `CDR.WA`).

---
Built by Emir · PRIMESCREEN v1.0
