# claude-sonnet-5-5-nothink — TEST RUN (3 of 100 images)

> **TEST RUN** — only 3 of the 100 images. It checks that the model works; don't compare its accuracy with full runs.

```
claude-sonnet-5-5-nothink   -   TEST RUN (3 of 100 images)   -   2026-09-30 12:14 UTC   [schema mode]
========================================================================
Accuracy (strict)    2/3   (66.7%)
Accuracy (lenient)   3/3   (100.0%)
Brand correct        3/3   (100.0%)
Confidence >= 0.8    2 answers, 2 strictly right (100.0%)
Cost                 $0.0339   (rates verified 2026-09-30)
Time                 4.7s total | mean 4.23s | median 4.41s | p95 4.68s
Errors               0
```

Provider `anthropic`, model `claude-sonnet-5-5`, options `{"thinking": "between_tools", "effort": "high"}`.

**Strict**: the exact reference (notation normalized). **Lenient**: also counts look-alikes listed in `also_accept` and the same watch on a different strap/bracelet. Errors count as failures.

## By brand

| Brand | Images | Strict | Lenient |
|---|---:|---:|---:|
| Omega | 1 | 0 (0.0%) | 1 (100.0%) |
| Patek Philippe | 1 | 1 (100.0%) | 1 (100.0%) |
| Rolex | 1 | 1 (100.0%) | 1 (100.0%) |

## Not strictly correct (1)

| # | Image | Expected | Got | Lenient | Error |
|---:|---|---|---|---|---|
| 11 | 011_omega_speedmaster-moonwatch-professional.jpg | `310.30.42.50.01.002` | `310.30.42.50.01.001` | yes (look-alike) |  |
