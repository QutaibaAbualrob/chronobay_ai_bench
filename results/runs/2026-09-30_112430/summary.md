# Comparison — run 2026-09-30_112430

```
MODEL                       STRICT  LENIENT       COST   $/IMAGE    MEAN     P95  MODE
deepseek-flash               66.7%   100.0%    $0.0015   $0.0005   4.77s   5.73s  prompt !
```

## Read before comparing

- **deepseek-flash** — prompt mode: JSON asked for in the prompt, not enforced by the API — invalid/empty JSON is counted as an error, not as a wrong identification. 0 of its 1 misses were invalid or empty JSON rather than wrong answers.
- **deepseek-flash** — DeepSeek caps each image at 1,024 tokens (images are scaled to ~1300x1300 px) — less detail than the other providers get, which matters for reading small engraved text. Its score reflects that limit as much as model capability. Its price also doubles at peak hours (01-04 and 06-10 UTC, weekdays); cost uses the rate in force when each request started.

Strict = exact reference (notation normalized). Lenient = also look-alikes listed in the answer key and strap/bracelet variants of the same watch. One pass per image unless noted: these models are non-deterministic, so a single pass carries unmeasured spread, and numbers from different sessions or prompt versions are not comparable.
