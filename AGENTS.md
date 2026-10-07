# AGENTS.md

Onboarding for any agent working in this repo. Last updated 2026-10-07.

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
- **Search can supply the right reference.** Stage 0 of Serper idea 1 replayed saved answers
  through web search with no model call. The right reference is the model's own answer or among
  the search candidates for Opus 91 of 99 photos (own answer alone 79), Sonnet 92 (72), Sol 87
  (70), DeepSeek 72 (44). This is a ceiling: the list has about 11 candidates and nothing has
  picked from it yet. See `results/SEARCH_STUDY.md`.
- **A second look improves the list, not the first answer.** Stage 1 ran the whole flow with
  Sonnet (thinking off): describe, search, choose. On the 91 photos that finished, the first
  choice is right 61 times with the pipeline and 61 without it. The right reference is among
  three options 82 times, against 72 for the model's own three. No signal reaches the 95% mark
  proposed for auto-fill. See `results/PIPELINE_STUDY.md`.
- **The Sonnet run is incomplete and was left that way.** The Anthropic account ran out of
  credit on 2026-10-06 after 91 of 100 choosing calls (rows 92 to 100 are missing). Qutaiba
  chose to run DeepSeek instead of finishing it. `pipeline_study.py run --resume
  results\pipeline\2026-10-06_134921_full --yes` would finish it for about $0.10.
- **DeepSeek through the same flow is below Sonnet without it.** DeepSeek Flash, all 100 photos:
  first choice 55 before and 57 after, right reference among three options 66 before and 72
  after. On the 91 photos both runs share, DeepSeek's three options hold the right reference
  63 times; Sonnet's own three, with no search, 72. DeepSeek costs $0.005 a photo against
  $0.022, takes 27 seconds against 6, and its second call gave no answer on 11 photos.
- **A cheap model that searches for itself does not catch Sonnet either.** GPT-6 Luna with
  OpenAI's web search: first reference right 61 of 90 photos against 46 without search, at the
  price of Sonnet's whole pipeline and four times the wait. See idea 5 below.
- **Next up:** nothing is running. Two runs are unfinished for lack of credit (Sonnet pipeline,
  Luna web search). The open choices are a stronger model through a flow, a second pass to
  measure spread, and real seller photos (see Open work).

## Candidate solutions not yet tested

Four ways to use the Serper search API to tell the model which references exist. Detail,
prices and a four-photo probe are in `FINDINGS.md`, section 4.

1. **Find candidates by search.** Chosen as the next thing to build and test, and revised the
   same day. The model names the brand, the model line and its best guesses; code searches
   WatchBase and the open web by line and by the model part of the guess; code ranks what comes
   back against what the model saw; the result is a list of at most three for the seller to
   confirm. Stage 0 is done and passed its stop rule. Stage 1 is built and has run on 91 of
   100 photos: the list of three got better, the first choice did not. The reasons, the design
   and both results are in `FINDINGS.md`, section 4.
2. **Check the model's own candidates.** Search each proposed reference and compare the page
   title with what the model saw in the photo.
3. **Google Lens on the seller's photo**, through Serper's Lens endpoint. Needs a public image URL.
4. **Catch new releases.** Search knows watches newer than the models do. Follows from 1 and 2.
5. **Let the model search for itself.** OpenAI's built-in web search on GPT-6 Luna: one call
   takes the photo, searches and answers. Proposed by Qutaiba on 2026-10-06. A ten-photo run
   to measure the cost gave 9 of 10 first references right at $0.018 a photo (1.6 searches a
   photo at $0.01 each). With search off, Luna got 55 of all 100 right at $0.0007 a photo.
   The full run with search, asking always for three references, reached 90 of 100 photos
   before the OpenAI account ran out of credit: first reference right 61 of 90 against 46
   without search, right one within three 70 against 58, at $0.022 a photo and 27 seconds. On
   85 shared photos that is still below Sonnet with no search (56 against 60). See
   `FINDINGS.md`, section 4, "Idea 5", and `results/WEBSEARCH_STUDY.md`.

WatchBase data read through search is not licensed (see `FINDINGS.md`, section 4). These are
tests of whether the approach works, not a decision to ship it.

## Read these first

| File | What it is |
|---|---|
| `FINDINGS.md` | Every finding so far, each marked measured, read, reported or inferred. Start here. |
| `AUTO_LISTING_SPEC.md` | The current design (draft 2), with decisions, open questions and tests. |
| `results/REPORT.md` | Latest benchmark result per model. Rebuilt after every run. |
| `REFERENCE_FORMATS.md` | How 19 brands build their reference numbers, how variants are written, and which rules are confirmed. |
| `results/DETAIL_STUDY.md` | How reliably models fill brand, model line and attributes on their own. Rebuilt by `detail_study.py`. |
| `results/GUIDE_STUDY.md` | Whether attaching `REFERENCE_FORMATS.md` to the prompt helps (DeepSeek Flash: no clear gain). Rebuilt by `guide_study.py`. |
| `results/SEARCH_STUDY.md` | Whether a web search can supply the right reference as a candidate (stage 0 of Serper idea 1). Rebuilt by `search_study.py report`. |
| `results/PIPELINE_STUDY.md` | The whole flow on the photos: describe, search, choose (stage 1 of Serper idea 1). Rebuilt by `pipeline_study.py report`. |
| `results/WEBSEARCH_STUDY.md` | An OpenAI model that searches the web itself, with search on and off (idea 5). Rebuilt by `websearch_study.py report`. |
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
| `search_study.py` | Replays saved answers through Serper searches and counts how often the right reference comes back. `plan` and `report` are free; `run` spends Serper credits, one per new search. |
| `results/serper/` | Saved search responses. Not in git: third-party content. Without it `search_study.py report` has nothing to read. |
| `pipeline_study.py` | Runs the flow per photo: a describing call, three Serper searches, a ranking in code, a choosing call. `run` costs about $0.022 a photo on Sonnet plus Serper credits and can be continued with `--resume`; `report` is free and rebuilds every run's report and the comparison. Anthropic and DeepSeek models. |
| `websearch_study.py` | One call per photo to an OpenAI model that searches the web itself (idea 5). `run` pays OpenAI's search fee, $0.01 a search, on every run; `report` is free. |
| `results/websearch/<run_id>/` | Saved answers and the report of each such run. `results/WEBSEARCH_STUDY.md` puts the runs side by side. |
| `results/pipeline/<run_id>/` | Saved answers of both calls and the run's report. Its `prompts/` folder is not in git: the prompts quote search results. |
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
.venv\Scripts\python.exe search_study.py report
.venv\Scripts\python.exe pipeline_study.py report
.venv\Scripts\python.exe websearch_study.py report
.venv\Scripts\python.exe reference_format_check.py
```

The last six read saved answers, saved searches or the answer key and make no API calls.

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
| 10 | Finish the Sonnet pipeline run: nine choosing calls are missing (`pipeline_study.py run --resume`) | About $0.10 | Credit on the Anthropic account. Set aside by Qutaiba on 2026-10-06 |
| 10b | Repeat the Sonnet choosing step on all 100 photos with the corrected candidate order | About $1.10 | Go-ahead |
| 10c | The pipeline on Opus, or a second pass on Sonnet, to see whether the result holds | About $5 on Opus (estimate), $2.20 on Sonnet | Go-ahead |
| 11 | Serper ideas 2 and 3 | About 300 free credits each | `SERPER_API_KEY`; idea 3 also needs public image URLs |
| 12 | Finish idea 5: ten photos of the Luna web search run have no answer (`websearch_study.py run --resume results\websearch\2026-10-06_153949_full --yes`) | About $0.25 | Credit on the OpenAI account |
| 12b | The same prompt and model with search off | Done 2026-10-06: $0.07, 55 of 100 | |

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
- **Serper credits are finite.** The free account started with 2,500; 1,623 were left on
  2026-10-06, after the two pipeline runs. It returns at most 10 results per search. Run
  `search_study.py plan` before `run`.
- **A failed second call is a result, not a gap.** DeepSeek's choosing call returned nothing on 11
  photos. The report keeps those photos and uses the code order for them.
- **The Sonnet pipeline run of 2026-10-06 is not a clean run.** It covers 91 of 100 photos, and on 9
  of them the choosing call saw a wrongly ordered list (a fault in the code, since corrected).
  Quote its numbers with both caveats. Nine of the ten Vacheron photos are among the missing.
- **An Anthropic photo costs more than the old estimate.** Sonnet 5.5 bills about 3,500 input
  tokens for a photo, not 1,500. A two-call flow on 100 photos costs about $2.20, not $1.
- **Sonnet with thinking off also varies between runs.** On 90 shared photos two prompts gave
  the same first reference only 64 times. Compare inside one run where possible.
- **OpenAI limits Luna to 200,000 tokens a minute on this account.** A call that searches carries
  15,000 to 30,000 tokens. Run `websearch_study.py` with two calls at once, its default.
- **A background run dies with the session that started it.** The Luna search run was cut off at
  82 photos on 2026-10-06. Runs save as they go; continue them with `--resume`.
- **Both paid accounts ran dry during this work.** Anthropic on 2026-10-06, OpenAI on 2026-10-07.
  Check with Qutaiba before a paid run.
- **The search study's numbers are ceilings.** "Own answer or any search" counts a photo when
  the right reference is somewhere in a list of about 11. It is not an accuracy.
- **The guide prints 20 answer-key references.** A model given `REFERENCE_FORMATS.md` can copy them.
  Score such runs on the other 80 rows; `guide_study.py` does.
- **The dataset photos came from the web.** Any test of reverse image search looks better on
  them than it will on a seller's own photo.
- **The current backend auto-fill cuts references.** Its cleaning pattern truncates every
  Omega, Patek, Audemars Piguet, TAG Heuer and Vacheron reference. See `FINDINGS.md`, section 6.2.
