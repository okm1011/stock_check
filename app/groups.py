from __future__ import annotations

# 대세 카드. 이 심볼은 알트 표에서 뺀다.
MACRO = [
    {"id": "oil", "label": "유가", "symbol": "CLUSDT", "hint": "WTI"},
    {"id": "soxl", "label": "SOXL", "symbol": "SOXLUSDT", "hint": "반도체 3X"},
    {"id": "nasdaq", "label": "나스닥", "symbol": "QQQUSDT", "hint": "QQQ"},
    {"id": "btc", "label": "비트코인", "symbol": "BTCUSDT", "hint": "BTC"},
    {"id": "eth", "label": "이더리움", "symbol": "ETHUSDT", "hint": "ETH"},
    {"id": "sol", "label": "솔라나", "symbol": "SOLUSDT", "hint": "SOL"},
]

MACRO_SYMBOLS = {m["symbol"] for m in MACRO}
OTHER = "기타"


def _strength(rows: list[dict]) -> dict:
    chgs = [float(r["change_pct"]) for r in rows if r.get("change_pct") is not None]
    n = len(chgs)
    if not n:
        return {"median_chg": None, "up_count": 0, "up_pct": None, "n": 0}
    chgs.sort()
    if n % 2:
        mid = chgs[n // 2]
    else:
        mid = (chgs[n // 2 - 1] + chgs[n // 2]) / 2
    up = sum(1 for x in chgs if x > 0)
    return {
        "median_chg": round(mid, 2),
        "up_count": up,
        "up_pct": round(100.0 * up / n, 0),
        "n": n,
    }


def group_rows(rows: list[dict]) -> dict:
    by_sym = {r["symbol"]: r for r in rows}
    macro = []
    for m in MACRO:
        item = dict(m)
        row = by_sym.get(m["symbol"])
        if row:
            item.update(row)
            item["listed"] = True
        else:
            item.update(
                {
                    "base": m["symbol"].replace("USDT", ""),
                    "price": None,
                    "change_pct": None,
                    "quote_volume": None,
                    "tags": [],
                    "brief": "",
                    "popularity": None,
                    "growth": None,
                    "transparency": None,
                    "listed": False,
                    "is_macro": True,
                }
            )
        macro.append(item)

    alts = [r for r in rows if r["symbol"] not in MACRO_SYMBOLS]
    buckets: dict[str, list[dict]] = {}
    for row in alts:
        tags = [t for t in (row.get("tags") or []) if t and t != OTHER]
        if not tags:
            buckets.setdefault(OTHER, []).append(row)
            continue
        for tag in tags:
            buckets.setdefault(tag, []).append(row)

    names = sorted((name for name in buckets if name != OTHER), key=lambda n: (-len(buckets[n]), n))
    if OTHER in buckets:
        names.append(OTHER)
    tag_groups = []
    for name in names:
        chunk = buckets[name]
        tag_groups.append(
            {
                "id": name,
                "label": name,
                "count": len(chunk),
                **_strength(chunk),
            }
        )
    return {
        "macro": macro,
        "tag_groups": tag_groups,
        "alt_count": len(alts),
        "alt_strength": _strength(alts),
    }
