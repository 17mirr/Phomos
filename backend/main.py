import yfinance as yf
import json
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
import time
import httpx
import base64
from dotenv import load_dotenv

load_dotenv()

# ---------- CONFIG ----------
T212_KEY      = os.getenv("T212_KEY", "")
T212_SECRET   = os.getenv("T212_SECRET", "")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY", "")
NEWS_KEY      = os.getenv("NEWS_KEY", "")

app = FastAPI(title="PHOMOS API v4.4")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ---------- UNIVERSE ----------
UNIVERSE = [
    {"ticker": "AAPL",  "name": "Apple",            "market": "US", "sector": "Technology"},
    {"ticker": "MSFT",  "name": "Microsoft",         "market": "US", "sector": "Technology"},
    {"ticker": "NVDA",  "name": "Nvidia",            "market": "US", "sector": "Technology"},
    {"ticker": "GOOGL", "name": "Alphabet",          "market": "US", "sector": "Technology"},
    {"ticker": "META",  "name": "Meta",              "market": "US", "sector": "Technology"},
    {"ticker": "AMZN",  "name": "Amazon",            "market": "US", "sector": "Consumer"},
    {"ticker": "TSLA",  "name": "Tesla",             "market": "US", "sector": "Consumer"},
    {"ticker": "JPM",   "name": "JPMorgan Chase",    "market": "US", "sector": "Financials"},
    {"ticker": "V",     "name": "Visa",              "market": "US", "sector": "Financials"},
    {"ticker": "JNJ",   "name": "Johnson & Johnson", "market": "US", "sector": "Healthcare"},
    {"ticker": "WMT",   "name": "Walmart",           "market": "US", "sector": "Retail"},
    {"ticker": "XOM",   "name": "ExxonMobil",        "market": "US", "sector": "Energy"},
    {"ticker": "UNH",   "name": "UnitedHealth",      "market": "US", "sector": "Healthcare"},
    {"ticker": "MA",    "name": "Mastercard",        "market": "US", "sector": "Financials"},
    {"ticker": "HD",    "name": "Home Depot",        "market": "US", "sector": "Retail"},
    {"ticker": "RXST",  "name": "RxSight",           "market": "US", "sector": "Healthcare"},
    {"ticker": "TMDX",  "name": "TransMedics",       "market": "US", "sector": "Healthcare"},
    {"ticker": "HIMS",  "name": "Hims & Hers",       "market": "US", "sector": "Healthcare"},
    {"ticker": "DUOL",  "name": "Duolingo",          "market": "US", "sector": "Technology"},
    {"ticker": "SOUN",  "name": "SoundHound AI",     "market": "US", "sector": "Technology"},
    {"ticker": "GCT",   "name": "GigaCloud Tech",    "market": "US", "sector": "Technology"},
    {"ticker": "IOT",   "name": "Samsara",           "market": "US", "sector": "Technology"},
    {"ticker": "AXON",  "name": "Axon Enterprise",   "market": "US", "sector": "Technology"},
    {"ticker": "CELH",  "name": "Celsius Holdings",  "market": "US", "sector": "Consumer"},
    {"ticker": "CAVA",  "name": "CAVA Group",        "market": "US", "sector": "Consumer"},
    {"ticker": "FTAI",  "name": "FTAI Aviation",     "market": "US", "sector": "Industrials"},
    {"ticker": "ASTS",  "name": "AST SpaceMobile",   "market": "US", "sector": "Technology"},
    {"ticker": "RKLB",  "name": "Rocket Lab",        "market": "US", "sector": "Industrials"},
    {"ticker": "IONQ",  "name": "IonQ",              "market": "US", "sector": "Technology"},
    {"ticker": "ACHR",  "name": "Archer Aviation",   "market": "US", "sector": "Industrials"},
    {"ticker": "OKLO",  "name": "Oklo",              "market": "US", "sector": "Energy"},
    {"ticker": "BFLY",  "name": "Butterfly Network", "market": "US", "sector": "Healthcare"},
    {"ticker": "MYO",   "name": "Myomo",             "market": "US", "sector": "Healthcare"},
    {"ticker": "CRWV",  "name": "CoreWeave",         "market": "US", "sector": "Technology"},
    {"ticker": "APO",   "name": "Apollo Global",     "market": "US", "sector": "Financials"},
    {"ticker": "AMD",   "name": "AMD",               "market": "US", "sector": "Technology"},
    {"ticker": "S",     "name": "SentinelOne",       "market": "US", "sector": "Technology"},
    {"ticker": "SHEL.L",  "name": "Shell",           "market": "UK", "sector": "Energy"},
    {"ticker": "AZN.L",   "name": "AstraZeneca",     "market": "UK", "sector": "Healthcare"},
    {"ticker": "HSBA.L",  "name": "HSBC",            "market": "UK", "sector": "Financials"},
    {"ticker": "ULVR.L",  "name": "Unilever",        "market": "UK", "sector": "Consumer"},
    {"ticker": "BP.L",    "name": "BP",              "market": "UK", "sector": "Energy"},
    {"ticker": "GSK.L",   "name": "GSK",             "market": "UK", "sector": "Healthcare"},
    {"ticker": "RIO.L",   "name": "Rio Tinto",       "market": "UK", "sector": "Materials"},
    {"ticker": "VOD.L",   "name": "Vodafone",        "market": "UK", "sector": "Technology"},
    {"ticker": "LLOY.L",  "name": "Lloyds Banking",  "market": "UK", "sector": "Financials"},
    {"ticker": "BATS.L",  "name": "BAT",             "market": "UK", "sector": "Consumer"},
    {"ticker": "SAP.DE",  "name": "SAP",             "market": "DE", "sector": "Technology"},
    {"ticker": "SIE.DE",  "name": "Siemens",         "market": "DE", "sector": "Industrials"},
    {"ticker": "ALV.DE",  "name": "Allianz",         "market": "DE", "sector": "Financials"},
    {"ticker": "BAYN.DE", "name": "Bayer",           "market": "DE", "sector": "Healthcare"},
    {"ticker": "VOW3.DE", "name": "Volkswagen",      "market": "DE", "sector": "Consumer"},
    {"ticker": "BMW.DE",  "name": "BMW",             "market": "DE", "sector": "Consumer"},
    {"ticker": "DTE.DE",  "name": "Deutsche Telekom","market": "DE", "sector": "Technology"},
    {"ticker": "MRK.DE",  "name": "Merck KGaA",     "market": "DE", "sector": "Healthcare"},
    {"ticker": "ADS.DE",  "name": "Adidas",          "market": "DE", "sector": "Consumer"},
    {"ticker": "DBK.DE",  "name": "Deutsche Bank",   "market": "DE", "sector": "Financials"},
    {"ticker": "MC.PA",   "name": "LVMH",            "market": "FR", "sector": "Consumer"},
    {"ticker": "TTE.PA",  "name": "TotalEnergies",   "market": "FR", "sector": "Energy"},
    {"ticker": "AIR.PA",  "name": "Airbus",          "market": "FR", "sector": "Industrials"},
    {"ticker": "BNP.PA",  "name": "BNP Paribas",    "market": "FR", "sector": "Financials"},
    {"ticker": "SAN.PA",  "name": "Sanofi",          "market": "FR", "sector": "Healthcare"},
    {"ticker": "OR.PA",   "name": "L'Oreal",         "market": "FR", "sector": "Consumer"},
    {"ticker": "RI.PA",   "name": "Pernod Ricard",   "market": "FR", "sector": "Consumer"},
    {"ticker": "KER.PA",  "name": "Kering",          "market": "FR", "sector": "Consumer"},
    {"ticker": "CAP.PA",  "name": "Capgemini",       "market": "FR", "sector": "Technology"},
    {"ticker": "DG.PA",   "name": "Vinci",           "market": "FR", "sector": "Industrials"},
    {"ticker": "PKO.WA",  "name": "PKO Bank Polski", "market": "PL", "sector": "Financials"},
    {"ticker": "PKN.WA",  "name": "PKN Orlen",       "market": "PL", "sector": "Energy"},
    {"ticker": "PZU.WA",  "name": "PZU",             "market": "PL", "sector": "Financials"},
    {"ticker": "KGH.WA",  "name": "KGHM",            "market": "PL", "sector": "Materials"},
    {"ticker": "LPP.WA",  "name": "LPP",             "market": "PL", "sector": "Retail"},
    {"ticker": "DNP.WA",  "name": "Dino Polska",     "market": "PL", "sector": "Retail"},
    {"ticker": "ALE.WA",  "name": "Allegro.eu",      "market": "PL", "sector": "Technology"},
    {"ticker": "CDR.WA",  "name": "CD Projekt",      "market": "PL", "sector": "Technology"},
    {"ticker": "INP.WA",  "name": "InPost SA",       "market": "PL", "sector": "Industrials"},
    {"ticker": "PEO.WA",  "name": "Bank Pekao",      "market": "PL", "sector": "Financials"},
    {"ticker": "MBK.WA",  "name": "mBank",           "market": "PL", "sector": "Financials"},
    {"ticker": "OPL.WA",  "name": "Orange Polska",   "market": "PL", "sector": "Technology"},
    {"ticker": "JSW.WA",  "name": "JSW",             "market": "PL", "sector": "Energy"},
    {"ticker": "BDX.WA",  "name": "Budimex",         "market": "PL", "sector": "Industrials"},
    {"ticker": "CCC.WA",  "name": "CCC Group",       "market": "PL", "sector": "Retail"},
    {"ticker": "ACP.WA",  "name": "Asseco Poland",   "market": "PL", "sector": "Technology"},
]

executor = ThreadPoolExecutor(max_workers=20)
_cache = {"data": None, "ts": 0}
CACHE_TTL = 55

from services.live_price import fetch_live_price
from engine.rolling_valuation import calculate_live_multiples

def fetch_fundamentals(item):
    try:
        tk = yf.Ticker(item["ticker"])
        info = tk.info
        cap_b = round((info.get("marketCap") or 0) / 1e9, 2)
        rev = info.get("revenueGrowth")
        rev_pct = round(rev * 100, 1) if rev is not None else None
        pe = info.get("trailingPE")
        pb = info.get("priceToBook")
        pe = round(pe, 1) if pe and pe > 0 else None
        pb = round(pb, 1) if pb and pb > 0 else None
        return {**item, "cap": cap_b, "rev": rev_pct, "pe": pe, "pb": pb, "currency": info.get("currency","USD"), "error": None}
    except Exception as e:
        return {**item, "cap": None, "rev": None, "pe": None, "pb": None, "currency": None, "error": str(e)}

def compute_sector_medians(stocks):
    df = pd.DataFrame(stocks)
    df = df[df["rev"].notna()]
    return df.groupby("sector")["rev"].median().round(1).to_dict()

def compute_share_gain(stocks, medians):
    result = []
    for s in stocks:
        med = medians.get(s["sector"])
        gain = round(s["rev"] - med, 1) if s["rev"] is not None and med is not None else None
        if s["rev"] is not None and gain is not None:
            signal = "strong" if s["rev"] >= 30 and gain >= 15 else "watch" if s["rev"] >= 12 and gain >= 4 else "pass"
        else:
            signal = "pass"
        result.append({**s, "sector_median": med, "gain": gain, "signal": signal})
    result.sort(key=lambda x: (x["gain"] or -999), reverse=True)
    return result

async def fetch_all():
    now = time.time()
    if _cache["data"] and (now - _cache["ts"]) < CACHE_TTL:
        return _cache["data"]
    loop = asyncio.get_running_loop()
    fund_raw, live_raw = await asyncio.gather(
        asyncio.gather(*[loop.run_in_executor(executor, fetch_fundamentals, i) for i in UNIVERSE]),
        asyncio.gather(*[loop.run_in_executor(executor, fetch_live_price, i["ticker"]) for i in UNIVERSE])
    )
    stocks = calculate_live_multiples(list(fund_raw), {d["ticker"]: d for d in live_raw})
    medians = compute_sector_medians(stocks)
    stocks = compute_share_gain(stocks, medians)
    valid = [s for s in stocks if s["rev"] is not None]
    summary = {
        "total": len(stocks), "with_data": len(valid),
        "avg_rev_growth": round(sum(s["rev"] for s in valid) / len(valid), 1) if valid else None,
        "avg_share_gain": round(sum(s["gain"] for s in valid if s["gain"] is not None) / len(valid), 1) if valid else None,
        "strong_count": len([s for s in stocks if s["signal"] == "strong"]),
        "watch_count": len([s for s in stocks if s["signal"] == "watch"]),
        "pass_count": len([s for s in stocks if s["signal"] == "pass"]),
        "movers_up": len([s for s in stocks if s.get("price_change_pct") and s["price_change_pct"] > 2]),
        "movers_dn": len([s for s in stocks if s.get("price_change_pct") and s["price_change_pct"] < -2]),
        "sector_medians": medians, "fetched_at": int(now),
    }
    result = {"stocks": stocks, "summary": summary, "version": "4.4"}
    _cache["data"] = result
    _cache["ts"] = now
    return result

# ---------- ENDPOINTS ----------
@app.get("/api/v2/live-metrics")
async def live_metrics():
    return await fetch_all()

@app.get("/api/screen")
async def screen():
    return await fetch_all()

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "4.4", "universe": len(UNIVERSE)}

@app.get("/api/v2/stock/{ticker}")
async def stock_detail(ticker: str):
    def _fetch():
        try:
            tk = yf.Ticker(ticker)
            info = tk.info
            total_cash = info.get("totalCash") or 0
            total_debt = info.get("totalDebt") or 0
            quarterly_earnings = []
            try:
                qf = tk.quarterly_financials
                qi = tk.quarterly_income_stmt
                if qf is not None and not qf.empty:
                    for col in list(qf.columns)[:8]:
                        q_rev = q_net = None
                        try: q_rev = qf.loc["Total Revenue", col] if "Total Revenue" in qf.index else qi.loc["Total Revenue", col]
                        except: pass
                        try: q_net = qf.loc["Net Income", col] if "Net Income" in qf.index else qi.loc["Net Income", col]
                        except: pass
                        quarterly_earnings.append({
                            "period": str(col)[:10],
                            "revenue": round(float(q_rev)/1e6,1) if q_rev is not None and q_rev==q_rev else None,
                            "net_income": round(float(q_net)/1e6,1) if q_net is not None and q_net==q_net else None,
                        })
            except: pass
            return {
                "ticker": ticker,
                "name": info.get("longName") or info.get("shortName"),
                "description": info.get("longBusinessSummary","")[:400],
                "sector": info.get("sector"), "industry": info.get("industry"),
                "country": info.get("country"), "employees": info.get("fullTimeEmployees"),
                "market_cap": round(info.get("marketCap",0)/1e9,2),
                "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "52w_high": info.get("fiftyTwoWeekHigh"), "52w_low": info.get("fiftyTwoWeekLow"),
                "pe_trailing": round(info.get("trailingPE"),1) if info.get("trailingPE") else None,
                "pe_forward": round(info.get("forwardPE"),1) if info.get("forwardPE") else None,
                "pb": round(info.get("priceToBook"),2) if info.get("priceToBook") else None,
                "ps": round(info.get("priceToSalesTrailing12Months"),2) if info.get("priceToSalesTrailing12Months") else None,
                "roe": round(info.get("returnOnEquity",0)*100,1) if info.get("returnOnEquity") else None,
                "roa": round(info.get("returnOnAssets",0)*100,1) if info.get("returnOnAssets") else None,
                "gross_margin": round(info.get("grossMargins",0)*100,1) if info.get("grossMargins") else None,
                "operating_margin": round(info.get("operatingMargins",0)*100,1) if info.get("operatingMargins") else None,
                "net_margin": round(info.get("profitMargins",0)*100,1) if info.get("profitMargins") else None,
                "revenue_growth": round(info.get("revenueGrowth",0)*100,1) if info.get("revenueGrowth") else None,
                "earnings_growth": round(info.get("earningsGrowth",0)*100,1) if info.get("earningsGrowth") else None,
                "total_cash": round(total_cash/1e9,2), "total_debt": round(total_debt/1e9,2),
                "net_cash": round((total_cash-total_debt)/1e9,2),
                "free_cashflow": round(info.get("freeCashflow",0)/1e9,2) if info.get("freeCashflow") else None,
                "dividend_yield": round(info.get("dividendYield",0)*100,2) if info.get("dividendYield") else None,
                "beta": round(info.get("beta"),2) if info.get("beta") else None,
                "quarterly_earnings": quarterly_earnings,
                "currency": info.get("currency","USD"),
            }
        except Exception as e:
            return {"ticker": ticker, "error": str(e)}
    return await asyncio.get_running_loop().run_in_executor(executor, _fetch)

# ---------- TRADING212 PORTFOLIO ----------
T212_MAP = {
    "MA_US_EQ": "MA", "ATOM_US_EQ": "ATOM", "CRWV_US_EQ": "CRWV",
    "APO_US_EQ": "APO", "AMD_US_EQ": "AMD", "DMYI_US_EQ": "IONQ",
    "S_US_EQ": "S", "ALCC1_US_EQ": "OKLO", "NPA_US_EQ": "ASTS",
    "MYO_US_EQ": "MYO", "GOOGL_US_EQ": "GOOGL", "LGVW_US_EQ": "BFLY",
}

@app.get("/api/portfolio")
async def get_portfolio():
    try:
        cred = base64.b64encode(f"{T212_KEY}:{T212_SECRET}".encode()).decode()
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                "https://live.trading212.com/api/v0/equity/positions",
                headers={"Authorization": f"Basic {cred}"}
            )
        if r.status_code == 401:
            return {"error": "Invalid T212 credentials", "tickers": []}
        positions = r.json()
        tickers = []
        for pos in positions:
            t212_ticker = pos["instrument"]["ticker"]
            phomos = T212_MAP.get(t212_ticker, t212_ticker.replace("_US_EQ","").replace("_EQ",""))
            tickers.append({
                "t212": t212_ticker, "phomos": phomos,
                "name": pos["instrument"]["name"],
                "currentPrice": pos["currentPrice"],
                "unrealizedPnL": pos["walletImpact"]["unrealizedProfitLoss"],
                "currentValue": pos["walletImpact"]["currentValue"],
                "currency": pos["walletImpact"]["currency"],
            })
        return {"tickers": tickers, "count": len(tickers)}
    except Exception as e:
        return {"error": str(e), "tickers": []}

# ---------- AI ANALYSIS ----------
_ai_cache = {}
AI_CACHE_TTL = 3600

@app.get("/api/ai-analysis/{ticker}")
async def ai_analysis(ticker: str):
    now = time.time()
    if ticker in _ai_cache and (now - _ai_cache[ticker]["ts"]) < AI_CACHE_TTL:
        return {"ticker": ticker, "analysis": _ai_cache[ticker]["analysis"], "cached": True}

    def _get_data():
        try:
            info = yf.Ticker(ticker).info
            return {
                "name": info.get("longName") or info.get("shortName", ticker),
                "sector": info.get("sector",""),
                "rev_growth": round((info.get("revenueGrowth") or 0)*100,1),
                "earnings_growth": round((info.get("earningsGrowth") or 0)*100,1),
                "gross_margin": round((info.get("grossMargins") or 0)*100,1),
                "net_margin": round((info.get("profitMargins") or 0)*100,1),
                "pe": round(info.get("trailingPE") or 0,1),
                "pe_forward": round(info.get("forwardPE") or 0,1),
                "market_cap": round((info.get("marketCap") or 0)/1e9,2),
                "net_cash": round(((info.get("totalCash") or 0)-(info.get("totalDebt") or 0))/1e9,2),
                "roe": round((info.get("returnOnEquity") or 0)*100,1),
                "description": (info.get("longBusinessSummary") or "")[:300],
            }
        except: return None

    loop = asyncio.get_running_loop()
    data = await loop.run_in_executor(executor, _get_data)
    if not data:
        return {"ticker": ticker, "error": "Could not fetch stock data"}

    prompt = f"""You are a concise equity analyst. Analyze {ticker} ({data['name']}) and explain in 3-4 sentences WHY it qualifies as a STRONG BUY based on high revenue growth and market share gain vs sector median.

Metrics: Revenue Growth {data['rev_growth']}%, Earnings Growth {data['earnings_growth']}%, Gross Margin {data['gross_margin']}%, Net Margin {data['net_margin']}%, P/E {data['pe']}x, Forward P/E {data['pe_forward']}x, Market Cap ${data['market_cap']}B, Net Cash ${data['net_cash']}B, ROE {data['roe']}%, Sector: {data['sector']}.
Business: {data['description']}

Write sharp, direct analysis. Focus on: why revenue growth is exceptional, what drives it, key risks, valuation. No fluff. Max 4 sentences."""

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": ANTHROPIC_KEY,
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 300,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
        data_r = r.json()
        analysis = data_r["content"][0]["text"]
        _ai_cache[ticker] = {"analysis": analysis, "ts": now}
        return {"ticker": ticker, "analysis": analysis, "cached": False}
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}

# ---------- NEWS ----------
def _parse_av_news(items):
    result = []
    for n in items:
        result.append({
            "title": n.get("title", ""),
            "publisher": n.get("source", ""),
            "link": n.get("url", ""),
            "published": n.get("time_published", ""),
            "thumbnail": n.get("banner_image", "") or "",
            "summary": (n.get("summary", "") or "")[:200],
            "sentiment": n.get("overall_sentiment_label", ""),
        })
    return result

@app.get("/api/news/{ticker}")
async def get_news(ticker: str):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                "https://www.alphavantage.co/query",
                params={
                    "function": "NEWS_SENTIMENT",
                    "tickers": ticker,
                    "apikey": NEWS_KEY,
                    "limit": "8",
                    "sort": "LATEST"
                }
            )
        data = r.json()
        items = data.get("feed", [])
        return {"ticker": ticker, "news": _parse_av_news(items)}
    except Exception as e:
        return {"ticker": ticker, "news": [], "error": str(e)}

@app.get("/api/market-news")
async def market_news():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                "https://www.alphavantage.co/query",
                params={
                    "function": "NEWS_SENTIMENT",
                    "topics": "financial_markets,economy_macro",
                    "apikey": NEWS_KEY,
                    "limit": "20",
                    "sort": "LATEST"
                }
            )
        data = r.json()
        items = data.get("feed", [])
        return {"news": _parse_av_news(items)}
    except Exception as e:
        return {"news": [], "error": str(e)}

# ---------- STATIC (LAST!) ----------
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")

# ---------- MORNING BRIEF ----------
_brief_cache = {}
BRIEF_CACHE_TTL = 1800  # 30 min

@app.get("/api/morning-brief")
async def morning_brief(tickers: str = ""):
    """
    tickers: comma-separated list e.g. "AAPL,AMD,ASML"
    If empty, tries to use portfolio tickers from T212.
    """
    cache_key = tickers or "portfolio"
    now = time.time()
    if cache_key in _brief_cache and (now - _brief_cache[cache_key]["ts"]) < BRIEF_CACHE_TTL:
        return _brief_cache[cache_key]["data"]

    # 1. Resolve tickers
    watch = [t.strip().upper() for t in tickers.split(",") if t.strip()] if tickers else []
    if not watch:
        # try portfolio
        try:
            cred = base64.b64encode(f"{T212_KEY}:{T212_SECRET}".encode()).decode()
            async with httpx.AsyncClient(timeout=8) as client:
                r = await client.get(
                    "https://live.trading212.com/api/v0/equity/positions",
                    headers={"Authorization": f"Basic {cred}"}
                )
            if r.status_code == 200:
                positions = r.json()
                watch = list({
                    T212_MAP.get(p["instrument"]["ticker"],
                    p["instrument"]["ticker"].replace("_US_EQ","").replace("_EQ",""))
                    for p in positions
                })[:8]
        except:
            pass

    if not watch:
        watch = ["SPY", "QQQ", "AMD", "NVDA"]

    # 2. Fetch market data
    def _fetch_market():
        results = {}
        for sym, yf_sym in [("SP500","^GSPC"),("NASDAQ","^IXIC"),("VIX","^VIX"),
                             ("GOLD","GC=F"),("SILVER","SI=F"),("BTC","BTC-USD")]:
            try:
                tk = yf.Ticker(yf_sym)
                hist = tk.history(period="2d")
                if len(hist) >= 2:
                    prev = hist["Close"].iloc[-2]
                    curr = hist["Close"].iloc[-1]
                    chg = round((curr - prev) / prev * 100, 2)
                    results[sym] = {"price": round(curr, 2), "change_pct": chg}
                elif len(hist) == 1:
                    results[sym] = {"price": round(hist["Close"].iloc[-1], 2), "change_pct": 0}
            except:
                results[sym] = {"price": None, "change_pct": None}
        # sanitize NaN
        for k in results:
            p = results[k].get("price")
            c = results[k].get("change_pct")
            import math
            results[k]["price"] = None if (p is None or (isinstance(p, float) and math.isnan(p))) else float(p)
            results[k]["change_pct"] = None if (c is None or (isinstance(c, float) and math.isnan(c))) else round(float(c), 2)
        return results

    # 3. Fetch news for tickers
    async def _fetch_news_for_tickers(tlist):
        all_news = []
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # market news
                r = await client.get(
                    "https://www.alphavantage.co/query",
                    params={
                        "function": "NEWS_SENTIMENT",
                        "topics": "financial_markets,economy_macro,earnings",
                        "apikey": NEWS_KEY,
                        "limit": "15",
                        "sort": "RELEVANCE_SCORE"
                    }
                )
                mkt_data = r.json()
                for n in mkt_data.get("feed", [])[:8]:
                    all_news.append({
                        "title": n.get("title",""),
                        "source": n.get("source",""),
                        "summary": (n.get("summary","") or "")[:300],
                        "sentiment": n.get("overall_sentiment_label",""),
                        "tickers_mentioned": [t["ticker"] for t in n.get("ticker_sentiment",[])],
                        "time": n.get("time_published",""),
                        "url": n.get("url",""),
                        "thumbnail": n.get("banner_image","") or "",
                    })
        except:
            pass
        return all_news

    loop = asyncio.get_running_loop()
    market_data = await loop.run_in_executor(executor, _fetch_market)
    news_items = await _fetch_news_for_tickers(watch)

    # 4. Claude generates the brief
    ticker_list = ", ".join(watch)
    news_text = "\n".join([
        f"- [{n['source']}] {n['title']} (sentiment: {n['sentiment']})\n  Summary: {n['summary'][:200]}"
        for n in news_items[:8]
    ])

    market_text = ""
    for k, v in market_data.items():
        if v["price"]:
            market_text += f"{k}: {v['price']} ({'+' if v['change_pct'] and v['change_pct']>0 else ''}{v['change_pct']}%)\n"

    prompt = f"""You are an institutional equity research analyst generating a personalized morning brief.

User's portfolio/watchlist: {ticker_list}

Market snapshot:
{market_text}

Today's top news:
{news_text}

Generate a JSON response with this exact structure:
{{
  "three_things": [
    {{"text": "concise insight 1 relevant to the user's holdings", "confidence": "High|Medium|Low"}},
    {{"text": "concise insight 2", "confidence": "High|Medium|Low"}},
    {{"text": "concise insight 3", "confidence": "High|Medium|Low"}}
  ],
  "portfolio_risk": {{
    "score": <integer 1-10>,
    "level": "Low|Medium|High",
    "drivers": ["driver 1", "driver 2", "driver 3"]
  }},
  "top_stories": [
    {{
      "title": "news headline",
      "source": "source name",
      "why_it_matters": "1-2 sentences on relevance to user portfolio",
      "why_now": "1 sentence on why timing matters today",
      "affected_tickers": ["TICK1", "TICK2"]
    }}
  ],
  "holdings": [
    {{
      "ticker": "TICK",
      "impact_score": <integer 1-10>,
      "sentiment": "Bullish|Neutral|Bearish",
      "sentiment_confidence": <integer 50-95>,
      "reason": "short phrase explaining today's move",
      "ai_note": "Thesis unchanged.|Elevated volatility expected.|Positive catalyst.|No action required.|Monitor closely."
    }}
  ]
}}

Rules:
- three_things must be personalized to this user's specific tickers
- portfolio_risk score reflects today's macro + holding-specific risk
- top_stories: max 3, only include if genuinely relevant to user holdings
- holdings: include all tickers from the watchlist
- Be concise and direct. No fluff. Institutional tone.
- Return ONLY valid JSON, no markdown, no preamble."""

    try:
        async with httpx.AsyncClient(timeout=45) as client:
            r = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": ANTHROPIC_KEY,
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 1500,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
        raw = r.json()["content"][0]["text"]
        # strip possible markdown fences
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        brief_data = json.loads(raw.strip())
    except Exception as e:
        brief_data = {
            "three_things": [
                {"text": "Market data loaded. AI analysis unavailable — check API key.", "confidence": "Low"}
            ],
            "portfolio_risk": {"score": 5, "level": "Medium", "drivers": ["AI unavailable"]},
            "top_stories": [],
            "holdings": [{"ticker": t, "impact_score": 5, "sentiment": "Neutral",
                          "sentiment_confidence": 50, "reason": "No data", "ai_note": "AI unavailable."} for t in watch]
        }

    result = {
        "tickers": watch,
        "market": market_data,
        "news_raw": news_items[:3],
        "brief": brief_data,
        "generated_at": int(now)
    }

    _brief_cache[cache_key] = {"data": result, "ts": now}
    return result

# ---------- STATIC (LAST!) ----------
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

