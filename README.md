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

`REPORT.md` is rebuilt after every run and re-score. It prefers each model's
latest full-dataset run over a smaller smoke test. Run folders are never
overwritten. `score` re-reads `raw/`, so fixing the answer key never costs a
re-run.
