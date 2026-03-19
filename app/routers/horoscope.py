"""Horoscope API router."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, HTTPException

from app import cache
from app.ai import generator
from app.models.schemas import HoroscopeRequest, HoroscopeResponse, SystemInfo
from app.systems import egyptian

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
    try:
        birth = date.fromisoformat(req.birth_date)
    except ValueError:
        raise HTTPException(status_code=422, detail="birth_date must be YYYY-MM-DD")

    today = date.today()
    cache_key = cache.make_key("egyptian", req.name, req.birth_date, "")
    cached = cache.get(cache_key)

    chart_data = egyptian.get_egyptian_sign(month=birth.month, day=birth.day)

    if cached:
        return HoroscopeResponse(
            date=today.isoformat(),
            name=req.name,
            chart_data=chart_data,
            daily_reading=cached,
        )

    reading_text = generator.generate_daily_reading("egyptian", chart_data, req.name, today)
    cache.set(cache_key, reading_text)

    return HoroscopeResponse(
        date=today.isoformat(),
        name=req.name,
        chart_data=chart_data,
        daily_reading=reading_text,
    )
