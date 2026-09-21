from __future__ import annotations

import time
from contextlib import asynccontextmanager
from pathlib import Path
from threading import Lock, Thread

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.templating import Jinja2Templates
from starlette.requests import Request

from app.binance import BinanceFutures
from app.config import PERIOD_SECONDS, load_config
from app.poller import Poller, backfill_missing
from app.sectors import SECTORS, group_rows
from app.store import Store, _minute_ts

CFG = load_config()
STORE = Store(CFG["db_path"])
POLLER = Poller(
    store=STORE,
    interval=int(CFG["poll_interval_seconds"]),
    history_days=int(CFG["history_days"]),
    quote=CFG["quote_asset"],
    contract=CFG["contract_type"],
)

_backfill_lock = Lock()
_backfilling: set[str] = set()

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


class NoteIn(BaseModel):
    category: str = Field(default="미분류", max_length=40)
    memo: str = Field(default="", max_length=500)


def _slack(period: str) -> int:
    sec = PERIOD_SECONDS.get(period, 3600)
    return max(180, min(sec // 4, 3600))


def _coverage(period: str) -> tuple[int, int]:
    sec = PERIOD_SECONDS.get(period)
    if not sec:
        return 0, 0
    then = _minute_ts() - sec
    have = STORE.prices_at(then, slack=_slack(period))
    symbols = STORE.symbols()
    return len(have), len(symbols)


def _kick_backfill(period: str) -> bool:
    if period not in PERIOD_SECONDS or period == "24h":
        return False
    have, total = _coverage(period)
    if total and have >= total * 0.9:
        return False
    with _backfill_lock:
        if period in _backfilling:
            return True
        _backfilling.add(period)

    def run() -> None:
        client = BinanceFutures()
        try:
            backfill_missing(STORE, client, period, STORE.symbols())
        except Exception as exc:
            print(f"[backfill {period}] {exc}", flush=True)
        finally:
            client.close()
            with _backfill_lock:
                _backfilling.discard(period)

    Thread(target=run, name=f"backfill-{period}", daemon=True).start()
    return True


def _rows_for(period: str) -> list[dict]:
    sec = PERIOD_SECONDS.get(period, PERIOD_SECONDS["24h"])
    then_prices = {} if period == "24h" else STORE.prices_at(_minute_ts() - sec, slack=_slack(period))
    out = []
    for r in STORE.rows():
        price = float(r["price"]) if r["price"] is not None else None
        change = None
        if period == "24h":
            change = r.get("change_24h")
            if change is not None:
                change = float(change)
        elif price and r["symbol"] in then_prices:
            base = then_prices[r["symbol"]]
            if base:
                change = (price - base) / base * 100.0
        out.append(
            {
                "symbol": r["symbol"],
                "base": r["base"],
                "kind": r.get("kind") or "COIN",
                "price": price,
                "change_pct": round(change, 2) if change is not None else None,
                "quote_volume": r.get("quote_volume"),
                "category": r.get("category") or "미분류",
                "memo": r.get("memo") or "",
            }
        )
    return out


@asynccontextmanager
async def lifespan(_app: FastAPI):
    POLLER.start()
    yield
    POLLER.stop()


app = FastAPI(title="stock_check", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return TEMPLATES.TemplateResponse(
        "index.html",
        {
            "request": request,
            "periods": CFG["periods"],
            "default_period": CFG["default_period"],
            "categories": CFG["categories"],
            "poll_interval": int(CFG["poll_interval_seconds"]),
            "sectors": [{"id": s, "label": l} for s, l in SECTORS],
        },
    )


@app.get("/api/meta")
def meta() -> dict:
    cats = list(dict.fromkeys(CFG["categories"] + STORE.note_categories()))
    have, total = _coverage(CFG["default_period"])
    return {
        "updated_at": STORE.last_updated(),
        "poll_status": POLLER.status,
        "last_error": POLLER.last_error,
        "count": total,
        "periods": CFG["periods"],
        "default_period": CFG["default_period"],
        "categories": cats,
        "poll_interval": int(CFG["poll_interval_seconds"]),
        "snapshot_coverage": have,
        "sectors": [{"id": s, "label": l} for s, l in SECTORS],
    }


@app.get("/api/rows")
def rows(period: str = "24h") -> dict:
    if period not in PERIOD_SECONDS:
        raise HTTPException(400, f"unknown period: {period}")
    filling = _kick_backfill(period)
    have, total = _coverage(period)
    rows = _rows_for(period)
    grouped = group_rows(rows)
    return {
        "period": period,
        "updated_at": STORE.last_updated(),
        "poll_status": POLLER.status,
        "last_error": POLLER.last_error,
        "backfill": filling or period in _backfilling,
        "coverage": have,
        "count": total,
        "now": int(time.time()),
        "rows": rows,
        **grouped,
    }


@app.put("/api/notes/{symbol}")
def save_note(symbol: str, body: NoteIn) -> dict:
    symbol = symbol.upper()
    known = set(STORE.symbols())
    if known and symbol not in known:
        raise HTTPException(404, "unknown symbol")
    STORE.save_note(symbol, body.category, body.memo)
    return {"ok": True, "symbol": symbol, "category": body.category, "memo": body.memo}
