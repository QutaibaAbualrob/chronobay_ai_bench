# Pipeline study: describe, search, choose - FULL RUN (100 images)

Stage 1 of Serper idea 1 (`FINDINGS.md`, section 4). Rebuilt by `pipeline_study.py report` from saved answers and saved searches.

Run `2026-10-06_140619_full`, model `deepseek-flash` (`deepseek-flash`, default settings). 100 photos. Each photo gets one describing call, three web searches, a ranking in code, and one choosing call that sees the photo again with up to 15 candidates.

## Result

Out of 100 photos.

| | Exact reference | Also counting accepted look-alikes |
|---|---:|---:|
| Model's own first reference (the baseline, from the same call) | 55 | 61 |
| **Pipeline's first choice** | 57 | 61 |
| Model's own references, up to three, contain it | 66 | 70 |
| **Pipeline's choices, up to three, contain it** | 72 | 75 |
| It was among the candidates shown to the choosing call | 78 | 83 |
| It was available at all: own references or any search (the ceiling) | 78 | 83 |

Code ranking alone, with no second call:

| | Exact reference | Also counting accepted look-alikes |
|---|---:|---:|
| First in the code order | 56 | 62 |
| Within the first three of the code order | 69 | 74 |

## What the pipeline changed

First choice against the model's own first reference: **6 gained, 4 lost**.

### Gained: own first reference wrong, pipeline's first choice right (6)

| Row | Expected | Model's own first | Pipeline chose | Reason the model gave |
|---:|---|---|---|---|
| 2 | `126500LN` | `116500LN` | `126500LN` | The photo shows a steel Cosmograph Daytona with a black dial whose three subdials have silver rings, a black Cerachrom tachymeter bezel and a steel O… |
| 12 | `210.30.42.20.01.010` | `210.30.42.20.01.002` | `210.30.42.20.01.010` | The dial has no date window, a black wave-pattern dial, and the watch is on a steel Milanese mesh bracelet, which points to the no-date Seamaster Div… |
| 44 | `WAZ1110.BA0875` | `WAZ1010.BA0842` | `WAZ1110.BA0875` | The photo shows a black dial in a steel 41mm case with a black coated bezel, three hands, a small date window at 3 and no chronograph pushers, exactl… |
| 58 | `E79363101B1E1` | `E7936310` | `E79363101B1E1` | The photo shows a plain black dial with no special-edition logo or markings (ruling out the American Airlines and MQ-9A Reaper variants) mounted on a… |
| 84 | `Q4018420` | `Q1548530` | `Q4018420` | The photo shows a plain silver dial with applied Arabic 12/6/9 and dart-shaped markers, a blued seconds hand, a white date window at 3 and a steel 40… |
| 85 | `Q9028181` | `Q9028471` | `Q9028181` | The photo shows a steel Polaris Chronograph with a blue dial and matching steel bracelet, which eliminates the black-dial (Q9028170, Q9028471), grey-… |

### Lost: own first reference right, pipeline's first choice wrong (4)

| Row | Expected | Model's own first | Pipeline chose | Reason the model gave |
|---:|---|---|---|---|
| 20 | `424.13.40.20.02.001` | `424.13.40.20.02.001` | `424.13.40.20.02.002` | The photo shows a plain silver/white dial with applied Roman numerals at 12/3/6/9, dauphine hands, date at 3, steel case on a black leather strap — t… |
| 65 | `WSSA0022` | `WSSA0022` | `WSSA0085` | The watch on its steel case has a silvered dial with Roman numerals, blued sword hands and a navy blue alligator strap, which matches the steel Santo… |
| 67 | `WSPN0007` | `WSPN0007` | `WSPN0015` | The watch has a plain polished steel bezel with no diamonds, a steel case and multi-link steel bracelet, and a silvered Roman-numeral dial with no da… |
| 78 | `IW328903` | `IW328903` | `IW328908` | The photo shows a 40mm steel Ingenieur with the grid-textured teal-green dial, applied baton markers, date at 3 and integrated steel bracelet, which… |

## Outcomes

What the seller would see. `auto_filled`: the choosing call said one candidate stands clear. `choose_one`: it ranked up to three and the seller taps. `not_identified`: it said none fit, or nothing was read from the photo.

| Outcome | Photos | Right reference delivered | Share right |
|---|---:|---:|---:|
| `auto_filled` | 28 | 21 (filled in is right) | 75% |
| `choose_one` | 69 | 49 (is among the options) | 71% |
| `not_identified` | 3 | 0 (was available all the same) | 0% |

Proposed pass marks in `AUTO_LISTING_SPEC.md`, section 10: `auto_filled` right at least 95 times in 100, `choose_one` options contain the right watch at least 95 times in 100, at least 70% of uploads `auto_filled`.

## Worked out after the run

These combinations were tried on the saved answers after the results were known. They cost nothing, and they need a fresh set of photos before they can be trusted.

| Way of combining the two calls | First choice right | Right one within the options |
|---|---:|---:|
| Model's own references only (no search, no second call) | 55 | 66 of three |
| The choosing call's ranking as it is | 57 | 72 of three |
| Model's own first reference, then the choosing call's picks | 55 | 72 of three, 72 of four, 72 of five |
| The same, but the choosing call's pick goes first when it says it has a clear leader | 57 | 72 of three |

When to trust the first choice:

| Signal | Photos | First choice right |
|---|---:|---:|
| The choosing call kept the model's own first reference | 74 | 51 |
| The choosing call changed it | 23 | 6 (the model's own first was right on 4) |
| The choosing call said it had a clear leader | 28 | 21 |
| Kept the model's own first and said clear leader | 21 | 18 |
| The describing call's own confidence was 0.8 or more | 14 | 10 |

The list shown to the choosing call never had a right own first reference moved down from first place.

## The describing call

Fields the answer key can check, out of 98 answered photos.

| Field | Right |
|---|---:|
| Brand | 96 |
| Movement | 95 |
| Case material (gold colours counted as gold; two-tone has no match in the key) | 92 |
| Bracelet material | 97 |

Dial colour, bezel, size and complications have no column in the answer key and are not scored.

References given per photo: one 4, two 12, three 82.

## Cost and speed

| | Per photo |
|---|---:|
| Describing call | $0.0019 |
| Choosing call | $0.0032 |
| Both calls | $0.0051 |
| Web searches | 2.9 |
| Candidates found (median) | 12 |
| Model time, both calls, median | 27.1s |
| Model time, slowest 5% start at | 107.4s |

Model cost of the run: $0.51. Search time is not included; the searches were made in a batch between the two calls. A search costs $0.001 at Serper's smallest paid pack (reported price).
Photos where the describing call gave no answer: 2; they count as wrong everywhere. Photos where the choosing call gave no answer: 11; for those the code order stands. Photos with no choosing call because there were fewer than two candidates: 0. Photos where an answer broke the format and was tidied to fit: 1.

## By brand

| Brand | Photos | Own first reference | Pipeline's first choice | Pipeline's three |
|---|---:|---:|---:|---:|
| Rolex | 10 | 8 | 9 | 10 |
| Omega | 10 | 4 | 4 | 7 |
| Patek Philippe | 10 | 9 | 9 | 9 |
| Audemars Piguet | 10 | 5 | 5 | 6 |
| Tag Heuer | 10 | 3 | 4 | 5 |
| Breitling | 10 | 5 | 6 | 6 |
| Cartier | 10 | 8 | 6 | 8 |
| IWC | 10 | 4 | 3 | 5 |
| Jaeger-LeCoultre | 10 | 2 | 4 | 6 |
| Vacheron Constantin | 10 | 7 | 7 | 10 |

## Every photo where the first choice is wrong (43)

| Row | Expected | Pipeline's choices | Outcome | Right one in its three | Shown to it | Available |
|---:|---|---|---|---|---|---|
| 9 | `124300` | `126000`, `124300`, `276200` | choose_one | yes | yes | yes |
| 11 | `310.30.42.50.01.002` | `310.30.42.50.01.001`, `310.30.42.50.01.002`, `310.30.42.50.01.004` | choose_one | yes | yes | yes |
| 13 | `220.10.41.21.03.001` | `231.10.42.21.03.001`, `220.10.41.21.03.001`, `231.10.42.21.06.001` | choose_one | yes | yes | yes |
| 16 | `234.32.41.21.01.001` | `233.32.41.21.01.002`, `233.92.41.21.01.001`, `233.32.41.21.01.001` | choose_one | no | yes | yes |
| 17 | `311.92.44.51.01.007` | `304.32.44.51.01.001`, `304.33.44.51.01.001`, `311.33.44.51.01.001` | choose_one | no | no | no |
| 18 | `210.90.42.20.01.001` | `210.30.42.20.01.002`, `210.30.42.20.01.010`, `210.30.42.20.06.002` | choose_one | no | no | no |
| 20 | `424.13.40.20.02.001` | `424.13.40.20.02.002`, `424.13.40.20.02.001`, `424.13.40.20.02.003` | choose_one | yes | yes | yes |
| 28 | `5270P-001` |  | not_identified | no | no | no |
| 32 | `16202ST.OO.1240ST.01` | `15400ST.OO.1220ST.03`, `15400ST.OO.1220ST.01`, `15400ST.OO.1220ST.02` | choose_one | no | no | no |
| 35 | `26574ST.OO.1220ST.02` | `26574ST.OO.1220ST.03`, `26574ST.OO.1220ST.02`, `26674ST.OO.1320ST.01` | choose_one | yes | yes | yes |
| 36 | `15210BC.OO.A002CR.01` | `15210ST.OO.A002KB.02`, `15210ST.OO.A002KB.01`, `15210ST.OO.A009KB.01` | choose_one | no | no | no |
| 38 | `15510OR.OO.1320OR.01` | `15500OR.OO.1220OR.01`, `15510OR.OO.1220OR.01`, `15400OR.OO.1220OR.03` | choose_one | no | no | no |
| 39 | `26405CE.OO.A002CA.01` | `26400IO.OO.A004CA.01`, `26400IO.OO.A004CA.02`, `26470IO.OO.A010CA.01` | choose_one | no | no | no |
| 41 | `CBN2A1B.BA0643` | `EFR-556D-1AV`, `EFR-539D-1AV` | choose_one | no | no | no |
| 42 | `CAW211P.FC6356` | `CAW2111.FC6286`, `CAW2111.FC6356`, `CAW211P.FC6356` | choose_one | yes | yes | yes |
| 43 | `WBP201A.BA0632` | `WBP2010.BA0632`, `WBP2110.BA0627`, `WAY201A.BA0927` | choose_one | no | yes | yes |
| 46 | `WBP1190.BZ0003` | `WBP1114.BA0000`, `WBP1110.BA0627`, `WBP1115.BA0000` | choose_one | no | yes | yes |
| 47 | `CBS2212.FC6535` | `CBM2112.FC6455`, `CV201AR.FC6256`, `CV201AR.BA0715` | choose_one | no | no | no |
| 49 | `WBP201D.FT6197` | `WBP201A.FT6197`, `WBP208B.FT6201`, `WBP208C.FT6201` | not_identified | no | no | no |
| 51 | `AB0138211B1A1` | `AB0139241C1A1`, `AB0139241C2A1`, `AB0137241C1A1` | choose_one | no | no | no |
| 54 | `AB0145211G1P1` | `AB0145221G1P1`, `AB0118221G1P2`, `AB0118221G1P1` | choose_one | no | no | no |
| 55 | `A32395101C1X1` | `A32397101C1X1`, `A32395101C1X2`, `V323952A1L1X1` | choose_one | no | yes | yes |
| 56 | `AB2010121B1A1` | `L3.781.4.56.2`, `L3.781.4.56.6`, `L3.781.4.56.9` | auto_filled | no | no | no |
| 63 | `W69016Z4` | `WSBB0026`, `W69012Z4`, `W6920046` | auto_filled | no | no | no |
| 65 | `WSSA0022` | `WSSA0085`, `WSSA0022`, `WSSA0023` | auto_filled | yes | yes | yes |
| 67 | `WSPN0007` | `WSPN0015`, `WSPN0007`, `WSPN0006` | choose_one | yes | yes | yes |
| 68 | `WSTA0065` | `W51002Q3`, `W51001Q3`, `WSTA0005` | choose_one | no | no | no |
| 72 | `IW501701` | `IW391406`, `IW391408`, `IW391502` | choose_one | no | no | no |
| 73 | `IW329301` | `IW328201`, `IW328202`, `IW328208` | auto_filled | no | no | no |
| 75 | `IW388101` | `IW377714`, `IW388103`, `IW377709` | choose_one | no | no | no |
| 76 | `IW328802` | `IW356808`, `IW356809`, `IW358002` | choose_one | no | yes | yes |
| 78 | `IW328903` | `IW328908`, `IW328903`, `IW328907` | choose_one | yes | yes | yes |
| 79 | `IW389101` | `IW389401`, `IW389101`, `IW388106` | choose_one | yes | yes | yes |
| 80 | `IW503302` |  | not_identified | no | no | no |
| 81 | `Q3858520` | `Q2438522`, `Q2438520`, `Q3868520` | choose_one | no | no | no |
| 82 | `Q1368430` | `Q1368420`, `Q1368430`, `Q1368470` | choose_one | yes | yes | yes |
| 86 | `Q3988482` | `Q3858523`, `Q3858520`, `Q3858522` | choose_one | no | no | no |
| 87 | `Q1302520` | `Q4142520`, `140.8.87`, `Q4148420` | auto_filled | no | no | no |
| 88 | `Q3468430` | `Q3468490`, `Q3448431`, `Q3448410` | auto_filled | no | yes | yes |
| 90 | `Q4138420` | `Q413842J`, `Q4138420`, `Q4138431` | choose_one | yes | yes | yes |
| 91 | `4520V/210A-B128` | `4500V/110A-B128`, `4520V/210A-B128`, `4500V/110A-B563` | choose_one | yes | yes | yes |
| 93 | `85180/000R-9248` | `85180/000R-B405`, `85180/000R-9248`, `85180/000R-9232` | choose_one | yes | yes | yes |
| 97 | `82035/000R-9359` | `82035/000R-H114`, `82035/000R-9359`, `82035/000R-9354` | auto_filled | yes | yes | yes |

## Limits

- One pass on 100 photos taken from the web. A seller's own photo is harder.
- The comparison inside this run is fair: both numbers come from the same describing call. Comparing with other runs is not, because the prompt is different.
- The search forms and the ranking rule were fixed before the run and not tuned on these photos.
- Google's results change; the saved searches are the record.
- WatchBase data read through search results is not licensed for use in a product.
- `clear_leader` is the model's own judgement. It decides between `auto_filled` and `choose_one`.
