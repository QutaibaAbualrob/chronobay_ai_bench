# Findings log: ChronoBay AI auto-listing

Everything established up to 2026-10-06, with how each finding was checked.
The design that follows from these findings is in `AUTO_LISTING_SPEC.md`.
No API key or other secret is written in this file.

Status words used below:

- **Measured**: from a test that was run, with saved results.
- **Read**: read directly in code, a schema or official documentation.
- **Reported**: from a web search result or a third-party page; not opened directly.
- **Inferred**: a conclusion drawn from other findings; not confirmed.

---

## 1. Benchmark: can a model name the reference from one photo?

**Measured.** 100 photos, 10 brands, one call per photo, no catalog. Full detail in `results/REPORT.md`.

| Model | Exact reference | Incl. look-alikes | Brand right | Right when confidence ≥ 0.8 | Cost per image | Median time |
|---|---:|---:|---:|---:|---:|---:|
| Claude Opus 5.5 (medium) | 79 | 84 | 100 | 19 of 19 | $0.022 | 6.2 s |
| Claude Sonnet 5.5 (no thinking) | 72 | 77 | 100 | 11 of 12 | $0.0084 | 2.5 s |
| GPT-6.1 Sol (low) | 70 | 77 | 100 | 59 of 73 | $0.0070 | 6.0 s |
| GPT-6 Luna (extra-high) | 52 | 54 | 98 | 22 of 33 | $0.0010 | 15.3 s |
| DeepSeek Flash | 48 | 53 | 93 | 9 of 11 | $0.0013 | 4.9 s |
| GPT-6 Luna (no thinking) | 38 | 41 | 97 | 13 of 24 | $0.0003 | 2.5 s |
| Claude Haiku 4.5 | 11 | 16 | 89 | 3 of 19 | $0.0025 | 1.5 s |

What it shows:

- The strong models recognise the watch: brand right every time, model line right in almost every miss.
- They cannot be trusted to recall the exact reference. Misses are mostly a neighbouring variant, the previous generation, or a reference newer than the model's knowledge.
- Fields visible in the photo are easy. From the photo alone, Opus and Sonnet got movement right 99 times in 100, case material 97 and 96, bracelet material 97.
- The model's own confidence is reliable only for Opus.
- No model reaches 90% alone.
- `gpt-6.1-sol` cannot run with reasoning off; its lowest setting is `low`.
- The DeepSeek row is its first run (2026-09-30). A second run on 2026-10-05 with a larger
  output limit scored 44 exact and 50 with look-alikes, and only 52 of its 100 answers were
  the same in both runs. `results/REPORT.md` shows the later run. The comparison is in
  `README.md` under Findings.

### Caveats on the benchmark

| Caveat | Status |
|---|---|
| One pass per photo. Differences of a few points may be noise. | |
| The photos came from the web, not from sellers. | |
| Row 12's photo was replaced on 2026-10-05 (old one in `dataset/images/_replaced/`). Every saved answer for row 12 was made on the old photo, so row 12 is out of date in all reports. | Read |
| Row 76: four models agree on `IW329001` against the key's `IW328802`. Probably an answer-key error. Not rechecked. | Inferred |
| Rows 66 and 98 are flagged with weaker evidence. Not rechecked. | Inferred |
| The look-alike list (`also_accept`, 27 rows) was written by Claude, has no source links and was never independently reviewed. It was fixed before any model ran and adds 2 to 7 answers per model. The exact score does not use it. | Read |
| `reports/ChronoBay_AI_Benchmark_Report_2026-09-30.pdf` covers only the first four models and labels watch 46 an "invented number", which is wrong (see section 2). | Read |

## 2. Watch 46: a reference newer than the models

**Measured and Reported.** The answer is `WBP1190.BZ0003`, the titanium TAG Heuer Solargraph released in 2026. All seven models missed it and all said stainless steel.

- Opus and Sonnet answered `WBP1114.BA0000` and `WBP1113.BA0000`. These are real references for the earlier steel Solargraph. An earlier claim that `.BA0000` is not a real TAG Heuer code was wrong.
- The lesson: a model cannot recall a reference it never learned. Only a current catalog fixes this.

## 3. Draft 1 of the architecture (Google Vision + Serper)

**Read and Measured.** Reviewed 2026-10-06 and replaced by `AUTO_LISTING_SPEC.md`.

| Finding | Status |
|---|---|
| Google Vision web detection returns page titles only for pages that already host the same image or a close copy. Similar-looking images come back as bare links. A seller's own photo is on no page. | Read (Google docs) |
| Web detection costs nothing for the first 1,000 calls a month, then $3.50 per 1,000. Text detection is $1.50 per 1,000. | Read (Google pricing) |
| The draft's $0.005 per listing budget fits only models scoring 11 to 52. | Measured |
| The draft's example of an "aftermarket strap" is wrong: `310.30.42.50.01.002` on leather is the factory reference `310.32.42.50.01.002`. For Omega, TAG Heuer and Breitling the strap is part of the reference. | Reported (omegawatches.com) |
| The draft named Claude 3.5 Sonnet, which was retired in October 2025. | Read |

### Google Vision test

`vision_test.py` is written and checked offline. **It has never been run against the API**: no `GOOGLE_VISION_API_KEY` is set. It reads 623 of 645 made-up page titles correctly across all 100 references.

## 4. WatchBase

| Finding | Status |
|---|---|
| WatchBase sells its data: US $0.30 per watch entry, no subscription. Images are not included. | Reported |
| WatchBase B.V. is a Dutch company; its terms of use name database rights over its watch data. | Reported |
| WatchBase pages refuse automated requests (HTTP 403). | Measured |
| Searching watchbase.com for 10 references, one per brand, found 9. Cartier `WSSA0018` was missing. The 2026 TAG Heuer was present. | Measured (general web search, not Serper) |
| Page titles follow one pattern and carry model, case material, dial colour and often the strap, for example `Rolex 126610LN-0001 : Submariner Date 41 Stainless Steel / Black / Cerachrom » WatchBase`. Size appears for only some watches; movement never. | Measured |
| WatchBase notation differs from the brands': `IW3716-17`, `3858520` (no Q), `126610LN-0001`. | Measured |
| The general query "Rolex 126610LN specs case material movement strap" returned marketplaces and dealers; WatchBase was not in the top ten. | Measured |
| Serper sells prepaid packs from $50 (50,000 searches) that expire after six months; 2,500 free searches. | Reported |

Conclusion: reading WatchBase through search results can cross-check a known reference. It does not identify a watch, it is not licensed, and it is weakest on the one field a photo cannot give (case size).

## 5. Rolex references

**Reported.** The last digit of a Rolex reference is the metal: 0 steel, 1 steel and Everose gold, 3 steel and yellow gold, 4 steel and white gold, 5 Everose gold, 6 platinum, 8 yellow gold, 9 white gold. Watches with the same reference differ only in dial and bracelet style; Rolex numbers those as `126334-0001` (Oyster bracelet), `126334-0002` (Jubilee), and so on.

## 6. ChronoBay backend as it is today

**Read** in `D:\orapex\chronobay\backend` on 2026-10-06. Nothing there was changed.

### 6.1 Listing data model (`prisma/schema/catalog.prisma`)

- `Product` has `referenceNumber`, `caseSize`, `brandId`, `modelId` (to `WatchModel`), `caseMaterialId`, `braceletMaterialId`, `movementTypeId`, `isLimitedEdition`, `watchGender`, `yearOfManufacture`, `marketPrice`, `suggestedPrice`.
- There is no dial colour, no gold colour, and no two-tone case material.
- Seeded values: case materials `stainless-steel`, `gold`, `platinum`, `titanium`, `ceramic`, `bronze`; bracelet materials `leather`, `metal`, `rubber`, `fabric`, `nylon`; movement types `automatic`, `manual`, `quartz`, `solar`, `hybrid`.
- `PLAN.md` in this repo says `referenceNumber` is missing from `Product`. That is out of date.

### 6.2 Current auto-fill (`src/modules/watch-autofill/`)

The reference is **not** auto-filled. The seller types it, and `POST /watch-autofill` fills the other fields from it. There is no photo step.

1. A pattern picks the longest letters-digits-letters token from the typed text.
2. A one-hour in-memory cache is checked.
3. Active and sold listings whose reference contains the typed text are counted, and the most common reference among them is found.
4. If the count reaches the admin setting `reference_matching_threshold` (default 3), the answer comes from the database: reference, brand and model only, at a fixed confidence of 0.8.
5. Otherwise a text-only request goes to OpenAI (`OPENAI_MODEL`, default `gpt-4.1-mini`), with ChronoBay's allowed values and up to 5 existing listings as context. The model answers from memory.
6. Values not in ChronoBay's lists are dropped.

It does not use WatchCharts, and nothing verifies the model's answer.

Problems found:

| Problem | Status |
|---|---|
| The cleaning pattern cuts 50 of the 100 answer-key references: every Omega, Patek, Audemars Piguet, TAG Heuer and Vacheron one. `310.30.42.50.01.002` becomes `310`; `5711/1A-010` becomes `5711`; `CBN2A1B.BA0643` becomes `BA0643`. | Measured |
| The cache key uses the cut reference, so different watches can share one cached answer for an hour. | Read |
| The database path matches any listing whose reference contains the typed text, so a cut reference can return a different watch at 0.8 confidence. | Read |
| Specs come from a small model's memory, the weakness the benchmark measured. | Read |
| The controller has no login guard; the only app-wide guard is the rate limiter. Not traced through every middleware. | Read, to verify |

### 6.3 WatchCharts integration (`src/modules/watchcharts/`)

- WatchCharts API v3 is integrated. Routes in use: `GET /watchcharts/market-price`, `/price-1y`, `/price-1y/by-reference`. Responses are cached in `WatchChartsCache`.
- Search and specs calls exist in the module, but no feature calls them yet.
- That controller also imports no login guard. To verify.

## 7. WatchCharts

### 7.1 Endpoints and credit costs

**Read** from `openapi.json` in the backend module.

| Endpoint | Level | Credits | Returns |
|---|---|---:|---|
| `/search/watch` | 1 | 1 | Matching watches (`uuid`, `model`) and their `variants` with `dial_color` |
| `/brand/list` | 1 | 1 | Brands with collections and watch counts |
| `/watch/info` | 1 | 3 | Brand, collection, model, market and dealer price |
| `/watch/price_1y` | 1 | 3 | Daily prices for a year |
| `/watch/retail` | 2 | 5 | Retail price |
| `/watch/listings` | 2 | 5 | Ten most recent listings |
| `/watch/appraisal` | 2 | 5 | Appraisal by condition and region |
| `/watch/price_5y` | 2 | 8 | Five-year price history |
| `/watch/specs` | 2 | 10 | Dial colour, case material (incl. yellow, rose, white gold and gold/steel), case diameter, movement type, complications, features, image |
| `/watch/price_full` | 2 | 10 | Full price history |

Limits: one request per second per key. The `confidence` field is about price data, not match quality.

### 7.2 Pricing and licence

**Reported.** WatchCharts is not free; there is a 7-day trial.

| Plan | Price | Credits | Endpoints |
|---|---|---|---|
| Professional, pay-as-you-go | $99/month | 2,500 credits for $200 | Level 1 |
| Professional + Level 1 API | from $600/month or $5,000/year | 1,000 per day | Level 1 |
| Professional + Level 2 API | from $1,000/month or $8,000/year | 3,000 per day | Level 1 and 2 |

Licence types: internal use, distribution, resale. Showing the data in listings falls under distribution. Which licence ChronoBay holds is unknown.

### 7.3 The key

- The backend reads `WATCHCHARTS_API_KEY` from its environment. No `.env` file exists on this machine; the key is empty in `.env.production.example`. **Read.**
- A real key is hardcoded as `fallbackKey` at about line 41 of `src/modules/watchcharts/services/watchcharts-client.service.ts`. It is used when the environment variable is empty. **Read.**

### 7.4 Live test of the hardcoded key

**Measured** on 2026-10-06 with two calls, 2 credits in total.

| | Result |
|---|---|
| Key valid | Yes |
| Daily credits (`Wc-Rolling-Credits`) | 1,000 |
| Used before the test | 0 |
| Top-up credits | 0 |
| `GET /brand/list` | 71 brands with collections |
| `GET /search/watch` Rolex `126610LN` | One result, `model` `126610`, no variants |

- The plan is probably "Professional + Level 1 API". **Inferred** from 1,000 credits a day.
- Specs are therefore probably not available. **Inferred**; `/watch/specs` was not called.
- Nothing else used this key that day, so production may run on a different key, or had no price lookups. **Inferred.**
- WatchCharts wrote the reference as `126610`, without `LN`, and returned no dial variants. One test only.

### 7.5 What the key is good for

| Benefit | Credits |
|---|---:|
| Confirm that a reference the model proposed exists | 1 |
| Get the model line and a market price for a confirmed watch | 3 |
| Build the brand and model-line lists once | 1 |

At 1,000 credits a day, shared with the price features: 1,000 listings checking one reference, about 330 checking three candidates, about 165 checking three candidates and fetching a price. Caching by reference stretches this.

## 8. Decisions taken (Qutaiba, 2026-10-06)

- Photos only; nothing depends on typed input.
- Tapping to confirm, or to choose between options, is accepted.
- When the reference cannot be confirmed, only the reference is left empty; the rest is filled from the photo.
- No aftermarket-strap detection.
- Authentication is out of scope.
- Cost budget is deferred.
- Dial colour, gold colour and two-tone are to be added.
- WatchCharts is proposed for the upcoming build plan.

## 9. Security items to fix

| Item | Where | Status |
|---|---|---|
| A live WatchCharts key is hardcoded in source. Replace the key, delete the fallback, set it only through the environment. | `backend/src/modules/watchcharts/services/watchcharts-client.service.ts`, about line 41 | Open |
| `/watch-autofill` and `/watchcharts/*` appear to have no login check, so anyone could spend OpenAI and WatchCharts credit. | Their controllers | To verify |
| An OpenAI key was pasted into a chat on 2026-10-01. It should be revoked if it has not been. | OpenAI dashboard | Unknown |

## 10. Still unknown

1. Which WatchCharts plan and licence ChronoBay holds, and whether `/watch/specs` works with the key.
2. How complete WatchCharts is for the ten brands and for 2026 references, and how its notation maps to the brands'.
3. Where case size will come from: WatchCharts Level 2, WatchBase's feed, or left empty.
4. How Google Vision behaves on these photos (test ready, not run).
5. How any of this performs on real seller photos. No such photos have been tested.
6. Whether the model plus a WatchCharts check beats the model alone (79, 72, 70).

## 11. Next tests, cheapest first

| Test | Cost | Answers |
|---|---|---|
| One `/watch/specs` call | 10 credits, or none if refused | Unknown 1 |
| Replay the 100 answer-key references through `/search/watch` | 100 credits | Unknown 2 |
| Replay each model's saved answers through `/search/watch` | Up to 100 credits per model | Unknown 6 |
| Google Vision on the 100 photos, original and altered | Free tier | Unknown 4 |
| Re-run row 12 on every model | A few cents | Fixes the stale row |
| 30 to 50 phone photos of real watches through the pipeline | $1 to $3 per model | Unknown 5 |
