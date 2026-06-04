def calculate_live_multiples(stocks: list, live_map: dict) -> list:
    result = []
    for s in stocks:
        live = live_map.get(s["ticker"], {})
        price = live.get("price")
        chg = live.get("price_change_pct")
        live_pe = s.get("pe")
        live_pb = s.get("pb")
        result.append({**s, "current_price": price, "price_change_pct": chg, "live_pe": live_pe, "live_pb": live_pb})
    return result
