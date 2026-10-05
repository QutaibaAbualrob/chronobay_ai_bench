"""DeepSeek (OpenAI-compatible) — prompt mode.

DeepSeek supports response_format json_object only, not json_schema, so the
schema goes in the prompt and the answer is validated here. The docs warn the
API "may occasionally return empty content": one automatic retry on an empty or
unparseable answer; a second failure is a schema-parse error, never a wrong
answer. Both attempts are billed, so both are counted.
"""
from __future__ import annotations

from datetime import datetime, timezone

import openai

import pricing
from schema import PROMPT_MODE_SUFFIX

from .base import (API_ERROR, AUTH, NETWORK, RATE_LIMIT, SCHEMA_PARSE, TIMEOUT, TRUNCATED, Provider,
                   ProviderResult, fail, parse_answer)

BASE_URL = "https://api.deepseek.com"
# Chosen, not an API limit: a 16,000-token run cost 42% more and scored no better (README, Findings).
MAX_OUTPUT_TOKENS = 8192


class DeepSeekProvider(Provider):
    provider = "deepseek"
    mode = "prompt"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = openai.OpenAI(api_key=self.api_key, base_url=BASE_URL, max_retries=4, timeout=self.timeout)

    def _identify(self, image_b64: str, mime: str, prompt: str, started: datetime) -> ProviderResult:
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt + PROMPT_MODE_SUFFIX},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{image_b64}"}},
            ],
        }]
        result = ProviderResult(input_tokens=0, output_tokens=0, cost_usd=0.0, cost_source="rate-table",
                                raw_response={"attempts": []})
        failures = []
        for attempt in (1, 2):
            attempt_started = datetime.now(timezone.utc)
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    response_format={"type": "json_object"},
                    max_tokens=min(self.max_tokens, MAX_OUTPUT_TOKENS),
                )
            except openai.RateLimitError as e:
                return self._error(result, attempt, RATE_LIMIT, str(e))
            except (openai.AuthenticationError, openai.PermissionDeniedError) as e:
                return self._error(result, attempt, AUTH, str(e))
            except openai.APITimeoutError as e:
                return self._error(result, attempt, TIMEOUT, str(e))
            except openai.APIConnectionError as e:
                return self._error(result, attempt, NETWORK, str(e))
            except openai.APIStatusError as e:
                return self._error(result, attempt, API_ERROR, f"HTTP {e.status_code}: {e.message}")

            result.attempts = attempt
            result.served_model = resp.model
            result.raw_response["attempts"].append(resp.to_dict())
            usage = resp.usage
            if usage:
                cached = getattr(usage, "prompt_cache_hit_tokens", None) or 0
                result.input_tokens += usage.prompt_tokens
                result.output_tokens += usage.completion_tokens
                result.cached_input_tokens += cached
                cost = pricing.cost_usd(self.provider, self.model, usage.prompt_tokens,
                                        usage.completion_tokens, cached, at=attempt_started)
                if cost is None or result.cost_usd is None:
                    result.cost_usd, result.cost_source = None, None
                else:
                    result.cost_usd += cost

            choice = resp.choices[0] if resp.choices else None
            text = choice.message.content if choice else None
            result.raw_text = text
            parsed, err, detail = parse_answer(text, allow_wrapping=True)
            if parsed is not None:
                result.parsed, result.error, result.error_detail = parsed, None, None
                return result
            failures.append(f"attempt {attempt}: {err} ({detail}; finish_reason={choice.finish_reason if choice else None})")

        # Both attempts ran out of output tokens (usually spent on reasoning): truncation, not bad JSON.
        category = TRUNCATED if all("finish_reason=length" in f for f in failures) else SCHEMA_PARSE
        result.error, result.error_detail = category, " | ".join(failures)
        return result

    @staticmethod
    def _error(result: ProviderResult, attempt: int, category: str, detail: str) -> ProviderResult:
        """An API error; a retry's error keeps the first attempt's billed usage."""
        if attempt == 1:
            return fail(category, detail, attempts=attempt)
        result.attempts, result.error, result.error_detail = attempt, category, detail[:2000]
        return result
