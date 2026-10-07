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
- `results/REPORT.md` also has a row named `deepseek-flash-guide` (52 exact). It is not an
  eighth model: it is DeepSeek Flash given the reference guide, and 20 of the answers are
  printed in that guide. See section 5.

### Attributes from the photo alone

**Measured** on 2026-10-06 from the saved answers of every full run. No new model calls.
The benchmark does not score these fields; they were compared with the answer key afterwards.

The fuller study is `results/DETAIL_STUDY.md`, written by `detail_study.py` (free to re-run). It leaves
out row 12, so its counts are out of 99, and adds: model line right 99 of 99 for the three strong
models; brand, model line and all three attributes together right on 93 to 94 photos; when the three
strong models agree on a reference (54 photos) it is right 51 times; rare values such as gold (16 of 16)
and ceramic (3 of 3) are recognised, so the scores are not just from guessing the common value.

| Model (run) | Exact reference | Brand | Movement | Case material | Bracelet material | All three attributes | All three, when the reference was wrong |
|---|---:|---:|---:|---:|---:|---:|---:|
| GPT-6.1 Sol, low | 70 | 100 | 100 | 98 | 96 | 94 | 26 of 30 |
| Claude Opus 5.5 | 79 | 100 | 99 | 97 | 97 | 93 | 19 of 21 |
| Claude Sonnet 5.5, no thinking | 72 | 100 | 99 | 96 | 97 | 93 | 23 of 28 |
| GPT-6 Luna, extra-high | 52 | 98 | 97 | 96 | 98 | 91 | 41 of 48 |
| DeepSeek Flash (2026-09-30) | 48 | 93 | 96 | 92 | 96 | 90 | 43 of 52 |
| DeepSeek Flash (2026-10-05) | 44 | 96 | 96 | 91 | 95 | 87 | 44 of 56 |
| GPT-6 Luna, no thinking | 38 | 97 | 94 | 93 | 98 | 85 | 49 of 62 |
| Claude Haiku 4.5 | 11 | 89 | 91 | 91 | 98 | 82 | 72 of 89 |

- Attributes hold up when the reference is wrong, which supports leaving only the reference empty.
- The strong models' few attribute misses sit in six rows, and most are not clear model errors:
  row 12 (photo since replaced), row 17 (`nylon` in the key, `fabric` answered; the two values
  overlap), rows 55 and 89 (`leather` in the key, all three strong models say `fabric`; to recheck),
  row 46 (titanium answered as steel; a real limit of photos), row 49 (mixed answers).
- Not measurable from saved data: dial colour, case size, gold colour and two-tone. The prompt
  never asked for them and the answer key has no such columns.

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

### Serper: four ways to use it (proposed 2026-10-06, none tested)

The guide test (section 5) showed that the model's misses are real-looking references with the
wrong digits. A search can supply references that exist. Four ways to use Serper for that, most
promising first:

| # | Idea | How it works | Main risk |
|---|---|---|---|
| 1 | **Find candidates by search** (revised below) | First version: the model describes the watch (brand, model line, dial colour, metal, bracelet). Code searches WatchBase with that description. The result titles are real watches with their references; the model picks among them by looking at the photo again. | The right watch is not in the results, or two results cannot be told apart from their titles. |
| 2 | **Check the model's own candidates** | Search each reference the model proposes and compare the page title (model line, metal, dial, strap) with what the model saw. | Most wrong answers are real neighbouring references, so an existence check alone catches little. |
| 3 | **Google Lens on the seller's photo** | Serper's Lens endpoint does reverse image search from an image URL. | Needs the photo at a public URL. The benchmark photos came from the web, so they flatter any image search. |
| 4 | **Catch new releases** | Search is current; the models are not (watch 46). | Covered by ideas 1 and 2 if they work. |

**Reported** (third-party review, not Serper's own page): $50 buys 50,000 credits, so $0.001 a
search; a Lens query costs 3 credits; credits expire six months after purchase. **Read** on
serper.dev: 2,500 free queries on signup, no card.

**Measured, small probe for idea 1** (2026-10-06, four photos DeepSeek missed, general web search
limited to watchbase.com, not Serper, description written from the answer key):

| Row | Expected | In the top ten? | Note |
|---:|---|---|---|
| 46 | `WBP1190.BZ0003` | Yes, third | Title reads "Titanium / Grey / Bracelet". All seven models missed this watch. |
| 72 | `IW501701` | Yes, as `IW5017-01` | `IW5017-02` has the same title words ("Stainless Steel / Silver"), so titles alone do not separate them. |
| 65 | `WSSA0022` | No | No steel Santos-Dumont on a strap came back. WatchBase's Cartier coverage is thin (also seen above). |
| 95 | `4600E/000A-B442` | No | The query said "blue dial", which was a guess; it returned `…-B487`, the blue one. The answer key has no dial colour. |

What the probe shows: the idea can find a watch the models cannot recall; a search built on the
dial colour fails when that one field is wrong; titles do not always separate candidates; and
coverage differs by brand. Four photos is not a measurement.

### Idea 1 revised: shortlist by model line (2026-10-06, proposed, not built)

The first version of idea 1 searched with the model's full description and asked the model for
one answer. Three checks, all free, changed the design.

**Measured, from saved answers** (latest full run per model, 99 photos, row 12 left out):

| Model | Exact | Misses | Misses with the right brand and model line | Misses within two characters |
|---|---:|---:|---:|---:|
| Claude Opus 5.5 | 79 | 20 | 20 | 11 |
| Claude Sonnet 5.5 (no thinking) | 72 | 27 | 27 | 18 |
| GPT-6.1 Sol (low) | 70 | 29 | 29 | 21 |
| DeepSeek Flash | 44 | 55 | 46 | 25 |

- A strong model that misses the reference has still named the right brand and model line
  every time. "Model line" is scored at collection level (Portugieser, Santos-Dumont), so this
  is an upper bound on what a lookup by line can reach.
- Two models' own answers already contain the right reference more often than one: Opus or
  Sonnet 89 of 99, Sonnet or Sol 87, all three 91.
- Eight photos were missed by all three strong models: rows 46, 54, 66, 76, 82, 86, 88, 91. On
  three of them (82, 88, 91) every model gave a look-alike the answer key accepts. Row 76 is
  the suspected answer-key error; row 46 is the 2026 release.
- 26 answer-key rows list look-alikes a photo cannot separate. One exact answer is not always
  possible from a photo; a short list is.

**Measured, second probe** (general web search, not Serper):

| Query | Result |
|---|---|
| Vacheron line name plus the model part of the reference (`FiftySix Self-Winding 4600E/000A`), WatchBase only | `…-B442` (Silver) first and `…-B487` (Blue) second. The titles separate them by dial colour. The first probe missed this watch because it searched on a guessed colour. |
| `WSSA0022` on WatchBase | Not there, even by exact reference. |
| `WSSA0022` on the open web | Nine results with the reference in the title (Chrono24, WatchCharts, retailers). |

**Read:** WatchCharts `/search/watch` needs a brand and a reference and matches part of a
reference. It cannot search by name, so it can list the siblings of a guessed reference but
cannot start from a description.

**The revised design:**

1. One model call returns brand, model line, up to three candidate references, and what is
   visible (dial colour, metal, bracelet, size, complications).
2. Code searches by **model line and the model part of the guessed reference**, the two fields
   that are reliable. Dial colour and the other attributes are not put in the query.
3. Two sources, merged: WatchBase pages and the open web. References are read out of the
   result titles with the patterns already in `vision_test.py`.
4. Code ranks the candidates by how many visible attributes agree. One wrong attribute lowers
   a candidate; it does not remove it. The model's own guesses always stay in the list.
5. The result is a list of at most three. One clear leader is `auto_filled`; otherwise
   `choose_one`, which the seller settles with a tap. A second model call looks at the photo
   again only when code cannot rank the list.

**The test, in two stages:**

- **Stage 0, no model calls.** Replay the saved answers: search with each model's saved line
  name and guess, and count how often the right reference is among the candidates, alone and
  together with the model's own guess. Also search each answer-key reference on both sources
  for coverage. About 500 to 700 of Serper's 2,500 free credits. If the right reference is
  not in the candidates clearly more often than the model's own guess is right, stop.
- **Stage 1, paid.** One run with the new prompt, then ranking, then the second call where
  needed. The pipeline's answer is compared with the model's own first guess from the same
  call, so run-to-run noise does not blur the result.

Search responses are third-party content. They are saved locally and kept out of git.

### Idea 1, stage 0 result (2026-10-06)

**Measured.** `search_study.py` replayed the saved answers of four models through Serper: 618
searches, 618 credits, no model call. Full tables are in `results/SEARCH_STUDY.md`, rebuilt for
free by `search_study.py report`. Serper's account page showed 1,882 of the 2,500 free credits
left afterwards.

Is the right reference available to pick from? 99 photos, row 12 left out:

| Right reference is the model's own answer, or among the candidates from | Opus 5.5 | Sonnet 5.5 | Sol | DeepSeek |
|---|---:|---:|---:|---:|
| nothing else (the model's own answer) | 79 | 72 | 70 | 44 |
| WatchBase, searched by model line | 88 | 83 | 79 | 56 |
| WatchBase, by model line and by the model part of the reference | 88 | 87 | 81 | 59 |
| the open web only | 89 | 84 | 83 | 65 |
| **all three searches** | **91** | **92** | **87** | **72** |
| all three, also counting accepted look-alikes | 93 | 94 | 89 | 76 |

- **The stop rule did not trigger.** The right reference is available 12 to 28 more times in 99
  than the model's own answer is right. Of Sonnet's 27 misses, search has the right reference
  for 20; of Opus's 20, for 12.
- **This is a ceiling, not an accuracy.** The merged list has a median of 11 candidates. With
  the model's own answer first and the rest in an order that uses nothing from the photo, the
  right reference is within the first three for Opus 87, Sonnet 82, Sol 79, DeepSeek 55, and
  within the first five for 88, 87, 80, 62. Choosing from the list is stage 1.
- **No single search is enough.** The open web adds the most on its own; WatchBase adds
  watches the open web search missed, and the reverse. On Sonnet's 27 misses the right
  reference came from the line search 11 times, the guess search 7, the open web 12, and from
  at least one of them 20.
- **Watch 46**, the 2026 release every model missed, is found by the WatchBase line search.
- **A weak model gains most and still ends lowest.** DeepSeek names the wrong brand or model
  line too often for the searches to start in the right place.

WatchBase coverage of the 100 answer-key references:

| | References |
|---|---:|
| The watch's own page came back | 92 |
| Named on another WatchBase page only | 2 (`AB0138211B1A1`, `AB01761A1K1X1`) |
| Not on WatchBase | 6 (Cartier `WSSA0018`, `WSSA0022`, `WSPA0009`, `WSPN0007`, `WSTA0065`; JLC `Q4138420`) |

All eight without a page of their own were found on the open web by brand and reference
(brand sites, Chrono24, retailers). Cartier is WatchBase's weak brand: 5 of 10.

Things learned about the tools:

- A free Serper account returns at most 10 results per search; asking for 20 is refused
  ("Query pattern not allowed for free accounts").
- Google shortens page titles, so the metal, dial and strap in a WatchBase title are often cut
  off. The snippet carries more.
- Brand sites put the reference in the page title or address, so an open web search by model
  line returns references without WatchBase.
- Serper's page-reading endpoint was not used. WatchBase refuses automated reading of its
  pages, and that block was left alone.

Limits: one day's Google results; top 10 only; the model lines come from the benchmark prompt,
which asks for one reference and no dial colour; the search forms were fixed in advance and not
tuned; a list that contains the right reference is not an answer.

### Idea 1, stage 1 result (2026-10-06, incomplete: 91 of 100 photos)

**Measured.** `pipeline_study.py` ran the whole flow with Claude Sonnet 5.5, thinking off (run
`2026-10-06_134921_full`): a describing call (brand, model line, dial colour, metal, bracelet,
bezel, size, complications, up to three references), three searches, a ranking in code, and a
choosing call that sees the photo again with up to 15 candidates. Full tables are in
`results/PIPELINE_STUDY.md`, rebuilt for free by `pipeline_study.py report`.

**The run is incomplete.** The Anthropic account ran out of credit after 91 choosing calls.
Rows 92 to 100, nine of the ten Vacheron Constantin photos, have a description and searches
but no choosing call. Everything below is on the 91 photos that have both calls. Model cost so
far: $2.11 (the estimate given before the run was $1.80 to $2.00). 149 new searches were
needed; 1,738 Serper credits were left.

| Out of 91 photos | Exact reference |
|---|---:|
| Model's own first reference (the baseline, from the same call) | 61 |
| Pipeline's first choice | 61 |
| Model's own references, up to three, contain it | 72 |
| Pipeline's three choices contain it | 82 |
| It was available at all: own references or any search | 85 |

- **The first choice did not improve.** The choosing call changed the model's own first
  reference on 29 photos: 11 became right and 11 that were right became wrong. A common loss:
  the brand's current catalogue reference comes back with a full description and wins over an
  older reference that was right (`WSSA0022` lost to `WSSA0085`).
- **The list of three improved.** The right reference is among the pipeline's three choices
  on 82 photos, against 72 for the model's own three.
- **No signal yet reaches the auto-fill mark.** The choosing call said it had a clear leader on
  24 photos and was right on 21 (88%). The proposed mark is 95%, on at least 70% of uploads.
- **Ranking in code did not beat the model's own order.** With the corrected code, the first
  candidate in the code order is right 60 times and the first three contain it 74 times.
  Catalogue lines read from search results are often cut short or name colours differently
  from what is seen (Omega's "black" Railmaster dial reads as brown in the photo), and a Rolex
  reference does not fix the dial at all.
- **The describing call keeps the photo-visible fields.** Brand 91 of 91, movement 90, case
  material 89, bracelet 88. Dial colour, size and complications cannot be scored: the answer
  key has no column for them.
- **Cost and speed.** $0.022 per photo for both calls, three searches, 6.2 seconds of model
  time at the median.

**A fault in the run.** On 9 of the 91 photos the list shown to the choosing call had the
model's own first reference, which was right, moved down from first place. The code that reads
catalogue lines from snippets had attached lines to the wrong watch. The choosing call still
chose right on 7 of the 9; rows 19 and 42 are among the 11 losses. The code is corrected; the
choosing calls were not repeated.

**Worked out afterwards from the saved answers** (free; needs fresh photos to confirm):

| Way of combining the two calls | First choice right | Right one within three |
|---|---:|---:|
| Model's own first reference, then the choosing call's picks | 61 | 83 |
| The same, with the choosing call's pick first when it says clear leader | 63 | 83 |

With four options the right reference is there 84 times, with five 85.

**Also measured:** on the 90 photos both runs share, the benchmark prompt gave 64 right first
references and the new prompt 61, and the first reference was the same in only 64. Sonnet with
thinking off also varies from run to run.

**Inferred.** Search plus a second look is worth it for a tap-to-choose list (about 9 in 10
within three options on these photos) and not for filling the reference in unasked. The design
should treat `choose_one` as the normal outcome until a signal for `auto_filled` is found.

The Sonnet run was left at 91 photos: on 2026-10-06 Qutaiba chose to run DeepSeek instead of
finishing it.

### Idea 1, stage 1 on DeepSeek Flash (2026-10-06, all 100 photos)

**Measured.** The same flow with DeepSeek Flash at its default settings (run
`2026-10-06_140619_full`), with the corrected ranking code. DeepSeek cannot be held to a schema
by its API, so the shape of the answer is asked for in the prompt, as in its benchmark runs.
Model cost $0.51; 115 new searches; 1,623 Serper credits left. Both runs side by side are in
`results/PIPELINE_STUDY.md`.

| | DeepSeek, 100 photos | DeepSeek, same 91 photos as Sonnet | Sonnet, 91 photos |
|---|---:|---:|---:|
| Model's own first reference | 55 | 48 | 61 |
| Pipeline's first choice | 57 | 50 | 61 |
| Model's own references, up to three, contain it | 66 | 58 | 72 |
| Pipeline's three choices contain it | 72 | 63 | 82 |
| It was available at all | 78 | 69 | 85 |
| Model cost per photo, both calls | $0.0051 | | $0.0221 |
| Model time per photo, both calls, median | 27.1 s | | 6.2 s |

- **Same pattern, smaller gain.** The first choice moves from 55 to 57 (6 gained, 4 lost). The
  list of three moves from 66 to 72. For Sonnet the list gained 10 on 91 photos.
- **DeepSeek with the whole flow is below Sonnet with none of it.** On the same 91 photos its
  three choices contain the right reference 63 times; Sonnet's own three references, with no
  search and no second call, contain it 72 times.
- **Its ceiling is lower.** The right reference was available for 78 photos. A search that
  starts from a wrong brand, model line or guess does not reach the watch.
- **It is a quarter of the price and a quarter of the speed.** The slowest 5% of photos took
  107 seconds or more of model time.
- **Its second call often fails.** DeepSeek reasons before answering and ran out of output on
  both attempts for 11 choosing calls and 2 describing calls. For those photos the code order
  stands. The failed calls cost $0.11 of the $0.51.
- **Auto-fill is further away.** It said it had a clear leader on 28 photos and was right on 21
  (75%).
- **Its first reference was better than in the benchmark.** 55 here, against 48 and 44 in its
  two benchmark runs. The prompt here asks for a description before the reference. DeepSeek
  also varies by several points between runs, so this is not proof that the prompt helps.

### Idea 5: let the model search for itself (OpenAI web search), proposed 2026-10-06, not tested

Qutaiba asked about running OpenAI's built-in web search with GPT-6 Luna. One call would take
the photo, search the web on its own and answer, in place of Serper, the ranking code and the
second call.

**Read** (OpenAI's pricing page, web search guide and the `gpt-6-luna` model page, 2026-10-06):

- `gpt-6-luna` supports the `web_search` tool, image input and structured outputs. Its
  reasoning effort can be none, low, medium (the default), high, xhigh or max.
- The tool costs $10.00 per 1,000 search calls, and the text it retrieves is billed as input
  tokens at the model's rate. Luna's tokens cost $0.10 per million in and $0.50 out.
- Searches can be limited to chosen sites (`filters.allowed_domains`, up to 100). The amount of
  text read per search can be set (`search_context_size`). The sources can be returned.

**Reported** (search summary, not opened): the request takes `max_tool_calls`, a cap on
built-in tool calls. A forum thread title says the cap was ignored in some cases. In the
ten-photo run below the cap held.

**Inferred:**

- The search fee sets the cost, not the model. A search is $0.01 here against $0.001 through
  Serper. Three searches a photo is $0.03, more than Sonnet's whole two-call flow ($0.022) and
  six times DeepSeek's ($0.005).
- It differs from the Serper flow in three ways that could help: the model writes its own
  queries, it can open and read pages instead of ten snippets, and it can search again after
  seeing results.
- Nothing is saved between runs. Every re-run pays the fee again, and a result cannot be
  re-scored against the same search results.
- Luna alone scored 38 (no thinking) to 52 (extra-high) in the benchmark, the same class as
  DeepSeek. The DeepSeek run above showed that searching did not lift a weak model to a strong
  one's level. Whether OpenAI's search does better than snippets is not known.

**Measured on ten photos** (2026-10-06, `websearch_study.py`, run
`2026-10-06_143916_test-10img`). GPT-6 Luna at its default reasoning effort, web search on with
a limit of three searches per photo, one call per photo. The ten are the fifth photo of each
brand, a mix of easy and hard ones. The purpose was to measure the cost.

| | Ten photos |
|---|---:|
| First reference right | 9 |
| Same photos, saved benchmark runs with no search: Luna no thinking / Luna extra-high / DeepSeek / Sonnet | 7 / 5 / 5 / 6 |
| Searches, as counted by the API | 16 (1.6 a photo) |
| Search fee at $0.01 | $0.16 |
| Model tokens | $0.02 |
| Cost per photo | $0.018 |
| Time per photo, median and longest | 21 s, 69 s |

- **Cost.** About $1.80 for 100 photos at this rate, and at most about $3.20 if every photo
  used all three searches.
- **How the fee is counted.** The response states the number of searches
  (`tool_usage.web_search.num_requests`). One search held about three queries (50 queries in
  16 searches), and opening a page was not counted. The limit of three held on every photo.
- **The answer format can be enforced while searching.** No call failed.
- **What the search did.** On three photos (rows 25, 55, 95) the model's first query carried a
  wrong reference and it ended on the right one. On several others it already had the right
  reference and searched to confirm it. The one miss is row 65: it answered `WSSA0046` for
  `WSSA0022`, a watch both pipeline runs also lost to a newer Cartier reference.
- **Ten photos cannot show a gain.** One or two photos either way move the figure by 10 to 20
  points. The full 100 with search have not been run.

**Measured with search off, all 100 photos** (2026-10-06, run `2026-10-06_144623_nosearch_full`).
The same model, the same setting and the same list of fields, with no search tool. Both runs
are side by side in `results/WEBSEARCH_STUDY.md`.

| Luna, default effort, no search | 100 photos |
|---|---:|
| First reference right | 55 |
| Its references, up to three, contain it | 59 |
| Brand right | 98 |
| Cost per photo | $0.0007 |
| Time per photo, median and longest | 12 s, 33 s |
| Calls that failed | 0 |

- **On the ten photos run both ways, search took Luna from 5 right to 9.** Four photos were
  right only with search (rows 15, 35, 85, 95) and none only without it. Same model, setting
  and fields, so on this sample the gain is the search and not the prompt. It is still ten
  photos.
- **Luna alone is level with DeepSeek alone, at a third of the cost.** With this prompt and no
  search both get the first reference right 55 times in 100; Luna costs $0.0007 a photo
  against $0.0019 for DeepSeek's describing call, and none of its calls failed. On the 91
  photos the Sonnet run covers: Luna 51, DeepSeek 48, Sonnet 61.
- **The prompt or the setting matters for Luna too.** 55 here against 38 (no thinking) and 52
  (extra-high) with the benchmark prompt. The setting differs as well as the prompt, so the
  two effects cannot be separated.
- **Luna rarely offers alternatives.** It gave one reference on 62 photos, two on 31 and three
  on 7, so its list of three is hardly better than its first answer.
- **Its confidence is not a signal.** It was 0.8 or more on 62 photos and right on 40 of them.
- **With search it gives one answer, not a list.** In the ten-photo search run Luna gave a
  single reference on all ten photos. The search improves that one answer: on three of the
  four photos it gained, the queries show the search correcting a wrong reference or supplying
  one (rows 35, 85, 95); on row 15 its first query already held the right reference, so that
  one may be run-to-run variation. When the single answer is wrong (row 65) the seller has no
  right option to tap. The prompt asks for a second or third reference "only for versions you
  cannot rule out", which is part of why.

**Measured with three references always asked for** (2026-10-06 and 2026-10-07). Qutaiba chose
to change the prompt so that the model always returns its best match and the two nearest
alternatives, and to run it with search off and with search on. Same model and setting.

| Luna, default effort, three references always | Search off, 100 photos | Search off, the 90 answered | Search on, 90 photos |
|---|---:|---:|---:|
| First reference right | 50 | 46 | 61 |
| Right one within its three | 63 | 58 | 70 |
| Searches per photo | | | 2.0 |
| Cost per photo | $0.0008 | | $0.0218 |
| Time per photo, median | 14 s | | 27 s |

- **The search run is incomplete: 90 of 100 photos.** Rows 67, 78, 83, 88, 89, 91, 92, 95, 98
  and 100 have no answer. It stopped twice. On 2026-10-06 it ended after 82 photos with no
  error, most likely because the session that started it closed. It was continued on
  2026-10-07 and stopped when the OpenAI account ran out of credit. `websearch_study.py run
  --resume results\websearch\2026-10-06_153949_full --yes` finishes it for about $0.25.
- **Search lifts Luna's first answer by about 15 photos in 90.** 21 photos are right only with
  search and 6 only without it. The list of three gains 12.
- **Search also breaks some answers.** On six photos (rows 25, 40, 45, 55, 75, 87) the first
  reference was right without search and wrong with it.
- **Luna with search is still below Sonnet with none.** On the 85 photos that both this run and
  the Sonnet pipeline run cover:

  | 85 shared photos | First right | Right one within three |
  |---|---:|---:|
  | Luna, search off | 42 | 54 |
  | Luna, search on | 56 | 65 |
  | Sonnet alone (its describing call) | 60 | 70 |
  | Sonnet with the Serper pipeline | 59 | 76 |
  | DeepSeek with the Serper pipeline | 48 | 58 |

- **It is not cheap.** $0.022 a photo, the same as Sonnet's whole two-call pipeline and twice
  Sonnet's describing call alone ($0.011). The search fee is $1.76 of the $1.97 spent. Asking
  for alternatives raised the searching from 1.6 to 2.0 a photo.
- **It is slow.** 27 seconds a photo at the median, 136 at the longest.
- **Its confidence is still not a signal.** With search it was 0.9 or more on 66 photos and
  right on 52.
- **The account's rate limit matters.** OpenAI allows this account 200,000 tokens a minute for
  Luna. A search call carries 15,000 to 30,000 tokens of retrieved text, so three calls at
  once were refused 21 times. Two at once, with waits, went through.
- **Asking for three always may cost a little on the first answer.** With search off the first
  reference was right 55 times with the earlier wording and 50 with this one. One run each, so
  this may be noise.

## 5. Reference formats

**Read, Reported and Measured.** The reference structure of 19 brands is written up in
`REFERENCE_FORMATS.md`, with each rule marked confirmed, observed or unconfirmed. Two tests were
run and can be repeated with `reference_format_check.py`: 180 of 180 checks agree against the
answer key, and 155 of 155 against 90 references outside it (133 of those are real predictions).
Several claims found online failed the check and are listed there.

### Rolex references

**Reported.** The last digit of a Rolex reference is the metal: 0 steel, 1 steel and Everose gold, 3 steel and yellow gold, 4 steel and white gold, 5 Everose gold, 6 platinum, 8 yellow gold, 9 white gold. Watches with the same reference differ only in dial and bracelet style; Rolex numbers those as `126334-0001` (Oyster bracelet), `126334-0002` (Jubilee), and so on.

### Attaching the guide to the prompt (DeepSeek Flash, 2026-10-06)

**Measured.** One full run of DeepSeek Flash with the whole of `REFERENCE_FORMATS.md` added after
the standard prompt (run `2026-10-06_121718_full`, model name `deepseek-flash-guide`), compared
with the two earlier runs on the plain prompt. Full tables are in `results/GUIDE_STUDY.md`,
rebuilt for free by `guide_study.py`.

| | Plain, run 1 | Plain, run 2 | With guide |
|---|---:|---:|---:|
| Exact reference, all 100 | 48 | 44 | 52 |
| Exact reference, 80 fair rows | 37 | 35 | 39 |
| Including look-alikes | 53 | 50 | 57 |
| Brand right | 93 | 96 | 91 |
| Calls with no answer | 2 | 2 | 6 |
| Cost per image | $0.0013 | $0.0019 | $0.0021 |
| Median time | 4.9s | 5.8s | 6.4s |

- The guide prints the reference of 20 answer-key rows as examples, so the model can copy
  them. The 80 rows it does not print are the fair test: 39, against 37 and 35.
- That gain of 2 to 4 is the same size as the gap between the two plain runs, which gave the
  same answer on only 52 of 100 photos. One run cannot tell it apart from chance.
- Nine rows were wrong in both plain runs and right with the guide (six of them fair rows).
  Three rows were right in both plain runs and wrong with the guide.
- Six calls ran out of output tokens twice and returned nothing, against two on the plain
  prompt. Each cost about $0.01, so they are $0.06 of the run's $0.21.
- Input rose from about 1,200 to 11,400 tokens per photo. DeepSeek cached most of it, so the
  cost rose little.

**Measured: why it did not help.** Every miss was sorted by the kind of mistake
(`results/GUIDE_STUDY.md`). On the plain prompt, only 2 misses per run were a reference written
in the wrong format, which is the one mistake a format guide can fix. The guide fixed them: 0
remain. The other 41 to 45 misses were already in the brand's format and named the right watch,
with the wrong digits: the generation (`15202ST` for `16202ST`), the dial or version number
(`WSSA0023` for `WSSA0022`, `B487` for `B442`) or the sub-model (`IW500705` for `IW501701`).
Those digits follow no rule; they are catalog entries. With the guide 37 such misses remain.

**Inferred.** A guide tells a model how a reference is built. It does not tell it which
references exist, which is the part the models get wrong.
Not tested: a stronger model, a shorter guide with only the rules, or repeated runs.

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

### 6.4 What the listing form asks the seller

**Read** on 2026-10-06 in the mobile app (`mobile/src/screens/CreateListingScreen/`,
`mobile/src/components/createListing/`, `mobile/src/utils/listingValidation.ts`). The web
frontend has its own form in `frontend/app/create-listing/`; it was not read in detail.

| Step | Asked | Required |
|---|---|---|
| 1. Photos | Main photo, watch face, case back, bracelet, side view; extra photos or videos | All five named photos |
| 2. Details | Category, brand, reference number, model, year of manufacture, case material, bracelet material, movement type, case size | Brand and model |
| 2. Condition | Overall condition | Yes |
| 2. Description | Description, limited edition, watch gender, what's included (box, papers, extra links, service records) | No |
| 2. Service | Last service date, service details | No |
| 3. Pricing | Asking price, pricing strategy, negotiable; market estimate and price history from WatchCharts | No (the backend checks the price) |
| 4. Review | Preview and terms | |
| 5. Proof of life | A photo of the watch set to a requested time | Yes, when the backend asks for it |

- Categories are `Luxury`, `Sports`, `Vintage`, `Dress`, `Diving`, `Racing`, `Pilot`, `Smartwatch`.
- Today's auto-fill is a button beside the reference field. The seller types the reference, and a
  sheet offers brand, model, case material, bracelet material, movement type, case size and
  release year to apply.
- The app keeps a `serialNumber` value in state but shows no field for it, and `Product` has no such column.
- The form has a `caseMaterialIsAi` flag, and case and bracelet materials accept new values typed by the seller.
- `mobile/src/services/referenceNumberService.ts` has a mistyped fallback address
  (`api.chronobay.ae.ae.ae.ae`), used only when the environment value is missing.

What this changes for the auto-listing design:

- The model will receive five labelled photos, not one. The benchmark tested one photo per watch,
  so accuracy with the real input is unmeasured.
- A case-back photo is always present, so reading engraved text is possible on every listing.
- Category, watch gender, limited edition and what's included are listing fields the design had
  not covered.
- Condition is required and cannot be read reliably from photos, so the seller must still choose it.
- Year of manufacture is the year this watch was made. Today's auto-fill writes the model's release
  year into it, which is a different thing.
- The market estimate is looked up by brand and reference, so a wrong reference also gives a wrong price.

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
7. Whether the reference guide helps a strong model. It was tested once, on DeepSeek Flash
   only, and showed no clear gain (section 5).
8. What signal can decide `auto_filled`. Stage 1 (section 4) showed a second call does not
   improve the first choice and that its own "clear leader" flag is right 88% of the time.
9. Whether the stage 1 result holds on a second run, on Opus, and on real seller photos. It is
   one incomplete run on 91 web photos.

## 11. Next tests, cheapest first

| Test | Cost | Answers |
|---|---|---|
| One `/watch/specs` call | 10 credits, or none if refused | Unknown 1 |
| Replay the 100 answer-key references through `/search/watch` | 100 credits | Unknown 2 |
| Replay each model's saved answers through `/search/watch` | Up to 100 credits per model | Unknown 6 |
| Google Vision on the 100 photos, original and altered | Free tier | Unknown 4 |
| Re-run row 12 on every model | A few cents | Fixes the stale row |
| 30 to 50 phone photos of real watches through the pipeline | $1 to $3 per model | Unknown 5 |
| Guided run on a strong model, scored on the 80 rows the guide does not print | $1 to $3 | Unknown 7 |
| Serper idea 1, stage 0 | Done 2026-10-06: 618 Serper credits | Section 4, "Idea 1, stage 0 result" |
| Serper idea 1, stage 1 | Run 2026-10-06, stopped at 91 of 100: $2.11 and 149 Serper credits | Section 4, "Idea 1, stage 1 result" |
| Serper idea 1, stage 1 on DeepSeek Flash | Done 2026-10-06: $0.51 and 115 Serper credits | Section 4, "Idea 1, stage 1 on DeepSeek Flash" |
| Finish the Sonnet run: nine choosing calls are missing (`pipeline_study.py run --resume`) | About $0.10; needs credit on the Anthropic account. Not pursued: Qutaiba chose DeepSeek instead | Completes that run |
| Repeat the Sonnet choosing step on all 100 with the corrected candidate order | About $1.10 | Whether the fault in that run cost anything |
| The pipeline on Opus, or a second pass on Sonnet | About $5 on Opus (estimated from its benchmark cost), about $2.20 on Sonnet | Unknown 9 |
| Serper idea 2: search the strong models' saved answers and compare titles with the photo attributes | About 300 Serper credits | How many wrong references a title check catches |
| Serper idea 3: Lens on the 100 photos, original and altered | 300 Serper credits, and the photos at a public URL | Whether reverse image search finds the watch |
