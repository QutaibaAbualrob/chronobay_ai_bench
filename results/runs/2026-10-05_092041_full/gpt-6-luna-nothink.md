# gpt-6-luna-nothink — FULL RUN (100 images)

```
gpt-6-luna-nothink   -   FULL RUN (100 images)   -   2026-10-05 09:20 UTC   [schema mode]
========================================================================
Accuracy (strict)    38/100   (38.0%)
Accuracy (lenient)   41/100   (41.0%)
Brand correct        97/100   (97.0%)
Confidence >= 0.8    24 answers, 13 strictly right (54.2%)
Cost                 $0.0287   (rates verified 2026-10-01)
Time                 37.9s total | mean 2.75s | median 2.46s | p95 4.14s
Errors               0
```

Provider `openai`, model `gpt-6-luna`, options `{"reasoning_effort": "none"}`.

**Strict**: the exact reference (notation normalized). **Lenient**: also counts look-alikes listed in `also_accept` and the same watch on a different strap/bracelet. Errors count as failures.

## By brand

| Brand | Images | Strict | Lenient |
|---|---:|---:|---:|
| Audemars Piguet | 10 | 4 (40.0%) | 4 (40.0%) |
| Breitling | 10 | 3 (30.0%) | 3 (30.0%) |
| Cartier | 10 | 6 (60.0%) | 6 (60.0%) |
| IWC | 10 | 3 (30.0%) | 3 (30.0%) |
| Jaeger-LeCoultre | 10 | 2 (20.0%) | 2 (20.0%) |
| Omega | 10 | 4 (40.0%) | 6 (60.0%) |
| Patek Philippe | 10 | 5 (50.0%) | 5 (50.0%) |
| Rolex | 10 | 5 (50.0%) | 6 (60.0%) |
| Tag Heuer | 10 | 3 (30.0%) | 3 (30.0%) |
| Vacheron Constantin | 10 | 3 (30.0%) | 3 (30.0%) |

## Not strictly correct (62)

| # | Image | Expected | Got | Lenient | Error |
|---:|---|---|---|---|---|
| 6 | 006_rolex_explorer-36.jpg | `124270` | `214270` |  |  |
| 7 | 007_rolex_sea-dweller.jpg | `126600` | `116680` |  |  |
| 8 | 008_rolex_yacht-master-40.jpg | `126622` | `226659` |  |  |
| 9 | 009_rolex_oyster-perpetual-41.jpg | `124300` | `126000` | yes (look-alike) |  |
| 10 | 010_rolex_submariner-no-date.jpg | `124060` | `226659` |  |  |
| 11 | 011_omega_speedmaster-moonwatch-professional.jpg | `310.30.42.50.01.002` | `310.30.42.50.01.001` | yes (look-alike) |  |
| 12 | 012_omega_seamaster-diver-300m.jpg | `210.30.42.20.01.010` | `210.30.42.20.01.001` | yes (look-alike) |  |
| 13 | 013_omega_seamaster-aqua-terra-150m-41.jpg | `220.10.41.21.03.001` | `220.10.41.21.03.002` |  |  |
| 14 | 014_omega_seamaster-planet-ocean-600m.jpg | `215.30.44.21.01.001` | `232.30.44.22.01.001` |  |  |
| 17 | 017_omega_speedmaster-dark-side-of-the-moon.jpg | `311.92.44.51.01.007` | `311.92.44.51.01.003` |  |  |
| 20 | 020_omega_de-ville-prestige.jpg | `424.13.40.20.02.001` | `431.13.41.21.02.001` |  |  |
| 22 | 022_patek_aquanaut.jpg | `5167A-001` | `5168G-010` |  |  |
| 24 | 024_patek_nautilus-moon-phase.jpg | `5712/1A-001` | `5990/1A-001` |  |  |
| 26 | 026_patek_world-time.jpg | `5230G-001` | `5130G-001` |  |  |
| 29 | 029_patek_calatrava-yellow-gold.jpg | `5196J-001` | `5227J-001` |  |  |
| 30 | 030_patek_twenty-4.jpg | `4910/1200A-001` | `4910/10A-011` |  |  |
| 31 | 031_ap_royal-oak-selfwinding-41.jpg | `15500ST.OO.1220ST.01` | `15500ST.OO.1220ST.03` |  |  |
| 32 | 032_ap_royal-oak-jumbo-extra-thin.jpg | `16202ST.OO.1240ST.01` | `15500ST.OO.1220ST.03` |  |  |
| 33 | 033_ap_royal-oak-offshore-chronograph-42.jpg | `26470ST.OO.A027CA.01` | `26400IO.OO.A004CA.01` |  |  |
| 34 | 034_ap_royal-oak-chronograph-41.jpg | `26240ST.OO.1320ST.02` | `26331ST.OO.1220ST.02` |  |  |
| 36 | 036_ap_code-11-59-selfwinding.jpg | `15210BC.OO.A002CR.01` | `15210ST.OO.A002CR.01` |  |  |
| 39 | 039_ap_royal-oak-offshore-chronograph-43-ceramic.jpg | `26405CE.OO.A002CA.01` | `26420CE.OO.A127CR.01` |  |  |
| 44 | 044_tagheuer_formula-1.jpg | `WAZ1110.BA0875` | `WAZ2011.BA0842` |  |  |
| 45 | 045_tagheuer_carrera-date.jpg | `WBN2110.BA0639` | `WBN2113.BA0639` |  |  |
| 46 | 046_tagheuer_aquaracer-professional-200-solargraph.jpg | `WBP1190.BZ0003` | `WBP1113.BA0000` |  |  |
| 47 | 047_tagheuer_carrera-chronograph-glassbox.jpg | `CBS2212.FC6535` | `CBN201D.FC6543` |  |  |
| 48 | 048_tagheuer_link-automatic.jpg | `WBC2110.BA0603` | `WAT2110.BA0950` |  |  |
| 49 | 049_tagheuer_aquaracer-professional-1000-superdiver.jpg | `WBP201D.FT6197` | `WBP208B.FT6201` |  |  |
| 50 | 050_tagheuer_autavia-calibre-heuer-02.jpg | `CBE2110.FC8226` | `CBE2110.FC ack?` |  |  |
| 51 | 051_breitling_navitimer-b01-chronograph-43.jpg | `AB0138211B1A1` | `AB0138211C1A1` |  |  |
| 52 | 052_breitling_superocean-automatic-42.jpg | `A17375211B1S1` | `AB2030161C1S1` |  |  |
| 54 | 054_breitling_premier-b01-chronograph-42.jpg | `AB0145211G1P1` | `431.13.42.51.02.001` |  |  |
| 55 | 055_breitling_avenger-automatic-gmt-45.jpg | `A32395101C1X1` | `A32320101C1X1` |  |  |
| 56 | 056_breitling_superocean-heritage-b20-automatic-42.jpg | `AB2010121B1A1` | `233.30.41.21.01.001` |  |  |
| 57 | 057_breitling_navitimer-automatic-41.jpg | `A17326211B1P1` | `A13314101B1X1` |  |  |
| 59 | 059_breitling_top-time-b01-chevrolet-corvette.jpg | `AB01761A1K1X1` | `AB01772A1B1X1` |  |  |
| 62 | 062_cartier_tank-must-large.jpg | `WSTA0041` | `WSTA0052` |  |  |
| 63 | 063_cartier_ballon-bleu-de-cartier-42.jpg | `W69016Z4` | `WSBB0040` |  |  |
| 66 | 066_cartier_pasha-de-cartier-41.jpg | `WSPA0009` | `WSPA0013` |  |  |
| 70 | 070_cartier_calibre-de-cartier-diver.jpg | `W7100056` | `W2CA0008` |  |  |
| 71 | 071_iwc_portugieser-chronograph.jpg | `IW371617` | `IW371605` |  |  |
| 72 | 072_iwc_portugieser-automatic-42.jpg | `IW501701` | `IW358303` |  |  |
| 73 | 073_iwc_big-pilot-s-watch-43.jpg | `IW329301` | `IW327001` |  |  |
| 74 | 074_iwc_pilot-s-watch-mark-xx.jpg | `IW328201` | `IW-327011` |  |  |
| 76 | 076_iwc_aquatimer-automatic-42.jpg | `IW328802` | `IW328902` |  |  |
| 79 | 079_iwc_pilot-s-watch-chronograph-top-gun.jpg | `IW389101` | `IW389404` |  |  |
| 80 | 080_iwc_portugieser-perpetual-calendar-44.jpg | `IW503302` | `5270R-001` |  |  |
| 81 | 081_jlc_reverso-classic-large-small-seconds.jpg | `Q3858520` | `Q3978430` |  |  |
| 82 | 082_jlc_master-ultra-thin-moon.jpg | `Q1368430` | `Q1368470` |  |  |
| 83 | 083_jlc_polaris-automatic.jpg | `Q9008180` | `Q9038180` |  |  |
| 85 | 085_jlc_polaris-chronograph.jpg | `Q9028181` | `Q4138180` |  |  |
| 86 | 086_jlc_reverso-tribute-duoface.jpg | `Q3988482` | `Q3978480` |  |  |
| 87 | 087_jlc_master-ultra-thin-perpetual.jpg | `Q1302520` | `Q4142520` |  |  |
| 88 | 088_jlc_rendez-vous-night-day.jpg | `Q3468430` | `Q3468421` |  |  |
| 89 | 089_jlc_reverso-tribute-chronograph.jpg | `Q389257J` | `Q3978430` |  |  |
| 91 | 091_vc_overseas-self-winding.jpg | `4520V/210A-B128` | `4600V/200A-B980` |  |  |
| 92 | 092_vc_overseas-chronograph.jpg | `5500V/110A-B148` | `5520V/210A-B148` |  |  |
| 94 | 094_vc_traditionnelle-manual-winding.jpg | `82172/000R-9382` | `85180/000R-9248` |  |  |
| 96 | 096_vc_overseas-dual-time.jpg | `7900V/110A-B334` | `7900V/110A-B546` |  |  |
| 98 | 098_vc_overseas-perpetual-calendar-ultra-thin.jpg | `4300V/120R-B064` | `4300V/000R-B509` |  |  |
| 99 | 099_vc_patrimony-moon-phase-retrograde-date.jpg | `4010U/000G-B330` | `4000U/000R-B516` |  |  |
| 100 | 100_vc_fiftysix-complete-calendar.jpg | `4000E/000A-B439` | `4000E/000A-B548` |  |  |
