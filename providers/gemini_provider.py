"""Gemini Interactions API (client.interactions.create) with a JSON response_format.

Untested live: no Gemini key yet. Gemini models can also be reached through
OpenRouter, which is how the default config runs them.
"""
from __future__ import annotations

import time
from datetime import datetime

from google import genai

import pricing
from schema import json_schema_without_additional_properties

from .base import (API_ERROR, AUTH, NETWORK, RATE_LIMIT, RETRYABLE_STATUS, TRUNCATED, Provider,
                   ProviderResult, fail, parse_answer)

MAX_ATTEMPTS = 5


class GeminiProvider(Provider):
    provider = "gemini"
    mode = "schema"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = genai.Client(api_key=self.api_key)

    def _identify(self, image_b64: str, mime: str, prompt: str, started: datetime) -> ProviderResult:
        interaction, attempts = None, 0
        for attempts in range(1, MAX_ATTEMPTS + 1):
            try:
                interaction = self.client.interactions.create(
                    model=self.model,
                    input=[
                        {"type": "text", "text": prompt},
                        {"type": "image", "data": image_b64, "mime_type": mime},
                    ],
                    response_format={"type": "text", "mime_type": "application/json",
                                     "schema": json_schema_without_additional_properties()},
                )
                break
            except Exception as e:
                status = getattr(e, "status_code", None)
                if status in (401, 403):
                    return fail(AUTH, str(e), attempts=attempts)
                if status is None:  # not an HTTP error — a bad request shape or a transport failure
                    category = NETWORK if "connect" in type(e).__name__.lower() else API_ERROR
                    return fail(category, f"{type(e).__name__}: {e}", attempts=attempts)
                if status not in RETRYABLE_STATUS or attempts == MAX_ATTEMPTS:
                    category = RATE_LIMIT if status == 429 else API_ERROR
                    return fail(category, f"HTTP {status}: {e}", attempts=attempts)
                time.sleep(min(2 ** attempts, 30))

        body = interaction.model_dump(mode="json", by_alias=True, exclude_none=True)
        body.pop("input", None)  # the echoed request would store the whole image again
        usage = interaction.usage
        input_tokens = (usage.total_input_tokens or 0) if usage else None
        # Thinking tokens are billed as output.
        output_tokens = ((usage.total_output_tokens or 0) + (usage.total_thought_tokens or 0)) if usage else None
        cached = (usage.total_cached_tokens or 0) if usage else 0
        cost = pricing.cost_usd(self.provider, self.model, input_tokens or 0, output_tokens or 0, cached) if usage else None
        result = ProviderResult(
            raw_response=body,
            raw_text=interaction.output_text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_input_tokens=cached,
            cost_usd=cost,
            cost_source="rate-table" if cost is not None else None,
            attempts=attempts,
            served_model=str(interaction.model) if interaction.model else None,
        )
        if interaction.status in ("incomplete", "budget_exceeded"):
            result.error, result.error_detail = TRUNCATED, f"status={interaction.status}"
            return result
        if interaction.status != "completed":
            result.error, result.error_detail = API_ERROR, f"status={interaction.status} errors={interaction.errors}"
            return result
        result.parsed, result.error, result.error_detail = parse_answer(result.raw_text)
        return result
