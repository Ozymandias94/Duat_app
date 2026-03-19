"""Western tropical natal chart calculations using kerykeion."""

from __future__ import annotations


def get_western_chart(
    name: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    lat: float,
    lng: float,
    tz_str: str,
) -> dict:
    from kerykeion import AstrologicalSubjectFactory

    subject = AstrologicalSubjectFactory.from_birth_data(
        name=name,
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        lat=lat,
        lng=lng,
        tz_str=tz_str,
        online=False,
    )

    def planet(p) -> dict:
        return {"sign": p.sign, "degree": round(p.abs_pos, 2)}

    return {
        "system": "Western (Tropical)",
        "sun": planet(subject.sun),
        "moon": planet(subject.moon),
        "ascendant": planet(subject.ascendant),
        "mercury": planet(subject.mercury),
        "venus": planet(subject.venus),
        "mars": planet(subject.mars),
        "jupiter": planet(subject.jupiter),
        "saturn": planet(subject.saturn),
        "uranus": planet(subject.uranus),
        "neptune": planet(subject.neptune),
        "pluto": planet(subject.pluto),
    }


def format_for_prompt(chart: dict) -> str:
    lines = [
        f"Sun in {chart['sun']['sign']} ({chart['sun']['degree']}°)",
        f"Moon in {chart['moon']['sign']} ({chart['moon']['degree']}°)",
        f"Ascendant in {chart['ascendant']['sign']}",
        f"Mercury in {chart['mercury']['sign']}",
        f"Venus in {chart['venus']['sign']}",
        f"Mars in {chart['mars']['sign']}",
        f"Jupiter in {chart['jupiter']['sign']}",
        f"Saturn in {chart['saturn']['sign']}",
        f"Uranus in {chart['uranus']['sign']}",
        f"Neptune in {chart['neptune']['sign']}",
        f"Pluto in {chart['pluto']['sign']}",
    ]
    return "\n".join(lines)
