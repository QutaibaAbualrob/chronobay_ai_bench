# Guide study: does attaching the reference guide help?

Model: `deepseek-flash`. Guide: `REFERENCE_FORMATS.md` (28,698 characters), added after the standard prompt. Rebuilt by `guide_study.py` from saved answers.

The guide prints the reference of **20 answer-key rows** as examples (rows 1, 4, 7, 9, 11, 12, 16, 21, 22, 31, 43, 51, 61, 63, 71, 81, 83, 84, 91, 93). The model can copy those, so the **80 rows the guide does not print** are the fair test.

## Scores

| Run | Folder | Exact, all 100 | Exact, 80 fair rows | Exact, 20 printed rows | Incl. look-alikes | Brand right | Failed calls |
|---|---|---:|---:|---:|---:|---:|---:|
| Plain prompt, run 1 | `2026-09-30_112454_full` | 48 | 37 | 11 | 53 | 93 | 2 |
| Plain prompt, run 2 | `2026-10-05_111103_full` | 44 | 35 | 9 | 50 | 96 | 2 |
| With guide | `2026-10-06_121718_full` | 52 | 39 | 13 | 57 | 91 | 6 |

## What kind of mistake each miss was

All 100 rows. A guide to reference formats can only fix the fourth kind.

| Kind of miss | Plain prompt, run 1 | Plain prompt, run 2 | With guide |
|---|---:|---:|---:|
| No answer | 2 | 2 | 6 |
| Wrong brand | 5 | 2 | 3 |
| Wrong model line | 2 | 5 | 2 |
| Right watch, reference not in the brand's format | 2 | 2 | 0 |
| Right watch, right format, wrong reference | 41 | 45 | 37 |

## Cost and speed

| Run | Cost per image | Median time | Slowest 5% start at | Input tokens | of which cached | Output tokens |
|---|---:|---:|---:|---:|---:|---:|
| Plain prompt, run 1 | $0.0013 | 4.9s | 43.5s | 1,249 | 227 | 1,916 |
| Plain prompt, run 2 | $0.0019 | 5.8s | 53.4s | 1,207 | 1,001 | 3,031 |
| With guide | $0.0021 | 6.4s | 80.1s | 11,403 | 9,970 | 3,107 |

## Exact matches by brand, 80 fair rows

| Brand | Fair rows | Plain prompt, run 1 | Plain prompt, run 2 | With guide |
|---|---:|---:|---:|---:|
| Audemars Piguet | 9 | 1 | 3 | 3 |
| Breitling | 9 | 3 | 3 | 4 |
| Cartier | 8 | 5 | 4 | 6 |
| IWC | 9 | 2 | 3 | 2 |
| Jaeger-LeCoultre | 7 | 3 | 1 | 1 |
| Omega | 7 | 5 | 5 | 5 |
| Patek Philippe | 8 | 4 | 3 | 5 |
| Rolex | 6 | 5 | 4 | 5 |
| Tag Heuer | 9 | 4 | 4 | 3 |
| Vacheron Constantin | 8 | 5 | 5 | 5 |

## What changed, row by row

The plain runs disagree with each other, so rows are grouped by what the plain prompt did across its 2 runs.

| Plain prompt | Rows | Right with guide | of which fair rows |
|---|---:|---:|---:|
| Right in every run | 34 | 31 | 24 of 27 |
| Right in some runs | 24 | 12 | 9 of 18 |
| Wrong in every run | 42 | 9 | 6 of 35 |

### Gained: wrong in every plain run, right with the guide (9)

| Row | Brand | Expected | Plain prompt, run 1 | Plain prompt, run 2 | With guide | Printed in guide |
|---:|---|---|---|---|---|---|
| 2 | Rolex | `126500LN` | `116500LN` | `116500LN-0002` | `126500LN` |  |
| 4 | Rolex | `126334` | `126234-0026` | `126234` | `126334-0023` | yes |
| 12 | Omega | `210.30.42.20.01.010` | `AB2010121B1A1` | `210.90.42.20.01.001` | `210.30.42.20.01.010` | yes |
| 30 | Patek Philippe | `4910/1200A-001` | `4910/1200A-010` | `4910/10A-012` | `4910/1200A-001` |  |
| 39 | Audemars Piguet | `26405CE.OO.A002CA.01` | `26703ST.OO.A002CA.01` | `26703ST.OO.A010CA.01` | `26405CE.OO.A002CA.01` |  |
| 58 | Breitling | `E79363101B1E1` | `E7936310/BC27/152E` | `E76325E5/BC02` | `E79363101B1E1` |  |
| 59 | Breitling | `AB01761A1K1X1` | `A25310241K1X1` | `AB01761A1A1` | `AB01761A1K1X1` |  |
| 62 | Cartier | `WSTA0041` | `W5200025` | `W5200003` | `WSTA0041` |  |
| 83 | Jaeger-LeCoultre | `Q9008180` | `Q9008480` | `Q9008480` | `Q9008180` | yes |

### Lost: right in every plain run, wrong with the guide (3)

| Row | Brand | Expected | Plain prompt, run 1 | Plain prompt, run 2 | With guide | Printed in guide |
|---:|---|---|---|---|---|---|
| 6 | Rolex | `124270` | `124270` | `124270` | `214270-0003` |  |
| 42 | Tag Heuer | `CAW211P.FC6356` | `CAW211P.FC6356` | `CAW211P.FC6356` | `CAW2111.FC6183` |  |
| 52 | Breitling | `A17375211B1S1` | `A17375211B1S1` | `A17375211B1S1` | `A17375E71B1S1` |  |

## Rows printed in the guide

Audemars Piguet 1, Breitling 1, Cartier 2, IWC 1, Jaeger-LeCoultre 3, Omega 3, Patek Philippe 2, Rolex 4, Tag Heuer 1, Vacheron Constantin 2.
