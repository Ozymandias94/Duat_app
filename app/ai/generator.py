"""Claude-powered daily horoscope reading generator."""

from __future__ import annotations

import logging
import os
from datetime import date

import anthropic

from app.systems import egyptian

logger = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-6"
FALLBACK_MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 512


def _call_claude(client: anthropic.Anthropic, *, model: str, max_tokens: int, system: str, messages: list) -> str:
    """Call Claude with automatic fallback to FALLBACK_MODEL on model errors."""
    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )
        return response.content[0].text
    except (anthropic.NotFoundError, anthropic.BadRequestError) as exc:
        if model == FALLBACK_MODEL:
            raise
        logger.warning("Primary model %s unavailable (%s), retrying with %s", model, exc, FALLBACK_MODEL)
        response = client.messages.create(
            model=FALLBACK_MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )
        return response.content[0].text


def generate_daily_reading(
    system: str,
    chart_data: dict,
    person_name: str,
    today: date,
) -> str:
    """Call Claude to generate a daily reading.

    The full engine.md is loaded from the path in SYSTEM_CONFIG["full_system_prompt"]
    and passed as the system prompt. The user message is a structured reading request
    matching engine Section 12.4 format.
    """
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    config = egyptian.SYSTEM_CONFIG
    max_tokens = config.get("max_tokens", MAX_TOKENS)

    with open(config["full_system_prompt"], "r", encoding="utf-8") as fh:
        system_prompt = fh.read()

    chart_text = egyptian.format_for_prompt(chart_data)
    user_prompt = (
        f"READING_TYPE: DAILY\n"
        f"PERSON_NAME: {person_name}\n"
        f"TODAY_DATE: {today.isoformat()}\n\n"
        f"NATAL_CHART_SUMMARY:\n{chart_text}\n\n"
        f"NOTE: Full ephemeris decan calculations are not yet available. "
        f"Generate a DAILY reading using the natal chart summary above. "
        f"Apply the voice and tone rules from Section 2, draw on the deity "
        f"library from Section 3, reference the active season from Section 4, "
        f"and follow the daily reading structure from Section 8.4."
    )

    logger.info("Calling Claude: system=%s model=%s max_tokens=%d", system, MODEL, max_tokens)
    text = _call_claude(
        client,
        model=MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    logger.info("Reading generated: system=%s chars=%d", system, len(text))
    return text
