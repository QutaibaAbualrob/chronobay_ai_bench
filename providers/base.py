"""Provider interface: every adapter turns (image, prompt) into a ProviderResult."""
from __future__ import annotations

import json
import re
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime, timezone

from pydantic import ValidationError

from schema import WatchIdentification

# Error categories. Anything but None is a failed answer, reported by category
# so provider errors are never mistaken for wrong identifications.
RATE_LIMIT = "rate-limit"
AUTH = "auth"
API_ERROR = "api-error"
TIMEOUT = "timeout"
NETWORK = "network"
SCHEMA_PARSE = "schema-parse"
REFUSAL = "refusal"
EMPTY = "empty"
TRUNCATED = "truncated"
CONFIG = "config"

RETRYABLE_STATUS = {408, 409, 429, 500, 502, 503, 504, 529}


@dataclass
class ProviderResult:
    parsed: dict | None = None          # validated WatchIdentification, as a dict
    raw_text: str | None = None         # the model's text answer, verbatim
    raw_response: dict | None = None    # full response body, kept for audit and re-scoring
    input_tokens: int | None = None
    output_tokens: int | None = None    # includes thinking/reasoning tokens where billed as output
    cached_input_tokens: int = 0
    cost_usd: float | None = None
    cost_source: str | None = None      # "reported" (provider's own figure) | "rate-table" | None
    elapsed_s: float = 0.0
    started_at: str = ""
    attempts: int = 1
    error: str | None = None
    error_detail: str | None = None
    served_model: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def fail(category: str, detail: str, **kw) -> ProviderResult:
    return ProviderResult(error=category, error_detail=detail[:2000], **kw)


_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)


def parse_answer(text: str | None, allow_wrapping: bool = False) -> tuple[dict | None, str | None, str | None]:
    """Validate a text answer against the contract.

    Returns (parsed, error_category, detail). allow_wrapping (prompt mode only)
    tolerates code fences or prose around a single JSON object — formatting
    noise, not an identification mistake.
    """
    if text is None or not text.strip():
        return None, EMPTY, "no text in response"
    candidate = text.strip()
    if allow_wrapping:
        candidate = _FENCE.sub("", candidate).strip()
        start, end = candidate.find("{"), candidate.rfind("}")
        if start != -1 and end > start:
            candidate = candidate[start:end + 1]
    try:
        data = json.loads(candidate)
    except json.JSONDecodeError as e:
        return None, SCHEMA_PARSE, f"invalid JSON: {e}"
    try:
        return WatchIdentification.model_validate(data).model_dump(), None, None
    except ValidationError as e:
        return None, SCHEMA_PARSE, f"schema mismatch: {e}"


class Provider(ABC):
    provider: str = ""
    mode: str = "schema"   # "schema": enforced server-side | "prompt": schema in prompt, validated here

    def __init__(self, model: str, api_key: str, options: dict, settings: dict):
        self.model = model
        self.api_key = api_key
        self.options = options
        self.max_tokens = settings["max_output_tokens"]
        self.timeout = settings["timeout_s"]

    def identify(self, image_b64: str, mime: str, prompt: str) -> ProviderResult:
        started = datetime.now(timezone.utc)
        t0 = time.perf_counter()
        try:
            result = self._identify(image_b64, mime, prompt, started)
        except Exception as e:  # a bug or an unmapped SDK error must not kill the whole run
            result = fail(API_ERROR, f"{type(e).__name__}: {e}")
        result.elapsed_s = round(time.perf_counter() - t0, 3)
        result.started_at = started.isoformat()
        return result

    @abstractmethod
    def _identify(self, image_b64: str, mime: str, prompt: str, started: datetime) -> ProviderResult:
        ...
