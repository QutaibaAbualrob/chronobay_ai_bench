# Comparison — FULL RUN (100 images) - run 2026-09-30_125653_full

```
MODEL                       STRICT  LENIENT       COST   $/IMAGE    MEAN     P95  MODE
claude-haiku-4-5             11.0%    16.0%    $0.2509   $0.0025   1.66s   3.12s  schema
```

Strict = exact reference (notation normalized). Lenient = also look-alikes listed in the answer key and strap/bracelet variants of the same watch. One pass per image unless noted: these models are non-deterministic, so a single pass carries unmeasured spread, and numbers from different sessions or prompt versions are not comparable.
