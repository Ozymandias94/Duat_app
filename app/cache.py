"""File-based daily cache for horoscope readings.

Cache keys include today's date, so entries automatically become stale
the next day and are pruned on the next write. Readings survive process
restarts because they are stored as JSON files under HOROSCOPE_CACHE_DIR
(defaults to /tmp/horoscope_cache).
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import date
from pathlib import Path

logger = logging.getLogger(__name__)

_CACHE_DIR = Path(os.environ.get("HOROSCOPE_CACHE_DIR", "/tmp/horoscope_cache"))


def _today() -> str:
    return date.today().isoformat()


def _key_to_path(key: tuple) -> Path:
    today = key[0]
    payload = "|".join(str(k) for k in key[1:])
    h = hashlib.sha256(payload.encode()).hexdigest()[:16]
    return _CACHE_DIR / today / f"{h}.json"


def make_key(system: str, name: str, birth_date: str, birth_time: str) -> tuple:
    return (_today(), system, name, birth_date, birth_time)


def get(key: tuple) -> str | None:
    path = _key_to_path(key)
    if path.exists():
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            logger.debug("Cache hit: %s", path.name)
            return value
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Cache read error: %s — %s", path, exc)
    return None


def set(key: tuple, value: str) -> None:
    today = _today()
    path = _key_to_path(key)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")
        logger.debug("Cache write: %s", path.name)
    except OSError as exc:
        logger.warning("Cache write error: %s — %s", path, exc)

    # Prune stale date directories (best-effort).
    try:
        for day_dir in _CACHE_DIR.iterdir():
            if day_dir.is_dir() and day_dir.name != today:
                for f in day_dir.iterdir():
                    f.unlink(missing_ok=True)
                day_dir.rmdir()
                logger.debug("Pruned stale cache dir: %s", day_dir.name)
    except OSError as exc:
        logger.warning("Cache pruning error: %s", exc)
