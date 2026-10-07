# Pipeline study: describe, search, choose

Stage 1 of Serper idea 1 (`FINDINGS.md`, section 4). Rebuilt by `pipeline_study.py report` from saved answers and saved searches.

Each photo gets one describing call (brand, model line, what is visible, up to three references), three web searches, a ranking in code, and one choosing call that sees the photo again with up to 15 candidates. "Own" is what the model gave in the describing call; "pipeline" is what comes out at the end. Both are from the same run, so they can be compared.

| Run | Model | Photos with both calls | Own first reference right | Pipeline's first choice right | Own three contain it | Pipeline's three contain it | Available at all | Model cost per photo |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| [2026-10-06_134921_full](pipeline/2026-10-06_134921_full/report.md) | claude-sonnet-5-5-nothink | 91 of 100 | 61 (67%) | 61 (67%) | 72 (79%) | 82 (90%) | 85 (93%) | $0.0221 |
| [2026-10-06_140619_full](pipeline/2026-10-06_140619_full/report.md) | deepseek-flash | 100 of 100 | 55 (55%) | 57 (57%) | 66 (66%) | 72 (72%) | 78 (78%) | $0.0051 |

Counts are exact references. Runs with different numbers of photos compare by the percentages.

## Read before comparing

- `2026-10-06_134921_full` is incomplete: 9 photos have no choosing call. Its counts cover only the photos that have both calls.
- `2026-10-06_134921_full`: Stopped at 91 of 100 photos on 2026-10-06 when the Anthropic account ran out of credit. Rows 92 to 100, nine of the ten Vacheron Constantin photos, have no choosing call. Left unfinished at Qutaiba's decision.
- `2026-10-06_134921_full`: In this run the code that reads catalogue lines from search results attached lines to the wrong watch, which moved some right references down the list the choosing call saw. The code was corrected afterwards and the choosing calls were not repeated. The code-ranking figures use the corrected code.

## What the columns mean

- **Own first reference right**: the first reference of the describing call. This is the model with no search and no second call.
- **Pipeline's first choice right**: the first reference after search and the choosing call.
- **Own three / pipeline's three contain it**: the right reference is among up to three options, which is what a seller would be shown to tap.
- **Available at all**: the right reference was among the model's own references or anything the searches returned. Nothing can do better than this without another source.
