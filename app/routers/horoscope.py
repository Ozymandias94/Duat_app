"""Horoscope API router."""

from __future__ import annotations

import logging
from datetime import date

from fastapi import APIRouter, HTTPException

from app import cache
from app.ai import generator
from app.models.schemas import HoroscopeRequest, HoroscopeResponse, SystemInfo, SystemReading
from app.systems import chinese, egyptian, vedic, western

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/horoscope", tags=["horoscope"])

SYSTEM_INFO = [
    SystemInfo(
        id="western",
        name="Western Astrology",
        description="Tropical zodiac natal chart using Swiss Ephemeris. Includes Sun, Moon, Ascendant, and seven classical + three modern planets.",
        requires_time=True,
        requires_location=True,
    ),
    SystemInfo(
        id="vedic",
        name="Vedic Astrology (Jyotish)",
        description="Sidereal zodiac with Lahiri ayanamsha and Whole Sign houses. Includes Nakshatra placement of the Moon.",
        requires_time=True,
        requires_location=True,
    ),
    SystemInfo(
        id="chinese",
        name="Chinese BaZi",
        description="Four Pillars of Destiny using the 60-Jiazi sexagenary cycle of Heavenly Stems and Earthly Branches.",
        requires_time=True,
        requires_location=False,
    ),
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
        if system == "western":
            return western.get_western_chart(
                name=req.name,
                year=birth.year, month=birth.month, day=birth.day,
                hour=hour, minute=minute,
                lat=req.birth_lat, lng=req.birth_lng,
                tz_str=req.birth_tz,
            )
        elif system == "vedic":
            return vedic.get_vedic_chart(
                name=req.name,
                year=birth.year, month=birth.month, day=birth.day,
                hour=hour, minute=minute,
                lat=req.birth_lat, lng=req.birth_lng,
                tz_str=req.birth_tz,
            )
        elif system == "chinese":
            return chinese.get_bazi_chart(
                year=birth.year, month=birth.month, day=birth.day, hour=hour
            )
        elif system == "egyptian":
            return egyptian.get_egyptian_sign(month=birth.month, day=birth.day)
        else:
            raise HTTPException(status_code=422, detail=f"Unknown system: {system}")
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Chart computation failed: system=%s error=%s", system, exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compute {system} chart. Check server logs for details.",
        ) from exc
