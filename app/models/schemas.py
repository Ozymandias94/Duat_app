from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class HoroscopeRequest(BaseModel):
    name: str = Field(..., description="Person's name")
    birth_date: str = Field(..., description="Birth date in YYYY-MM-DD format")


class HoroscopeResponse(BaseModel):
    date: str
    name: str
    chart_data: dict[str, Any]
    daily_reading: str


class SystemInfo(BaseModel):
    id: str
    name: str
    description: str
    requires_time: bool
    requires_location: bool
