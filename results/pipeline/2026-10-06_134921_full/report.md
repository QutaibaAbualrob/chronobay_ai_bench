# Pipeline study: describe, search, choose - FULL RUN (100 images)

Stage 1 of Serper idea 1 (`FINDINGS.md`, section 4). Rebuilt by `pipeline_study.py report` from saved answers and saved searches.

Run `2026-10-06_134921_full`, model `claude-sonnet-5-5-nothink` (`claude-sonnet-5-5`, thinking between_tools, effort high). 91 photos. Each photo gets one describing call, three web searches, a ranking in code, and one choosing call that sees the photo again with up to 15 candidates.

> **INCOMPLETE.** The run stopped before the choosing call for 9 photos (rows 92, 93, 94, 95, 96, 97, 98, 99, 100). Every table below covers the 91 photos that have both calls. Continue the run with `--resume` to finish it.

## Result

Out of 91 photos.

| | Exact reference | Also counting accepted look-alikes |
|---|---:|---:|
| Model's own first reference (the baseline, from the same call) | 61 | 68 |
| **Pipeline's first choice** | 61 | 65 |
| Model's own references, up to three, contain it | 72 | 76 |
| **Pipeline's choices, up to three, contain it** | 82 | 83 |
| It was among the candidates shown to the choosing call | 85 | 86 |
| It was available at all: own references or any search (the ceiling) | 85 | 86 |

Code ranking alone, with no second call:

| | Exact reference | Also counting accepted look-alikes |
|---|---:|---:|
| First in the code order | 60 | 67 |
| Within the first three of the code order | 74 | 77 |

## What the pipeline changed

First choice against the model's own first reference: **11 gained, 11 lost**.

### Gained: own first reference wrong, pipeline's first choice right (11)

| Row | Expected | Model's own first | Pipeline chose | Reason the model gave |
|---:|---|---|---|---|
| 11 | `310.30.42.50.01.002` | `310.30.42.50.01.001` | `310.30.42.50.01.002` | The watch is a steel Speedmaster with a black dial, black bezel and five-link steel bracelet, with sapphire-style sub-dials and the 3861 layout. Refe… |
| 12 | `210.30.42.20.01.010` | `210.30.42.20.01.001` | `210.30.42.20.01.010` | The photo shows a no-date black wave dial Seamaster Diver 300M with black ceramic bezel and a steel mesh (Milanese) bracelet, which matches the 210.3… |
| 32 | `16202ST.OO.1240ST.01` | `15202ST.OO.1240ST.01` | `16202ST.OO.1240ST.01` | The photo shows a 39mm Royal Oak Extra-Thin with a blue Grande Tapisserie dial, date window at 3, and a satin-finished case and bracelet that looks s… |
| 39 | `26405CE.OO.A002CA.01` | `26405CE.OO.A002CA.02` | `26405CE.OO.A002CA.01` | The watch shows a black ceramic case and ceramic bezel with a grey Mega Tapisserie dial, silver-grey counters, titanium pushpiece guards and a dark r… |
| 44 | `WAZ1110.BA0875` | `WAZ1112.BA0875` | `WAZ1110.BA0875` | The watch shows a black dial with a date window at 9, a large '12' and TAG logo at 7-8 o'clock, a black bezel with white numerals on a steel bracelet… |
| 46 | `WBP1190.BZ0003` | `WBP1180.BA0000` | `WBP1190.BZ0003` | The watch has a grey horizontally-grooved dial with rose-gold accents and a sandblasted grey titanium-look bezel on a matching bracelet, matching the… |
| 49 | `WBP201D.FT6197` | `WBP201A.FT6197` | `WBP201D.FT6197` | The watch shows a black DLC-coated case with black ceramic bezel, pale luminous SuperLuminova dial with horizontal grooves, and a black rubber strap,… |
| 55 | `A32395101C1X1` | `A32397101C1X1` | `A32395101C1X1` | The watch is a steel Avenger Automatic GMT 45 with a blue dial on a blue textile-style strap with white stitching; candidates 1, 2 and 3 are all stra… |
| 66 | `WSPA0009` | `WSPA0013` | `WSPA0009` | The watch is a modern Pasha de Cartier 35mm automatic in steel on a steel bracelet with a silvered guilloche dial, blue steel sword hands, Arabic 12/… |
| 72 | `IW501701` | `IW501702` | `IW501701` | The watch shows a silver-white dial with rose-gold Arabic numerals and rose-gold leaf hands, a power reserve subdial at 2, small seconds at 8, a date… |
| 78 | `IW328903` | `IW328904` | `IW328903` | The watch is a stainless steel Ingenieur Automatic 40 with an integrated bracelet and a teal/blue-green textured dial with date at 9; the dial shade… |

### Lost: own first reference right, pipeline's first choice wrong (11)

| Row | Expected | Model's own first | Pipeline chose | Reason the model gave |
|---:|---|---|---|---|
| 19 | `220.10.40.20.01.001` | `220.10.40.20.01.001` | `220.10.40.20.06.001` | The photo shows a 40mm Railmaster on a brushed steel bracelet with a brown-grey brushed dial, 3-6-9-12 numerals and vintage-lume triangle markers, wh… |
| 34 | `26240ST.OO.1320ST.02` | `26240ST.OO.1320ST.02` | `26240ST.OO.1320ST.06` | The photo shows a steel Royal Oak chronograph with a black/grey Grande Tapisserie dial, black subdials and a 24 date window, matching the black-dial… |
| 38 | `15510OR.OO.1320OR.01` | `15510OR.OO.1320OR.01` | `15510OR.OO.1320OR.03` | The watch is a pink gold Royal Oak on a matching pink gold bracelet with a blue Grande Tapisserie dial, date window at 3 and no chronograph subdials,… |
| 42 | `CAW211P.FC6356` | `CAW211P.FC6356` | `CAW211B.FC6302` | The watch shows a steel square Monaco Calibre 11 with a blue sunray dial, white sub-registers, red accents, a date window at 6 and a perforated black… |
| 52 | `A17375211B1S1` | `A17375211B1S1` | `A17375A51B2S1` | The photo shows a Superocean Automatic 42 with a black dial, white chapter ring, a black/grey ceramic bezel, a steel case and a black textured rubber… |
| 62 | `WSTA0041` | `WSTA0041` | `WSTA0138` | The photo shows a steel rectangular Tank Must with a silver dial, Roman numerals, blue cabochon crown and a black grained calfskin strap, matching th… |
| 63 | `W69016Z4` | `W69016Z4` | `WSBB0026` | The photo shows a steel Ballon Bleu 42mm with a silver guilloché dial, blue sword hands, date at 3 and a black alligator strap with deployant, matchi… |
| 65 | `WSSA0022` | `WSSA0022` | `WSSA0085` | The watch shows an all-steel case with a silver sunburst Roman dial, blue sapphire cabochon crown with diamond-set guard, and a navy blue alligator s… |
| 68 | `WSTA0065` | `WSTA0065` | `WSTA0129` | The watch is a stainless steel Tank Française with a steel bracelet, silver sunburst dial with black Roman numerals, blue sword hands and a cabochon… |
| 75 | `IW388101` | `IW388101` | `IW388120` | The watch is a 41mm stainless steel IWC Pilot's Chronograph with a sunburst blue dial, three subdials, day-date window and dark navy leather strap wi… |
| 87 | `Q1302520` | `Q1302520` | `Q1142510` | The watch is a pink gold Master Ultra Thin Perpetual with a silvered/eggshell dial, applied pink gold markers and a brown alligator strap; Q1142510 i… |

## Outcomes

What the seller would see. `auto_filled`: the choosing call said one candidate stands clear. `choose_one`: it ranked up to three and the seller taps. `not_identified`: it said none fit, or nothing was read from the photo.

| Outcome | Photos | Right reference delivered | Share right |
|---|---:|---:|---:|
| `auto_filled` | 24 | 21 (filled in is right) | 88% |
| `choose_one` | 67 | 59 (is among the options) | 88% |
| `not_identified` | 0 | 0 (was available all the same) | - |

Proposed pass marks in `AUTO_LISTING_SPEC.md`, section 10: `auto_filled` right at least 95 times in 100, `choose_one` options contain the right watch at least 95 times in 100, at least 70% of uploads `auto_filled`.

## Worked out after the run

These combinations were tried on the saved answers after the results were known. They cost nothing, and they need a fresh set of photos before they can be trusted.

| Way of combining the two calls | First choice right | Right one within the options |
|---|---:|---:|
| Model's own references only (no search, no second call) | 61 | 72 of three |
| The choosing call's ranking as it is | 61 | 82 of three |
| Model's own first reference, then the choosing call's picks | 61 | 83 of three, 84 of four, 85 of five |
| The same, but the choosing call's pick goes first when it says it has a clear leader | 63 | 83 of three |

When to trust the first choice:

| Signal | Photos | First choice right |
|---|---:|---:|
| The choosing call kept the model's own first reference | 62 | 50 |
| The choosing call changed it | 29 | 11 (the model's own first was right on 11) |
| The choosing call said it had a clear leader | 24 | 21 |
| Kept the model's own first and said clear leader | 20 | 18 |
| The describing call's own confidence was 0.8 or more | 10 | 10 |

On 9 photos the list shown to the choosing call had the model's own first reference, which was right, moved down from first place, because the code order held something against it. The choosing call still chose right on 7 of them; rows 19, 42 are among the lost.

Notes on this run:

- Stopped at 91 of 100 photos on 2026-10-06 when the Anthropic account ran out of credit. Rows 92 to 100, nine of the ten Vacheron Constantin photos, have no choosing call. Left unfinished at Qutaiba's decision.
- In this run the code that reads catalogue lines from search results attached lines to the wrong watch, which moved some right references down the list the choosing call saw. The code was corrected afterwards and the choosing calls were not repeated. The code-ranking figures use the corrected code.

## The describing call

Fields the answer key can check, out of 91 answered photos.

| Field | Right |
|---|---:|
| Brand | 91 |
| Movement | 90 |
| Case material (gold colours counted as gold; two-tone has no match in the key) | 89 |
| Bracelet material | 88 |

Dial colour, bezel, size and complications have no column in the answer key and are not scored.

References given per photo: one 4, two 17, three 70.

## Cost and speed

| | Per photo |
|---|---:|
| Describing call | $0.0110 |
| Choosing call | $0.0111 |
| Both calls | $0.0221 |
| Web searches | 3.0 |
| Candidates found (median) | 12 |
| Model time, both calls, median | 6.2s |
| Model time, slowest 5% start at | 8.5s |

Model cost of the run: $2.01. Search time is not included; the searches were made in a batch between the two calls. A search costs $0.001 at Serper's smallest paid pack (reported price).
Photos where the describing call gave no answer: 0; they count as wrong everywhere. Photos where the choosing call gave no answer: 0; for those the code order stands. Photos with no choosing call because there were fewer than two candidates: 0. Photos where an answer broke the format and was tidied to fit: 0.

## By brand

| Brand | Photos | Own first reference | Pipeline's first choice | Pipeline's three |
|---|---:|---:|---:|---:|
| Rolex | 10 | 10 | 10 | 10 |
| Omega | 10 | 7 | 8 | 10 |
| Patek Philippe | 10 | 9 | 9 | 9 |
| Audemars Piguet | 10 | 5 | 5 | 8 |
| Tag Heuer | 10 | 7 | 9 | 9 |
| Breitling | 10 | 5 | 5 | 7 |
| Cartier | 10 | 7 | 4 | 10 |
| IWC | 10 | 7 | 8 | 10 |
| Jaeger-LeCoultre | 10 | 4 | 3 | 8 |
| Vacheron Constantin | 1 | 0 | 0 | 1 |

## Every photo where the first choice is wrong (30)

| Row | Expected | Pipeline's choices | Outcome | Right one in its three | Shown to it | Available |
|---:|---|---|---|---|---|---|
| 17 | `311.92.44.51.01.007` | `311.92.44.51.01.003`, `311.92.44.51.01.004`, `311.92.44.51.01.007` | choose_one | yes | yes | yes |
| 19 | `220.10.40.20.01.001` | `220.10.40.20.06.001`, `220.10.40.20.01.001`, `235.10.38.20.13.001` | choose_one | yes | yes | yes |
| 29 | `5196J-001` | `96J`, `3796J`, `5227J-001` | choose_one | no | no | no |
| 31 | `15500ST.OO.1220ST.01` | `15550ST.OO.1356ST.02`, `15550ST.OO.1356ST.08`, `15450ST.OO.1256ST.01` | choose_one | no | yes | yes |
| 34 | `26240ST.OO.1320ST.02` | `26240ST.OO.1320ST.06`, `26240ST.OO.1320ST.02`, `26331ST.OO.1220ST.02` | choose_one | yes | yes | yes |
| 35 | `26574ST.OO.1220ST.02` | `26574ST.OO.1220ST.03`, `26574ST.OO.1220ST.02`, `26574ST.OO.1220ST.01` | choose_one | yes | yes | yes |
| 36 | `15210BC.OO.A002CR.01` | `15210BC.OO.A002KB.02`, `15210BC.OO.A002KB.01`, `15210CR.OO.A002KB.01` | choose_one | no | no | no |
| 38 | `15510OR.OO.1320OR.01` | `15510OR.OO.1320OR.03`, `15510OR.OO.1320OR.01`, `15510OR.OO.1320OR.02` | choose_one | yes | yes | yes |
| 42 | `CAW211P.FC6356` | `CAW211B.FC6302`, `CAW2111.FC6183`, `CAW211R.FC6401` | choose_one | no | yes | yes |
| 51 | `AB0138211B1A1` | `AB0138211C1A1`, `AB0138241C1A1`, `AB0138241C1P1` | choose_one | no | yes | yes |
| 52 | `A17375211B1S1` | `A17375A51B2S1`, `A17375211B1S1`, `A17376211B1S1` | choose_one | yes | yes | yes |
| 54 | `AB0145211G1P1` | `AB0145221G1P1`, `AB0145371G1P1`, `AB0118221G1P1` | choose_one | no | no | no |
| 59 | `AB01761A1K1X1` | `AB01766A1K1X1`, `AB01765A1K1X1`, `AB01762C1I1X1` | choose_one | no | no | no |
| 60 | `A32398101B1A1` | `A323982B1B1A1`, `A32398101B1A1`, `GB0412121B1A1` | choose_one | yes | yes | yes |
| 62 | `WSTA0041` | `WSTA0138`, `WSTA0136`, `WSTA0041` | choose_one | yes | yes | yes |
| 63 | `W69016Z4` | `WSBB0026`, `W69016Z4`, `WSBB0027` | choose_one | yes | yes | yes |
| 65 | `WSSA0022` | `WSSA0085`, `WSSA0022`, `WSSA0046` | auto_filled | yes | yes | yes |
| 67 | `WSPN0007` | `WSPN0006`, `WSPN0013`, `WSPN0007` | choose_one | yes | yes | yes |
| 68 | `WSTA0065` | `WSTA0129`, `WSTA0065`, `WSTA0005` | choose_one | yes | yes | yes |
| 69 | `WSNM0004` | `WSNM0015`, `WSNM0016`, `WSNM0004` | choose_one | yes | yes | yes |
| 75 | `IW388101` | `IW388120`, `IW388101`, `IW388111` | choose_one | yes | yes | yes |
| 76 | `IW328802` | `IW329001`, `IW328802`, `IW329004` | choose_one | yes | yes | yes |
| 81 | `Q3858520` | `Q2458420`, `Q2458422`, `Q3848422` | choose_one | no | no | no |
| 82 | `Q1368430` | `Q1368420`, `Q1368430`, `Q136842A` | choose_one | yes | yes | yes |
| 85 | `Q9028181` | `Q9028180`, `Q9028181`, `Q9028480` | auto_filled | yes | yes | yes |
| 86 | `Q3988482` | `Q3978480`, `Q3978482`, `Q3988481` | auto_filled | no | no | no |
| 87 | `Q1302520` | `Q1142510`, `Q1142501`, `Q1302520` | choose_one | yes | yes | yes |
| 88 | `Q3468430` | `Q3468421`, `Q3468430`, `Q3468422` | choose_one | yes | yes | yes |
| 89 | `Q389257J` | `Q389256J`, `Q389257J`, `Q3892470` | choose_one | yes | yes | yes |
| 91 | `4520V/210A-B128` | `4500V/110A-B128`, `4520V/210A-B128`, `4500V/110A-B705` | choose_one | yes | yes | yes |

## Limits

- One pass on 100 photos taken from the web. A seller's own photo is harder.
- The comparison inside this run is fair: both numbers come from the same describing call. Comparing with other runs is not, because the prompt is different.
- The search forms and the ranking rule were fixed before the run and not tuned on these photos.
- Google's results change; the saved searches are the record.
- WatchBase data read through search results is not licensed for use in a product.
- `clear_leader` is the model's own judgement. It decides between `auto_filled` and `choose_one`.
