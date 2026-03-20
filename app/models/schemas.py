from __future__ import annotations

import re
from datetime import date
from typing import Any, Literal

import pytz
from pydantic import BaseModel, Field, field_validator

SystemName = Literal["western", "vedic", "chinese", "egyptian"]


class HoroscopeRequest(BaseModel):
    name: str = Field(..., description="Person's name")
    birth_date: str = Field(..., description="Birth date in YYYY-MM-DD format")
    birth_time: str = Field("12:00", description="Birth time in HH:MM (24h), defaults to noon")
    birth_lat: float = Field(..., description="Birth latitude in decimal degrees")
    birth_lng: float = Field(..., description="Birth longitude in decimal degrees")
    birth_tz: str = Field(..., description="IANA timezone string, e.g. 'America/New_York'")
    systems: list[SystemName] = Field(
        default=["western", "vedic", "chinese", "egyptian"],
        description="Which astrological systems to include",
    )

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: str) -> str:
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError("birth_date must be in YYYY-MM-DD format")
        return v

    @field_validator("birth_time")
    @classmethod
    def validate_birth_time(cls, v: str) -> str:
        if not re.match(r"^\d{2}:\d{2}$", v):
            raise ValueError("birth_time must be in HH:MM format (e.g. '14:30')")
        h, m = int(v[:2]), int(v[3:])
        if not 0 <= h <= 23:
            raise ValueError("birth_time hours must be 00-23")
        if not 0 <= m <= 59:
            raise ValueError("birth_time minutes must be 00-59")
        return v

    @field_validator("birth_tz")
    @classmethod
    def validate_birth_tz(cls, v: str) -> str:
        try:
            pytz.timezone(v)
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValueError(
                f"Unknown timezone '{v}'. Use an IANA timezone string, e.g. 'America/New_York'."
            )
        return v


class SystemReading(BaseModel):
    chart_data: dict[str, Any]
    daily_reading: str


class HoroscopeResponse(BaseModel):
    date: str
    name: str
    readings: dict[str, SystemReading]


class SystemInfo(BaseModel):
    id: str
    name: str
    description: str
    requires_time: bool
    requires_location: bool
