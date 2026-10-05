# Comparison — FULL RUN (100 images) - run 2026-10-05_092041_full

```
MODEL                       STRICT  LENIENT       COST   $/IMAGE    MEAN     P95  MODE
gpt-6-luna-xhigh             52.0%    54.0%    $0.1012   $0.0010  18.39s  38.92s  schema
gpt-6-luna-nothink           38.0%    41.0%    $0.0287   $0.0003   2.75s   4.14s  schema
```

Strict = exact reference (notation normalized). Lenient = also look-alikes listed in the answer key and strap/bracelet variants of the same watch. One pass per image unless noted: these models are non-deterministic, so a single pass carries unmeasured spread, and numbers from different sessions or prompt versions are not comparable.
