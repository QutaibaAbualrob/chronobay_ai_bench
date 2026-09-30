# deepseek-flash — FULL RUN (100 images)

```
deepseek-flash   -   FULL RUN (100 images)   -   2026-09-30 11:24 UTC   [prompt mode]
========================================================================
Accuracy (strict)    48/100   (48.0%)
Accuracy (lenient)   53/100   (53.0%)
Brand correct        93/100   (93.0%)
Confidence >= 0.8    11 answers, 9 strictly right (81.8%)
Cost                 $0.1304   (rates verified 2026-09-30)
Time                 302.9s total | mean 10.87s | median 4.94s | p95 43.50s
Errors               2 (2 schema-parse)
```

> prompt mode: JSON asked for in the prompt, not enforced by the API — invalid/empty JSON is counted as an error, not as a wrong identification
> DeepSeek caps each image at 1,024 tokens (images are scaled to ~1300x1300 px) — less detail than the other providers get, which matters for reading small engraved text. Its score reflects that limit as much as model capability. Its price also doubles at peak hours (01-04 and 06-10 UTC, weekdays); cost uses the rate in force when each request started.

Provider `deepseek`, model `deepseek-flash`.

**Strict**: the exact reference (notation normalized). **Lenient**: also counts look-alikes listed in `also_accept` and the same watch on a different strap/bracelet. Errors count as failures.

## By brand

| Brand | Images | Strict | Lenient |
|---|---:|---:|---:|
| Audemars Piguet | 10 | 2 (20.0%) | 3 (30.0%) |
| Breitling | 10 | 3 (30.0%) | 3 (30.0%) |
| Cartier | 10 | 6 (60.0%) | 7 (70.0%) |
| IWC | 10 | 3 (30.0%) | 3 (30.0%) |
| Jaeger-LeCoultre | 10 | 3 (30.0%) | 4 (40.0%) |
| Omega | 10 | 6 (60.0%) | 6 (60.0%) |
| Patek Philippe | 10 | 6 (60.0%) | 6 (60.0%) |
| Rolex | 10 | 8 (80.0%) | 9 (90.0%) |
| Tag Heuer | 10 | 5 (50.0%) | 5 (50.0%) |
| Vacheron Constantin | 10 | 6 (60.0%) | 7 (70.0%) |

## Not strictly correct (52)

| # | Image | Expected | Got | Lenient | Error |
|---:|---|---|---|---|---|
| 2 | 002_rolex_cosmograph-daytona.jpg | `126500LN` | `116500LN` | yes (look-alike) |  |
| 4 | 004_rolex_datejust-41.jpg | `126334` | `126234-0026` |  |  |
| 12 | 012_omega_seamaster-diver-300m.jpg | `210.30.42.20.01.010` | `AB2010121B1A1` |  |  |
| 14 | 014_omega_seamaster-planet-ocean-600m.jpg | `215.30.44.21.01.001` | `232.30.46.21.01.002` |  |  |
| 16 | 016_omega_seamaster-300-heritage.jpg | `234.32.41.21.01.001` | `233.32.41.21.01.002` |  |  |
| 17 | 017_omega_speedmaster-dark-side-of-the-moon.jpg | `311.92.44.51.01.007` | `329.32.44.51.01.001` |  |  |
| 25 | 025_patek_annual-calendar.jpg | `5396R-011` | — |  | schema-parse: attempt 1: empty (no text in response; finish_reason=length) / attempt 2: empty (no text in response; finish_reason=leng |
| 26 | 026_patek_world-time.jpg | `5230G-001` | `5110G-001` |  |  |
| 28 | 028_patek_perpetual-calendar-chronograph.jpg | `5270P-001` | `IW371616` |  |  |
| 30 | 030_patek_twenty-4.jpg | `4910/1200A-001` | `4910/1200A-010` |  |  |
| 32 | 032_ap_royal-oak-jumbo-extra-thin.jpg | `16202ST.OO.1240ST.01` | `15202ST.OO.1240ST.01` | yes (look-alike) |  |
| 33 | 033_ap_royal-oak-offshore-chronograph-42.jpg | `26470ST.OO.A027CA.01` | `26170ST.OO.D305CR.01` |  |  |
| 34 | 034_ap_royal-oak-chronograph-41.jpg | `26240ST.OO.1320ST.02` | `26331ST.OO.1220ST.01` |  |  |
| 35 | 035_ap_royal-oak-perpetual-calendar.jpg | `26574ST.OO.1220ST.02` | `26574ST.OO.1220ST.01` |  |  |
| 36 | 036_ap_code-11-59-selfwinding.jpg | `15210BC.OO.A002CR.01` | `15210ST.OO.A002CR.01` |  |  |
| 37 | 037_ap_royal-oak-offshore-diver.jpg | `15720ST.OO.A027CA.01` | `15710ST.OO.A027CA.01` |  |  |
| 38 | 038_ap_royal-oak-selfwinding-41-rose-gold.jpg | `15510OR.OO.1320OR.01` | `15202OR.OO.1240OR.01` |  |  |
| 39 | 039_ap_royal-oak-offshore-chronograph-43-ceramic.jpg | `26405CE.OO.A002CA.01` | `26703ST.OO.A002CA.01` |  |  |
| 41 | 041_tagheuer_carrera-chronograph.jpg | `CBN2A1B.BA0643` | `CBM2110.BA0651` |  |  |
| 44 | 044_tagheuer_formula-1.jpg | `WAZ1110.BA0875` | `WAZ1010.BA0842` |  |  |
| 45 | 045_tagheuer_carrera-date.jpg | `WBN2110.BA0639` | `WAR201A.BA0723` |  |  |
| 46 | 046_tagheuer_aquaracer-professional-200-solargraph.jpg | `WBP1190.BZ0003` | `WBP1110.BA0627` |  |  |
| 47 | 047_tagheuer_carrera-chronograph-glassbox.jpg | `CBS2212.FC6535` | `CBN2011.FC6573` |  |  |
| 51 | 051_breitling_navitimer-b01-chronograph-43.jpg | `AB0138211B1A1` | `AB0138241C1A1` |  |  |
| 53 | 053_breitling_chronomat-b01-42.jpg | `AB0134101B1A1` | `AB011012/BF76` |  |  |
| 54 | 054_breitling_premier-b01-chronograph-42.jpg | `AB0145211G1P1` | `AB0118221G1P1` |  |  |
| 55 | 055_breitling_avenger-automatic-gmt-45.jpg | `A32395101C1X1` | `A32397101C1X1` |  |  |
| 56 | 056_breitling_superocean-heritage-b20-automatic-42.jpg | `AB2010121B1A1` | `L3.774.4.50.6` |  |  |
| 58 | 058_breitling_aerospace-evo.jpg | `E79363101B1E1` | `E7936310/BC27/152E` |  |  |
| 59 | 059_breitling_top-time-b01-chevrolet-corvette.jpg | `AB01761A1K1X1` | `A25310241K1X1` |  |  |
| 62 | 062_cartier_tank-must-large.jpg | `WSTA0041` | `W5200025` |  |  |
| 63 | 063_cartier_ballon-bleu-de-cartier-42.jpg | `W69016Z4` | `W69012Z4` | yes (look-alike) |  |
| 65 | 065_cartier_santos-dumont-large.jpg | `WSSA0022` | `WSSA0023` |  |  |
| 68 | 068_cartier_tank-francaise.jpg | `WSTA0065` | `W51008Q3` |  |  |
| 72 | 072_iwc_portugieser-automatic-42.jpg | `IW501701` | `IW500701` |  |  |
| 73 | 073_iwc_big-pilot-s-watch-43.jpg | `IW329301` | `IW328201` |  |  |
| 74 | 074_iwc_pilot-s-watch-mark-xx.jpg | `IW328201` | `IW327001` |  |  |
| 75 | 075_iwc_pilot-s-watch-chronograph-41.jpg | `IW388101` | `IW377714` |  |  |
| 76 | 076_iwc_aquatimer-automatic-42.jpg | `IW328802` | `2861.55.87` |  |  |
| 79 | 079_iwc_pilot-s-watch-chronograph-top-gun.jpg | `IW389101` | `IW389404` |  |  |
| 80 | 080_iwc_portugieser-perpetual-calendar-44.jpg | `IW503302` | `5204R-011` |  |  |
| 81 | 081_jlc_reverso-classic-large-small-seconds.jpg | `Q3858520` | `Q2438522` |  |  |
| 82 | 082_jlc_master-ultra-thin-moon.jpg | `Q1368430` | `Q1368420` | yes (look-alike) |  |
| 83 | 083_jlc_polaris-automatic.jpg | `Q9008180` | `Q9008480` |  |  |
| 84 | 084_jlc_master-control-date.jpg | `Q4018420` | `Q1548530` |  |  |
| 86 | 086_jlc_reverso-tribute-duoface.jpg | `Q3988482` | `Q397848J` |  |  |
| 87 | 087_jlc_master-ultra-thin-perpetual.jpg | `Q1302520` | — |  | schema-parse: attempt 1: empty (no text in response; finish_reason=length) / attempt 2: empty (no text in response; finish_reason=leng |
| 88 | 088_jlc_rendez-vous-night-day.jpg | `Q3468430` | `Q3468490` |  |  |
| 91 | 091_vc_overseas-self-winding.jpg | `4520V/210A-B128` | `4500V/110A-B128` | yes (look-alike) |  |
| 97 | 097_vc_historiques-american-1921.jpg | `82035/000R-9359` | `82035/000R-9354` |  |  |
| 98 | 098_vc_overseas-perpetual-calendar-ultra-thin.jpg | `4300V/120R-B064` | `4000V/210R-B966` |  |  |
| 99 | 099_vc_patrimony-moon-phase-retrograde-date.jpg | `4010U/000G-B330` | `4010U/000R-B329` |  |  |
