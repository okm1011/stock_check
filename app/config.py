from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "config.yaml"

PERIOD_SECONDS = {
    "15m": 15 * 60,
    "1h": 60 * 60,
    "4h": 4 * 60 * 60,
    "24h": 24 * 60 * 60,
    "7d": 7 * 24 * 60 * 60,
}


def load_config(path: Path | None = None) -> dict[str, Any]:
    cfg_path = path or DEFAULT_CONFIG
    with cfg_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    data.setdefault("host", "127.0.0.1")
    data.setdefault("port", 8090)
    data.setdefault("poll_interval_seconds", 60)
    data.setdefault("quote_asset", "USDT")
    data.setdefault("contract_type", "PERPETUAL")
    data.setdefault("default_period", "24h")
    data.setdefault("periods", list(PERIOD_SECONDS))
    data.setdefault("history_days", 8)
    data.setdefault("rootdata_interval_seconds", 86400)
    db = data.get("db_path", "data/stock_check.db")
    data["db_path"] = str((ROOT / db).resolve()) if not Path(db).is_absolute() else db
    return data
