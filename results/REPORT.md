# ChronoBay watch-identification benchmark

Updated 2026-09-30 14:56. 100 watches in the answer key. This page is rebuilt after every run; the detailed reports it links to are never changed.

## Latest result per model

| Model | Exact reference | Incl. look-alikes | Brand right | Cost / image | Median time | Errors | Images | Run | Detailed report |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| **deepseek-flash** | **48.0%** (48/100) | 53.0% | 93.0% | $0.0013 | 4.9s | 2 | 100 | 2026-09-30 11:24 | [deepseek-flash.md](runs/2026-09-30_112454_full/deepseek-flash.md) |

## Exact reference by brand

| Brand | deepseek-flash |
|---|---:|
| Audemars Piguet | 2/10 |
| Breitling | 3/10 |
| Cartier | 6/10 |
| IWC | 3/10 |
| Jaeger-LeCoultre | 3/10 |
| Omega | 6/10 |
| Patek Philippe | 6/10 |
| Rolex | 8/10 |
| Tag Heuer | 5/10 |
| Vacheron Constantin | 6/10 |

## Read before comparing

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
| 2026-09-30_112454_full | deepseek-flash | 100 | [summary](runs/2026-09-30_112454_full/summary.md) | [deepseek-flash](runs/2026-09-30_112454_full/deepseek-flash.md) |

## Test runs

A subset of the images, to check that a model or setting works before paying for a full run. Not comparable with full runs — a few images say little about accuracy.

| Run | Models | Images | Summary | Detailed reports |
|---|---|---:|---|---|
| 2026-09-30_112430_test-3img | deepseek-flash | 3 of 100 | [summary](runs/2026-09-30_112430_test-3img/summary.md) | [deepseek-flash](runs/2026-09-30_112430_test-3img/deepseek-flash.md) |
