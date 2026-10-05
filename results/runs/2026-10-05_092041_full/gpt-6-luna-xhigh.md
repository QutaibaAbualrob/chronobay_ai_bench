# gpt-6-luna-xhigh — FULL RUN (100 images)

```
gpt-6-luna-xhigh   -   FULL RUN (100 images)   -   2026-10-05 09:21 UTC   [schema mode]
========================================================================
Accuracy (strict)    52/100   (52.0%)
Accuracy (lenient)   54/100   (54.0%)
Brand correct        98/100   (98.0%)
Confidence >= 0.8    33 answers, 22 strictly right (66.7%)
Cost                 $0.1012   (rates verified 2026-10-01)
Time                 238.5s total | mean 18.39s | median 15.29s | p95 38.92s
Errors               0
```

Provider `openai`, model `gpt-6-luna`, options `{"reasoning_effort": "xhigh"}`.

**Strict**: the exact reference (notation normalized). **Lenient**: also counts look-alikes listed in `also_accept` and the same watch on a different strap/bracelet. Errors count as failures.

## By brand

| Brand | Images | Strict | Lenient |
|---|---:|---:|---:|
| Audemars Piguet | 10 | 5 (50.0%) | 5 (50.0%) |
| Breitling | 10 | 3 (30.0%) | 3 (30.0%) |
| Cartier | 10 | 4 (40.0%) | 4 (40.0%) |
| IWC | 10 | 3 (30.0%) | 3 (30.0%) |
| Jaeger-LeCoultre | 10 | 3 (30.0%) | 3 (30.0%) |
| Omega | 10 | 7 (70.0%) | 8 (80.0%) |
| Patek Philippe | 10 | 8 (80.0%) | 8 (80.0%) |
| Rolex | 10 | 8 (80.0%) | 9 (90.0%) |
| Tag Heuer | 10 | 6 (60.0%) | 6 (60.0%) |
| Vacheron Constantin | 10 | 5 (50.0%) | 5 (50.0%) |

## Not strictly correct (48)

| # | Image | Expected | Got | Lenient | Error |
|---:|---|---|---|---|---|
| 6 | 006_rolex_explorer-36.jpg | `124270` | `214270` |  |  |
| 9 | 009_rolex_oyster-perpetual-41.jpg | `124300` | `126000` | yes (look-alike) |  |
| 11 | 011_omega_speedmaster-moonwatch-professional.jpg | `310.30.42.50.01.002` | `310.30.42.50.01.001` | yes (look-alike) |  |
| 12 | 012_omega_seamaster-diver-300m.jpg | `210.30.42.20.01.010` | `233.30.41.21.01.001` |  |  |
| 17 | 017_omega_speedmaster-dark-side-of-the-moon.jpg | `311.92.44.51.01.007` | `311.92.44.51.01.006` |  |  |
| 24 | 024_patek_nautilus-moon-phase.jpg | `5712/1A-001` | `5990/1A-001` |  |  |
| 25 | 025_patek_annual-calendar.jpg | `5396R-011` | `5205R-010` |  |  |
| 31 | 031_ap_royal-oak-selfwinding-41.jpg | `15500ST.OO.1220ST.01` | `15510ST.OO.1320ST.06` |  |  |
| 32 | 032_ap_royal-oak-jumbo-extra-thin.jpg | `16202ST.OO.1240ST.01` | `15400ST.OO.1220ST.03` |  |  |
| 34 | 034_ap_royal-oak-chronograph-41.jpg | `26240ST.OO.1320ST.02` | `26240ST.OO.1320ST.08` |  |  |
| 36 | 036_ap_code-11-59-selfwinding.jpg | `15210BC.OO.A002CR.01` | `15210ST.OO.A002CR.01` |  |  |
| 39 | 039_ap_royal-oak-offshore-chronograph-43-ceramic.jpg | `26405CE.OO.A002CA.01` | `26400IO.OO.A004CA.01` |  |  |
| 41 | 041_tagheuer_carrera-chronograph.jpg | `CBN2A1B.BA0643` | `CBN2A1A.BA0643` |  |  |
| 44 | 044_tagheuer_formula-1.jpg | `WAZ1110.BA0875` | `WAZ1010.BA0842` |  |  |
| 46 | 046_tagheuer_aquaracer-professional-200-solargraph.jpg | `WBP1190.BZ0003` | `WBP1311.BA0005` |  |  |
| 49 | 049_tagheuer_aquaracer-professional-1000-superdiver.jpg | `WBP201D.FT6197` | `WBP5114.FT6259` |  |  |
| 51 | 051_breitling_navitimer-b01-chronograph-43.jpg | `AB0138211B1A1` | `AB0138211C1A1` |  |  |
| 52 | 052_breitling_superocean-automatic-42.jpg | `A17375211B1S1` | `A17320` |  |  |
| 54 | 054_breitling_premier-b01-chronograph-42.jpg | `AB0145211G1P1` | `AB0118221G1P1` |  |  |
| 55 | 055_breitling_avenger-automatic-gmt-45.jpg | `A32395101C1X1` | `A32320101C1X1` |  |  |
| 56 | 056_breitling_superocean-heritage-b20-automatic-42.jpg | `AB2010121B1A1` | `234.30.41.21.01.001` |  |  |
| 57 | 057_breitling_navitimer-automatic-41.jpg | `A17326211B1P1` | `A17325211B1P1` |  |  |
| 59 | 059_breitling_top-time-b01-chevrolet-corvette.jpg | `AB01761A1K1X1` | `AB01766A1A1X1` |  |  |
| 61 | 061_cartier_santos-de-cartier-large.jpg | `WSSA0018` | `WSSA0029` |  |  |
| 62 | 062_cartier_tank-must-large.jpg | `WSTA0041` | `W5200013` |  |  |
| 64 | 064_cartier_tank-louis-cartier.jpg | `WGTA0011` | `W5310002` |  |  |
| 66 | 066_cartier_pasha-de-cartier-41.jpg | `WSPA0009` | `W31074M7` |  |  |
| 67 | 067_cartier_panthere-de-cartier-medium.jpg | `WSPN0007` | `W25075Z5` |  |  |
| 68 | 068_cartier_tank-francaise.jpg | `WSTA0065` | `W51008Q3` |  |  |
| 72 | 072_iwc_portugieser-automatic-42.jpg | `IW501701` | `IW500107` |  |  |
| 74 | 074_iwc_pilot-s-watch-mark-xx.jpg | `IW328201` | `IW327001` |  |  |
| 75 | 075_iwc_pilot-s-watch-chronograph-41.jpg | `IW388101` | `IW377714` |  |  |
| 76 | 076_iwc_aquatimer-automatic-42.jpg | `IW328802` | `IW329001` |  |  |
| 78 | 078_iwc_ingenieur-automatic-40.jpg | `IW328903` | `IW328907` |  |  |
| 79 | 079_iwc_pilot-s-watch-chronograph-top-gun.jpg | `IW389101` | `IW389404` |  |  |
| 80 | 080_iwc_portugieser-perpetual-calendar-44.jpg | `IW503302` | `5270R-001` |  |  |
| 81 | 081_jlc_reverso-classic-large-small-seconds.jpg | `Q3858520` | `Q3858522` |  |  |
| 82 | 082_jlc_master-ultra-thin-moon.jpg | `Q1368430` | `Q1368480` |  |  |
| 83 | 083_jlc_polaris-automatic.jpg | `Q9008180` | `Q159.8.96` |  |  |
| 85 | 085_jlc_polaris-chronograph.jpg | `Q9028181` | `Q4138480` |  |  |
| 86 | 086_jlc_reverso-tribute-duoface.jpg | `Q3988482` | `Q3978430` |  |  |
| 88 | 088_jlc_rendez-vous-night-day.jpg | `Q3468430` | `Q3468420` |  |  |
| 90 | 090_jlc_master-control-chronograph.jpg | `Q4138420` | `Q1538530` |  |  |
| 91 | 091_vc_overseas-self-winding.jpg | `4520V/210A-B128` | `4500V/110A-B126` |  |  |
| 95 | 095_vc_fiftysix-self-winding.jpg | `4600E/000A-B442` | `4600E/000A-B487` |  |  |
| 96 | 096_vc_overseas-dual-time.jpg | `7900V/110A-B334` | `7900V/110A-B546` |  |  |
| 98 | 098_vc_overseas-perpetual-calendar-ultra-thin.jpg | `4300V/120R-B064` | `4300V/000R-B509` |  |  |
| 100 | 100_vc_fiftysix-complete-calendar.jpg | `4000E/000A-B439` | `4000E/000G-B548` |  |  |
