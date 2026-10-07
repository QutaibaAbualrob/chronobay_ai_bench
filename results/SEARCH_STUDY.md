# Search study: can a web search supply the right reference?

Stage 0 of Serper idea 1 (`FINDINGS.md`, section 4). Rebuilt by `search_study.py report` from saved searches.

No model was called. The saved answers of earlier full runs were replayed: for each photo, the brand, model line and reference the model gave were turned into Google searches through Serper (US, English, top 10 results), and the references read out of the results are the candidates. 618 searches are saved; they cost 618 Serper credits.

## Is the watch on WatchBase at all?

One search per answer-key reference, limited to watchbase.com.

**The watch's own page came back for 92 of the 100 answer-key references.** 2 more are named on another WatchBase page (a family or movement page), so WatchBase has them. 6 are not on WatchBase.

| Brand | References | Own page found | Listed elsewhere only | Not on WatchBase |
|---|---:|---:|---|---|
| Rolex | 10 | 10 |  |  |
| Omega | 10 | 10 |  |  |
| Patek Philippe | 10 | 10 |  |  |
| Audemars Piguet | 10 | 10 |  |  |
| Tag Heuer | 10 | 10 |  |  |
| Breitling | 10 | 8 | `AB0138211B1A1`, `AB01761A1K1X1` |  |
| Cartier | 10 | 5 |  | `WSSA0018`, `WSSA0022`, `WSPA0009`, `WSPN0007`, `WSTA0065` |
| IWC | 10 | 10 |  |  |
| Jaeger-LeCoultre | 10 | 9 |  | `Q4138420` |
| Vacheron Constantin | 10 | 10 |  |  |

The 8 references with no page of their own were then searched on the open web (brand and reference, no site limit): **8 of 8 found.**

| Row | Reference | On the open web | Sites |
|---:|---|---|---|
| 51 | `AB0138211B1A1` | yes | betteridge.com, breitling.com, chrono24.com, jomashop.com |
| 59 | `AB01761A1K1X1` | yes | betteridge.com, breitling.com, chrono24.com, instagram.com |
| 61 | `WSSA0018` | yes | cartier.com, chrono24.com, ebay.com, mayors.com |
| 65 | `WSSA0022` | yes | cartier.com, chrono24.com, luxuryofwatches.com, mayors.com |
| 66 | `WSPA0009` | yes | ablogtowatch.com, betteridge.com, bucherer.com, cartier.com |
| 67 | `WSPN0007` | yes | cartier.com, chrono24.com, ebay.com, grandcaliber.com |
| 68 | `WSTA0065` | yes | cartier.com, chrono24.com, ebay.com, houseofkennedy.com |
| 90 | `Q4138420` | yes | chrono24.com, cooperjewelers.com, essential-watches.com, grandcaliber.com |

## Is the right reference among the candidates?

99 photos (row 12 is left out: its photo was replaced after the answers were saved). "Among the candidates" means the exact reference, after normalising notation.

| | claude-opus-5-5 | claude-sonnet-5-5-nothink | gpt-6.1-sol-low | deepseek-flash |
|---|---:|---:|---:|---:|
| The model's own answer is right (the baseline) | 79 | 72 | 70 | 44 |
| Right reference among candidates: WatchBase, by the model line the model gave | 41 | 42 | 40 | 32 |
| Right reference among candidates: WatchBase, by the model part of the model's reference | 77 | 75 | 69 | 46 |
| Right reference among candidates: Open web, by model line, metal and strap | 62 | 58 | 58 | 49 |
| Right reference among candidates: any of the three searches | 89 | 90 | 87 | 72 |
| **Own answer or any search** (the most a chooser could reach) | 91 | 92 | 87 | 72 |
| Same, also counting accepted look-alikes | 93 | 94 | 89 | 76 |

What each source adds to the model's own answer:

| Right reference is the model's own answer, or among the candidates from | claude-opus-5-5 | claude-sonnet-5-5-nothink | gpt-6.1-sol-low | deepseek-flash |
|---|---:|---:|---:|---:|
| nothing else (own answer only) | 79 | 72 | 70 | 44 |
| WatchBase by model line | 88 | 83 | 79 | 56 |
| WatchBase by model line and by the model part of the reference | 88 | 87 | 81 | 59 |
| the open web only | 89 | 84 | 83 | 65 |
| all three | 91 | 92 | 87 | 72 |

The guess search was made only for wrong guesses. For a right guess the result of the answer-key search above is used, which is the same search.

## On the photos the model got wrong

| | claude-opus-5-5 | claude-sonnet-5-5-nothink | gpt-6.1-sol-low | deepseek-flash |
|---|---:|---:|---:|---:|
| Photos the model got wrong | 20 | 27 | 29 | 55 |
| Search has the right reference: WatchBase, by the model line the model gave | 9 | 11 | 9 | 12 |
| Search has the right reference: WatchBase, by the model part of the model's reference | 3 | 7 | 3 | 5 |
| Search has the right reference: Open web, by model line, metal and strap | 10 | 12 | 13 | 21 |
| **Search has the right reference: any** | 12 | 20 | 17 | 28 |
| No search has it | 8 | 7 | 12 | 27 |
| ... because the model named the wrong brand or none | 0 | 0 | 0 | 4 |
| ... because WatchBase does not have the watch | 0 | 0 | 1 | 2 |
| ... although WatchBase has the watch | 8 | 7 | 11 | 21 |

## How long is the candidate list?

All three searches merged. Order: the model's own answer first, then references that more searches agree on, then by position in the results. Apart from the model's own answer, this order uses nothing the model saw in the photo; stage 1 would rank by that.

| | claude-opus-5-5 | claude-sonnet-5-5-nothink | gpt-6.1-sol-low | deepseek-flash |
|---|---:|---:|---:|---:|
| Median number of candidates per photo | 11 | 11 | 11 | 10 |
| Largest | 23 | 21 | 23 | 21 |
| Photos with no candidate at all | 0 | 0 | 0 | 3 |
| Model's own answer first, then the list: right reference within the first 3 | 87 | 82 | 79 | 55 |
| Model's own answer first, then the list: right reference within the first 5 | 88 | 87 | 80 | 62 |
| Model's own answer first, then the list: right reference within the first 10 | 91 | 91 | 85 | 68 |

## By brand

Each cell: the model's own answer is right / own answer or any search.

| Brand | Photos | claude-opus-5-5 | claude-sonnet-5-5-nothink | gpt-6.1-sol-low | deepseek-flash |
|---|---:|---:|---:|---:|---:|
| Rolex | 10 | 10 / 10 | 10 / 10 | 7 / 10 | 6 / 9 |
| Omega | 9 | 7 / 8 | 6 / 8 | 8 / 9 | 5 / 8 |
| Patek Philippe | 10 | 10 / 10 | 8 / 9 | 10 / 10 | 5 / 8 |
| Audemars Piguet | 10 | 7 / 7 | 6 / 9 | 6 / 7 | 4 / 6 |
| Tag Heuer | 10 | 9 / 10 | 6 / 8 | 8 / 9 | 4 / 7 |
| Breitling | 10 | 7 / 8 | 9 / 9 | 5 / 7 | 3 / 5 |
| Cartier | 10 | 8 / 10 | 6 / 10 | 6 / 8 | 5 / 7 |
| IWC | 10 | 7 / 9 | 9 / 10 | 6 / 9 | 4 / 6 |
| Jaeger-LeCoultre | 10 | 7 / 9 | 4 / 9 | 5 / 8 | 2 / 6 |
| Vacheron Constantin | 10 | 7 / 10 | 8 / 10 | 9 / 10 | 6 / 10 |

## Every photo claude-opus-5-5 got wrong (20)

| Row | Expected | Model's answer | Found by | Place in list | List size | On WatchBase |
|---:|---|---|---|---:|---:|---|
| 11 | `310.30.42.50.01.002` | `310.30.42.50.01.001` | line, guess, open | 2 | 14 | yes |
| 15 | `131.10.39.20.02.001` | `131.10.41.21.02.001` | - |  | 13 | yes |
| 31 | `15500ST.OO.1220ST.01` | `15510ST.OO.1320ST.06` | - |  | 9 | yes |
| 32 | `16202ST.OO.1240ST.01` | `15202ST.OO.1240ST.01` | look-alike only |  | 12 | yes |
| 34 | `26240ST.OO.1320ST.02` | `26331ST.OO.1220ST.02` | - |  | 10 | yes |
| 46 | `WBP1190.BZ0003` | `WBP1114.BA0000` | line | 8 | 13 | yes |
| 54 | `AB0145211G1P1` | `AB01451A1G1P1` | look-alike only |  | 10 | yes |
| 57 | `A17326211B1P1` | `A17326241B1P1` | - |  | 18 | yes |
| 59 | `AB01761A1K1X1` | `AB01762A1K1X1` | open | 2 | 2 | yes |
| 64 | `WGTA0011` | `W1529756` | line, open | 1 | 11 | yes |
| 66 | `WSPA0009` | `WSPA0013` | open | 1 | 3 | no |
| 75 | `IW388101` | `IW377714` | - |  | 23 | yes |
| 76 | `IW328802` | `IW329001` | line, open | 6 | 16 | yes |
| 79 | `IW389101` | `IW389001` | line, open | 1 | 21 | yes |
| 82 | `Q1368430` | `Q1368420` | line, open | 1 | 10 | yes |
| 86 | `Q3988482` | `Q713848J` | - |  | 12 | yes |
| 88 | `Q3468430` | `Q3448420` | line, open | 1 | 18 | yes |
| 91 | `4520V/210A-B128` | `4500V/110A-B128` | open | 6 | 18 | yes |
| 98 | `4300V/120R-B064` | `4300V/120R-B509` | line, guess | 3 | 12 | yes |
| 99 | `4010U/000G-B330` | `4010U/000G-B329` | line, guess, open | 1 | 9 | yes |

## Every photo claude-sonnet-5-5-nothink got wrong (27)

| Row | Expected | Model's answer | Found by | Place in list | List size | On WatchBase |
|---:|---|---|---|---:|---:|---|
| 11 | `310.30.42.50.01.002` | `310.30.42.50.01.001` | line, guess, open | 2 | 14 | yes |
| 13 | `220.10.41.21.03.001` | `220.10.41.21.03.002` | - |  | 21 | yes |
| 20 | `424.13.40.20.02.001` | `424.13.40.20.02.002` | guess | 3 | 20 | yes |
| 28 | `5270P-001` | `5204G-001` | - |  | 13 | yes |
| 30 | `4910/1200A-001` | `4910/1201A-012` | open | 2 | 11 | yes |
| 35 | `26574ST.OO.1220ST.02` | `26574ST.OO.1220ST.03` | guess | 14 | 14 | yes |
| 36 | `15210BC.OO.A002CR.01` | `15210BC.OO.A002KB.01` | look-alike only |  | 15 | yes |
| 38 | `15510OR.OO.1320OR.01` | `15510OR.OO.1320OR.02` | guess | 1 | 21 | yes |
| 39 | `26405CE.OO.A002CA.01` | `26405CE.OO.A002CA.02` | guess | 1 | 15 | yes |
| 44 | `WAZ1110.BA0875` | `WAZ1112.BA0875` | - |  | 8 | yes |
| 45 | `WBN2110.BA0639` | `WBN2312.BA0000` | look-alike only |  | 11 | yes |
| 46 | `WBP1190.BZ0003` | `WBP1113.BA0000` | line | 9 | 14 | yes |
| 49 | `WBP201D.FT6197` | `WBP201E.FT6197` | line, guess, open | 1 | 5 | yes |
| 54 | `AB0145211G1P1` | `AB0145171G1P1` | - |  | 14 | yes |
| 62 | `WSTA0041` | `WSTA0042` | line, open | 2 | 13 | yes |
| 65 | `WSSA0022` | `WSSA0023` | open | 5 | 7 | no |
| 66 | `WSPA0009` | `WSPA0013` | open | 2 | 5 | no |
| 69 | `WSNM0004` | `WSNM0015` | line, open | 1 | 9 | yes |
| 76 | `IW328802` | `IW329001` | line, open | 6 | 16 | yes |
| 81 | `Q3858520` | `Q3848422` | line | 6 | 9 | yes |
| 82 | `Q1368430` | `Q1368420` | line, open | 1 | 10 | yes |
| 85 | `Q9028181` | `Q902868J` | line | 3 | 8 | yes |
| 86 | `Q3988482` | `Q3978480` | - |  | 12 | yes |
| 88 | `Q3468430` | `Q3448421` | line, open | 1 | 17 | yes |
| 89 | `Q389257J` | `Q3922470` | open | 3 | 8 | yes |
| 91 | `4520V/210A-B128` | `4500V/110A-B128` | open | 4 | 15 | yes |
| 98 | `4300V/120R-B064` | `4300V/120R-B509` | line, guess | 3 | 14 | yes |

## Every photo gpt-6.1-sol-low got wrong (29)

| Row | Expected | Model's answer | Found by | Place in list | List size | On WatchBase |
|---:|---|---|---|---:|---:|---|
| 2 | `126500LN` | `116500LN-0002` | line, open | 2 | 9 | yes |
| 5 | `228238` | `218238` | line, open | 1 | 7 | yes |
| 8 | `126622` | `116622-0003` | line, guess, open | 1 | 9 | yes |
| 17 | `311.92.44.51.01.007` | `311.92.44.51.01.003` | guess, open | 1 | 17 | yes |
| 31 | `15500ST.OO.1220ST.01` | `15400ST.OO.1220ST.03` | - |  | 13 | yes |
| 32 | `16202ST.OO.1240ST.01` | `15202ST.OO.1240ST.01` | look-alike only |  | 12 | yes |
| 34 | `26240ST.OO.1320ST.02` | `26315ST.OO.1256ST.02` | open | 11 | 11 | yes |
| 38 | `15510OR.OO.1320OR.01` | `15500OR.OO.1220OR.01` | - |  | 14 | yes |
| 41 | `CBN2A1B.BA0643` | `CAR201Z.BA0714` | - |  | 8 | yes |
| 46 | `WBP1190.BZ0003` | `WBP1310.BA0005` | line | 8 | 13 | yes |
| 51 | `AB0138211B1A1` | `AB0138241C1A1` | open | 3 | 17 | yes |
| 52 | `A17375211B1S1` | `A17376211B1S1` | - |  | 15 | yes |
| 54 | `AB0145211G1P1` | `AB0145331G1P1` | - |  | 14 | yes |
| 55 | `A32395101C1X1` | `A32397101C1X1` | line | 9 | 10 | yes |
| 57 | `A17326211B1P1` | `A17326241B1P1` | - |  | 18 | yes |
| 62 | `WSTA0041` | `W5200013` | - |  | 10 | yes |
| 64 | `WGTA0011` | `W1560017` | open | 1 | 6 | yes |
| 66 | `WSPA0009` | `W31044M7` | open | 2 | 5 | no |
| 67 | `WSPN0007` | `WSPN0006` | look-alike only |  | 3 | no |
| 72 | `IW501701` | `IW500701` | guess | 14 | 20 | yes |
| 75 | `IW388101` | `IW377714` | - |  | 23 | yes |
| 76 | `IW328802` | `IW329001` | line, open | 6 | 16 | yes |
| 80 | `IW503302` | `IW503402` | open | 5 | 15 | yes |
| 81 | `Q3858520` | `Q3858522` | - |  | 7 | yes |
| 82 | `Q1368430` | `Q1368420` | line, open | 1 | 10 | yes |
| 85 | `Q9028181` | `Q9028180` | line | 4 | 9 | yes |
| 86 | `Q3988482` | `Q3978480` | - |  | 12 | yes |
| 88 | `Q3468430` | `Q3448430` | line, open | 1 | 18 | yes |
| 91 | `4520V/210A-B128` | `4500V/110A-B128` | open | 6 | 18 | yes |

## Every photo deepseek-flash got wrong (55)

| Row | Expected | Model's answer | Found by | Place in list | List size | On WatchBase |
|---:|---|---|---|---:|---:|---|
| 2 | `126500LN` | `116500LN-0002` | line, open | 2 | 9 | yes |
| 4 | `126334` | `126234` | - |  | 7 | yes |
| 9 | `124300` | `126000-0005` | line, open | 3 | 7 | yes |
| 10 | `124060` | `114060` | line, open | 1 | 6 | yes |
| 11 | `310.30.42.50.01.002` | `3570.50.00` | open | 6 | 10 | yes |
| 13 | `220.10.41.21.03.001` | `231.10.42.21.03.001` | open | 18 | 20 | yes |
| 16 | `234.32.41.21.01.001` | `233.32.41.21.01.002` | open | 4 | 13 | yes |
| 17 | `311.92.44.51.01.007` | `329.32.44.51.01.001` | - |  | 9 | yes |
| 23 | `5227G-010` | `5227G-001` | guess | 5 | 12 | yes |
| 26 | `5230G-001` | `-` | - |  | 0 | yes |
| 27 | `5968A-001` | `5164A-001` | open | 5 | 8 | yes |
| 28 | `5270P-001` | `5172G-010` | - |  | 4 | yes |
| 30 | `4910/1200A-001` | `4910/10A-012` | open | 4 | 13 | yes |
| 32 | `16202ST.OO.1240ST.01` | `15202ST.OO.1240ST.01` | look-alike only |  | 12 | yes |
| 34 | `26240ST.OO.1320ST.02` | `26331ST.OO.1220ST.01` | open | 7 | 10 | yes |
| 35 | `26574ST.OO.1220ST.02` | `26574ST.OO.1220ST.01` | guess | 14 | 14 | yes |
| 36 | `15210BC.OO.A002CR.01` | `15210ST.OO.A002KB.01` | look-alike only |  | 13 | yes |
| 38 | `15510OR.OO.1320OR.01` | `15202OR.OO.1240OR.01` | - |  | 12 | yes |
| 39 | `26405CE.OO.A002CA.01` | `26703ST.OO.A010CA.01` | - |  | 10 | yes |
| 41 | `CBN2A1B.BA0643` | `CAZ1010.BA0842` | - |  | 13 | yes |
| 43 | `WBP201A.BA0632` | `WBP1110.BA0627` | - |  | 14 | yes |
| 44 | `WAZ1110.BA0875` | `WAZ1010.BA0842` | line, open | 1 | 21 | yes |
| 45 | `WBN2110.BA0639` | `WBN2010.BA0634` | open | 1 | 9 | yes |
| 46 | `WBP1190.BZ0003` | `WBP1112.BA0627` | line | 8 | 14 | yes |
| 47 | `CBS2212.FC6535` | `CBN2011.FC6484` | - |  | 12 | yes |
| 51 | `AB0138211B1A1` | `AB0138241C1A1` | - |  | 14 | yes |
| 53 | `AB0134101B1A1` | `A1338811/BB24/173A` | - |  | 3 | yes |
| 54 | `AB0145211G1P1` | `AB0118221G1P1` | - |  | 14 | yes |
| 55 | `A32395101C1X1` | `A32397101C1X1` | line | 9 | 10 | yes |
| 56 | `AB2010121B1A1` | `L3.781.4.56.6` | - |  | 0 | yes |
| 58 | `E79363101B1E1` | `E76325E5/BC02` | - |  | 2 | yes |
| 59 | `AB01761A1K1X1` | `AB01761A1A1` | open | 1 | 2 | yes |
| 61 | `WSSA0018` | `WSSA0009` | open | 11 | 13 | no |
| 62 | `WSTA0041` | `W5200003` | look-alike only |  | 10 | yes |
| 64 | `WGTA0011` | `WGTA0089` | line | 8 | 12 | yes |
| 67 | `WSPN0007` | `WSPN0006` | look-alike only |  | 3 | no |
| 68 | `WSTA0065` | `W51008Q3` | - |  | 13 | no |
| 72 | `IW501701` | `IW500705` | guess | 14 | 20 | yes |
| 73 | `IW329301` | `IW327001` | - |  | 16 | yes |
| 74 | `IW328201` | `IW327001` | - |  | 16 | yes |
| 76 | `IW328802` | `215.32.44.21.01.001` | - |  | 10 | yes |
| 79 | `IW389101` | `IW389404` | open | 8 | 10 | yes |
| 80 | `IW503302` | `IW392101` | - |  | 15 | yes |
| 82 | `Q1368430` | `Q1368470` | line, open | 1 | 9 | yes |
| 83 | `Q9008180` | `Q9008480` | - |  | 9 | yes |
| 84 | `Q4018420` | `Q1548530` | open | 5 | 11 | yes |
| 85 | `Q9028181` | `Q9028480` | line | 4 | 8 | yes |
| 86 | `Q3988482` | `Q2438522` | - |  | 7 | yes |
| 87 | `Q1302520` | `-` | - |  | 0 | yes |
| 88 | `Q3468430` | `Q3468490` | line, open | 1 | 18 | yes |
| 89 | `Q389257J` | `Q2542570` | - |  | 9 | yes |
| 91 | `4520V/210A-B128` | `4500V/110A-B128` | open | 4 | 15 | yes |
| 95 | `4600E/000A-B442` | `4600E/000A-B487` | open | 2 | 6 | yes |
| 97 | `82035/000R-9359` | `82035/000R-9354` | line, guess, open | 2 | 9 | yes |
| 100 | `4000E/000A-B439` | `4000E/000A-B548` | line, guess, open | 1 | 4 | yes |

## Limits

- Google's results change. These are the results on the day each search was made; the saved responses are the record.
- Only the top 10 results of each search were read.
- The model line and the attributes come from runs made with the benchmark prompt, which asks for one reference and no dial colour. A prompt written for this pipeline may do better or worse.
- References are read from titles, links and snippets with one pattern per brand, for the ten benchmark brands only.
- A candidate list that contains the right reference is not an answer. Picking from it is stage 1.
- WatchBase data read through search results is not licensed for use in a product.
