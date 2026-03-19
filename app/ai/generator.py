"""Claude-powered daily horoscope reading generator."""

from __future__ import annotations

import os
from datetime import date

import anthropic

from app.systems import western, vedic, chinese, egyptian

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 512

SYSTEM_PROMPT = (
    "You are a masterful astrologer fluent in multiple ancient and modern traditions. "
    "Generate a personalized daily horoscope reading for the user based on their natal "
    "chart data and today's date. The reading must be:\n"
    "- Personalized: reference their specific signs, planets, or pillars\n"
    "- Forward-looking: speak to what today holds for them\n"
    "- 150–200 words\n"
    "- Written in second person (you / your)\n"
    "- Thoughtful, poetic, and concrete in its guidance\n"
    "Do not include disclaimers about astrology being for entertainment."
)

_FORMATTERS = {
    "western": western.format_for_prompt,
    "vedic": vedic.format_for_prompt,
    "chinese": chinese.format_for_prompt,
    "egyptian": egyptian.format_for_prompt,
}

_SYSTEM_NAMES = {
    "western": "Western Tropical Astrology",
    "vedic": "Vedic Jyotish Astrology",
    "chinese": "Chinese BaZi (Four Pillars of Destiny)",
    "egyptian": "Ancient Egyptian Astrology",
}


def generate_daily_reading(
    system: str,
    chart_data: dict,
    person_name: str,
    today: date,
) -> str:
    """Call Claude to generate a daily reading for the given system and chart."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    formatter = _FORMATTERS[system]
    chart_text = formatter(chart_data)
    system_name = _SYSTEM_NAMES[system]

    user_prompt = (
        f"Today is {today.strftime('%A, %B %d, %Y')}.\n\n"
        f"Generate a {system_name} daily horoscope reading for {person_name}.\n\n"
        f"Their natal chart:\n{chart_text}\n\n"
        f"Focus on what today's energies mean specifically for someone with these placements."
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return response.content[0].text
