"""The unified output contract every model must answer in.

Vocabularies are copied from the ChronoBay seeders
(backend/prisma/seeders/brands.seeder.ts, movement-types.seeder.ts,
case-materials.seeder.ts, bracelet-materials.seeder.ts). The seeders store
key/label pairs; the key is what lands in the DB, so the key is what we use.
"""
from __future__ import annotations

import copy
from typing import Literal

from pydantic import BaseModel, ConfigDict

# Extracted from backend/prisma/seeders/*.seeder.ts — do not hand-edit.
BRANDS = ["Rolex", "Omega", "Patek Philippe", "Audemars Piguet", "Tag Heuer",
          "Breitling", "Cartier", "IWC", "Jaeger-LeCoultre", "Vacheron Constantin"]
MOVEMENTS = ["automatic", "manual", "quartz", "solar", "hybrid"]
CASE_MATERIALS = ["stainless-steel", "gold", "platinum", "titanium", "ceramic", "bronze"]
BRACELET_MATERIALS = ["leather", "metal", "rubber", "fabric", "nylon"]

UNKNOWN = "unknown"


class WatchIdentification(BaseModel):
    """"unknown" is always allowed — without it the schema forces a guess."""

    model_config = ConfigDict(extra="forbid")

    brand: Literal["Rolex", "Omega", "Patek Philippe", "Audemars Piguet", "Tag Heuer",
                   "Breitling", "Cartier", "IWC", "Jaeger-LeCoultre", "Vacheron Constantin",
                   "unknown"]
    model_family: str
    reference_number: str  # the scored field
    movement: Literal["automatic", "manual", "quartz", "solar", "hybrid", "unknown"]
    case_material: Literal["stainless-steel", "gold", "platinum", "titanium", "ceramic",
                           "bronze", "unknown"]
    bracelet_material: Literal["leather", "metal", "rubber", "fabric", "nylon", "unknown"]
    confidence: float  # model's own 0.0–1.0 estimate that reference_number is exactly right


def _strip_titles(node):
    if isinstance(node, dict):
        return {k: _strip_titles(v) for k, v in node.items() if k != "title"}
    if isinstance(node, list):
        return [_strip_titles(v) for v in node]
    return node


def json_schema() -> dict:
    """Strict JSON schema shared by every schema-mode provider.

    Pydantic emits enums for the Literals, marks every field required, and
    extra="forbid" adds additionalProperties: false — what strict modes need.
    """
    return _strip_titles(WatchIdentification.model_json_schema())


def json_schema_without_additional_properties() -> dict:
    schema = copy.deepcopy(json_schema())
    schema.pop("additionalProperties", None)
    return schema


# Appended to the shared prompt for providers that can only do json_object mode.
PROMPT_MODE_SUFFIX = """
Reply with ONLY a JSON object — no prose, no code fences — with exactly these keys:
{"brand": "...", "model_family": "...", "reference_number": "...", "movement": "...", "case_material": "...", "bracelet_material": "...", "confidence": 0.0}
"""
