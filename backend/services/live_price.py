import yfinance as yf

def fetch_live_price(ticker: str) -> dict:
    try:
        tk = yf.Ticker(ticker)
        info = tk.info
        price = info.get("currentPrice") or info.get("regularMarketPrice")
        prev = info.get("previousClose") or info.get("regularMarketPreviousClose")
        chg = round((price - prev) / prev * 100, 2) if price and prev else None
        return {"ticker": ticker, "price": price, "price_change_pct": chg}
    except:
        return {"ticker": ticker, "price": None, "price_change_pct": None}
