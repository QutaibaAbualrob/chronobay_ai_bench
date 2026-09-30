# claude-opus-5-5 — FULL RUN (100 images)

```
claude-opus-5-5   -   FULL RUN (100 images)   -   2026-09-30 12:51 UTC   [schema mode]
========================================================================
Accuracy (strict)    79/100   (79.0%)
Accuracy (lenient)   84/100   (84.0%)
Brand correct        100/100   (100.0%)
Confidence >= 0.8    19 answers, 19 strictly right (100.0%)
Cost                 $2.2296   (rates verified 2026-09-30)
Time                 175.3s total | mean 6.89s | median 6.22s | p95 10.83s
Errors               0
```

Provider `anthropic`, model `claude-opus-5-5`, options `{"effort": "medium"}`.

**Strict**: the exact reference (notation normalized). **Lenient**: also counts look-alikes listed in `also_accept` and the same watch on a different strap/bracelet. Errors count as failures.

## By brand

| Brand | Images | Strict | Lenient |
|---|---:|---:|---:|
| Audemars Piguet | 10 | 7 (70.0%) | 8 (80.0%) |
| Breitling | 10 | 7 (70.0%) | 7 (70.0%) |
| Cartier | 10 | 8 (80.0%) | 8 (80.0%) |
| IWC | 10 | 7 (70.0%) | 7 (70.0%) |
| Jaeger-LeCoultre | 10 | 7 (70.0%) | 9 (90.0%) |
| Omega | 10 | 7 (70.0%) | 8 (80.0%) |
| Patek Philippe | 10 | 10 (100.0%) | 10 (100.0%) |
| Rolex | 10 | 10 (100.0%) | 10 (100.0%) |
| Tag Heuer | 10 | 9 (90.0%) | 9 (90.0%) |
| Vacheron Constantin | 10 | 7 (70.0%) | 8 (80.0%) |

## Not strictly correct (21)

| # | Image | Expected | Got | Lenient | Error |
|---:|---|---|---|---|---|
| 11 | 011_omega_speedmaster-moonwatch-professional.jpg | `310.30.42.50.01.002` | `310.30.42.50.01.001` | yes (look-alike) |  |
| 12 | 012_omega_seamaster-diver-300m.jpg | `210.30.42.20.01.010` | `210.90.42.20.01.001` |  |  |
| 15 | 015_omega_constellation-39.jpg | `131.10.39.20.02.001` | `131.10.41.21.02.001` |  |  |
| 31 | 031_ap_royal-oak-selfwinding-41.jpg | `15500ST.OO.1220ST.01` | `15510ST.OO.1320ST.06` |  |  |
| 32 | 032_ap_royal-oak-jumbo-extra-thin.jpg | `16202ST.OO.1240ST.01` | `15202ST.OO.1240ST.01` | yes (look-alike) |  |
| 34 | 034_ap_royal-oak-chronograph-41.jpg | `26240ST.OO.1320ST.02` | `26331ST.OO.1220ST.02` |  |  |
| 46 | 046_tagheuer_aquaracer-professional-200-solargraph.jpg | `WBP1190.BZ0003` | `WBP1114.BA0000` |  |  |
| 54 | 054_breitling_premier-b01-chronograph-42.jpg | `AB0145211G1P1` | `AB01451A1G1P1` |  |  |
| 57 | 057_breitling_navitimer-automatic-41.jpg | `A17326211B1P1` | `A17326241B1P1` |  |  |
| 59 | 059_breitling_top-time-b01-chevrolet-corvette.jpg | `AB01761A1K1X1` | `AB01762A1K1X1` |  |  |
| 64 | 064_cartier_tank-louis-cartier.jpg | `WGTA0011` | `W1529756` |  |  |
| 66 | 066_cartier_pasha-de-cartier-41.jpg | `WSPA0009` | `WSPA0013` |  |  |
| 75 | 075_iwc_pilot-s-watch-chronograph-41.jpg | `IW388101` | `IW377714` |  |  |
| 76 | 076_iwc_aquatimer-automatic-42.jpg | `IW328802` | `IW329001` |  |  |
| 79 | 079_iwc_pilot-s-watch-chronograph-top-gun.jpg | `IW389101` | `IW389001` |  |  |
| 82 | 082_jlc_master-ultra-thin-moon.jpg | `Q1368430` | `Q1368420` | yes (look-alike) |  |
| 86 | 086_jlc_reverso-tribute-duoface.jpg | `Q3988482` | `Q713848J` |  |  |
| 88 | 088_jlc_rendez-vous-night-day.jpg | `Q3468430` | `Q3448420` | yes (look-alike) |  |
| 91 | 091_vc_overseas-self-winding.jpg | `4520V/210A-B128` | `4500V/110A-B128` | yes (look-alike) |  |
| 98 | 098_vc_overseas-perpetual-calendar-ultra-thin.jpg | `4300V/120R-B064` | `4300V/120R-B509` |  |  |
| 99 | 099_vc_patrimony-moon-phase-retrograde-date.jpg | `4010U/000G-B330` | `4010U/000G-B329` |  |  |
