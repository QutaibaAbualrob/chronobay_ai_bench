# ChronoBay watch-identification benchmark

Updated 2026-10-06 15:25. 100 watches in the answer key. This page is rebuilt after every run; the detailed reports it links to are never changed.

## Latest result per model

| Model | Exact reference | Incl. look-alikes | Brand right | Cost / image | Median time | Errors | Images | Run | Detailed report |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| **claude-opus-5-5** | **79.0%** (79/100) | 84.0% | 100.0% | $0.0223 | 6.2s | 0 | 100 | 2026-09-30 12:51 | [claude-opus-5-5.md](runs/2026-09-30_125151_full/claude-opus-5-5.md) |
| **claude-sonnet-5-5-nothink** | **72.0%** (72/100) | 77.0% | 100.0% | $0.0084 | 2.5s | 0 | 100 | 2026-09-30 12:14 | [claude-sonnet-5-5-nothink.md](runs/2026-09-30_121426_full/claude-sonnet-5-5-nothink.md) |
| **gpt-6.1-sol-low** | **70.0%** (70/100) | 77.0% | 100.0% | $0.0070 | 6.0s | 0 | 100 | 2026-10-05 09:33 | [gpt-6.1-sol-low.md](runs/2026-10-05_093336_full/gpt-6.1-sol-low.md) |
| **gpt-6-luna-xhigh** | **52.0%** (52/100) | 54.0% | 98.0% | $0.0010 | 15.3s | 0 | 100 | 2026-10-05 09:21 | [gpt-6-luna-xhigh.md](runs/2026-10-05_092041_full/gpt-6-luna-xhigh.md) |
| **deepseek-flash-guide** | **52.0%** (52/100) | 57.0% | 91.0% | $0.0021 | 6.4s | 6 | 100 | 2026-10-06 12:17 | [deepseek-flash-guide.md](runs/2026-10-06_121718_full/deepseek-flash-guide.md) |
| **deepseek-flash** | **44.0%** (44/100) | 50.0% | 96.0% | $0.0019 | 5.8s | 2 | 100 | 2026-10-05 11:11 | [deepseek-flash.md](runs/2026-10-05_111103_full/deepseek-flash.md) |
| **gpt-6-luna-nothink** | **38.0%** (38/100) | 41.0% | 97.0% | $0.0003 | 2.5s | 0 | 100 | 2026-10-05 09:20 | [gpt-6-luna-nothink.md](runs/2026-10-05_092041_full/gpt-6-luna-nothink.md) |
| **claude-haiku-4-5** | **11.0%** (11/100) | 16.0% | 89.0% | $0.0025 | 1.5s | 0 | 100 | 2026-09-30 12:56 | [claude-haiku-4-5.md](runs/2026-10-1_125653_full/claude-haiku-4-5.md) |
| **gpt-6-luna** (TEST RUN only) | **100.0%** (3/3) | 100.0% | 100.0% | $0.0005 | 8.4s | 0 | 3 of 100 | 2026-10-01 10:09 | [gpt-6-luna.md](runs/2026-10-01_100948_test-3img/gpt-6-luna.md) |

## Exact reference by brand

| Brand | claude-opus-5-5 | claude-sonnet-5-5-nothink | gpt-6.1-sol-low | gpt-6-luna-xhigh | deepseek-flash-guide | deepseek-flash | gpt-6-luna-nothink | claude-haiku-4-5 | gpt-6-luna |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Audemars Piguet | 7/10 | 6/10 | 6/10 | 5/10 | 4/10 | 4/10 | 4/10 | 1/10 | — |
| Breitling | 7/10 | 9/10 | 5/10 | 3/10 | 4/10 | 3/10 | 3/10 | 0/10 | — |
| Cartier | 8/10 | 6/10 | 6/10 | 4/10 | 8/10 | 5/10 | 6/10 | 0/10 | — |
| IWC | 7/10 | 9/10 | 6/10 | 3/10 | 3/10 | 4/10 | 3/10 | 1/10 | — |
| Jaeger-LeCoultre | 7/10 | 4/10 | 5/10 | 3/10 | 2/10 | 2/10 | 2/10 | 1/10 | — |
| Omega | 7/10 | 6/10 | 8/10 | 7/10 | 6/10 | 5/10 | 4/10 | 3/10 | 1/1 |
| Patek Philippe | 10/10 | 8/10 | 10/10 | 8/10 | 7/10 | 5/10 | 5/10 | 2/10 | 1/1 |
| Rolex | 10/10 | 10/10 | 7/10 | 8/10 | 8/10 | 6/10 | 5/10 | 2/10 | 1/1 |
| Tag Heuer | 9/10 | 6/10 | 8/10 | 6/10 | 4/10 | 4/10 | 3/10 | 1/10 | — |
| Vacheron Constantin | 7/10 | 8/10 | 9/10 | 5/10 | 6/10 | 6/10 | 3/10 | 0/10 | — |

## Read before comparing

- **deepseek-flash-guide** — given `REFERENCE_FORMATS.md` after the prompt, so it is not comparable with the other rows. That file prints some answer-key references, which the model can copy; see [GUIDE_STUDY.md](GUIDE_STUDY.md) for the score without them.
- **deepseek-flash-guide** — prompt mode: JSON asked for in the prompt, not enforced by the API — invalid/empty JSON is counted as an error, not as a wrong identification.
- **deepseek-flash-guide** — DeepSeek caps each image at 1,024 tokens (images are scaled to ~1300x1300 px) — less detail than the other providers get, which matters for reading small engraved text. Its score reflects that limit as much as model capability. Its price also doubles at peak hours (01-04 and 06-10 UTC, weekdays); cost uses the rate in force when each request started.
- **deepseek-flash** — prompt mode: JSON asked for in the prompt, not enforced by the API — invalid/empty JSON is counted as an error, not as a wrong identification.
- **deepseek-flash** — DeepSeek caps each image at 1,024 tokens (images are scaled to ~1300x1300 px) — less detail than the other providers get, which matters for reading small engraved text. Its score reflects that limit as much as model capability. Its price also doubles at peak hours (01-04 and 06-10 UTC, weekdays); cost uses the rate in force when each request started.

## What the columns mean

- **Exact reference** — the model named the exact reference number (notation normalized: case, spaces and `. - /` ignored). This is the headline number.
- **Incl. look-alikes** — also counts references a photo can't tell apart (another size, the previous generation — listed per watch in the answer key) and the same watch on another strap.
- **Errors** — calls with no usable answer (timeouts, refusals, empty or invalid JSON). They count as misses and are listed in the detailed report.
- A single pass per image carries unmeasured spread; results from different prompts or sessions are not directly comparable.

## Full runs

Every image in the answer key (100). Compare these.

| Run | Models | Images | Summary | Detailed reports |
|---|---|---:|---|---|
| 2026-10-1_125653_full | claude-haiku-4-5 | 100 | [summary](runs/2026-10-1_125653_full/summary.md) | [claude-haiku-4-5](runs/2026-10-1_125653_full/claude-haiku-4-5.md) |
| 2026-10-06_121718_full | deepseek-flash-guide | 100 | [summary](runs/2026-10-06_121718_full/summary.md) | [deepseek-flash-guide](runs/2026-10-06_121718_full/deepseek-flash-guide.md) |
| 2026-10-05_111103_full | deepseek-flash | 100 | [summary](runs/2026-10-05_111103_full/summary.md) | [deepseek-flash](runs/2026-10-05_111103_full/deepseek-flash.md) |
| 2026-10-05_093336_full | gpt-6.1-sol-low | 100 | [summary](runs/2026-10-05_093336_full/summary.md) | [gpt-6.1-sol-low](runs/2026-10-05_093336_full/gpt-6.1-sol-low.md) |
| 2026-10-05_092041_full | gpt-6-luna-nothink, gpt-6-luna-xhigh | 100 | [summary](runs/2026-10-05_092041_full/summary.md) | [gpt-6-luna-nothink](runs/2026-10-05_092041_full/gpt-6-luna-nothink.md), [gpt-6-luna-xhigh](runs/2026-10-05_092041_full/gpt-6-luna-xhigh.md) |
| 2026-09-30_125151_full | claude-opus-5-5 | 100 | [summary](runs/2026-09-30_125151_full/summary.md) | [claude-opus-5-5](runs/2026-09-30_125151_full/claude-opus-5-5.md) |
| 2026-09-30_121426_full | claude-sonnet-5-5-nothink | 100 | [summary](runs/2026-09-30_121426_full/summary.md) | [claude-sonnet-5-5-nothink](runs/2026-09-30_121426_full/claude-sonnet-5-5-nothink.md) |
| 2026-09-30_112454_full | deepseek-flash | 100 | [summary](runs/2026-09-30_112454_full/summary.md) | [deepseek-flash](runs/2026-09-30_112454_full/deepseek-flash.md) |

## Test runs

A subset of the images, to check that a model or setting works before paying for a full run. Not comparable with full runs — a few images say little about accuracy.

| Run | Models | Images | Summary | Detailed reports |
|---|---|---:|---|---|
| 2026-10-01_100948_test-3img | gpt-6-luna | 3 of 100 | [summary](runs/2026-10-01_100948_test-3img/summary.md) | [gpt-6-luna](runs/2026-10-01_100948_test-3img/gpt-6-luna.md) |
| 2026-09-30_121405_test-3img | claude-sonnet-5-5-nothink | 3 of 100 | [summary](runs/2026-09-30_121405_test-3img/summary.md) | [claude-sonnet-5-5-nothink](runs/2026-09-30_121405_test-3img/claude-sonnet-5-5-nothink.md) |
| 2026-09-30_112430_test-3img | deepseek-flash | 3 of 100 | [summary](runs/2026-09-30_112430_test-3img/summary.md) | [deepseek-flash](runs/2026-09-30_112430_test-3img/deepseek-flash.md) |
