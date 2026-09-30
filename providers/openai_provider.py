"""OpenAI Responses API with a strict json_schema text format.

responses.create + our own validation rather than responses.parse, so the
usage survives an unparseable answer. Untested live: no OpenAI key yet.
"""
from __future__ import annotations

from datetime import datetime

import openai

import pricing
from schema import json_schema

from .base import (API_ERROR, AUTH, NETWORK, RATE_LIMIT, REFUSAL, TIMEOUT, TRUNCATED, Provider,
                   ProviderResult, fail, parse_answer)


class OpenAIProvider(Provider):
    provider = "openai"
    mode = "schema"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = openai.OpenAI(api_key=self.api_key, max_retries=4, timeout=self.timeout)

    def _identify(self, image_b64: str, mime: str, prompt: str, started: datetime) -> ProviderResult:
        try:
            resp = self.client.responses.create(
                model=self.model,
                max_output_tokens=self.max_tokens,
                input=[{
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {"type": "input_image", "image_url": f"data:{mime};base64,{image_b64}", "detail": "high"},
                    ],
                }],
                text={"format": {"type": "json_schema", "name": "watch_identification",
                                 "schema": json_schema(), "strict": True}},
            )
        except openai.RateLimitError as e:
            return fail(RATE_LIMIT, str(e))
        except (openai.AuthenticationError, openai.PermissionDeniedError) as e:
            return fail(AUTH, str(e))
        except openai.APITimeoutError as e:
            return fail(TIMEOUT, str(e))
        except openai.APIConnectionError as e:
            return fail(NETWORK, str(e))
        except openai.APIStatusError as e:
            return fail(API_ERROR, f"HTTP {e.status_code}: {e.message}")

        usage = resp.usage
        input_tokens = usage.input_tokens if usage else None
        output_tokens = usage.output_tokens if usage else None
        cached = (usage.input_tokens_details.cached_tokens or 0) if usage and usage.input_tokens_details else 0
        cost = pricing.cost_usd(self.provider, self.model, input_tokens or 0, output_tokens or 0, cached) if usage else None
        result = ProviderResult(
            raw_response=resp.to_dict(),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_input_tokens=cached,
            cost_usd=cost,
            cost_source="rate-table" if cost is not None else None,
            served_model=resp.model,
        )

        for item in resp.output or []:
            for part in getattr(item, "content", None) or []:
                if getattr(part, "type", None) == "refusal":
                    result.error, result.error_detail = REFUSAL, part.refusal
                    return result
        result.raw_text = resp.output_text
        if resp.status == "incomplete":
            reason = resp.incomplete_details.reason if resp.incomplete_details else "unknown"
            result.error, result.error_detail = TRUNCATED, f"incomplete: {reason}"
            return result
        result.parsed, result.error, result.error_detail = parse_answer(result.raw_text)
        return result
