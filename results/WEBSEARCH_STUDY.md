# Web search study: the model searches for itself

Idea 5 in `FINDINGS.md`, section 4. Rebuilt by `websearch_study.py report` from saved answers.

One call per photo to an OpenAI model. With search on, the model may search the web a limited number of times before it answers; with search off it answers from the photo alone. The answer is a description and up to three references.

| Run | Model | Search | References asked for | Photos | First reference right | Its three contain it | Searches per photo | Cost per photo | Time, median |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| [2026-10-06_143916_test-10img](websearch/2026-10-06_143916_test-10img/report.md) | gpt-6-luna (default effort) | on, limit 3 | up to three | 10 | 9 (90%) | 9 (90%) | 1.6 | $0.0181 | 20.9s |
| [2026-10-06_144623_nosearch_full](websearch/2026-10-06_144623_nosearch_full/report.md) | gpt-6-luna (default effort) | off | up to three | 100 | 55 (55%) | 59 (59%) | 0.0 | $0.0007 | 12.0s |
| [2026-10-06_153026_nosearch_full](websearch/2026-10-06_153026_nosearch_full/report.md) | gpt-6-luna (default effort) | off | always three | 100 | 50 (50%) | 63 (63%) | 0.0 | $0.0008 | 13.6s |
| [2026-10-06_153949_full](websearch/2026-10-06_153949_full/report.md) | gpt-6-luna (default effort) | on, limit 3 | always three | 90 of 100 | 61 (68%) | 70 (78%) | 2.0 | $0.0218 | 27.4s |

## Search on against search off, same photos

Same model, same setting and the same way of asking for references. Only the photos both runs have are counted.

| Search on | Search off | References asked for | Photos in both | First right: on | First right: off | Right with search only | Right without search only | Three contain it: on | Three contain it: off |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `2026-10-06_143916_test-10img` | `2026-10-06_144623_nosearch_full` | up to three | 10 | 9 | 5 | 4 | 0 | 9 | 5 |
| `2026-10-06_153949_full` | `2026-10-06_153026_nosearch_full` | always three | 90 | 61 | 46 | 21 | 6 | 70 | 58 |

Counts are exact references. A run on part of the photos is a test run: it shows cost and whether the flow works, and its accuracy moves a lot with one or two photos.

The cost of a search run is the model's tokens plus OpenAI's fee of $0.01 a search (price checked 2026-10-06), counted from what each response reports.
