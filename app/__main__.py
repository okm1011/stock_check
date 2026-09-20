from __future__ import annotations

import uvicorn

from app.config import load_config
from app.web import app


def main() -> None:
    cfg = load_config()
    uvicorn.run(
        app,
        host=str(cfg["host"]),
        port=int(cfg["port"]),
        log_level="info",
    )


if __name__ == "__main__":
    main()
