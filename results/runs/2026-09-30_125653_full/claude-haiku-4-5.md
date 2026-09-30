# claude-haiku-4-5 — FULL RUN (100 images)

```
claude-haiku-4-5   -   FULL RUN (100 images)   -   2026-09-30 12:56 UTC   [schema mode]
========================================================================
Accuracy (strict)    11/100   (11.0%)
Accuracy (lenient)   16/100   (16.0%)
Brand correct        89/100   (89.0%)
Confidence >= 0.8    19 answers, 3 strictly right (15.8%)
Cost                 $0.2509   (rates verified 2026-09-30)
Time                 42.9s total | mean 1.66s | median 1.46s | p95 3.12s
Errors               0
```

Provider `anthropic`, model `claude-haiku-4-5`.

**Strict**: the exact reference (notation normalized). **Lenient**: also counts look-alikes listed in `also_accept` and the same watch on a different strap/bracelet. Errors count as failures.

## By brand

| Brand | Images | Strict | Lenient |
|---|---:|---:|---:|
| Audemars Piguet | 10 | 1 (10.0%) | 1 (10.0%) |
| Breitling | 10 | 0 (0.0%) | 0 (0.0%) |
| Cartier | 10 | 0 (0.0%) | 1 (10.0%) |
| IWC | 10 | 1 (10.0%) | 1 (10.0%) |
| Jaeger-LeCoultre | 10 | 1 (10.0%) | 1 (10.0%) |
| Omega | 10 | 3 (30.0%) | 3 (30.0%) |
| Patek Philippe | 10 | 2 (20.0%) | 2 (20.0%) |
| Rolex | 10 | 2 (20.0%) | 6 (60.0%) |
| Tag Heuer | 10 | 1 (10.0%) | 1 (10.0%) |
| Vacheron Constantin | 10 | 0 (0.0%) | 0 (0.0%) |

## Not strictly correct (89)

| # | Image | Expected | Got | Lenient | Error |
|---:|---|---|---|---|---|
| 1 | 001_rolex_submariner-date.jpg | `126610LN` | `116610LN` | yes (look-alike) |  |
| 2 | 002_rolex_cosmograph-daytona.jpg | `126500LN` | `116500LN` | yes (look-alike) |  |
| 5 | 005_rolex_day-date-40.jpg | `228238` | `18238` |  |  |
| 6 | 006_rolex_explorer-36.jpg | `124270` | `214270` |  |  |
| 7 | 007_rolex_sea-dweller.jpg | `126600` | `116610LN` |  |  |
| 8 | 008_rolex_yacht-master-40.jpg | `126622` | `116622` | yes (look-alike) |  |
| 9 | 009_rolex_oyster-perpetual-41.jpg | `124300` | `1601` |  |  |
| 10 | 010_rolex_submariner-no-date.jpg | `124060` | `114060` | yes (look-alike) |  |
| 11 | 011_omega_speedmaster-moonwatch-professional.jpg | `310.30.42.50.01.002` | `3570.50.00` |  |  |
| 12 | 012_omega_seamaster-diver-300m.jpg | `210.30.42.20.01.010` | `300M` |  |  |
| 13 | 013_omega_seamaster-aqua-terra-150m-41.jpg | `220.10.41.21.03.001` | `231.10.42.21.01.001` |  |  |
| 15 | 015_omega_constellation-39.jpg | `131.10.39.20.02.001` | `123.10.38.21.02.001` |  |  |
| 16 | 016_omega_seamaster-300-heritage.jpg | `234.32.41.21.01.001` | `2254.50.00` |  |  |
| 17 | 017_omega_speedmaster-dark-side-of-the-moon.jpg | `311.92.44.51.01.007` | `311.32.42.30.01.001` |  |  |
| 19 | 019_omega_seamaster-railmaster.jpg | `220.10.40.20.01.001` | `unknown` |  |  |
| 21 | 021_patek_nautilus.jpg | `5711/1A-010` | `3700/1A` |  |  |
| 22 | 022_patek_aquanaut.jpg | `5167A-001` | `5065A-001` |  |  |
| 23 | 023_patek_calatrava-white-gold.jpg | `5227G-010` | `5100G` |  |  |
| 25 | 025_patek_annual-calendar.jpg | `5396R-011` | `5115R-001` |  |  |
| 26 | 026_patek_world-time.jpg | `5230G-001` | `5130P` |  |  |
| 28 | 028_patek_perpetual-calendar-chronograph.jpg | `5270P-001` | `unknown` |  |  |
| 29 | 029_patek_calatrava-yellow-gold.jpg | `5196J-001` | `3796` |  |  |
| 30 | 030_patek_twenty-4.jpg | `4910/1200A-001` | `4910/10A-011` |  |  |
| 31 | 031_ap_royal-oak-selfwinding-41.jpg | `15500ST.OO.1220ST.01` | `5711/1A-011` |  |  |
| 32 | 032_ap_royal-oak-jumbo-extra-thin.jpg | `16202ST.OO.1240ST.01` | `15400ST.OO.1220ST.01` |  |  |
| 33 | 033_ap_royal-oak-offshore-chronograph-42.jpg | `26470ST.OO.A027CA.01` | `26170TI.OO.1000TI.01` |  |  |
| 34 | 034_ap_royal-oak-chronograph-41.jpg | `26240ST.OO.1320ST.02` | `26300ST.OO.1110ST.01` |  |  |
| 35 | 035_ap_royal-oak-perpetual-calendar.jpg | `26574ST.OO.1220ST.02` | `26574ST.OO.1220ST.01` |  |  |
| 36 | 036_ap_code-11-59-selfwinding.jpg | `15210BC.OO.A002CR.01` | `15210ST.OO.A002CR.01` |  |  |
| 37 | 037_ap_royal-oak-offshore-diver.jpg | `15720ST.OO.A027CA.01` | `26470ST.OO.1000ST.01` |  |  |
| 38 | 038_ap_royal-oak-selfwinding-41-rose-gold.jpg | `15510OR.OO.1320OR.01` | `15400OR.OO.D002CR.01` |  |  |
| 39 | 039_ap_royal-oak-offshore-chronograph-43-ceramic.jpg | `26405CE.OO.A002CA.01` | `26400SO.OO.A002CA.01` |  |  |
| 41 | 041_tagheuer_carrera-chronograph.jpg | `CBN2A1B.BA0643` | `CAZ1010.BA0842` |  |  |
| 42 | 042_tagheuer_monaco-calibre-11.jpg | `CAW211P.FC6356` | `CBL2111.BA0644` |  |  |
| 43 | 043_tagheuer_aquaracer-professional-300.jpg | `WBP201A.BA0632` | `WAY201A.BA0927` |  |  |
| 45 | 045_tagheuer_carrera-date.jpg | `WBN2110.BA0639` | `WAR211A.BA0782` |  |  |
| 46 | 046_tagheuer_aquaracer-professional-200-solargraph.jpg | `WBP1190.BZ0003` | `WAY201S.BA0927` |  |  |
| 47 | 047_tagheuer_carrera-chronograph-glassbox.jpg | `CBS2212.FC6535` | `CAL7750` |  |  |
| 48 | 048_tagheuer_link-automatic.jpg | `WBC2110.BA0603` | `WAT2110.BA0950` |  |  |
| 49 | 049_tagheuer_aquaracer-professional-1000-superdiver.jpg | `WBP201D.FT6197` | `WAY101A.FT6141` |  |  |
| 50 | 050_tagheuer_autavia-calibre-heuer-02.jpg | `CBE2110.FC8226` | `CY2110.FC6171` |  |  |
| 51 | 051_breitling_navitimer-b01-chronograph-43.jpg | `AB0138211B1A1` | `A23322` |  |  |
| 52 | 052_breitling_superocean-automatic-42.jpg | `A17375211B1S1` | `A13050.1` |  |  |
| 53 | 053_breitling_chronomat-b01-42.jpg | `AB0134101B1A1` | `323.30.40.40.06.001` |  |  |
| 54 | 054_breitling_premier-b01-chronograph-42.jpg | `AB0145211G1P1` | `Q4014420` |  |  |
| 55 | 055_breitling_avenger-automatic-gmt-45.jpg | `A32395101C1X1` | `A13385101C1A1` |  |  |
| 56 | 056_breitling_superocean-heritage-b20-automatic-42.jpg | `AB2010121B1A1` | `2210.50.00` |  |  |
| 57 | 057_breitling_navitimer-automatic-41.jpg | `A17326211B1P1` | `A17314101B1X1` |  |  |
| 58 | 058_breitling_aerospace-evo.jpg | `E79363101B1E1` | `V7632522/BC46` |  |  |
| 59 | 059_breitling_top-time-b01-chevrolet-corvette.jpg | `AB01761A1K1X1` | `A25395A6/BB81` |  |  |
| 60 | 060_breitling_chronomat-automatic-gmt-40.jpg | `A32398101B1A1` | `A13381` |  |  |
| 61 | 061_cartier_santos-de-cartier-large.jpg | `WSSA0018` | `WSSA0061` |  |  |
| 62 | 062_cartier_tank-must-large.jpg | `WSTA0041` | `W5200014` |  |  |
| 63 | 063_cartier_ballon-bleu-de-cartier-42.jpg | `W69016Z4` | `W69012Z4` | yes (look-alike) |  |
| 64 | 064_cartier_tank-louis-cartier.jpg | `WGTA0011` | `W5200027` |  |  |
| 65 | 065_cartier_santos-dumont-large.jpg | `WSSA0022` | `WSSA0061` |  |  |
| 66 | 066_cartier_pasha-de-cartier-41.jpg | `WSPA0009` | `W31044M7` |  |  |
| 67 | 067_cartier_panthere-de-cartier-medium.jpg | `WSPN0007` | `W25014B9` |  |  |
| 68 | 068_cartier_tank-francaise.jpg | `WSTA0065` | `W51011Q3` |  |  |
| 69 | 069_cartier_drive-de-cartier.jpg | `WSNM0004` | `WGNM0003` |  |  |
| 70 | 070_cartier_calibre-de-cartier-diver.jpg | `W7100056` | `W7100055` |  |  |
| 71 | 071_iwc_portugieser-chronograph.jpg | `IW371617` | `IW371446` |  |  |
| 72 | 072_iwc_portugieser-automatic-42.jpg | `IW501701` | `IW500107` |  |  |
| 73 | 073_iwc_big-pilot-s-watch-43.jpg | `IW329301` | `5004` |  |  |
| 74 | 074_iwc_pilot-s-watch-mark-xx.jpg | `IW328201` | `E79362` |  |  |
| 75 | 075_iwc_pilot-s-watch-chronograph-41.jpg | `IW388101` | `IW377714` |  |  |
| 76 | 076_iwc_aquatimer-automatic-42.jpg | `IW328802` | `IW329001` |  |  |
| 78 | 078_iwc_ingenieur-automatic-40.jpg | `IW328903` | `IW323401` |  |  |
| 79 | 079_iwc_pilot-s-watch-chronograph-top-gun.jpg | `IW389101` | `IW388002` |  |  |
| 80 | 080_iwc_portugieser-perpetual-calendar-44.jpg | `IW503302` | `5270R-001` |  |  |
| 81 | 081_jlc_reverso-classic-large-small-seconds.jpg | `Q3858520` | `Q2738422` |  |  |
| 82 | 082_jlc_master-ultra-thin-moon.jpg | `Q1368430` | `Q1362520` |  |  |
| 83 | 083_jlc_polaris-automatic.jpg | `Q9008180` | `9068670` |  |  |
| 84 | 084_jlc_master-control-date.jpg | `Q4018420` | `Q1548420` |  |  |
| 85 | 085_jlc_polaris-chronograph.jpg | `Q9028181` | `9028670` |  |  |
| 86 | 086_jlc_reverso-tribute-duoface.jpg | `Q3988482` | `Q2708410` |  |  |
| 88 | 088_jlc_rendez-vous-night-day.jpg | `Q3468430` | `Q3468420` |  |  |
| 89 | 089_jlc_reverso-tribute-chronograph.jpg | `Q389257J` | `Q2788570` |  |  |
| 90 | 090_jlc_master-control-chronograph.jpg | `Q4138420` | `Q1538420` |  |  |
| 91 | 091_vc_overseas-self-winding.jpg | `4520V/210A-B128` | `4500V/110A-B126` |  |  |
| 92 | 092_vc_overseas-chronograph.jpg | `5500V/110A-B148` | `3570.50.00` |  |  |
| 93 | 093_vc_patrimony-self-winding.jpg | `85180/000R-9248` | `81172/000R-9142` |  |  |
| 94 | 094_vc_traditionnelle-manual-winding.jpg | `82172/000R-9382` | `87172/000R-9166` |  |  |
| 95 | 095_vc_fiftysix-self-winding.jpg | `4600E/000A-B442` | `4600E/000A-B548` |  |  |
| 96 | 096_vc_overseas-dual-time.jpg | `7900V/110A-B334` | `49150/000A-9016` |  |  |
| 97 | 097_vc_historiques-american-1921.jpg | `82035/000R-9359` | `87172/000R-9341` |  |  |
| 98 | 098_vc_overseas-perpetual-calendar-ultra-thin.jpg | `4300V/120R-B064` | `5140R-001` |  |  |
| 99 | 099_vc_patrimony-moon-phase-retrograde-date.jpg | `4010U/000G-B330` | `47112/000G-9405` |  |  |
| 100 | 100_vc_fiftysix-complete-calendar.jpg | `4000E/000A-B439` | `4400V/000A-B526` |  |  |
