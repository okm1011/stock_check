"""RootData 공개 목록 페이지에서 태그·설명·인기·성장 지표를 하루 한 번 모은다.

유료 Open API 키는 쓰지 않는다. 목록 HTML에 이미 들어 있는 값을 읽는다.
투명성 점수는 홈 순위(상위 일부)에만 있다.
"""

from __future__ import annotations

import json
import time
from threading import Event, Thread

import httpx

from app.store import Store

LIST_URL = "https://ko.rootdata.com/projects"
HOME_URL = "https://ko.rootdata.com/"


def norm_base(base: str) -> str:
    b = (base or "").upper().strip()
    for prefix in ("1000000", "1000", "1M"):
        if b.startswith(prefix) and len(b) > len(prefix):
            return b[len(prefix):]
    return b


def _num(value) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _text(value) -> str:
    if isinstance(value, dict):
        value = value.get("ko_value") or value.get("en_value") or ""
    text = str(value or "").replace("\n", " ").strip()
    if len(text) > 280:
        return text[:277].rstrip() + "…"
    return text


def _tags(value) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            out.append(item.strip())
        elif isinstance(item, dict):
            name = _text(item.get("name") or item.get("tag_name") or "")
            if name:
                out.append(name)
    return list(dict.fromkeys(out))


def _parse_embedded(html: str, marker: str):
    idx = html.find(marker)
    if idx < 0:
        return None
    raw = html[idx:idx + 900000]
    un = raw.replace('\\"', '"').replace("\\\\", "\\").replace("\\/", "/")
    starts = [p for p in (un.find("{"), un.find("[")) if p >= 0]
    if not starts:
        return None
    start = min(starts)
    opening = un[start]
    closing = "}" if opening == "{" else "]"
    depth = 0
    in_str = False
    esc = False
    for pos, ch in enumerate(un[start:], start):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == opening:
            depth += 1
        elif ch == closing:
            depth -= 1
            if depth == 0:
                return json.loads(un[start:pos + 1])
    return None


class RootDataSync:
    def __init__(self, store: Store, interval: int) -> None:
        self.store = store
        self.interval = max(3600, int(interval))
        self._stop = Event()
        self._thread: Thread | None = None
        self.status = "idle"
        self.last_error = ""
        self.updated_at: int | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = Thread(target=self._run, name="rootdata", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=8)

    def _run(self) -> None:
        if self._stop.wait(8):
            return
        while not self._stop.is_set():
            outcome = "wait"
            try:
                outcome = self.tick()
            except Exception as exc:
                self.status = "error"
                self.last_error = str(exc)
                outcome = "error"
            if outcome == "ok":
                wait = self.interval
            elif outcome == "error":
                wait = 600
            else:
                wait = 20
            if self._stop.wait(wait):
                return

    def tick(self) -> str:
        wanted: set[str] = set()
        for _symbol, base in self.store.symbol_bases():
            key = norm_base(base)
            if key:
                wanted.add(key)
        if not wanted:
            self.status = "wait"
            self.last_error = ""
            return "wait"

        self.status = "sync"
        self.last_error = ""
        client = httpx.Client(
            timeout=40.0,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept-Language": "ko",
            },
            follow_redirects=True,
        )
        try:
            transparency = self._transparency(client)
            best: dict[str, dict] = {}
            first = self._list_page(client, 1)
            items = first.get("items") or []
            total = int(first.get("total") or len(items) or 0)
            limit = max(1, len(items) or 30)
            pages = min(2000, max(1, (total + limit - 1) // limit))
            self._take(items, wanted, transparency, best)
            self.last_error = f"1/{pages}"
            for page in range(2, pages + 1):
                if self._stop.is_set():
                    break
                page_items = self._list_page(client, page).get("items") or []
                self._take(page_items, wanted, transparency, best)
                self.last_error = f"{page}/{pages}"
                if len(page_items) < limit:
                    break
            self.status = "ok"
            self.last_error = ""
            self.updated_at = int(time.time())
            return "ok"
        finally:
            client.close()

    def _get(self, client: httpx.Client, url: str) -> str:
        last = ""
        for attempt in range(4):
            if self._stop.is_set():
                raise RuntimeError("중단됨")
            try:
                resp = client.get(url)
                if resp.status_code in (429, 503):
                    time.sleep(8 * (attempt + 1))
                    last = f"HTTP {resp.status_code}"
                    continue
                resp.raise_for_status()
                time.sleep(0.25)
                return resp.text
            except httpx.HTTPError as exc:
                last = str(exc)
                time.sleep(2 * (attempt + 1))
        raise RuntimeError(last or "RootData 페이지를 읽지 못했습니다")

    def _list_page(self, client: httpx.Client, page: int) -> dict:
        url = LIST_URL if page <= 1 else f"{LIST_URL}?page={page}"
        html = self._get(client, url)
        data = _parse_embedded(html, 'initialData\\":')
        if not isinstance(data, dict) or "items" not in data:
            raise RuntimeError(f"{page}페이지에서 목록을 찾지 못했습니다")
        return data

    def _transparency(self, client: httpx.Client) -> dict[str, float]:
        try:
            html = self._get(client, HOME_URL)
        except Exception:
            return {}
        rows = _parse_embedded(html, 'initialRankData\\":')
        if not isinstance(rows, list):
            return {}
        out: dict[str, float] = {}
        for row in rows:
            if not isinstance(row, dict):
                continue
            token = norm_base(str(row.get("tokenSymbol") or ""))
            score = _num(row.get("transparencyScore"))
            if token and score is not None:
                out[token] = score
        return out

    def _take(self, items: list, wanted: set[str], transparency: dict[str, float], best: dict[str, dict]) -> None:
        for item in items:
            if not isinstance(item, dict):
                continue
            base = norm_base(str(item.get("lssuingCode") or ""))
            if base not in wanted:
                continue
            popularity = _num(item.get("eval"))
            prev = best.get(base)
            if prev is not None and (prev["popularity"] or -1) > (popularity or -1):
                continue
            name = item.get("name")
            row = {
                "base": base,
                "project_id": int(item["id"]) if item.get("id") else None,
                "name": _text(name) if isinstance(name, dict) else str(name or ""),
                "tags": _tags(item.get("tagList")),
                "popularity": popularity,
                "growth": _num(item.get("rdGrowth")),
                "transparency": transparency.get(base),
                "brief": _text(item.get("briefIntd")),
            }
            best[base] = row
            self.store.upsert_profile(**row)
