# deepseek-flash — FULL RUN (100 images)

```
deepseek-flash   -   FULL RUN (100 images)   -   2026-10-05 11:11 UTC   [prompt mode]
========================================================================
Accuracy (strict)    44/100   (44.0%)
Accuracy (lenient)   50/100   (50.0%)
Brand correct        96/100   (96.0%)
Confidence >= 0.8    12 answers, 9 strictly right (75.0%)
Cost                 $0.1852   (rates verified 2026-09-30)
Time                 457.4s total | mean 15.16s | median 5.82s | p95 53.39s
Errors               2 (2 truncated)
```

> prompt mode: JSON asked for in the prompt, not enforced by the API — invalid/empty JSON is counted as an error, not as a wrong identification
> DeepSeek caps each image at 1,024 tokens (images are scaled to ~1300x1300 px) — less detail than the other providers get, which matters for reading small engraved text. Its score reflects that limit as much as model capability. Its price also doubles at peak hours (01-04 and 06-10 UTC, weekdays); cost uses the rate in force when each request started.

Provider `deepseek`, model `deepseek-flash`.

**Strict**: the exact reference (notation normalized). **Lenient**: also counts look-alikes listed in `also_accept` and the same watch on a different strap/bracelet. Errors count as failures.

## By brand

| Brand | Images | Strict | Lenient |
|---|---:|---:|---:|
| Audemars Piguet | 10 | 4 (40.0%) | 5 (50.0%) |
| Breitling | 10 | 3 (30.0%) | 3 (30.0%) |
| Cartier | 10 | 5 (50.0%) | 6 (60.0%) |
| IWC | 10 | 4 (40.0%) | 4 (40.0%) |
| Jaeger-LeCoultre | 10 | 2 (20.0%) | 2 (20.0%) |
| Omega | 10 | 5 (50.0%) | 5 (50.0%) |
| Patek Philippe | 10 | 5 (50.0%) | 5 (50.0%) |
| Rolex | 10 | 6 (60.0%) | 9 (90.0%) |
| Tag Heuer | 10 | 4 (40.0%) | 4 (40.0%) |
| Vacheron Constantin | 10 | 6 (60.0%) | 7 (70.0%) |

## Not strictly correct (56)

| # | Image | Expected | Got | Lenient | Error |
|---:|---|---|---|---|---|
| 2 | 002_rolex_cosmograph-daytona.jpg | `126500LN` | `116500LN-0002` | yes (look-alike) |  |
| 4 | 004_rolex_datejust-41.jpg | `126334` | `126234` |  |  |
| 9 | 009_rolex_oyster-perpetual-41.jpg | `124300` | `126000-0005` | yes (look-alike) |  |
| 10 | 010_rolex_submariner-no-date.jpg | `124060` | `114060` | yes (look-alike) |  |
| 11 | 011_omega_speedmaster-moonwatch-professional.jpg | `310.30.42.50.01.002` | `3570.50.00` |  |  |
| 12 | 012_omega_seamaster-diver-300m.jpg | `210.30.42.20.01.010` | `210.90.42.20.01.001` |  |  |
| 13 | 013_omega_seamaster-aqua-terra-150m-41.jpg | `220.10.41.21.03.001` | `231.10.42.21.03.001` |  |  |
| 16 | 016_omega_seamaster-300-heritage.jpg | `234.32.41.21.01.001` | `233.32.41.21.01.002` |  |  |
| 17 | 017_omega_speedmaster-dark-side-of-the-moon.jpg | `311.92.44.51.01.007` | `329.32.44.51.01.001` |  |  |
| 23 | 023_patek_calatrava-white-gold.jpg | `5227G-010` | `5227G-001` |  |  |
| 26 | 026_patek_world-time.jpg | `5230G-001` | — |  | truncated: attempt 1: empty (no text in response; finish_reason=length) / attempt 2: empty (no text in response; finish_reason=leng |
| 27 | 027_patek_aquanaut-chronograph.jpg | `5968A-001` | `5164A-001` |  |  |
| 28 | 028_patek_perpetual-calendar-chronograph.jpg | `5270P-001` | `5172G-010` |  |  |
| 30 | 030_patek_twenty-4.jpg | `4910/1200A-001` | `4910/10A-012` |  |  |
| 32 | 032_ap_royal-oak-jumbo-extra-thin.jpg | `16202ST.OO.1240ST.01` | `15202ST.OO.1240ST.01` | yes (look-alike) |  |
| 34 | 034_ap_royal-oak-chronograph-41.jpg | `26240ST.OO.1320ST.02` | `26331ST.OO.1220ST.01` |  |  |
| 35 | 035_ap_royal-oak-perpetual-calendar.jpg | `26574ST.OO.1220ST.02` | `26574ST.OO.1220ST.01` |  |  |
| 36 | 036_ap_code-11-59-selfwinding.jpg | `15210BC.OO.A002CR.01` | `15210ST.OO.A002KB.01` |  |  |
| 38 | 038_ap_royal-oak-selfwinding-41-rose-gold.jpg | `15510OR.OO.1320OR.01` | `15202OR.OO.1240OR.01` |  |  |
| 39 | 039_ap_royal-oak-offshore-chronograph-43-ceramic.jpg | `26405CE.OO.A002CA.01` | `26703ST.OO.A010CA.01` |  |  |
| 41 | 041_tagheuer_carrera-chronograph.jpg | `CBN2A1B.BA0643` | `CAZ1010.BA0842` |  |  |
| 43 | 043_tagheuer_aquaracer-professional-300.jpg | `WBP201A.BA0632` | `WBP1110.BA0627` |  |  |
| 44 | 044_tagheuer_formula-1.jpg | `WAZ1110.BA0875` | `WAZ1010.BA0842` |  |  |
| 45 | 045_tagheuer_carrera-date.jpg | `WBN2110.BA0639` | `WBN2010.BA0634` |  |  |
| 46 | 046_tagheuer_aquaracer-professional-200-solargraph.jpg | `WBP1190.BZ0003` | `WBP1112.BA0627` |  |  |
| 47 | 047_tagheuer_carrera-chronograph-glassbox.jpg | `CBS2212.FC6535` | `CBN2011.FC6484` |  |  |
| 51 | 051_breitling_navitimer-b01-chronograph-43.jpg | `AB0138211B1A1` | `AB0138241C1A1` |  |  |
| 53 | 053_breitling_chronomat-b01-42.jpg | `AB0134101B1A1` | `A1338811/BB24/173A` |  |  |
| 54 | 054_breitling_premier-b01-chronograph-42.jpg | `AB0145211G1P1` | `AB0118221G1P1` |  |  |
| 55 | 055_breitling_avenger-automatic-gmt-45.jpg | `A32395101C1X1` | `A32397101C1X1` |  |  |
| 56 | 056_breitling_superocean-heritage-b20-automatic-42.jpg | `AB2010121B1A1` | `L3.781.4.56.6` |  |  |
| 58 | 058_breitling_aerospace-evo.jpg | `E79363101B1E1` | `E76325E5/BC02` |  |  |
| 59 | 059_breitling_top-time-b01-chevrolet-corvette.jpg | `AB01761A1K1X1` | `AB01761A1A1` |  |  |
| 61 | 061_cartier_santos-de-cartier-large.jpg | `WSSA0018` | `WSSA0009` |  |  |
| 62 | 062_cartier_tank-must-large.jpg | `WSTA0041` | `W5200003` |  |  |
| 64 | 064_cartier_tank-louis-cartier.jpg | `WGTA0011` | `WGTA0089` |  |  |
| 67 | 067_cartier_panthere-de-cartier-medium.jpg | `WSPN0007` | `WSPN0006` | yes (look-alike) |  |
| 68 | 068_cartier_tank-francaise.jpg | `WSTA0065` | `W51008Q3` |  |  |
| 72 | 072_iwc_portugieser-automatic-42.jpg | `IW501701` | `IW500705` |  |  |
| 73 | 073_iwc_big-pilot-s-watch-43.jpg | `IW329301` | `IW327001` |  |  |
| 74 | 074_iwc_pilot-s-watch-mark-xx.jpg | `IW328201` | `IW327001` |  |  |
| 76 | 076_iwc_aquatimer-automatic-42.jpg | `IW328802` | `215.32.44.21.01.001` |  |  |
| 79 | 079_iwc_pilot-s-watch-chronograph-top-gun.jpg | `IW389101` | `IW389404` |  |  |
| 80 | 080_iwc_portugieser-perpetual-calendar-44.jpg | `IW503302` | `IW392101` |  |  |
| 82 | 082_jlc_master-ultra-thin-moon.jpg | `Q1368430` | `Q1368470` |  |  |
| 83 | 083_jlc_polaris-automatic.jpg | `Q9008180` | `Q9008480` |  |  |
| 84 | 084_jlc_master-control-date.jpg | `Q4018420` | `Q1548530` |  |  |
| 85 | 085_jlc_polaris-chronograph.jpg | `Q9028181` | `Q9028480` |  |  |
| 86 | 086_jlc_reverso-tribute-duoface.jpg | `Q3988482` | `Q2438522` |  |  |
| 87 | 087_jlc_master-ultra-thin-perpetual.jpg | `Q1302520` | — |  | truncated: attempt 1: empty (no text in response; finish_reason=length) / attempt 2: empty (no text in response; finish_reason=leng |
| 88 | 088_jlc_rendez-vous-night-day.jpg | `Q3468430` | `Q3468490` |  |  |
| 89 | 089_jlc_reverso-tribute-chronograph.jpg | `Q389257J` | `Q2542570` |  |  |
| 91 | 091_vc_overseas-self-winding.jpg | `4520V/210A-B128` | `4500V/110A-B128` | yes (look-alike) |  |
| 95 | 095_vc_fiftysix-self-winding.jpg | `4600E/000A-B442` | `4600E/000A-B487` |  |  |
| 97 | 097_vc_historiques-american-1921.jpg | `82035/000R-9359` | `82035/000R-9354` |  |  |
| 100 | 100_vc_fiftysix-complete-calendar.jpg | `4000E/000A-B439` | `4000E/000A-B548` |  |  |
