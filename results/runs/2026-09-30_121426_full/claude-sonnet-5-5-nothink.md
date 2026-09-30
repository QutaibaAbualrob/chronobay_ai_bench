# claude-sonnet-5-5-nothink — FULL RUN (100 images)

```
claude-sonnet-5-5-nothink   -   FULL RUN (100 images)   -   2026-09-30 12:14 UTC   [schema mode]
========================================================================
Accuracy (strict)    72/100   (72.0%)
Accuracy (lenient)   77/100   (77.0%)
Brand correct        100/100   (100.0%)
Confidence >= 0.8    12 answers, 11 strictly right (91.7%)
Cost                 $0.8442   (rates verified 2026-09-30)
Time                 65.6s total | mean 2.56s | median 2.53s | p95 3.56s
Errors               0
```

Provider `anthropic`, model `claude-sonnet-5-5`, options `{"thinking": "between_tools", "effort": "high"}`.

**Strict**: the exact reference (notation normalized). **Lenient**: also counts look-alikes listed in `also_accept` and the same watch on a different strap/bracelet. Errors count as failures.

## By brand

| Brand | Images | Strict | Lenient |
|---|---:|---:|---:|
| Audemars Piguet | 10 | 6 (60.0%) | 7 (70.0%) |
| Breitling | 10 | 9 (90.0%) | 9 (90.0%) |
| Cartier | 10 | 6 (60.0%) | 7 (70.0%) |
| IWC | 10 | 9 (90.0%) | 9 (90.0%) |
| Jaeger-LeCoultre | 10 | 4 (40.0%) | 5 (50.0%) |
| Omega | 10 | 6 (60.0%) | 7 (70.0%) |
| Patek Philippe | 10 | 8 (80.0%) | 8 (80.0%) |
| Rolex | 10 | 10 (100.0%) | 10 (100.0%) |
| Tag Heuer | 10 | 6 (60.0%) | 6 (60.0%) |
| Vacheron Constantin | 10 | 8 (80.0%) | 9 (90.0%) |

## Not strictly correct (28)

| # | Image | Expected | Got | Lenient | Error |
|---:|---|---|---|---|---|
| 11 | 011_omega_speedmaster-moonwatch-professional.jpg | `310.30.42.50.01.002` | `310.30.42.50.01.001` | yes (look-alike) |  |
| 12 | 012_omega_seamaster-diver-300m.jpg | `210.30.42.20.01.010` | `210.90.42.20.01.001` |  |  |
| 13 | 013_omega_seamaster-aqua-terra-150m-41.jpg | `220.10.41.21.03.001` | `220.10.41.21.03.002` |  |  |
| 20 | 020_omega_de-ville-prestige.jpg | `424.13.40.20.02.001` | `424.13.40.20.02.002` |  |  |
| 28 | 028_patek_perpetual-calendar-chronograph.jpg | `5270P-001` | `5204G-001` |  |  |
| 30 | 030_patek_twenty-4.jpg | `4910/1200A-001` | `4910/1201A-012` |  |  |
| 35 | 035_ap_royal-oak-perpetual-calendar.jpg | `26574ST.OO.1220ST.02` | `26574ST.OO.1220ST.03` |  |  |
| 36 | 036_ap_code-11-59-selfwinding.jpg | `15210BC.OO.A002CR.01` | `15210BC.OO.A002KB.01` | yes (strap variant) |  |
| 38 | 038_ap_royal-oak-selfwinding-41-rose-gold.jpg | `15510OR.OO.1320OR.01` | `15510OR.OO.1320OR.02` |  |  |
| 39 | 039_ap_royal-oak-offshore-chronograph-43-ceramic.jpg | `26405CE.OO.A002CA.01` | `26405CE.OO.A002CA.02` |  |  |
| 44 | 044_tagheuer_formula-1.jpg | `WAZ1110.BA0875` | `WAZ1112.BA0875` |  |  |
| 45 | 045_tagheuer_carrera-date.jpg | `WBN2110.BA0639` | `WBN2312.BA0000` |  |  |
| 46 | 046_tagheuer_aquaracer-professional-200-solargraph.jpg | `WBP1190.BZ0003` | `WBP1113.BA0000` |  |  |
| 49 | 049_tagheuer_aquaracer-professional-1000-superdiver.jpg | `WBP201D.FT6197` | `WBP201E.FT6197` |  |  |
| 54 | 054_breitling_premier-b01-chronograph-42.jpg | `AB0145211G1P1` | `AB0145171G1P1` |  |  |
| 62 | 062_cartier_tank-must-large.jpg | `WSTA0041` | `WSTA0042` | yes (look-alike) |  |
| 65 | 065_cartier_santos-dumont-large.jpg | `WSSA0022` | `WSSA0023` |  |  |
| 66 | 066_cartier_pasha-de-cartier-41.jpg | `WSPA0009` | `WSPA0013` |  |  |
| 69 | 069_cartier_drive-de-cartier.jpg | `WSNM0004` | `WSNM0015` |  |  |
| 76 | 076_iwc_aquatimer-automatic-42.jpg | `IW328802` | `IW329001` |  |  |
| 81 | 081_jlc_reverso-classic-large-small-seconds.jpg | `Q3858520` | `Q3848422` |  |  |
| 82 | 082_jlc_master-ultra-thin-moon.jpg | `Q1368430` | `Q1368420` | yes (look-alike) |  |
| 85 | 085_jlc_polaris-chronograph.jpg | `Q9028181` | `Q902868J` |  |  |
| 86 | 086_jlc_reverso-tribute-duoface.jpg | `Q3988482` | `Q3978480` |  |  |
| 88 | 088_jlc_rendez-vous-night-day.jpg | `Q3468430` | `Q3448421` |  |  |
| 89 | 089_jlc_reverso-tribute-chronograph.jpg | `Q389257J` | `Q3922470` |  |  |
| 91 | 091_vc_overseas-self-winding.jpg | `4520V/210A-B128` | `4500V/110A-B128` | yes (look-alike) |  |
| 98 | 098_vc_overseas-perpetual-calendar-ultra-thin.jpg | `4300V/120R-B064` | `4300V/120R-B509` |  |  |
