# Comparison — FULL RUN (100 images) - run 2026-09-30_112454_full

```
MODEL                       STRICT  LENIENT       COST   $/IMAGE    MEAN     P95  MODE
deepseek-flash               48.0%    53.0%    $0.1304   $0.0013  10.87s  43.50s  prompt !
```

## Read before comparing

- **deepseek-flash** — prompt mode: JSON asked for in the prompt, not enforced by the API — invalid/empty JSON is counted as an error, not as a wrong identification. 2 of its 52 misses were invalid or empty JSON rather than wrong answers.
- **deepseek-flash** — DeepSeek caps each image at 1,024 tokens (images are scaled to ~1300x1300 px) — less detail than the other providers get, which matters for reading small engraved text. Its score reflects that limit as much as model capability. Its price also doubles at peak hours (01-04 and 06-10 UTC, weekdays); cost uses the rate in force when each request started.
- **deepseek-flash** — errors: 2 (2 schema-parse); each counts as a failure.

Strict = exact reference (notation normalized). Lenient = also look-alikes listed in the answer key and strap/bracelet variants of the same watch. One pass per image unless noted: these models are non-deterministic, so a single pass carries unmeasured spread, and numbers from different sessions or prompt versions are not comparable.
