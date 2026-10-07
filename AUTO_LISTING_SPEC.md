# ChronoBay AI Auto-Listing: specification (draft 2)

Written 2026-10-06. Replaces the "Two-Stage Retrieval + Decision Agent" draft
(Google Vision web detection + Serper search + lazy cache).

Sources for this draft:

- the benchmark in this repo (100 photos, 7 models, `results/REPORT.md`);
- the review of draft 1 (2026-10-06);
- product decisions by Qutaiba (2026-10-06), listed in section 2;
- ChronoBay's backend as read on 2026-10-06: `backend/prisma/schema/catalog.prisma`,
  `backend/prisma/seeders/`, `backend/src/modules/watchcharts/` (types, README, `openapi.json`).

Anything marked **Unverified** has not been tested or confirmed and must be before launch.

---

## 1. Goal

A seller uploads photos of a watch and types nothing. ChronoBay returns a pre-filled
listing draft. The seller confirms it, or picks between at most three options, by tapping.

## 2. Decisions (2026-10-06)

| Topic | Decision |
|---|---|
| Input | Photos only. The feature is for sellers who don't want to type, so nothing may depend on typed input. |
| Strap | No aftermarket-strap detection. The existing bracelet material field is still filled from the photo (assumed; say if it should be left out). |
| Authentication | Out of scope. The result is a suggestion about what the watch appears to be, never a statement that it is genuine. |
| Cost | No per-listing budget for now. Measured costs are in Appendix A for the later discussion. |
| New fields | Add dial colour, gold colour and two-tone. |
| Confirming | Tapping to confirm, or to choose between options, is accepted. |
| When the reference can't be confirmed | Only the reference is left empty. Everything the photo shows is still filled. |

## 3. What ChronoBay already has

**Product fields** (`catalog.prisma`, model `Product`): `brandId`, `modelId` (to `WatchModel`),
`referenceNumber`, `caseSize`, `caseMaterialId`, `braceletMaterialId`, `movementTypeId`,
`isLimitedEdition`, `watchGender`, `yearOfManufacture`, `watchConditionId`, `whatsIncluded`,
`marketPrice`, `suggestedPrice`, `images`.

- There is **no dial colour field**.
- Case materials are seeded with six values: `stainless-steel`, `gold`, `platinum`, `titanium`,
  `ceramic`, `bronze`. There is no gold colour and no two-tone.
- Bracelet materials: `leather`, `metal`, `rubber`, `fabric`, `nylon`. Movement types:
  `automatic`, `manual`, `quartz`, `solar`, `hybrid`.

**WatchCharts API v3** is already integrated (`backend/src/modules/watchcharts/`). It is the
catalog draft 1 said did not exist.

| Endpoint | Level | Returns |
|---|---|---|
| `GET /search/watch` (`brand_name`, `reference`, `exact_match`) | 1 | Matching watches with `uuid` and `model` (e.g. `116500`), each with `variants`: `uuid`, `model` (e.g. `116500-0001`), `dial_color`. Partial matches by default. |
| `GET /watch/info` (`uuid`) | 1 | `brand`, `collection` (e.g. `Daytona`), `model`, market price. |
| `GET /watch/specs` (`uuid`) | 2 | `Dial Color`, `Case Material`, `Bezel Material`, `Case Diameter`, `Movement Type`, `Complications`, `Features`, `Image` (base64), and more. |

- `Case Material` values include `Steel`, `Yellow gold`, `Rose gold`, `Red gold`, `White gold`,
  `Gold/steel`, `Platinum`, `Titanium`, `Ceramic`, `Bronze`. So gold colour and two-tone
  are available from WatchCharts.
- `Dial Color` has 23 values (`Black`, `Silver`, `White`, `Blue`, `Grey`, `Mother of pearl`,
  `Champagne`, `Green`, `Brown`, `Gold`, `Transparent`, `Skeletonized`, `Pink`, `Red`, `Yellow`,
  `Purple`, `Orange`, `Bordeaux`, `Bronze`, `Silver (solid)`, `Gold (solid)`, `Meteorite`, `Turquoise`).
- `Movement Type`: `Automatic`, `Quartz`, `Manual winding`, `Solar`, `Smartwatch`.
- There is no strap or bracelet field.
- Limits: **1 request per second per API key**, and every call consumes data credits:
  search 1, watch info 3, specs 10.
- Tested 2026-10-06 with the key in the backend source: the key works and has 1,000
  credits per day, which matches the Level 1 plan. A search for Rolex `126610LN` returned
  `126610` with no variants. Details in `FINDINGS.md`, section 7.
- The `confidence` field in search results is WatchCharts' confidence in its *price data*.
  It is not a match score and must not be used as one.
- A `WatchChartsCache` table already caches WatchCharts data per brand and reference.

**Unverified:** whether ChronoBay's WatchCharts plan includes Level 2 (`/watch/specs`), the
credit cost per call, whether the licence allows storing and displaying specs and images,
how partial matching behaves, and how complete the catalog is for the ten brands and for
references released in 2026. WatchCharts' notation may also differ from the brand's: its
own example writes `116500` where Rolex writes `116500LN`. Which form is stored in
`referenceNumber`, and how the two are matched, needs deciding after test 1.

## 4. What the benchmark showed

One model call, one photo, no catalog. 100 photos, 10 brands.

| Model | Exact reference | Incl. look-alikes | Brand right | Right when confidence ≥ 0.8 |
|---|---:|---:|---:|---:|
| Claude Opus 5.5 (medium) | 79 | 84 | 100 | 19 of 19 |
| Claude Sonnet 5.5 (no thinking) | 72 | 77 | 100 | 11 of 12 |
| GPT-6.1 Sol (low) | 70 | 77 | 100 | 59 of 73 |
| GPT-6 Luna (extra-high) | 52 | 54 | 98 | 22 of 33 |
| DeepSeek Flash | 48 | 53 | 93 | 9 of 11 |
| GPT-6 Luna (no thinking) | 38 | 41 | 97 | 13 of 24 |
| Claude Haiku 4.5 | 11 | 16 | 89 | 3 of 19 |

What this means for the design:

- **The model recognises the watch.** The three strong models got the brand right every time
  and usually named the right model line.
- **The model cannot be trusted to recall the exact reference.** Misses were mostly a
  neighbouring variant, the previous generation, or a reference newer than the model's
  knowledge (watch 46, released in 2026: all seven models missed it).
- **Fields visible in the photo are easy.** From the photo alone, Opus and Sonnet got
  movement right 99 times in 100, case material 97 and 96, bracelet material 97.
- **Self-reported confidence is not a safe gate.** Only Opus was reliable at 0.8 and above.
- **No model reaches 90% on its own.** The catalog step below is what has to close the gap,
  and that is not yet proven.
- **Telling the model how references are built does not close it.** DeepSeek Flash was given
  the reference-format guide (`REFERENCE_FORMATS.md`) with the prompt. On the 80 photos the
  guide does not give away it scored 39, against 37 and 35 without it. Its misses were already
  in the right format; the wrong part was digits that follow no rule. The model needs to be
  told which references exist, which is what step 2 does. One run on one model; see
  `results/GUIDE_STUDY.md`.

Caveats: one pass per photo; the photos came from the web; answer-key rows 12 and 76 are
probably wrong and not yet rechecked.

## 5. Pipeline

```
photos
  │
  ▼
1. Read the photos            one vision-model call: brand, model line, what is visible,
                              up to 3 candidate references, any reference printed in a photo
  │
  ▼
2. Check candidates           WatchCharts search per candidate: does it exist, which
   against the catalog        variants and dial colours does it have
  │
  ▼
3. Fetch specs                WatchCharts specs for candidates that exist
  │
  ▼
4. Decide (rules in code)     compare what the photo shows with each candidate's specs
  │
  ├── one candidate fits  →  auto_filled
  ├── two or three fit    →  choose_one   (seller taps the right one)
  └── none fit            →  not_identified (reference left empty, the rest filled from the photo)
  │
  ▼
5. Seller confirms            reference image from WatchCharts shown next to the seller's photo
  │
  ▼
6. Record the outcome         what was suggested, what the seller accepted or changed
```

### Step 1: read the photos

One call to a vision model with the listing's photos (start with at most four). Structured
output is enforced by the API (section 6.1). Instructions for the model:

- Give the reference in the brand's official format. For Rolex give the base reference
  (`126334`), not a catalogue suffix.
- List up to three candidates, best first, including look-alikes it cannot rule out
  (previous generation, other size).
- If a reference is printed in any photo (warranty card, hang tag, caseback), copy it exactly.
  This costs the seller nothing: many listings already include a photo of the papers.
- Never copy a serial number into the output.
- Answer `unknown` rather than guess when the brand is not one of the ten or the photo is not a watch.

### Step 2: check candidates against the catalog

For each candidate, and for the printed reference if there is one, call
`/search/watch` with `exact_match=false`.

- No result: the candidate is dropped. This removes references that do not exist.
- A result: keep its `uuid` and its `variants` with their dial colours.

Compare references after normalising notation (case, spaces, dots, dashes, slashes), as
`scoring.py` in this repo does.

**Alternative under test: search first, then choose.** In the flow above the model must recall
the reference and the catalog only confirms it. The alternative reverses that: the model
describes the watch, a search returns real references that fit the description, and the model
picks one while looking at the photo. It was proposed on 2026-10-06 using the Serper search API
over WatchBase pages, with three related ideas (check the model's candidates by search, Google
Lens on the photo, catching new releases). None is tested beyond two small probes. They are
listed in `FINDINGS.md`, section 4, with the revised design: search by model line and by the
model part of the guessed reference, rank in code, return at most three. WatchCharts search
could supply the siblings of a guessed reference, since it matches part of a reference, but
it cannot search by name.

Stage 0 of its test is done (2026-10-06, `results/SEARCH_STUDY.md`). Replaying saved answers
through search, with no model call, put the right reference in the candidate list or in the
model's own answer for Opus 91 of 99 photos (own answer alone 79), Sonnet 92 (72) and Sol 87
(70). The list has about 11 candidates, so this is the most a chooser could reach, not a
result. WatchBase has 94 of the 100 answer-key watches; the open web has the other six.

Stage 1 ran the whole flow with Sonnet, thinking off (2026-10-06, `results/PIPELINE_STUDY.md`).
It stopped at 91 of 100 photos when the Anthropic account ran out of credit. On those 91:

- The first choice is right 61 times with the flow and 61 times from the model alone.
- The right reference is among three options 82 times, against 72 for the model's own three.
- The choosing call's own "clear leader" flag is right 21 times in 24.

DeepSeek Flash went through the same flow on all 100 photos: first choice 55 before and 57
after, right reference among three options 66 before and 72 after, at $0.005 a photo and 27
seconds. On the 91 photos both runs share, its three options hold the right reference 63
times, fewer than Sonnet's own three with no search (72). A cheap model does not make up the
difference by searching.

What this means for step 4: `choose_one` should be the normal outcome. Nothing measured so far
is reliable enough to fill the reference in unasked at the 95% mark in section 10. Ranking by
attributes read from search text did not beat the model's own order either, so "rules in code
decide" needs a structured catalog, not search snippets.

### Step 3: fetch specs

This step runs only when a spec source has been chosen (section 7.1). Without one, the
Case and Complications checks in step 4 are skipped, case size stays empty, and case
material and movement come from the photo.

For each surviving candidate call `/watch/specs`, and `/watch/info` for the chosen one.
Cache every search and specs response in `WatchChartsCache` (new `type` values `search`
and `specs`), so each reference is fetched once.

### Step 4: decide

A candidate **fits** when all of these hold. A check with no data on either side is skipped.

| Check | Rule |
|---|---|
| Exists | WatchCharts returned the reference. |
| Dial | The photo's dial colour matches the watch's `Dial Color`, or one of its variants. That variant is selected. |
| Case | The photo's case colour is compatible with `Case Material` (table in section 7). |
| Complications | Every complication visible in the photo (date, chronograph, GMT, moon phase) is in `Complications`. |

| Outcome | When | What the seller sees |
|---|---|---|
| `auto_filled` | Exactly one candidate fits, and it is the model's first candidate or the printed reference. | The filled draft, with the WatchCharts image for comparison. |
| `choose_one` | Two or three candidates fit, or the only one that fits was not the first candidate. | Up to three options with image, reference, model line, dial colour and size. One tap. |
| `not_identified` | No candidate fits. | A draft with everything the photo shows: brand, model line, case material, bracelet material, movement and dial colour. The reference and case size are left empty. |
| `unsupported` | Not a watch, or not one of the ten brands. | The normal manual form. |

Two look-alike generations that both fit (for example `116610LN` and `126610LN`) end in
`choose_one`. The system asks; it does not guess.

The model's own confidence number is logged but is not part of the rule.

**Optional later step.** For `choose_one`, a second model call can compare the seller's photo
with the candidates' WatchCharts images and pick one. Add it only if the tests in section 10
show it improves accuracy.

## 6. Contracts

### 6.1 Vision model output

```json
{
  "is_watch": true,
  "brand": "Rolex",
  "collection": "Cosmograph Daytona",
  "candidates": ["126500LN", "116500LN"],
  "printed_reference": null,
  "printed_reference_source": null,
  "dial_color": "White",
  "case_color": "silver",
  "bracelet_material": "metal",
  "case_material": "stainless-steel",
  "movement": "automatic",
  "complications_visible": ["Chronograph", "Tachymeter"],
  "confidence": 0.6
}
```

| Field | Values |
|---|---|
| `brand` | The ten seeded brands, or `unknown`. |
| `candidates` | 0 to 3 reference strings. |
| `printed_reference_source` | `warranty_card`, `hang_tag`, `caseback`, `other`, or null. |
| `dial_color` | The WatchCharts `Dial Color` list, or `unknown`. |
| `case_color` | `silver`, `yellow-gold`, `rose-gold`, `two-tone`, `black`, `bronze`, `other`, `unknown`. The model reports colour, not metal: steel, white gold, platinum and titanium look alike in a photo. |
| `bracelet_material` | `leather`, `metal`, `rubber`, `fabric`, `nylon`, `unknown`. |
| `case_material` | ChronoBay's case materials, or `unknown`. The model's estimate from the photo, used when no spec source confirms it. |
| `movement` | ChronoBay's movement types, or `unknown`. Same use. |
| `complications_visible` | Subset of the WatchCharts `Complications` list. |

### 6.2 Pipeline result (to the app)

```json
{
  "outcome": "choose_one",
  "options": [
    {
      "watchcharts_uuid": "…",
      "brand": "Rolex",
      "collection": "Daytona",
      "reference_number": "126500LN",
      "variant": "…",
      "dial_color": "White",
      "case_size": 40,
      "case_material": "stainless-steel",
      "gold_color": null,
      "movement": "automatic",
      "is_limited_edition": false,
      "reference_image": "…"
    },
    {
      "watchcharts_uuid": "…",
      "brand": "Rolex",
      "collection": "Daytona",
      "reference_number": "116500LN",
      "variant": "…",
      "dial_color": "White",
      "case_size": 40,
      "case_material": "stainless-steel",
      "gold_color": null,
      "movement": "automatic",
      "is_limited_edition": false,
      "reference_image": "…"
    }
  ],
  "from_photo": { "bracelet_material": "metal", "dial_color": "White" },
  "run_id": "…"
}
```

`options` has one entry for `auto_filled`, two or three for `choose_one`, none otherwise.
The example is the look-alike case: both generations exist with a white dial, so the seller
chooses.

## 7. Where each listing field comes from

| Product field | Source | Notes |
|---|---|---|
| `brandId` | Photo | 100 of 100 for the strong models. |
| `modelId` | WatchCharts `collection` | Match to an existing `WatchModel` for the brand. **Unverified:** how missing models should be created. |
| `referenceNumber` | Candidate confirmed by WatchCharts | |
| `caseSize` | Spec source (section 7.1) | `"41mm"` becomes `41`. Size cannot be read from a photo, so it stays empty until a spec source is chosen. |
| `caseMaterialId`, gold colour | Spec source when there is one (mapping below); otherwise the model's estimate from the photo | From the photo alone, Opus and Sonnet were right 97 and 96 times in 100. The photo cannot separate steel from white gold or platinum. |
| `movementTypeId` | Spec source when there is one; otherwise the model's estimate | `Automatic` → `automatic`, `Manual winding` → `manual`, `Quartz` → `quartz`, `Solar` → `solar`. WatchCharts has no `hybrid`. From the photo alone: 99 in 100. |
| dial colour (new) | WatchCharts variant, checked against the photo | |
| `braceletMaterialId` | Photo | WatchCharts has no strap field. |
| `isLimitedEdition` | WatchCharts `Features` contains `Limited edition` | |
| `marketPrice`, `suggestedPrice` | Existing WatchCharts price flow | Now keyed to the confirmed watch. |
| condition, year, what's included, price, description | Seller | Not part of this feature. |

**Case material mapping (proposed):**

| WatchCharts `Case Material` | ChronoBay case material | Gold colour |
|---|---|---|
| `Steel` | `stainless-steel` | |
| `Yellow gold` | `gold` | `yellow` |
| `Rose gold`, `Red gold` | `gold` | `rose` |
| `White gold` | `gold` | `white` |
| `Gold/steel` | `two-tone` (new) | From `Bezel Material` when it is a gold, otherwise from the photo. **Unverified.** |
| `Platinum`, `Titanium`, `Ceramic`, `Bronze` | same name | |
| anything else | left empty | Logged for review. |

**Photo case colour compatibility (starting table, to tune):** `silver` with Steel, White gold,
Platinum, Titanium; `yellow-gold` with Yellow gold; `rose-gold` with Rose gold, Red gold;
`two-tone` with Gold/steel; `black` with Ceramic, Carbon, or any case with the
`Pvd/dlc coating` feature; `bronze` with Bronze.

**How references differ by brand.** For Rolex the reference fixes the model, size, metal and
bezel: the last digit is the metal (0 steel, 3 steel and yellow gold, 4 steel and white gold,
8 yellow gold, 9 white gold). Watches with the same reference differ only in dial and
bracelet style. Rolex numbers those as `126334-0001` (Oyster bracelet) and `126334-0002`
(Jubilee bracelet), and WatchCharts models them as variants (its example: `116500-0001`).
For Omega, TAG Heuer and Breitling the strap is part of the reference. Proposed, following
the strap decision in section 2: a reference that differs only in its strap code counts as
correct.

### 7.1 Where specs come from (decision needed)

The reference check in step 2 uses WatchCharts search, which ChronoBay already has. Specs,
case size above all, need a source. The options:

| Option | Gives | Cost | Main risks |
|---|---|---|---|
| A. The photo only | Case material, movement, bracelet material, dial colour. No case size. | None | Steel, white gold and platinum look alike. |
| B. WatchCharts `/watch/specs` | Structured specs and a reference image | Level 2 plan and credits. **Unverified.** | 1 request per second. |
| C. WatchBase Data Feed | Structured specs, no images | US $0.30 per watch entry, per WatchBase's site. **Unverified:** whether entries may be stored. | |
| D. WatchBase pages found through a search API (Serper) | From the page title: model name, case material, dial colour, often the strap, sometimes the size. Movement and diameter only when the snippet happens to include them. | About $0.001 per search | Listed below. |

**Test of option D** (2026-10-06; 10 references, one per brand; a general web search
limited to watchbase.com, not Serper itself):

- 9 of 10 references had a WatchBase page, including the 2026 TAG Heuer `WBP1190.BZ0003`.
  Cartier `WSSA0018` was not found.
- Titles follow one pattern, for example
  `Rolex 126610LN-0001 : Submariner Date 41 Stainless Steel / Black / Cerachrom » WatchBase`.
- The size is in the title for only some watches (the Rolex, TAG Heuer and Breitling in the sample).
- Notation differs from the brands': `IW3716-17` for `IW371617`, `3858520` for `Q3858520`,
  `126610LN-0001` for `126610LN`.
- The general query from draft 1 (`Rolex 126610LN specs case material movement strap`)
  returned marketplaces and dealers. WatchBase was not in the top ten, so it has to be
  targeted by name.
- WatchBase's pages refused automated requests (HTTP 403), so only titles and snippets
  are available this way.

**Risks of option D:**

- It takes WatchBase's paid product through search results. WatchBase B.V. (Amsterdam)
  names database rights in its terms of use and sells the same data. Get this checked
  before depending on it.
- Snippets are short and chosen by the search engine. A field can be missing, or come
  from another site.
- It needs a reference to search for, so it does not help identify the watch.
- It depends on a third-party service that scrapes Google results.

**Recommendation:** start with option A plus the WatchCharts search already in place.
That fills every field except case size at no new cost. Add B or C for case size and for
the reference image. Use D only as a cross-check, and only after test 5.

## 8. Changes needed in ChronoBay

| Change | Why |
|---|---|
| `Product.dialColor` (new) | Decision in section 2. Proposed vocabulary: the WatchCharts list. |
| `Product.goldColor` (new, nullable: `yellow`, `rose`, `white`) | Keeps the existing `gold` material and its filters working. |
| Case material `two-tone` (new seed) | Steel and gold. |
| `Product.watchChartsUuid` (new, nullable) | Ties later price lookups to the confirmed watch. |
| `WatchChartsCache` types `search`, `specs` | One fetch per reference. |
| `AutoListingRun` table | Photos used, model and version, candidates, checks, outcome, what the seller accepted or changed. This is the only way to measure accuracy in production. |

Labels need Arabic translations where the app shows them.

## 9. Limits and failures

- **WatchCharts rate limit.** One request per second for the whole key, shared with the
  price features. Worst case for one listing with nothing cached is three searches, three
  specs and one info call: about seven seconds. Use one queue for all WatchCharts calls.
- **Speed.** One model call measured 2.5 s (Sonnet) to 6 s (Opus, Sol) at the median, and
  up to 15 s at the slow end. Run the pipeline as a background job and fill the draft when
  it finishes.
- **WatchCharts unavailable or out of credits.** Return `not_identified` with the
  photo-visible fields. Do not fall back to the model's unverified reference.
- **Model timeout, refusal or invalid output.** One retry, then the manual form.
- **Reference missing from WatchCharts.** The watch ends as `not_identified`. Log these:
  they show where the catalog is incomplete.
- **Abuse.** Each run costs money. Limit runs per seller per day and skip photos whose
  file hash was already processed.
- **Privacy.** Photos go to the model provider. Strip location data first, and never store
  or return a serial number.

## 10. Tests before building

| # | Test | Cost | Answers |
|---|---|---|---|
| 1 | Replay the saved benchmark answers through WatchCharts search and specs. No new model calls. | WatchCharts credits only | How many of the 100 answer-key references WatchCharts has, including 2026 ones. How many wrong model answers the checks catch or correct. |
| 2 | Confirm the WatchCharts plan: Level 2 access, credits per call, licence to store and show specs and images. | None | Whether section 5 is allowed at all. |
| 3 | Collect 30 to 50 phone photos of real watches that were never online. | Time | Whether accuracy holds on real seller photos. |
| 4 | Run the full pipeline on the benchmark photos and on the photos from test 3. | About $1 to $3 per model | The numbers below. |
| 5 | Only if option D in section 7.1 is wanted: run the 100 answer-key references through Serper and compare what the WatchBase title and snippet give with the answer key. | Serper's free tier (needs an account) | How often option D returns the right case material, size, dial colour and movement. |

**Proposed pass marks** (to be agreed):

- `auto_filled` listings have the right reference at least 95 times in 100.
- When the outcome is `choose_one`, the right watch is among the options at least 95 times in 100.
- At least 70% of uploads end as `auto_filled`.

The baseline to beat is one model call with no catalog: 79, 72 and 70 exact for Opus,
Sonnet and Sol.

## 11. Out of scope

Authentication and counterfeit detection; aftermarket parts; condition grading; pricing
(already built); any typed input.

## 12. Open questions

1. Does the WatchCharts plan cover `/watch/specs`, and what does each call cost?
2. May specs and images from WatchCharts be stored and shown in listings?
3. Which spec source (section 7.1)? Case size has no source until this is decided.
4. How should a `collection` with no matching `WatchModel` be handled?
5. Which model runs step 1? Decide after test 4; cost is deferred.
6. Should the dial colour list be WatchCharts' 23 values or a shorter ChronoBay list?

---

## Appendix A. Measured cost and speed

One call with one photo, from the benchmark runs.

| Model | Cost per call | Median time | Slowest 5% |
|---|---:|---:|---:|
| Claude Opus 5.5 (medium) | $0.022 | 6.2 s | 10.8 s |
| Claude Sonnet 5.5 (no thinking) | $0.0084 | 2.5 s | 3.6 s |
| GPT-6.1 Sol (low) | $0.0070 | 6.0 s | 14.7 s |
| GPT-6 Luna (extra-high) | $0.0010 | 15.3 s | 38.9 s |
| DeepSeek Flash | $0.0013 | 4.9 s | 43.5 s |
| GPT-6 Luna (no thinking) | $0.0003 | 2.5 s | 4.1 s |
| Claude Haiku 4.5 | $0.0025 | 1.5 s | 3.1 s |

More photos per call raise the cost roughly in proportion. WatchCharts credits are extra and unknown.

## Appendix B. What was dropped from draft 1

| Dropped | Why |
|---|---|
| Google Vision web detection as the candidate source | It returns page titles only for images that are already on the web, so it fails on a seller's own photo. |
| Serper search as the main source of specs, and the cache built from search snippets | Snippets are unverified text from arbitrary sites. Searching WatchBase by name is kept as option D in section 7.1, as a cross-check only. |
| Aftermarket-strap status | Decision in section 2. It was also wrong for brands whose reference includes the strap. |
| The model's confidence as the gate for auto-fill | Unreliable for every model except Opus. |
| The $0.005 per listing budget | Deferred. Only models scoring 11 to 52 fit it. |
