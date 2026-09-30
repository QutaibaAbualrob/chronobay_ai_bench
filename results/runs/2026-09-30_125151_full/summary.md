# Comparison — FULL RUN (100 images) - run 2026-09-30_125151_full

```
MODEL                       STRICT  LENIENT       COST   $/IMAGE    MEAN     P95  MODE
claude-opus-5-5              79.0%    84.0%    $2.2296   $0.0223   6.89s  10.83s  schema
```

Strict = exact reference (notation normalized). Lenient = also look-alikes listed in the answer key and strap/bracelet variants of the same watch. One pass per image unless noted: these models are non-deterministic, so a single pass carries unmeasured spread, and numbers from different sessions or prompt versions are not comparable.
