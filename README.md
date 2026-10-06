# ChronoBay AI watch-identification benchmark

Can a vision model identify a watch from one photo well enough to auto-fill a
ChronoBay listing? This runs models against 100 labelled photos (10 per brand
ChronoBay seeds) and reports, per model: how often it gets the exact reference
number, what it cost, and how long it took.

## Setup (Windows)

```bash
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
copy config.example.py config.py
```

Put your API keys in `config.py` (it is gitignored), or set them as environment
variables. Pick the models to run in `MODELS` in the same file.

## Commands

```bash
.venv\Scripts\python.exe bench.py validate                         # check the dataset — spends nothing
.venv\Scripts\python.exe bench.py estimate --all                   # projected cost — no API calls
.venv\Scripts\python.exe bench.py run --models claude-opus-5-5 --limit 3   # smallest real spend
.venv\Scripts\python.exe bench.py run --all --limit 10             # 10 images, one per brand
.venv\Scripts\python.exe bench.py run --all                        # full sweep
.venv\Scripts\python.exe bench.py run --all --repeats 3            # 3 passes: mean and spread
.venv\Scripts\python.exe bench.py score results\raw\<run_id>       # re-score saved answers — $0
```

`run` validates the dataset first and refuses to start if anything is wrong,
then shows a cost projection and asks before spending (`--yes` skips the
question). `--limit N` picks images round-robin across brands; `--ids 3,17,42`
picks exact rows.

## Dataset

- `dataset/images/` — the photos (gitignored; sourced from the web).
- `dataset/ground_truth.csv` — the answer key. One row per image:
  `reference_number` is the scored answer; `also_accept` lists references a
  photo cannot tell apart from it (another size, the previous generation, the
  same watch on another strap), separated by `|`.
- Every row must be `verified=true` — checked against the brand's site or
  WatchBase. A wrong answer-key row silently turns a correct model answer into
  a recorded failure, which is why `validate` refuses unverified rows.

## What the numbers mean

- **Strict accuracy** — the answer is the exact reference. Notation is
  normalized first: case, spaces, `. - /` are ignored; Rolex's catalog form
  `M126610LN-0001` reads as `126610LN`; JLC's shop code `JLQ1368430` reads as
  `Q1368430`. `score --raw-match` turns all of that off.
- **Lenient accuracy** — strict, or a reference listed in `also_accept`, or the
  same watch on a different strap/bracelet (recognized from the reference
  itself for TAG Heuer, Breitling, Omega and Audemars Piguet).
- **Errors** (rate limits, refusals, invalid JSON, …) count as failures but are
  listed separately, so an error is never mistaken for a wrong identification.
- **Confidence ≥ 0.8** — how often the model is right when it says it is sure;
  the basis for "only auto-fill when the model is confident".
- **Cost** — OpenRouter reports the actual charge per call; everything else is
  tokens × the dated rates in `pricing.py`. A rate older than 30 days prints a
  warning; a model with no rate shows cost as unavailable, never $0.00.
- **Time** — wall-clock per call (mean, median, p95) plus the model's total.

Single runs carry unmeasured spread — these models are non-deterministic. Use
`--repeats` for a mean and range. Numbers from different sessions, or from a
different `PROMPT`, are not comparable: every run records the prompt's hash.

## Providers

| Provider | How | Answer format |
|---|---|---|
| Anthropic | `messages.create` + `output_config.format` | schema enforced by the API |
| OpenAI | `responses.create` + strict `json_schema` | schema enforced by the API |
| Gemini | `interactions.create` + JSON `response_format` | schema enforced by the API |
| OpenRouter | chat completions + strict `json_schema` | schema enforced by the API |
| DeepSeek | chat completions + `json_object` | **prompt mode**: schema in the prompt, validated here, one retry |

Notes:

- **DeepSeek** (`deepseek-flash`) caps each image at 1,024 tokens, far less
  detail than the others get, and its price doubles at peak hours (01–04 and
  06–10 UTC, weekdays). Reports footnote both.
- **OpenAI and Gemini direct** are implemented against the installed SDKs but
  not yet run with a real key. The default config reaches their models through
  OpenRouter instead.
- **Claude refusals** are recorded as errors. The API's automatic fallback to
  another model is deliberately not enabled: it would put another model's
  answer under Claude's name.

## Findings

### DeepSeek (`deepseek-flash`) — two full runs, 2026-09-30 and 2026-10-05

| | `2026-09-30_112454_full` | `2026-10-05_111103_full` |
|---|---:|---:|
| Output limit | 8,192 tokens | 16,000 tokens |
| Strict / lenient | 48 / 53 | 44 / 50 |
| Brand correct | 93 | 96 |
| Errors | 2 | 2 |
| Cost | $0.130 | $0.185 |
| Median / p95 time | 4.9s / 43.5s | 5.8s / 53.4s |

- **Output limit: raising it did not help, so it is back at 8,192.** DeepSeek
  reasons by default, and a few calls spend the whole output budget on
  reasoning and return no answer. The second run raised the provider's limit
  to the shared `MAX_OUTPUT_TOKENS` (16,000) to test whether that was holding
  the score down. It was not: two calls still ran out on both attempts, the
  score did not improve, and the run cost 42% more. `meta.json` records the
  shared setting (16,000) for both runs, not the provider's own limit — this
  table is the record of which run used which.
- **The first run's two `schema-parse` errors were truncations** (both
  attempts ended with `finish_reason=length` and no text). The `truncated`
  label was added to the provider after that run.
- **A single pass is not a stable number.** Only 52 of the 100 answers were
  the same in both runs: 34 photos right both times, 42 wrong both times, 24
  flipped. The 4-point gap between the runs is inside that spread. Use
  `--repeats`.
- **The 1,024-token image cap shows no effect.** In the first run 61 photos
  hit the cap and 39 went through under it: 30/61 strict (49%) against 18/39
  (46%). Opus and GPT-6.1 Sol show the same small difference between the two
  sets.
- **The misses are recall of the reference, not vision.** Counted from the
  saved answers (the harness does not score these fields): movement 96/100,
  case material 91–92, bracelet material 95–96. In the second run 46 of the
  56 misses are the right brand with the wrong reference — typically the
  previous generation's reference, the wrong case size, the wrong variant
  suffix, or a sibling model. Of the 42 photos wrong in both runs, Breitling
  has 7, Audemars Piguet, IWC and Jaeger-LeCoultre 6 each, TAG Heuer 5;
  Claude Opus 5.5 got 30 of the 42 right.
- **Its confidence is a usable filter.** Across both runs, answers with
  confidence ≥ 0.8 were strictly right 18 times out of 23; below 0.3, 7 out
  of 35. More than half its answers (115 of 196) carry confidence below 0.5.
- **More reasoning goes with wrong answers.** In the second run the 25 photos
  with the least reasoning scored 17/25, the 25 with the most scored 7/25.

### Dataset changes

- **2026-10-05 — row 12 photo replaced.** The distant wrist shot (678×452)
  was swapped for a 1024×1024 product photo. Every run up to and including
  `2026-10-05_111103_full` scored row 12 on the old photo, where no model
  matched the key. The old file is kept in `dataset/images/_replaced/`.

## Results

```
results/
  REPORT.md                 start here: latest result per model, by-brand table, links
  runs/<run_id>/            one folder per run
    summary.md              every model in the run, ranked, with caveats
    <model>.md              detailed report: every miss next to the expected answer
    <model>.json            the same, machine-readable
  runs/<run_id>_rescored_<date>/   output of `bench.py score`
  raw/<run_id>/             every raw API response + meta.json (gitignored)
```

A run over every image is a **full run** (`2026-09-30_112454_full`). A run over
part of them (`--limit`, `--ids`) is a **test run**
(`2026-09-30_112430_test-3img`): it checks that a model or setting works before
paying for the full run, and its accuracy is not comparable. Test runs say so
in the folder name, in every report title, and in their own section of
`REPORT.md`.

`REPORT.md` is rebuilt after every run and re-score. It shows each model's
latest full run, and falls back to a test run (marked "TEST RUN only") when a
model has no full run yet. Run folders are never overwritten. `score` re-reads
`raw/`, so fixing the answer key never costs a re-run.

## Google Vision web-detection test

`vision_test.py` is a separate experiment: it asks Google Cloud Vision's web
detection about each photo and checks whether the right reference number is in
the answer. It needs `GOOGLE_VISION_API_KEY` in `config.py`.

```bash
.venv\Scripts\python.exe vision_test.py run --limit 3                    # 3 images
.venv\Scripts\python.exe vision_test.py run                              # all images, as they are
.venv\Scripts\python.exe vision_test.py run --variant altered            # rotated, warped, cropped copies
.venv\Scripts\python.exe vision_test.py score results\vision\<run_id>    # re-score saved responses, $0
```

Web detection finds pages that already host the same image. The dataset photos
came from the web and a seller's own photo did not, so every number in the
report is split by whether Google found a copy of the photo. The `altered`
variant sends changed copies that Google should no longer recognise.

Results go to `results/vision/<run_id>/` (`report.md`, `report.json`, raw
`responses/`). The first 1,000 calls a month are free; after that $0.0035 each.
