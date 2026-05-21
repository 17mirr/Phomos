import yfinance as yf
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
from concurrent.futures import ThreadPoolExecutor
import os

app = FastAPI(title="PRIMESCREEN API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- UNIVERSE ----------
# US tickers + GPW tickers (GPW uses .WA suffix)
UNIVERSE = [
    # US
    {"ticker": "RXST",  "name": "RxSight",         "market": "US", "sector": "Healthcare"},
    {"ticker": "TMDX",  "name": "TransMedics",      "market": "US", "sector": "Healthcare"},
    {"ticker": "HIMS",  "name": "Hims & Hers",      "market": "US", "sector": "Healthcare"},
    {"ticker": "DUOL",  "name": "Duolingo",          "market": "US", "sector": "Technology"},
    {"ticker": "SOUN",  "name": "SoundHound AI",     "market": "US", "sector": "Technology"},
    {"ticker": "GCT",   "name": "GigaCloud Tech",    "market": "US", "sector": "Technology"},
    {"ticker": "IOT",   "name": "Samsara",           "market": "US", "sector": "Technology"},
    {"ticker": "AXON",  "name": "Axon Enterprise",   "market": "US", "sector": "Technology"},
    {"ticker": "CELH",  "name": "Celsius Holdings",  "market": "US", "sector": "Consumer"},
    {"ticker": "CAVA",  "name": "CAVA Group",        "market": "US", "sector": "Consumer"},
    {"ticker": "FTAI",  "name": "FTAI Aviation",     "market": "US", "sector": "Industrials"},
    {"ticker": "NOVA",  "name": "Sunnova Energy",    "market": "US", "sector": "Energy"},
    {"ticker": "ASTS",  "name": "AST SpaceMobile",   "market": "US", "sector": "Technology"},
    {"ticker": "RKLB",  "name": "Rocket Lab",        "market": "US", "sector": "Industrials"},
    {"ticker": "ACHR",  "name": "Archer Aviation",   "market": "US", "sector": "Industrials"},
    # GPW Poland (.WA)
    {"ticker": "CDR.WA",  "name": "CD Projekt",       "market": "PL", "sector": "Technology"},
    {"ticker": "ALE.WA",  "name": "Allegro.eu",       "market": "PL", "sector": "Technology"},
    {"ticker": "11B.WA",  "name": "11 bit studios",   "market": "PL", "sector": "Technology"},
    {"ticker": "LVC.WA",  "name": "LiveChat Software","market": "PL", "sector": "Technology"},
    {"ticker": "INP.WA",  "name": "InPost SA",        "market": "PL", "sector": "Industrials"},
    {"ticker": "KRU.WA",  "name": "Kruk SA",          "market": "PL", "sector": "Financials"},
    {"ticker": "PCO.WA",  "name": "Pepco Group",      "market": "PL", "sector": "Retail"},
    {"ticker": "PKN.WA",  "name": "PKN Orlen",        "market": "PL", "sector": "Energy"},
    {"ticker": "MBR.WA",  "name": "Mabion SA",        "market": "PL", "sector": "Healthcare"},
    {"ticker": "CMR.WA",  "name": "Comarch SA",       "market": "PL", "sector": "Technology"},
]

executor = ThreadPoolExecutor(max_workers=8)

def fetch_ticker(item: dict) -> dict:
    try:
        tk = yf.Ticker(item["ticker"])
        info = tk.info

        # Market cap in billions
        raw_cap = info.get("marketCap") or 0
        cap_b = round(raw_cap / 1e9, 2)

        # Revenue growth YoY (quarterly)
        rev_growth = info.get("revenueGrowth")
        rev_growth_pct = round(rev_growth * 100, 1) if rev_growth is not None else None

        # Valuation
        pe = info.get("trailingPE")
        pb = info.get("priceToBook")
        pe = round(pe, 1) if pe and pe > 0 else None
        pb = round(pb, 1) if pb and pb > 0 else None

        # Currency
        currency = info.get("currency", "USD")

        return {
            **item,
            "cap": cap_b,
            "rev": rev_growth_pct,
            "pe": pe,
            "pb": pb,
            "currency": currency,
            "error": None,
        }
    except Exception as e:
        return {**item, "cap": None, "rev": None, "pe": None, "pb": None, "currency": None, "error": str(e)}


def compute_sector_medians(stocks: list) -> dict:
    df = pd.DataFrame(stocks)
    df = df[df["rev"].notna()]
    return df.groupby("sector")["rev"].median().round(1).to_dict()


def compute_share_gain(stocks: list, medians: dict) -> list:
    result = []
    for s in stocks:
        med = medians.get(s["sector"])
        if s["rev"] is not None and med is not None:
            gain = round(s["rev"] - med, 1)
        else:
            gain = None

        # Signal logic
        if s["rev"] is not None and gain is not None:
            if s["rev"] >= 30 and gain >= 15:
                signal = "strong"
            elif s["rev"] >= 12 and gain >= 4:
                signal = "watch"
            else:
                signal = "pass"
        else:
            signal = "pass"

        result.append({**s, "sector_median": med, "gain": gain, "signal": signal})

    result.sort(key=lambda x: (x["gain"] or -999), reverse=True)
    return result


@app.get("/api/screen")
async def screen():
    loop = asyncio.get_event_loop()
    tasks = [loop.run_in_executor(executor, fetch_ticker, item) for item in UNIVERSE]
    raw = await asyncio.gather(*tasks)
    stocks = list(raw)

    medians = compute_sector_medians(stocks)
    stocks = compute_share_gain(stocks, medians)

    # Summary stats
    valid = [s for s in stocks if s["rev"] is not None]
    summary = {
        "total": len(stocks),
        "with_data": len(valid),
        "avg_rev_growth": round(sum(s["rev"] for s in valid) / len(valid), 1) if valid else None,
        "avg_share_gain": round(sum(s["gain"] for s in valid if s["gain"] is not None) / len(valid), 1) if valid else None,
        "strong_count": len([s for s in stocks if s["signal"] == "strong"]),
        "watch_count": len([s for s in stocks if s["signal"] == "watch"]),
        "pass_count": len([s for s in stocks if s["signal"] == "pass"]),
        "sector_medians": medians,
    }

    return {"stocks": stocks, "summary": summary}


@app.get("/api/health")
async def health():
    return {"status": "ok", "universe": len(UNIVERSE)}


# Serve frontend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
