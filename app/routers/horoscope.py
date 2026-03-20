"""Horoscope API router."""

from __future__ import annotations

import logging
from datetime import date

from fastapi import APIRouter, HTTPException

from app import cache
from app.ai import generator
from app.models.schemas import HoroscopeRequest, HoroscopeResponse, SystemInfo, SystemReading
from app.systems import egyptian

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/horoscope", tags=["horoscope"])

SYSTEM_INFO = [
    SystemInfo(
        id="egyptian",
        name="Egyptian Astrology",
        description="Ancient Egyptian zodiac based on birth date correspondence to deities, derived from Dendera temple sources and surviving literature.",
        requires_time=False,
        requires_location=False,
    ),
]


@router.get("/systems", response_model=list[SystemInfo])
def list_systems():
    return SYSTEM_INFO


@router.post("/daily", response_model=HoroscopeResponse)
def daily_horoscope(req: HoroscopeRequest):
    # Validated by Pydantic — safe to parse directly.
    birth = date.fromisoformat(req.birth_date)
    birth_hour = int(req.birth_time[:2])
    birth_minute = int(req.birth_time[3:])

    today = date.today()
    readings: dict[str, SystemReading] = {}

    for system in req.systems:
        cache_key = cache.make_key(system, req.name, req.birth_date, req.birth_time)
        cached = cache.get(cache_key)
        if cached:
            logger.info("Cache hit: system=%s name=%s", system, req.name)
            chart_data = _compute_chart(system, req, birth, birth_hour, birth_minute)
            readings[system] = SystemReading(chart_data=chart_data, daily_reading=cached)
            continue

        logger.info("Generating reading: system=%s name=%s", system, req.name)
        chart_data = _compute_chart(system, req, birth, birth_hour, birth_minute)
        reading_text = generator.generate_daily_reading(system, chart_data, req.name, today)
        cache.set(cache_key, reading_text)
        readings[system] = SystemReading(chart_data=chart_data, daily_reading=reading_text)

    return HoroscopeResponse(
        date=today.isoformat(),
        name=req.name,
        readings=readings,
    )


def _compute_chart(system: str, req: HoroscopeRequest, birth: date, hour: int, minute: int) -> dict:
    try:
        return egyptian.get_egyptian_sign(month=birth.month, day=birth.day)
    except Exception as exc:
        logger.error("Chart computation failed: system=%s error=%s", system, exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compute {system} chart. Check server logs for details.",
        ) from exc
