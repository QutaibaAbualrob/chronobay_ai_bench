"""OpenRouter chat completions with a strict json_schema response_format.

OpenRouter returns the real charge in every response (usage.cost, in credits;
1 credit = 1 USD), so no rate table is needed. provider.require_parameters
keeps requests off upstream providers that would ignore response_format.
"""
from __future__ import annotations

import time
from datetime import datetime

import requests

from schema import json_schema

from .base import (API_ERROR, AUTH, NETWORK, RATE_LIMIT, REFUSAL, RETRYABLE_STATUS, TIMEOUT,
                   TRUNCATED, Provider, ProviderResult, fail, parse_answer)

URL = "https://openrouter.ai/api/v1/chat/completions"
MAX_ATTEMPTS = 5


def _content_text(content) -> str | None:
    if content is None or isinstance(content, str):
        return content
    return "".join(part.get("text", "") for part in content if isinstance(part, dict))


class OpenRouterProvider(Provider):
    provider = "openrouter"
    mode = "schema"

    def _identify(self, image_b64: str, mime: str, prompt: str, started: datetime) -> ProviderResult:
        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{image_b64}"}},
                ],
            }],
            "response_format": {"type": "json_schema", "json_schema": {
                "name": "watch_identification", "strict": True, "schema": json_schema()}},
            "provider": {"require_parameters": True},
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "X-Title": "ChronoBay AI Bench"}

        resp, attempts = None, 0
        for attempts in range(1, MAX_ATTEMPTS + 1):
            try:
                resp = requests.post(URL, json=payload, headers=headers, timeout=self.timeout)
            except requests.Timeout as e:
                if attempts == MAX_ATTEMPTS:
                    return fail(TIMEOUT, str(e), attempts=attempts)
            except requests.RequestException as e:
                if attempts == MAX_ATTEMPTS:
                    return fail(NETWORK, str(e), attempts=attempts)
            else:
                if resp.status_code not in RETRYABLE_STATUS:
                    break
                if attempts == MAX_ATTEMPTS:
                    category = RATE_LIMIT if resp.status_code == 429 else API_ERROR
                    return fail(category, f"HTTP {resp.status_code}: {resp.text[:500]}", attempts=attempts)
            retry_after = resp.headers.get("retry-after") if resp is not None else None
            time.sleep(float(retry_after) if retry_after and retry_after.isdigit() else min(2 ** attempts, 30))

        if resp.status_code in (401, 403):
            return fail(AUTH, f"HTTP {resp.status_code}: {resp.text[:500]}", attempts=attempts)
        try:
            body = resp.json()
        except ValueError:
            return fail(API_ERROR, f"HTTP {resp.status_code}: non-JSON body {resp.text[:500]}", attempts=attempts)
        if resp.status_code != 200 or "error" in body:
            return fail(API_ERROR, f"HTTP {resp.status_code}: {body.get('error', body)}",
                        raw_response=body, attempts=attempts)

        usage = body.get("usage") or {}
        cost = usage.get("cost")
        result = ProviderResult(
            raw_response=body,
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
            cached_input_tokens=(usage.get("prompt_tokens_details") or {}).get("cached_tokens") or 0,
            cost_usd=float(cost) if cost is not None else None,
            cost_source="reported" if cost is not None else None,
            attempts=attempts,
            served_model=body.get("model"),
        )
        choice = (body.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        if message.get("refusal"):
            result.error, result.error_detail = REFUSAL, str(message["refusal"])
            return result
        result.raw_text = _content_text(message.get("content"))
        finish = choice.get("finish_reason")
        if finish == "length":
            result.error, result.error_detail = TRUNCATED, "finish_reason=length"
            return result
        if finish == "content_filter":
            result.error, result.error_detail = REFUSAL, "finish_reason=content_filter"
            return result
        result.parsed, result.error, result.error_detail = parse_answer(result.raw_text)
        return result
