# AGENTS.md

Onboarding for any agent working in this repo. Last updated 2026-10-06.

## What this is

ChronoBay is a marketplace for luxury watches. This repo is the evaluation workspace
for one planned feature: **AI auto-listing**. A seller uploads
photos of a watch, types nothing, and gets a pre-filled listing to confirm.

The repo holds a benchmark that measures how well vision models identify a watch from a
photo, the findings from that work, and the design for the feature.

The person you work with is Qutaiba. He reports the results to a supervisor, so anything
written here may be forwarded. Write for a reader who was not in the conversation.

## Objective

1. **Decide how auto-listing should work**, using measured evidence instead of estimates.
2. **Prove or disprove the design** in `AUTO_LISTING_SPEC.md` before anyone builds it.
3. **Keep the benchmark trustworthy**, because every decision rests on its numbers.

## Where things stand

- **Benchmark:** seven models have full 100-photo runs. The best gets the exact reference
  79 times in 100 (Claude Opus 5.5); the best value gets 72 (Claude Sonnet 5.5, no thinking).
  The strong models always get the brand right. No model reaches 90% alone.
- **Main lesson:** models recognise the watch but cannot reliably recall its exact reference.
  A catalog has to confirm the reference.
- **A format guide in the prompt does not fix that.** DeepSeek Flash given `REFERENCE_FORMATS.md`
  scored 39 on the 80 photos the guide does not give away, against 37 and 35 without it. Almost
  every miss is the right watch in the right format with the wrong digits, and those digits
  follow no rule. Tested on DeepSeek only, one run.
- **Design:** draft 2 is written. The model reads the photos and proposes up to three
  references; WatchCharts confirms which exist; code decides between auto-fill, a
  tap-to-choose list, or leaving the reference empty.
- **Catalog source:** ChronoBay's backend already integrates WatchCharts. A live test showed
  the key works with 1,000 credits a day, which looks like the Level 1 plan. Specs need Level 2.
- **Not yet proven:** that the model plus a WatchCharts check beats the model alone, and how
  any of it performs on real seller photos.

## Read these first

| File | What it is |
|---|---|
| `FINDINGS.md` | Every finding so far, each marked measured, read, reported or inferred. Start here. |
| `AUTO_LISTING_SPEC.md` | The current design (draft 2), with decisions, open questions and tests. |
| `results/REPORT.md` | Latest benchmark result per model. Rebuilt after every run. |
| `REFERENCE_FORMATS.md` | How 19 brands build their reference numbers, how variants are written, and which rules are confirmed. |
| `results/DETAIL_STUDY.md` | How reliably models fill brand, model line and attributes on their own. Rebuilt by `detail_study.py`. |
| `results/GUIDE_STUDY.md` | Whether attaching `REFERENCE_FORMATS.md` to the prompt helps (DeepSeek Flash: no clear gain). Rebuilt by `guide_study.py`. |
| `README.md` | How to run the benchmark, what the scores mean, and run-by-run notes. |
| `PLAN.md` | The original benchmark plan. Historical; parts are out of date. |

## Repo map

| Path | Purpose |
|---|---|
| `bench.py` | Benchmark commands: `validate`, `estimate`, `run`, `score`. |
| `providers/` | One adapter per API: Anthropic, OpenAI, Gemini, OpenRouter, DeepSeek. |
| `schema.py` | The JSON answer every model must return. Values mirror ChronoBay's seeders. |
| `scoring.py` | Exact and look-alike matching of reference numbers. |
| `report.py` | Per-run reports and `results/REPORT.md`. |
| `pricing.py` | Dated price table used to compute cost. |
| `vision_test.py` | Google Cloud Vision web-detection test. Built, never run against the API. |
| `detail_study.py` | Field-by-field study from saved answers. No API calls. |
| `guide_study.py` | Compares plain-prompt runs with runs given the guide (the `guide` model option). No API calls. |
| `reference_format_check.py` | Tests the rules in `REFERENCE_FORMATS.md` against the answer key and 90 outside references. No API calls. |
| `dataset/ground_truth.csv` | The answer key: 100 rows, 10 brands. |
| `dataset/images/` | The photos. Not in git; they came from the web. |
| `results/runs/`, `results/raw/` | Reports and raw API responses per run. |
| `reports/` | The PDF sent to the supervisor on 2026-09-30. It has known errors (see Traps). |
| `config.py` | API keys and the model list. Not in git. |

**Related repo:** the ChronoBay app is at `D:\orapex\chronobay` (NestJS and Prisma backend
in `backend/`). Treat it as read-only unless Qutaiba asks for a change there.

## Running things

Windows, Python 3.14, virtual environment in `.venv`.

```bash
.venv\Scripts\python.exe bench.py validate
.venv\Scripts\python.exe bench.py run --models claude-sonnet-5-5-nothink --limit 3
.venv\Scripts\python.exe bench.py run --models claude-opus-5-5
.venv\Scripts\python.exe bench.py score results\raw\<run_id>
.venv\Scripts\python.exe vision_test.py run --limit 3
.venv\Scripts\python.exe detail_study.py
.venv\Scripts\python.exe guide_study.py
.venv\Scripts\python.exe reference_format_check.py
```

The last three read saved answers or the answer key and make no API calls.

- A run over all 100 photos is a **full run**; anything smaller is a **test run** and is
  labelled as one in folder names and reports.
- `score` re-reads saved responses, so fixing the answer key never costs a re-run.
- Run folders are never overwritten.
- A model entry in `config.py` can carry `"guide": "<file>"`. That file's text is added after
  the prompt for that model only. Give such an entry its own name (`deepseek-flash-guide`):
  its score is not comparable with the plain prompt.

## Rules for working here

**Keys and secrets**

- Keys live only in `config.py` or environment variables. Never ask for a key in chat,
  never print `config.py`, and never write a key into a file, report or commit.
- If a key appears in chat, do not use it; say it should be revoked.
- A live WatchCharts key is hardcoded in the app repo. Refer to it by file and line only.

**Spending**

- State the model, setting and estimated cost in one line before any paid call.
- Run exactly what was asked. Do not add runs or raise a model's effort unasked.
- When the model is not named, ask, or pick the cheapest sensible option and say so.
- WatchCharts calls spend shared daily credits. Get a go-ahead before making them.

**Facts**

- Check watch references online before stating anything about them. A claim made from
  memory already produced an error in the PDF report.
- Mark what is unverified. Do not present an estimate as a measurement.
- Record new findings in `FINDINGS.md` with how they were checked.

**The repo**

- Other sessions and Qutaiba also change this repo. Check `git log` and file dates before
  assuming it is as you left it.
- Commit or push only when asked.
- Report outcomes plainly, including failures and anything skipped.

## Decisions already made

Taken by Qutaiba on 2026-10-06. Do not reopen them without a reason.

- Photos only. Nothing may depend on typed input.
- Tapping to confirm, or to choose between options, is accepted.
- When the reference cannot be confirmed, only the reference is left empty. The rest is
  filled from the photo.
- No aftermarket-strap detection.
- Authentication of watches is out of scope.
- The cost budget is deferred.
- Dial colour, gold colour and two-tone are to be added to listings.
- WatchCharts is proposed for the upcoming build plan.

## Open work, cheapest first

| # | Task | Cost | Needs |
|---|---|---|---|
| 1 | One `/watch/specs` call to learn whether Level 2 is available | 10 credits | Go-ahead |
| 2 | Replay the 100 answer-key references through WatchCharts search | 100 credits | Go-ahead |
| 3 | Replay each model's saved answers through WatchCharts search | Up to 100 credits per model | Go-ahead |
| 4 | Google Vision test on the 100 photos, original and altered | Free tier | `GOOGLE_VISION_API_KEY` in `config.py` |
| 5 | Re-run row 12 on every model | A few cents | Go-ahead |
| 6 | Recheck answer-key rows 76, 66 and 98 online | None | |
| 7 | Correct and rebuild the PDF report, adding the newer models | None | Go-ahead |
| 8 | Test the pipeline on 30 to 50 phone photos of real watches | $1 to $3 per model | The photos |
| 9 | Only if the guide question is still open: repeat the guided run, or try it on a strong model | $0.20 per DeepSeek run; $1 to $3 on a strong model | Go-ahead |

Questions only Qutaiba or his team can answer: which WatchCharts plan and licence ChronoBay
holds, and where case size should come from.

## Traps

- **Row 12 is stale.** Its photo was replaced on 2026-10-05. Every saved answer for that
  row was made on the old photo.
- **One pass is not a stable number.** DeepSeek's two full runs agreed on only 52 of 100
  answers. Treat gaps of a few points as noise unless `--repeats` was used.
- **The look-alike list is one agent's judgment.** `also_accept` (27 rows) was written by
  Claude with no source links and no independent review. Quote the exact score first.
- **The PDF report has errors.** It covers four models, mislabels watch 46 as an "invented
  number", and calls the answer key hand-verified. Its builder script is not in this repo.
- **`PLAN.md` is out of date** on several points, including its claim that `Product` has no
  `referenceNumber`.
- **A run folder is misnamed.** The Haiku run is at `results/runs/2026-10-1_125653_full`.
- **WatchCharts `confidence` is about price data**, not about how well a reference matched.
- **WatchCharts notation differs from the brands'.** It returned `126610` for `126610LN`.
- **The guide prints 20 answer-key references.** A model given `REFERENCE_FORMATS.md` can copy them.
  Score such runs on the other 80 rows; `guide_study.py` does.
- **The dataset photos came from the web.** Any test of reverse image search looks better on
  them than it will on a seller's own photo.
- **The current backend auto-fill cuts references.** Its cleaning pattern truncates every
  Omega, Patek, Audemars Piguet, TAG Heuer and Vacheron reference. See `FINDINGS.md`, section 6.2.
