# ChronoBay AI Watch-Identification Benchmark

## Context

ChronoBay needs to know whether a vision model can identify a watch from a photo
well enough to auto-fill a listing. Right now that is an open question with no
number attached to it — nobody knows if this feature is viable, or which model to
buy.

This builds a local, repeatable benchmark that answers it: 100 watch images across
the 10 brands ChronoBay already seeds, a fixed JSON contract every model must
answer in, strict exact-match scoring on the reference number, and a report giving
success rate, the specific failures, dollar cost, and wall-clock time per model.

Three facts found during research that shape the design:

- **No public watch-reference dataset exists.** The dataset is the real work and
  must be built locally. Qutaiba supplies the images; this plan delivers the
  scaffold and a validator that refuses to run on an incomplete dataset.
- **ChronoBay already seeds exactly 10 brands** (`backend/prisma/seeders/brands.seeder.ts`)
  plus controlled vocabularies for movement, case material, and bracelet material.
  The benchmark's JSON schema mirrors them, so the score answers the *product*
  question, not an abstract one.
- **Provider APIs moved since mid-2026.** OpenAI is now `client.responses.parse(text_format=...)`;
  Gemini is now `client.interactions.create(response_format=...)`, not
  `generate_content`. DeepSeek's vision lives on one experimental model and supports
  only `json_object`, not `json_schema`. Anthropic Sonnet 5 pricing changed on
  2026-09-01 ($2/$10 → $3/$15). Pricing is therefore **never hardcoded in code** — it
  lives in a dated config file.

Location: `/home/quta/orapex/chronobay_ai_bench/` (directory already exists, empty).

**Out of scope:** adding a `referenceNumber` column to `Product`. Worth noting that
`backend/prisma/schema/catalog.prisma:3` has no such field, so the value this
benchmark measures has nowhere to land in the API yet. Separate task.

---

## Decisions taken

| Decision | Choice | Why |
|---|---|---|
| Providers | Anthropic, OpenAI, Gemini, OpenRouter, **DeepSeek** | As chosen |
| Scoring | Strict exact-match on `reference_number` | As chosen |
| Dataset | **Manifest pre-filled with 100 rows; Qutaiba sources one image per row and verifies each reference** | Saves choosing 100 watches; the verification step cannot be skipped (see below) |
| Cost source | OpenRouter reports real cost; others = tokens × dated rate table | Rates go stale (Sonnet 5 just changed) |
| Raw responses | Always saved | Re-score offline later without re-spending |

Two substitutions from the literal request, both flagged:

1. **Filename format.** `modelName_day/month date_min:hours` cannot be a filename —
   `/` is a path separator and `:` breaks on non-Linux. Using
   `claude-opus-5_2026-09-09_1432.md` instead: same information, sorts
   chronologically, safe everywhere.
2. **Match normalization.** Exact-match compares after uppercasing and stripping
   spaces/dots/hyphens, so `126610LN`, `126610 ln` and `126-610-LN` all count as
   the same reference. `--raw-match` disables this for byte-identical comparison.

---

## Layout

```
chronobay_ai_bench/
├── README.md                  # how to run, how to label, what the numbers mean
├── requirements.txt
├── .gitignore                 # config.py, results/raw/, dataset/images/
├── config.py                  # ← API KEYS + models edited HERE (gitignored)
├── config.example.py          # tracked template
├── pricing.py                 # per-model $/1M rates, each with last_verified date
├── schema.py                  # the unified JSON contract (Pydantic)
├── bench.py                   # CLI entry point: run | score | validate | estimate
├── scoring.py                 # strict exact-match + normalization
├── report.py                  # console + markdown + json writers
├── providers/
│   ├── base.py                # Provider ABC → ProviderResult
│   ├── anthropic_provider.py
│   ├── openai_provider.py
│   ├── gemini_provider.py
│   ├── openrouter_provider.py
│   └── deepseek_provider.py
├── dataset/
│   ├── images/                # ← drop the 100 images here
│   └── ground_truth.csv       # ← fill this in
└── results/
    ├── raw/<run_id>/          # every raw response (gitignored, re-scorable)
    └── claude-opus-5_2026-09-09_1432.md
```

This split matches AGENTS.md §21: narrative reports tracked, raw output gitignored,
and every output path is a new file — never an overwrite.

---

## The unified output contract (`schema.py`)

The vocabularies are lifted verbatim from the ChronoBay seeders, so the benchmark
scores against the exact strings the database stores:

```python
# Extracted from backend/prisma/seeders/*.seeder.ts — do not hand-edit.
BRANDS = ["Rolex", "Omega", "Patek Philippe", "Audemars Piguet", "Tag Heuer",
          "Breitling", "Cartier", "IWC", "Jaeger-LeCoultre", "Vacheron Constantin"]
MOVEMENTS = ["automatic", "manual", "quartz", "solar", "hybrid"]
CASE_MATERIALS = ["stainless-steel", "gold", "platinum", "titanium", "ceramic", "bronze"]
BRACELET_MATERIALS = ["leather", "metal", "rubber", "fabric", "nylon"]
```

The seeders store `key`/`label` pairs (`movement-types.seeder.ts:12-18`); `key` is
what lands in the DB, so `key` is what gets scored. A model answering `"Automatic"`
is normalized to `automatic` before comparison.

Every provider is forced into this one shape, so results are comparable:

```python
class WatchIdentification(BaseModel):
    brand: Literal["Rolex", "Omega", "Patek Philippe", "Audemars Piguet",
                   "Tag Heuer", "Breitling", "Cartier", "IWC",
                   "Jaeger-LeCoultre", "Vacheron Constantin", "unknown"]
    model_family: str          # "Submariner Date"
    reference_number: str      # "126610LN"  ← the scored field
    movement: Literal["automatic","manual","quartz","solar","hybrid","unknown"]
    case_material: Literal["stainless-steel","gold","platinum","titanium",
                           "ceramic","bronze","unknown"]
    bracelet_material: Literal["leather","metal","rubber","fabric","nylon","unknown"]
    confidence: float          # 0.0–1.0, model's own estimate
```

Enums are copied verbatim from the ChronoBay seeders
(`brands.seeder.ts`, `movement-types.seeder.ts`, `case-materials.seeder.ts`,
`bracelet-materials.seeder.ts`). `"unknown"` is always allowed — a model that
declines to guess must be able to say so, otherwise the schema forces hallucination.

Only `reference_number` is scored. The other fields are captured because they cost
nothing extra and make a later re-score under tiered rules possible.

---

## Provider adapters

Each implements `identify(image_bytes, mime) -> ProviderResult`, carrying the parsed
JSON, raw text, input/output tokens, reported cost (or `None`), elapsed seconds, and
any error. Verified call shapes:

- **Anthropic** — `client.messages.parse(model=..., output_format=WatchIdentification)`
  with an `{"type":"image","source":{"type":"base64",...}}` content block. Read
  `response.usage.input_tokens` / `.output_tokens`.
- **OpenAI** — `client.responses.parse(model=..., input=[...], text_format=WatchIdentification)`,
  result at `response.output_parsed`, usage at `usage.input_tokens` / `.output_tokens`.
- **Gemini** — `client.interactions.create(model=..., input=[{"type":"text",...},
  {"type":"image","data":<b64>,"mime_type":...}], response_format={"type":"text",
  "mime_type":"application/json","schema": WatchIdentification.model_json_schema()})`.
- **OpenRouter** — POST `https://openrouter.ai/api/v1/chat/completions` with
  `response_format={"type":"json_schema","json_schema":{"name":...,"strict":true,
  "schema":...}}`. Usage accounting is automatic: read the real dollar figure from
  `usage.cost`.
- **DeepSeek** — OpenAI-compatible, `base_url="https://api.deepseek.com"`. Vision is
  available on **`deepseek-v4-flash-vision-exp` only** (`-flash` and `-pro` are
  text-only; `deepseek-chat` was discontinued 2026-07-24). Images go in as base64
  data URLs.

**Because these APIs moved recently, the implementation verifies each call against
the installed SDK in the venv (`.venv/lib/python3.*/site-packages/<pkg>/`) before
writing it** — method names and parameters come from the package on disk, not recall.

### Two output-enforcement modes

DeepSeek supports only `response_format={"type":"json_object"}` — **not**
`json_schema`. So the harness carries two strategies, and every provider declares
which one it used:

| Mode | Providers | How |
|---|---|---|
| `schema` | Anthropic, OpenAI, Gemini, OpenRouter | Schema enforced server-side; malformed JSON is near-impossible |
| `prompt` | DeepSeek | Schema embedded in the prompt, `json_object` set, response parsed and validated against the Pydantic model client-side |

`prompt` mode gets one automatic retry on unparseable or empty output (DeepSeek's
docs warn it "may occasionally return empty content"). A second failure is recorded
as a `schema-parse` error, never as a wrong answer.

**The report prints the mode next to each model**, because it is a confound: a model
that cannot emit valid JSON has not failed at identifying watches, and the two must
not be read as the same number.

### DeepSeek's 384-token image cap

DeepSeek tokenizes each image to **at most 384 tokens** — far less than the other
providers spend per image. Reading a small engraved reference number is precisely the
task that cap penalises. Expect a low score for a structural reason rather than a
reasoning one; the report footnotes this next to DeepSeek's row so the result is not
misread as a like-for-like comparison.

A single shared prompt string lives in `config.py` and is sent identically to every
model. Any change to it invalidates cross-run comparability, which the README states.

---

## Dataset scaffold

`dataset/ground_truth.csv` ships **pre-filled with 100 rows** — 10 per brand, chosen
as well-known, visually distinct references. Qutaiba sources one image per row and
confirms the reference.

```csv
id,image_file,brand,model_family,reference_number,movement,case_material,bracelet_material,source_url,verified
1,rolex_submariner_01.jpg,Rolex,Submariner Date,126610LN,automatic,stainless-steel,metal,,false
2,rolex_daytona_01.jpg,Rolex,Cosmograph Daytona,126500LN,automatic,stainless-steel,metal,,false
3,omega_speedmaster_01.jpg,Omega,Speedmaster Moonwatch,310.30.42.50.01.002,manual,stainless-steel,metal,,false
5,patek_nautilus_01.jpg,Patek Philippe,Nautilus,5711/1A-010,automatic,stainless-steel,metal,,false
7,cartier_santos_01.jpg,Cartier,Santos de Cartier,WSSA0029,automatic,stainless-steel,metal,,false
8,iwc_portugieser_01.jpg,IWC,Portugieser Chronograph,IW371617,automatic,stainless-steel,leather,,false
```

**The `verified` column is the load-bearing part.** The pre-filled references are
written from model recall, and a wrong ground-truth row silently converts a *correct*
model answer into a recorded failure — the worst possible defect in a benchmark,
because it is invisible in the output. So:

- `source_url` records where the image came from.
- `verified` flips to `true` only after the reference is confirmed against the
  brand's own site or WatchBase.
- **`bench.py validate` refuses to run while any row is `verified=false`.**

The pre-filled list saves the work of *choosing* 100 watches. It does not save the
checking, and the tool will not let it be skipped.

`bench.py validate` is a hard gate — the runner refuses to spend money unless:
every row is `verified=true`; every row has a `reference_number` and a `source_url`;
every `image_file` exists, opens, and is a supported type; every enum value is in the
ChronoBay vocabulary; ids are unique; and no duplicate reference numbers hide behind
different images (flagged, not fatal).

It prints a per-brand count so the 10×10 balance is visible before a run.

---

## Scoring, cost, timing

**Scoring** (`scoring.py`) — normalize both sides (uppercase, strip ` .-/`), compare
for equality. A provider error or unparseable response is a failure, recorded with
its reason so errors are never silently counted as wrong answers.

**Cost** — OpenRouter's `usage.cost` is authoritative and used directly. For the
other three, `input_tokens × rate_in + output_tokens × rate_out` using
`pricing.py`, where each entry carries `last_verified` and a source URL. If an entry
is older than 30 days the report prints a staleness warning next to the dollar
figure rather than quietly reporting a wrong number. Unknown model → cost reported
as `unavailable`, never as `$0.00`.

DeepSeek's pricing page did not return figures during research, so its rates are
filled in from `api-docs.deepseek.com/quick_start/pricing` at implementation time and
dated like the rest. Note that DeepSeek bills each image at up to 384 tokens at
V4-Flash rates, so image cost is bounded and small.

**Timing** — `time.perf_counter()` around each call. Report total wall-clock, plus
mean / median / p95 per model, since a single mean hides a slow tail.

---

## The report

Written to `results/<model>_<YYYY-MM-DD>_<HHMM>.md` and a machine-readable `.json`
alongside. A combined `comparison_<timestamp>.md` ranks all models tested in the run.

```
claude-opus-5   —   2026-09-09 14:32   [schema mode]
════════════════════════════════════════════
Accuracy   41/100   (41.0%)
Cost       $0.8420   (rates verified 2026-09-09)
Time       184.2s total | mean 1.84s | median 1.61s | p95 3.90s
Errors     2 (1 rate-limit, 1 schema-parse)

FAILED (59)
 #3   omega_speedmaster_01.jpg   expected 310.30.42.50.01.002  got 311.30.42.30.01.005
 #24  rolex_submariner_02.jpg    expected 126610LN             got 116610LN
 #37  cartier_santos_04.jpg      expected WSSA0029             got —  (ERROR: schema-parse)
```

The combined comparison carries the confounds inline, so the table cannot be read
naively:

```
MODEL                          ACC     COST      MEAN    MODE
claude-opus-5                  41.0%   $0.8420   1.84s   schema
gpt-6-astra                    33.0%   $0.6100   2.10s   schema
gemini-3.8-flash               29.0%   $0.0910   0.94s   schema
deepseek-v4-flash-vision-exp    8.0%   $0.0130   1.21s   prompt ⚠

⚠ deepseek-v4-flash-vision-exp caps images at 384 tokens — far below the other
  providers. Its score reflects that limit as much as model capability, and 6 of
  its 92 failures were invalid JSON rather than wrong answers.
```

---

## CLI

```bash
bench.py validate                       # gate the dataset, spends nothing
bench.py estimate --all                 # projected $ cost before committing
bench.py run --models claude-opus-5,gpt-6-astra
bench.py run --all --limit 10           # cheap smoke test on 10 images
bench.py run --all --repeats 3          # 3 passes, reports mean ± spread
bench.py score results/raw/<run_id>     # re-score saved responses, $0
```

`--limit` and `estimate` exist because 100 images × 4 providers is real money; the
default path should never be "spend it and find out."

`--repeats` matters for honesty: these models are non-deterministic, so a single
100-image pass is one sample with unknown variance. Default is 1 to keep cost down;
the README states plainly that a single run's number carries unmeasured spread, and
that comparing a number to one from an earlier session is not valid (AGENTS.md §17).

Concurrency is a bounded thread pool (default 4, `--concurrency`) with exponential
backoff on 429/5xx, so a full sweep is minutes rather than an hour.

---

## Files to create

**Step 0, before any code:** write this plan verbatim to
`/home/quta/orapex/chronobay_ai_bench/PLAN.md`, so the work survives this session and
can be picked up cold from inside the bench directory itself. Everything below
follows from it.

All new, under `/home/quta/orapex/chronobay_ai_bench/`. Nothing in `backend/`,
`mobile/`, or `frontend/` is touched. Values are *read* from
`backend/prisma/seeders/*.seeder.ts` to build the enums; those files are not modified.

---

## Verification

1. `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt` — Arch marks
   the system Python `EXTERNALLY-MANAGED`, so a venv is required, not optional.
   Confirm each SDK has a Python 3.14 wheel; if one does not, report it rather than
   silently dropping that provider.
2. `bench.py validate` against a deliberately broken CSV (missing ref, missing image,
   bad enum, `verified=false`) — must fail with a specific message for each, and
   spend nothing.
3. `bench.py estimate --all` — prints a dollar projection with no API calls made.
4. `bench.py run --models claude-opus-5 --limit 3` — smallest real spend. Confirm a
   result file appears with the right name, non-zero cost, non-zero timing, and that
   `results/raw/` holds three response bodies.
5. `bench.py score results/raw/<that run>` — reproduces the same accuracy from disk
   with zero further spend. This proves re-scoring works before the full sweep.
6. `bench.py run --models deepseek-v4-flash-vision-exp --limit 3` — exercises the
   `prompt` enforcement path specifically. Confirm the JSON parses, that the retry
   fires on an empty response, and that a second failure lands as `schema-parse`
   rather than as a wrong answer.
7. Force an error (bad API key on one provider) and confirm it is reported as an
   error, not silently scored as a wrong answer.
8. Only then, the full `bench.py run --all`.

Steps 2–7 cost cents at most. The full sweep is the last thing that happens.
