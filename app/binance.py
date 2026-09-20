from __future__ import annotations

import time

import httpx

FAPI = "https://fapi.binance.com"


class BinanceFutures:
    def __init__(self) -> None:
        self._http = httpx.Client(timeout=30.0, headers={"User-Agent": "stock-check/0.1"})

    def close(self) -> None:
        self._http.close()

    def usdt_perpetuals(self, quote: str = "USDT", contract: str = "PERPETUAL") -> list[dict]:
        data = self._http.get(f"{FAPI}/fapi/v1/exchangeInfo").json()
        out: list[dict] = []
        for s in data.get("symbols", []):
            if s.get("status") != "TRADING":
                continue
            if s.get("contractType") != contract:
                continue
            if s.get("quoteAsset") != quote:
                continue
            out.append(
                {
                    "symbol": s["symbol"],
                    "base": s.get("baseAsset") or s["symbol"].replace(quote, ""),
                    "status": s.get("status", "TRADING"),
                }
            )
        out.sort(key=lambda r: r["symbol"])
        return out

    def ticker_24h(self) -> list[dict]:
        data = self._http.get(f"{FAPI}/fapi/v1/ticker/24hr").json()
        if not isinstance(data, list):
            return []
        return data

    def kline_close_at(self, symbol: str, ts: int) -> float | None:
        """1분봉 종가. ts는 초 단위."""
        start_ms = (ts - (ts % 60)) * 1000
        for attempt in range(3):
            try:
                resp = self._http.get(
                    f"{FAPI}/fapi/v1/klines",
                    params={
                        "symbol": symbol,
                        "interval": "1m",
                        "startTime": start_ms,
                        "limit": 1,
                    },
                )
                if resp.status_code == 429:
                    time.sleep(1.2 * (attempt + 1))
                    continue
                if resp.status_code >= 400:
                    return None
                rows = resp.json()
                if not rows:
                    return None
                return float(rows[0][4])
            except Exception:
                time.sleep(0.4 * (attempt + 1))
        return None
