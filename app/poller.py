from __future__ import annotations

import time
from threading import Event, Thread

from app.binance import BinanceFutures
from app.config import PERIOD_SECONDS
from app.store import Store, _minute_ts


class Poller:
    def __init__(self, store: Store, interval: int, history_days: int, quote: str, contract: str) -> None:
        self.store = store
        self.interval = max(30, int(interval))
        self.history_days = max(2, int(history_days))
        self.quote = quote
        self.contract = contract
        self.binance = BinanceFutures()
        self._stop = Event()
        self._thread: Thread | None = None
        self._symbols_at = 0.0
        self.status = "idle"
        self.last_error = ""

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = Thread(target=self._run, name="poller", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=8)
        self.binance.close()

    def _run(self) -> None:
        while not self._stop.is_set():
            started = time.monotonic()
            try:
                self.tick()
                self.last_error = ""
            except Exception as exc:
                self.status = "error"
                self.last_error = str(exc)
            wait = self.interval - (time.monotonic() - started)
            end = time.monotonic() + max(1.0, wait)
            while not self._stop.is_set() and time.monotonic() < end:
                time.sleep(min(0.5, end - time.monotonic()))

    def tick(self) -> None:
        self.status = "fetching"
        now = time.monotonic()
        if now - self._symbols_at > 6 * 3600 or not self.store.symbols():
            info = self.binance.usdt_perpetuals(self.quote, self.contract)
            self.store.replace_symbols(
                [(r["symbol"], r["base"], r["status"], r.get("kind") or "COIN") for r in info]
            )
            self._symbols_at = now

        wanted = set(self.store.symbols())
        tickers = self.binance.ticker_24h()
        ts = _minute_ts()
        rows = []
        prices: dict[str, float] = {}
        for t in tickers:
            sym = t.get("symbol")
            if sym not in wanted:
                continue
            try:
                price = float(t["lastPrice"])
            except (KeyError, TypeError, ValueError):
                continue
            chg = _f(t.get("priceChangePercent"))
            qvol = _f(t.get("quoteVolume"))
            rows.append((sym, price, chg, qvol, ts))
            prices[sym] = price
        if rows:
            self.store.upsert_tickers(rows)
            self.store.insert_snapshots(ts, prices)
            keep_from = ts - self.history_days * 86400
            self.store.prune_snapshots(keep_from)
        self.status = "ok"


def backfill_missing(store: Store, binance: BinanceFutures, period: str, symbols: list[str]) -> None:
    """기간 시작가 스냅샷이 없으면 1분봉으로 한 번 채운다."""
    sec = PERIOD_SECONDS.get(period)
    if not sec or period == "24h":
        return
    then = _minute_ts() - sec
    have = store.prices_at(then)
    missing = [s for s in symbols if s not in have]
    if not missing:
        return
    filled: dict[str, float] = {}
    for i, sym in enumerate(missing):
        px = binance.kline_close_at(sym, then)
        if px is not None:
            filled[sym] = px
        if filled and (len(filled) % 25 == 0 or i == len(missing) - 1):
            store.insert_snapshots(then, filled)
            filled = {}
        if (i + 1) % 40 == 0:
            time.sleep(0.4)


def _f(v) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None
