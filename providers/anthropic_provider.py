"""Anthropic Messages API with server-side structured output (output_config.format).

messages.create + our own validation rather than messages.parse: parse() raises
on an invalid answer and the usage (already paid for) would be lost with it.
"""
from __future__ import annotations

from datetime import datetime

import anthropic

import pricing
from schema import json_schema

from .base import (API_ERROR, AUTH, EMPTY, NETWORK, RATE_LIMIT, REFUSAL, TIMEOUT, TRUNCATED,
                   Provider, ProviderResult, fail, parse_answer)


class AnthropicProvider(Provider):
    provider = "anthropic"
    mode = "schema"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = anthropic.Anthropic(api_key=self.api_key, max_retries=4, timeout=self.timeout)

    def _identify(self, image_b64: str, mime: str, prompt: str, started: datetime) -> ProviderResult:
        output_config: dict = {"format": {"type": "json_schema", "schema": json_schema()}}
        if self.options.get("effort"):
            output_config["effort"] = self.options["effort"]
        try:
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                output_config=output_config,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": mime, "data": image_b64}},
                        {"type": "text", "text": prompt},
                    ],
                }],
            )
        except anthropic.RateLimitError as e:
            return fail(RATE_LIMIT, str(e))
        except (anthropic.AuthenticationError, anthropic.PermissionDeniedError) as e:
            return fail(AUTH, str(e))
        except anthropic.APITimeoutError as e:
            return fail(TIMEOUT, str(e))
        except anthropic.APIConnectionError as e:
            return fail(NETWORK, str(e))
        except anthropic.APIStatusError as e:
            return fail(API_ERROR, f"HTTP {e.status_code}: {e.message}")

        usage = resp.usage
        cached = usage.cache_read_input_tokens or 0
        input_tokens = usage.input_tokens + cached + (usage.cache_creation_input_tokens or 0)
        result = ProviderResult(
            raw_response=resp.to_dict(),
            input_tokens=input_tokens,
            output_tokens=usage.output_tokens,
            cached_input_tokens=cached,
            cost_usd=pricing.cost_usd(self.provider, self.model, input_tokens, usage.output_tokens, cached),
            cost_source="rate-table",
            served_model=resp.model,
        )
        if result.cost_usd is None:
            result.cost_source = None

        if resp.stop_reason == "refusal":
            details = getattr(resp, "stop_details", None)
            category = getattr(details, "category", None)
            result.error, result.error_detail = REFUSAL, f"stop_reason=refusal category={category}"
            return result
        text = "".join(b.text for b in resp.content if b.type == "text")
        result.raw_text = text
        if resp.stop_reason == "max_tokens":
            result.error, result.error_detail = TRUNCATED, f"hit max_tokens={self.max_tokens}"
            return result
        parsed, err, detail = parse_answer(text)
        result.parsed, result.error, result.error_detail = parsed, err, detail
        if err == EMPTY:
            result.error_detail = f"no text block (stop_reason={resp.stop_reason})"
        return result
