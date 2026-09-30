# Comparison — FULL RUN (100 images) - run 2026-09-30_121426_full

```
MODEL                       STRICT  LENIENT       COST   $/IMAGE    MEAN     P95  MODE
claude-sonnet-5-5-nothink    72.0%    77.0%    $0.8442   $0.0084   2.56s   3.56s  schema
```

Strict = exact reference (notation normalized). Lenient = also look-alikes listed in the answer key and strap/bracelet variants of the same watch. One pass per image unless noted: these models are non-deterministic, so a single pass carries unmeasured spread, and numbers from different sessions or prompt versions are not comparable.
