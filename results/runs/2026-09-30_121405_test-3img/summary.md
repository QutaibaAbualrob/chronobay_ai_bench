# Comparison — TEST RUN (3 of 100 images) - run 2026-09-30_121405_test-3img

> **TEST RUN** — only 3 of the 100 images. It checks that the model works; don't compare its accuracy with full runs.

```
MODEL                       STRICT  LENIENT       COST   $/IMAGE    MEAN     P95  MODE
claude-sonnet-5-5-nothink    66.7%   100.0%    $0.0339   $0.0113   4.23s   4.68s  schema
```

Strict = exact reference (notation normalized). Lenient = also look-alikes listed in the answer key and strap/bracelet variants of the same watch. One pass per image unless noted: these models are non-deterministic, so a single pass carries unmeasured spread, and numbers from different sessions or prompt versions are not comparable.
