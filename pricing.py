"""Per-model token rates in USD per 1M tokens, each with the date it was checked.

Rates are never hardcoded in provider code: they live here, dated, with a source,
so a stale rate shows up as a warning next to the dollar figure instead of
quietly producing a wrong number. OpenRouter is not listed — it reports the real
charge in every response (usage.cost), which the harness uses directly.

Keys are "<provider>:<provider model id>".
"""
from __future__ import annotations

from datetime import date, datetime, timezone

STALE_AFTER_DAYS = 30

ANTHROPIC_SOURCE = "https://platform.claude.com/docs/en/about-claude/pricing"
DEEPSEEK_SOURCE = "https://api-docs.deepseek.com/quick_start/pricing/"
OPENAI_SOURCE = "https://developers.openai.com/api/docs/pricing"

# DeepSeek prices differ by time of day. Peak hours (UTC, Monday–Friday):
# 01:00–04:00 and 06:00–10:00, excluding Chinese public holidays — holidays
# are not modelled here, so a holiday request is costed at the higher peak rate.
DEEPSEEK_PEAK_HOURS_UTC = [(1, 4), (6, 10)]

_DEEPSEEK_FLASH = {
    "off_peak": {"in": 0.15, "in_cached": 0.003, "out": 0.60},
    "peak": {"in": 0.30, "in_cached": 0.006, "out": 1.20},
    "schedule": "deepseek",
    "last_verified": "2026-09-30",
    "source": DEEPSEEK_SOURCE,
}

PRICES: dict[str, dict] = {
    "anthropic:claude-opus-5-5": {"in": 4.00, "out": 20.00, "last_verified": "2026-09-30", "source": ANTHROPIC_SOURCE},
    "anthropic:claude-opus-5": {"in": 5.00, "out": 25.00, "last_verified": "2026-09-30", "source": ANTHROPIC_SOURCE},
    "anthropic:claude-sonnet-5-5": {"in": 2.00, "out": 10.00, "last_verified": "2026-09-30", "source": ANTHROPIC_SOURCE},
    # The scheduled 2026-09-01 increase to $3/$15 was cancelled; $2/$10 is now standard.
    "anthropic:claude-sonnet-5": {"in": 2.00, "out": 10.00, "last_verified": "2026-09-30", "source": ANTHROPIC_SOURCE},
    "anthropic:claude-haiku-4-5": {"in": 1.00, "out": 5.00, "last_verified": "2026-09-30", "source": ANTHROPIC_SOURCE},
    "anthropic:claude-fable-5-1": {"in": 10.00, "out": 50.00, "last_verified": "2026-09-30", "source": ANTHROPIC_SOURCE},
    "deepseek:deepseek-flash": _DEEPSEEK_FLASH,
    # Legacy names, still accepted and served by the current Flash model.
    "deepseek:deepseek-v4-flash": _DEEPSEEK_FLASH,
    "deepseek:deepseek-v4-flash-vision-exp": _DEEPSEEK_FLASH,
    # OpenAI direct (short-context rates).
    "openai:gpt-6.1-sol": {"in": 2.00, "in_cached": 0.10, "out": 10.00, "last_verified": "2026-10-05", "source": OPENAI_SOURCE},
    "openai:gpt-6-luna": {"in": 0.10, "in_cached": 0.01, "out": 0.50, "last_verified": "2026-10-01", "source": OPENAI_SOURCE},
    "openai:gpt-5.6-luna": {"in": 0.20, "in_cached": 0.02, "out": 1.20, "last_verified": "2026-10-01", "source": OPENAI_SOURCE},
    # Gemini direct: add dated entries here before running it,
    # otherwise its cost is reported as "unavailable".
}


def lookup(provider: str, model: str) -> dict | None:
    return PRICES.get(f"{provider}:{model}")


def is_deepseek_peak(ts: datetime) -> bool:
    ts = ts.astimezone(timezone.utc)
    if ts.weekday() >= 5:
        return False
    return any(start <= ts.hour < end for start, end in DEEPSEEK_PEAK_HOURS_UTC)


def cost_usd(provider: str, model: str, input_tokens: int, output_tokens: int,
             cached_input_tokens: int = 0, at: datetime | None = None) -> float | None:
    """Token cost, or None when the model has no rate (never $0.00 for unknown)."""
    entry = lookup(provider, model)
    if entry is None:
        return None
    if entry.get("schedule") == "deepseek":
        rates = entry["peak"] if is_deepseek_peak(at or datetime.now(timezone.utc)) else entry["off_peak"]
    else:
        rates = entry
    uncached = max(input_tokens - cached_input_tokens, 0)
    in_cached_rate = rates.get("in_cached", rates["in"])
    return (uncached * rates["in"] + cached_input_tokens * in_cached_rate + output_tokens * rates["out"]) / 1_000_000


def staleness_warning(provider: str, model: str, today: date | None = None) -> str | None:
    entry = lookup(provider, model)
    if entry is None:
        return None
    verified = date.fromisoformat(entry["last_verified"])
    age = ((today or date.today()) - verified).days
    if age > STALE_AFTER_DAYS:
        return f"rates last verified {entry['last_verified']} ({age} days ago) — check {entry['source']}"
    return None
