# deepseek-flash

```
deepseek-flash   -   2026-09-30 11:24 UTC   [prompt mode]
=========================================================
Accuracy (strict)    2/3   (66.7%)
Accuracy (lenient)   3/3   (100.0%)
Brand correct        3/3   (100.0%)
Confidence >= 0.8    0 answers, 0 strictly right (n/a)
Cost                 $0.0015   (rates verified 2026-09-30)
Time                 5.7s total | mean 4.77s | median 5.09s | p95 5.73s
Errors               0
```

> prompt mode: JSON asked for in the prompt, not enforced by the API — invalid/empty JSON is counted as an error, not as a wrong identification
> DeepSeek caps each image at 1,024 tokens (images are scaled to ~1300x1300 px) — less detail than the other providers get, which matters for reading small engraved text. Its score reflects that limit as much as model capability. Its price also doubles at peak hours (01-04 and 06-10 UTC, weekdays); cost uses the rate in force when each request started.

Provider `deepseek`, model `deepseek-flash`.

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
