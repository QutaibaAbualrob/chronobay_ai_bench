# Comparison — TEST RUN (3 of 100 images) - run 2026-10-01_100948_test-3img

> **TEST RUN** — only 3 of the 100 images. It checks that the model works; don't compare its accuracy with full runs.

```
MODEL                       STRICT  LENIENT       COST   $/IMAGE    MEAN     P95  MODE
gpt-6-luna                  100.0%   100.0%    $0.0016   $0.0005   8.72s  10.03s  schema
```

Strict = exact reference (notation normalized). Lenient = also look-alikes listed in the answer key and strap/bracelet variants of the same watch. One pass per image unless noted: these models are non-deterministic, so a single pass carries unmeasured spread, and numbers from different sessions or prompt versions are not comparable.
