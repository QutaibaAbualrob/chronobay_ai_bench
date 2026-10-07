# Web search study: the model searches for itself - FULL RUN (100 images)

Idea 5 in `FINDINGS.md`, section 4. Rebuilt by `websearch_study.py report` from saved answers.

Run `2026-10-06_144623_nosearch_full`, model `gpt-6-luna` (`gpt-6-luna`, default reasoning effort). Web search was off. One call per photo. 100 photos. It was asked for up to three references, a second or third only where it could not rule a version out.

## Result

Out of 100 photos.

| | Exact reference | Also counting accepted look-alikes |
|---|---:|---:|
| First reference is right | 55 | 57 |
| Its references, up to three, contain it | 59 | 60 |
| Brand right | 98 | |

Where the right reference stands in its list: first 55, second 4, third 0, not in it 41. References given per photo: one 62, two 31, three 7, none 0.

For context, the same photos in the saved benchmark runs (one reference, no search, a different prompt): gpt-6-luna-nothink 38, gpt-6-luna-xhigh 52, deepseek-flash 44, claude-sonnet-5-5-nothink 72 right.

## Cost and speed

| | Per photo | This run |
|---|---:|---:|
| Searches made | 0.0 | 0 |
| Pages opened | 0.0 | 0 |
| Search fee at $0.01 a search | $0.0000 | $0.00 |
| Model tokens | $0.0007 | $0.07 |
| **Total** | **$0.0007** | **$0.07** |
| Input tokens | 3,031 | |
| Output tokens | 876 | |
| Time, median | 12.0s | |
| Time, longest | 32.5s | |


Calls that failed: 0. Answers tidied to fit the format: 0. Answer format enforced by the API: yes.

## Every photo

| Row | Expected | Its references | First right | In its three | Searches | Time | What it searched for |
|---:|---|---|:-:|:-:|---:|---:|---|
| 1 | `126610LN` | `126610LN`, `116610LN` | yes | yes | 0 | 7s |  |
| 2 | `126500LN` | `126500`, `116500` | no | no | 0 | 7s |  |
| 3 | `126710BLRO` | `126710BLRO` | yes | yes | 0 | 6s |  |
| 4 | `126334` | `126334` | yes | yes | 0 | 8s |  |
| 5 | `228238` | `228238` | yes | yes | 0 | 7s |  |
| 6 | `124270` | `124270`, `214270`, `224270` | yes | yes | 0 | 10s |  |
| 7 | `126600` | `126600` | yes | yes | 0 | 4s |  |
| 8 | `126622` | `126622`, `116622` | yes | yes | 0 | 6s |  |
| 9 | `124300` | `126000`, `124300` | no | yes | 0 | 13s |  |
| 10 | `124060` | `124060`, `114060` | yes | yes | 0 | 12s |  |
| 11 | `310.30.42.50.01.002` | `310.30.42.50.01.002`, `310.30.42.50.01.001` | yes | yes | 0 | 13s |  |
| 12 | `210.30.42.20.01.010` | `210.30.42.20.01.010` | yes | yes | 0 | 7s |  |
| 13 | `220.10.41.21.03.001` | `220.10.41.21.03.001`, `220.10.38.20.03.001` | yes | yes | 0 | 10s |  |
| 14 | `215.30.44.21.01.001` | `232.30.44.22.01.001` | no | no | 0 | 11s |  |
| 15 | `131.10.39.20.02.001` | `131.10.41.21.02.001` | no | no | 0 | 12s |  |
| 16 | `234.32.41.21.01.001` | `234.32.41.21.01.001`, `233.32.41.21.01.001` | yes | yes | 0 | 7s |  |
| 17 | `311.92.44.51.01.007` | `311.92.44.51.01.003` | no | no | 0 | 9s |  |
| 18 | `210.90.42.20.01.001` | `210.90.42.20.01.001` | yes | yes | 0 | 10s |  |
| 19 | `220.10.40.20.01.001` | `220.10.40.20.01.001` | yes | yes | 0 | 13s |  |
| 20 | `424.13.40.20.02.001` | `424.13.40.20.02.001` | yes | yes | 0 | 9s |  |
| 21 | `5711/1A-010` | `5711/1A-010`, `5711/1A-001` | yes | yes | 0 | 8s |  |
| 22 | `5167A-001` | `5167A-001` | yes | yes | 0 | 7s |  |
| 23 | `5227G-010` | `5227G-010`, `5296G-010` | yes | yes | 0 | 10s |  |
| 24 | `5712/1A-001` | `5990/1A-001` | no | no | 0 | 12s |  |
| 25 | `5396R-011` | `5396R-011`, `5396R-001`, `5205R-010` | yes | yes | 0 | 33s |  |
| 26 | `5230G-001` | `5230G-014`, `5230G-001`, `5130G-001` | no | yes | 0 | 17s |  |
| 27 | `5968A-001` | `5968A-001` | yes | yes | 0 | 6s |  |
| 28 | `5270P-001` | `5270P-001` | yes | yes | 0 | 18s |  |
| 29 | `5196J-001` | `5196J-001`, `3796J-001` | yes | yes | 0 | 11s |  |
| 30 | `4910/1200A-001` | `4910/1200A-010` | no | no | 0 | 12s |  |
| 31 | `15500ST.OO.1220ST.01` | `15500ST.OO.1220ST.03`, `15510ST.OO.1320ST.06`, `15400ST.OO.1220ST.03` | no | no | 0 | 15s |  |
| 32 | `16202ST.OO.1240ST.01` | `15500ST.OO.1220ST.03`, `15510ST.OO.1320ST.06` | no | no | 0 | 9s |  |
| 33 | `26470ST.OO.A027CA.01` | `26400SO.OO.A335CA.01` | no | no | 0 | 12s |  |
| 34 | `26240ST.OO.1320ST.02` | `26331ST.OO.1220ST.02` | no | no | 0 | 13s |  |
| 35 | `26574ST.OO.1220ST.02` | `26574ST.OO.1220ST.01` | no | no | 0 | 14s |  |
| 36 | `15210BC.OO.A002CR.01` | `15170ST.OO.A002CR.01`, `15180ST.OO.A002CR.01` | no | no | 0 | 30s |  |
| 37 | `15720ST.OO.A027CA.01` | `15720ST.OO.A027CA.01`, `15710ST.OO.A027CA.01` | yes | yes | 0 | 15s |  |
| 38 | `15510OR.OO.1320OR.01` | `15510OR.OO.1320OR.01`, `15500OR.OO.1220OR.01` | yes | yes | 0 | 13s |  |
| 39 | `26405CE.OO.A002CA.01` | `26420CE.OO.A127CR.01` | no | no | 0 | 9s |  |
| 40 | `15407ST.OO.1220ST.01` | `26510ST.OO.1220ST.01` | no | no | 0 | 20s |  |
| 41 | `CBN2A1B.BA0643` | `CBN2A1A.BA0643` | no | no | 0 | 20s |  |
| 42 | `CAW211P.FC6356` | `CAW211P.FC6356`, `CAW2111.FC6183` | yes | yes | 0 | 13s |  |
| 43 | `WBP201A.BA0632` | `WBP201A.BA0632` | yes | yes | 0 | 9s |  |
| 44 | `WAZ1110.BA0875` | `WAZ1010.BA0842` | no | no | 0 | 13s |  |
| 45 | `WBN2110.BA0639` | `WBN2110.BA0639` | yes | yes | 0 | 9s |  |
| 46 | `WBP1190.BZ0003` | `WBP1181.BA0000` | no | no | 0 | 12s |  |
| 47 | `CBS2212.FC6535` | `CBS2212.FC6535` | yes | yes | 0 | 10s |  |
| 48 | `WBC2110.BA0603` | `WBC2110.BA0603`, `WAT2110.BA0950` | yes | yes | 0 | 10s |  |
| 49 | `WBP201D.FT6197` | `WBP201D.FT6197` | yes | yes | 0 | 9s |  |
| 50 | `CBE2110.FC8226` | `CBE2110.FC8226` | yes | yes | 0 | 8s |  |
| 51 | `AB0138211B1A1` | `AB0138211C1A1` | no | no | 0 | 9s |  |
| 52 | `A17375211B1S1` | `A17365C9/BD67/161S` | no | no | 0 | 21s |  |
| 53 | `AB0134101B1A1` | `AB0134101B1A1` | yes | yes | 0 | 9s |  |
| 54 | `AB0145211G1P1` | `AB0118221G1P1` | no | no | 0 | 23s |  |
| 55 | `A32395101C1X1` | `A32395101C1X1`, `A32320101C1X1` | yes | yes | 0 | 13s |  |
| 56 | `AB2010121B1A1` | `234.30.41.21.01.001`, `233.30.41.21.01.001` | no | no | 0 | 18s |  |
| 57 | `A17326211B1P1` | `A17325211B1P1` | no | no | 0 | 17s |  |
| 58 | `E79363101B1E1` | `E79363101B1E1` | yes | yes | 0 | 32s |  |
| 59 | `AB01761A1K1X1` | `AB01772A1A1X1` | no | no | 0 | 14s |  |
| 60 | `A32398101B1A1` | `A32398101B1A1` | yes | yes | 0 | 12s |  |
| 61 | `WSSA0018` | `WSSA0018` | yes | yes | 0 | 9s |  |
| 62 | `WSTA0041` | `W5200013`, `WSTA0051` | no | no | 0 | 9s |  |
| 63 | `W69016Z4` | `W69016Z4` | yes | yes | 0 | 8s |  |
| 64 | `WGTA0011` | `WGTA0011`, `WGTA0091` | yes | yes | 0 | 12s |  |
| 65 | `WSSA0022` | `WSSA0032` | no | no | 0 | 15s |  |
| 66 | `WSPA0009` | `W31074M7` | no | no | 0 | 20s |  |
| 67 | `WSPN0007` | `187901`, `1566` | no | no | 0 | 21s |  |
| 68 | `WSTA0065` | `W51002Q3`, `WSTA0065` | no | yes | 0 | 12s |  |
| 69 | `WSNM0004` | `WSNM0004` | yes | yes | 0 | 10s |  |
| 70 | `W7100056` | `W7100056`, `W7100057` | yes | yes | 0 | 10s |  |
| 71 | `IW371617` | `IW371617` | yes | yes | 0 | 15s |  |
| 72 | `IW501701` | `IW501701`, `IW500705` | yes | yes | 0 | 16s |  |
| 73 | `IW329301` | `IW329301` | yes | yes | 0 | 11s |  |
| 74 | `IW328201` | `IW328201`, `IW327001`, `IW327009` | yes | yes | 0 | 19s |  |
| 75 | `IW388101` | `IW388101`, `IW377714` | yes | yes | 0 | 17s |  |
| 76 | `IW328802` | `IW328801`, `IW329001` | no | no | 0 | 25s |  |
| 77 | `IW356501` | `IW356501`, `IW356517` | yes | yes | 0 | 14s |  |
| 78 | `IW328903` | `IW328903` | yes | yes | 0 | 8s |  |
| 79 | `IW389101` | `IW389101`, `IW389008`, `IW389108` | yes | yes | 0 | 25s |  |
| 80 | `IW503302` | `5270R-001` | no | no | 0 | 20s |  |
| 81 | `Q3858520` | `Q3858522`, `Q3858520` | no | yes | 0 | 19s |  |
| 82 | `Q1368430` | `Q1368420` | no | no | 0 | 9s |  |
| 83 | `Q9008180` | `Q9008180` | yes | yes | 0 | 12s |  |
| 84 | `Q4018420` | `Q4018420` | yes | yes | 0 | 8s |  |
| 85 | `Q9028181` | `Q4138180` | no | no | 0 | 13s |  |
| 86 | `Q3988482` | `Q3978480` | no | no | 0 | 8s |  |
| 87 | `Q1302520` | `Q1302520` | yes | yes | 0 | 14s |  |
| 88 | `Q3468430` | `Q3468420`, `Q3468421`, `Q3468120` | no | no | 0 | 13s |  |
| 89 | `Q389257J` | `Q397846J` | no | no | 0 | 22s |  |
| 90 | `Q4138420` | `Q151842A` | no | no | 0 | 14s |  |
| 91 | `4520V/210A-B128` | `4500V/110A-B126` | no | no | 0 | 8s |  |
| 92 | `5500V/110A-B148` | `5500V/110A-B148` | yes | yes | 0 | 11s |  |
| 93 | `85180/000R-9248` | `85180/000R-9248` | yes | yes | 0 | 15s |  |
| 94 | `82172/000R-9382` | `82172/000R-9382` | yes | yes | 0 | 12s |  |
| 95 | `4600E/000A-B442` | `4600E/000A-B487` | no | no | 0 | 13s |  |
| 96 | `7900V/110A-B334` | `7900V/110A-B546`, `47450/B01A-9227` | no | no | 0 | 11s |  |
| 97 | `82035/000R-9359` | `82035/000R-9359`, `1100S/000R-B430` | yes | yes | 0 | 10s |  |
| 98 | `4300V/120R-B064` | `4300V/000R-B509` | no | no | 0 | 12s |  |
| 99 | `4010U/000G-B330` | `4000U/000R-B516` | no | no | 0 | 23s |  |
| 100 | `4000E/000A-B439` | `4000E/000A-B548` | no | no | 0 | 15s |  |

## Limits

- Nothing is saved between runs. A second run searches again, pays again and may get other results.
- The photos came from the web, so a search can land on the page a photo was taken from.
- One pass. Small differences between runs are noise.
