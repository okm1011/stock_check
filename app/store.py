from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path


def _minute_ts(ts: int | None = None) -> int:
    raw = int(ts if ts is not None else time.time())
    return raw - (raw % 60)


class Store:
    def __init__(self, db_path: str) -> None:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA busy_timeout=5000")
        self._init()

    def _init(self) -> None:
        with self._lock:
            self._conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS symbols (
                  symbol TEXT PRIMARY KEY,
                  base TEXT NOT NULL,
                  status TEXT NOT NULL,
                  kind TEXT NOT NULL DEFAULT 'COIN'
                );

                CREATE TABLE IF NOT EXISTS tickers (
                  symbol TEXT PRIMARY KEY,
                  price REAL NOT NULL,
                  change_24h REAL,
                  quote_volume REAL,
                  updated_at INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS snapshots (
                  ts INTEGER NOT NULL,
                  symbol TEXT NOT NULL,
                  price REAL NOT NULL,
                  PRIMARY KEY (ts, symbol)
                );
                CREATE INDEX IF NOT EXISTS idx_snap_ts ON snapshots(ts);

                CREATE TABLE IF NOT EXISTS notes (
                  symbol TEXT PRIMARY KEY,
                  category TEXT NOT NULL DEFAULT '미분류',
                  memo TEXT NOT NULL DEFAULT '',
                  updated_at INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS profiles (
                  base TEXT PRIMARY KEY,
                  project_id INTEGER,
                  name TEXT NOT NULL DEFAULT '',
                  tags TEXT NOT NULL DEFAULT '[]',
                  popularity REAL,
                  growth REAL,
                  transparency REAL,
                  brief TEXT NOT NULL DEFAULT '',
                  updated_at INTEGER NOT NULL
                );
                """
            )
            try:
                self._conn.execute(
                    "ALTER TABLE symbols ADD COLUMN kind TEXT NOT NULL DEFAULT 'COIN'"
                )
            except sqlite3.OperationalError:
                pass
            self._conn.commit()

    def replace_symbols(self, rows: list[tuple[str, str, str, str]]) -> None:
        with self._lock:
            self._conn.execute("DELETE FROM symbols")
            self._conn.executemany(
                "INSERT INTO symbols(symbol, base, status, kind) VALUES (?, ?, ?, ?)",
                rows,
            )
            self._conn.commit()

    def symbols(self) -> list[str]:
        with self._lock:
            cur = self._conn.execute("SELECT symbol FROM symbols ORDER BY symbol")
            return [r[0] for r in cur.fetchall()]

    def symbol_bases(self) -> list[tuple[str, str]]:
        with self._lock:
            cur = self._conn.execute("SELECT symbol, base FROM symbols ORDER BY symbol")
            return [(r[0], r[1]) for r in cur.fetchall()]

    def upsert_tickers(self, rows: list[tuple[str, float, float | None, float | None, int]]) -> None:
        with self._lock:
            self._conn.executemany(
                """
                INSERT INTO tickers(symbol, price, change_24h, quote_volume, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(symbol) DO UPDATE SET
                  price=excluded.price,
                  change_24h=excluded.change_24h,
                  quote_volume=excluded.quote_volume,
                  updated_at=excluded.updated_at
                """,
                rows,
            )
            self._conn.commit()

    def insert_snapshots(self, ts: int, prices: dict[str, float]) -> None:
        ts = _minute_ts(ts)
        with self._lock:
            self._conn.executemany(
                "INSERT OR REPLACE INTO snapshots(ts, symbol, price) VALUES (?, ?, ?)",
                [(ts, sym, px) for sym, px in prices.items()],
            )
            self._conn.commit()

    def prune_snapshots(self, older_than: int) -> None:
        with self._lock:
            self._conn.execute("DELETE FROM snapshots WHERE ts < ?", (older_than,))
            self._conn.commit()

    def prices_at(self, ts: int, slack: int = 180) -> dict[str, float]:
        ts = _minute_ts(ts)
        slack = max(60, int(slack))
        with self._lock:
            cur = self._conn.execute(
                """
                SELECT ts FROM snapshots
                WHERE ts BETWEEN ? AND ?
                ORDER BY ABS(ts - ?) ASC
                LIMIT 1
                """,
                (ts - slack, ts + slack, ts),
            )
            row = cur.fetchone()
            if not row:
                return {}
            cur = self._conn.execute(
                "SELECT symbol, price FROM snapshots WHERE ts = ?",
                (int(row[0]),),
            )
            return {r[0]: float(r[1]) for r in cur.fetchall()}

    def last_updated(self) -> int | None:
        with self._lock:
            cur = self._conn.execute("SELECT MAX(updated_at) FROM tickers")
            val = cur.fetchone()[0]
            return int(val) if val else None

    def upsert_profile(
        self,
        base: str,
        project_id: int | None,
        name: str,
        tags: list[str],
        popularity: float | None,
        growth: float | None,
        transparency: float | None,
        brief: str,
    ) -> None:
        now = int(time.time())
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO profiles(
                  base, project_id, name, tags, popularity, growth, transparency, brief, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(base) DO UPDATE SET
                  project_id=excluded.project_id,
                  name=excluded.name,
                  tags=excluded.tags,
                  popularity=excluded.popularity,
                  growth=excluded.growth,
                  transparency=excluded.transparency,
                  brief=excluded.brief,
                  updated_at=excluded.updated_at
                """,
                (
                    base,
                    project_id,
                    name.strip(),
                    json.dumps(tags, ensure_ascii=False),
                    popularity,
                    growth,
                    transparency,
                    brief.strip(),
                    now,
                ),
            )
            self._conn.commit()

    def profile_map(self) -> dict[str, dict]:
        with self._lock:
            cur = self._conn.execute(
                """
                SELECT base, project_id, name, tags, popularity, growth, transparency, brief, updated_at
                FROM profiles
                """
            )
            out: dict[str, dict] = {}
            for r in cur.fetchall():
                try:
                    tags = json.loads(r["tags"] or "[]")
                except json.JSONDecodeError:
                    tags = []
                if not isinstance(tags, list):
                    tags = []
                out[r["base"]] = {
                    "project_id": r["project_id"],
                    "name": r["name"] or "",
                    "tags": [str(t) for t in tags if t],
                    "popularity": r["popularity"],
                    "growth": r["growth"],
                    "transparency": r["transparency"],
                    "brief": r["brief"] or "",
                    "updated_at": int(r["updated_at"]),
                }
            return out

    def profiles_updated_at(self) -> int | None:
        with self._lock:
            cur = self._conn.execute("SELECT MAX(updated_at) FROM profiles")
            val = cur.fetchone()[0]
            return int(val) if val else None

    def rows(self) -> list[dict]:
        with self._lock:
            cur = self._conn.execute(
                """
                SELECT
                  s.symbol,
                  s.base,
                  COALESCE(s.kind, 'COIN') AS kind,
                  t.price,
                  t.change_24h,
                  t.quote_volume,
                  t.updated_at
                FROM symbols s
                JOIN tickers t ON t.symbol = s.symbol
                ORDER BY s.symbol
                """
            )
            return [dict(r) for r in cur.fetchall()]
