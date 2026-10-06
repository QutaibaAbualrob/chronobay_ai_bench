# deepseek-flash-guide — FULL RUN (100 images)

```
deepseek-flash-guide   -   FULL RUN (100 images)   -   2026-10-06 12:17 UTC   [prompt mode]
========================================================================
Accuracy (strict)    52/100   (52.0%)
Accuracy (lenient)   57/100   (57.0%)
Brand correct        91/100   (91.0%)
Confidence >= 0.8    8 answers, 8 strictly right (100.0%)
Cost                 $0.2109   (rates verified 2026-09-30)
Time                 429.4s total | mean 16.73s | median 6.36s | p95 80.11s
Errors               6 (6 truncated)
```

> prompt mode: JSON asked for in the prompt, not enforced by the API — invalid/empty JSON is counted as an error, not as a wrong identification
> DeepSeek caps each image at 1,024 tokens (images are scaled to ~1300x1300 px) — less detail than the other providers get, which matters for reading small engraved text. Its score reflects that limit as much as model capability. Its price also doubles at peak hours (01-04 and 06-10 UTC, weekdays); cost uses the rate in force when each request started.

Provider `deepseek`, model `deepseek-flash`, options `{"guide": "REFERENCE_FORMATS.md"}`.

**Strict**: the exact reference (notation normalized). **Lenient**: also counts look-alikes listed in `also_accept` and the same watch on a different strap/bracelet. Errors count as failures.

## By brand

| Brand | Images | Strict | Lenient |
|---|---:|---:|---:|
| Audemars Piguet | 10 | 4 (40.0%) | 5 (50.0%) |
| Breitling | 10 | 4 (40.0%) | 4 (40.0%) |
| Cartier | 10 | 8 (80.0%) | 8 (80.0%) |
| IWC | 10 | 3 (30.0%) | 3 (30.0%) |
| Jaeger-LeCoultre | 10 | 2 (20.0%) | 4 (40.0%) |
| Omega | 10 | 6 (60.0%) | 6 (60.0%) |
| Patek Philippe | 10 | 7 (70.0%) | 7 (70.0%) |
| Rolex | 10 | 8 (80.0%) | 9 (90.0%) |
| Tag Heuer | 10 | 4 (40.0%) | 4 (40.0%) |
| Vacheron Constantin | 10 | 6 (60.0%) | 7 (70.0%) |

## Not strictly correct (48)

| # | Image | Expected | Got | Lenient | Error |
|---:|---|---|---|---|---|
| 6 | 006_rolex_explorer-36.jpg | `124270` | `214270-0003` |  |  |
| 9 | 009_rolex_oyster-perpetual-41.jpg | `124300` | `126000-0006` | yes (look-alike) |  |
| 11 | 011_omega_speedmaster-moonwatch-professional.jpg | `310.30.42.50.01.002` | `311.30.42.30.01.005` |  |  |
| 14 | 014_omega_seamaster-planet-ocean-600m.jpg | `215.30.44.21.01.001` | `210.30.42.20.01.001` |  |  |
| 16 | 016_omega_seamaster-300-heritage.jpg | `234.32.41.21.01.001` | `233.32.41.21.01.001` |  |  |
| 17 | 017_omega_speedmaster-dark-side-of-the-moon.jpg | `311.92.44.51.01.007` | `310.32.42.50.01.002` |  |  |
| 25 | 025_patek_annual-calendar.jpg | `5396R-011` | — |  | truncated: attempt 1: empty (no text in response; finish_reason=length) / attempt 2: empty (no text in response; finish_reason=leng |
| 26 | 026_patek_world-time.jpg | `5230G-001` | — |  | truncated: attempt 1: empty (no text in response; finish_reason=length) / attempt 2: empty (no text in response; finish_reason=leng |
| 28 | 028_patek_perpetual-calendar-chronograph.jpg | `5270P-001` | — |  | truncated: attempt 1: empty (no text in response; finish_reason=length) / attempt 2: empty (no text in response; finish_reason=leng |
| 32 | 032_ap_royal-oak-jumbo-extra-thin.jpg | `16202ST.OO.1240ST.01` | `15202ST.OO.1240ST.01` | yes (look-alike) |  |
| 34 | 034_ap_royal-oak-chronograph-41.jpg | `26240ST.OO.1320ST.02` | `26331ST.OO.1220ST.01` |  |  |
| 35 | 035_ap_royal-oak-perpetual-calendar.jpg | `26574ST.OO.1220ST.02` | `26574ST.OO.1220ST.01` |  |  |
| 36 | 036_ap_code-11-59-selfwinding.jpg | `15210BC.OO.A002CR.01` | `15210ST.OO.A002CR.01` |  |  |
| 37 | 037_ap_royal-oak-offshore-diver.jpg | `15720ST.OO.A027CA.01` | `15710ST.OO.A027CA.01` |  |  |
| 38 | 038_ap_royal-oak-selfwinding-41-rose-gold.jpg | `15510OR.OO.1320OR.01` | `15500OR.OO.1220OR.01` |  |  |
| 41 | 041_tagheuer_carrera-chronograph.jpg | `CBN2A1B.BA0643` | `CBN2010.BA0642` |  |  |
| 42 | 042_tagheuer_monaco-calibre-11.jpg | `CAW211P.FC6356` | `CAW2111.FC6183` |  |  |
| 44 | 044_tagheuer_formula-1.jpg | `WAZ1110.BA0875` | `WAZ1010.BA0842` |  |  |
| 45 | 045_tagheuer_carrera-date.jpg | `WBN2110.BA0639` | `WBN2411.BA0621` |  |  |
| 46 | 046_tagheuer_aquaracer-professional-200-solargraph.jpg | `WBP1190.BZ0003` | `WBP1111.BA0627` |  |  |
| 47 | 047_tagheuer_carrera-chronograph-glassbox.jpg | `CBS2212.FC6535` | `CBN2011.FC6652` |  |  |
| 51 | 051_breitling_navitimer-b01-chronograph-43.jpg | `AB0138211B1A1` | `AB0138241C1A1` |  |  |
| 52 | 052_breitling_superocean-automatic-42.jpg | `A17375211B1S1` | `A17375E71B1S1` |  |  |
| 53 | 053_breitling_chronomat-b01-42.jpg | `AB0134101B1A1` | — |  | truncated: attempt 1: empty (no text in response; finish_reason=length) / attempt 2: empty (no text in response; finish_reason=leng |
| 54 | 054_breitling_premier-b01-chronograph-42.jpg | `AB0145211G1P1` | `AB0118221G1P1` |  |  |
| 55 | 055_breitling_avenger-automatic-gmt-45.jpg | `A32395101C1X1` | `A32397101C1X1` |  |  |
| 56 | 056_breitling_superocean-heritage-b20-automatic-42.jpg | `AB2010121B1A1` | `L3.781.4.56.6` |  |  |
| 65 | 065_cartier_santos-dumont-large.jpg | `WSSA0022` | `WSSA0023` |  |  |
| 68 | 068_cartier_tank-francaise.jpg | `WSTA0065` | `WSTA0067` |  |  |
| 72 | 072_iwc_portugieser-automatic-42.jpg | `IW501701` | `IW500705` |  |  |
| 73 | 073_iwc_big-pilot-s-watch-43.jpg | `IW329301` | `IW327004` |  |  |
| 74 | 074_iwc_pilot-s-watch-mark-xx.jpg | `IW328201` | `IW327001` |  |  |
| 75 | 075_iwc_pilot-s-watch-chronograph-41.jpg | `IW388101` | `IW377714` |  |  |
| 76 | 076_iwc_aquatimer-automatic-42.jpg | `IW328802` | `210.32.42.20.01.001` |  |  |
| 79 | 079_iwc_pilot-s-watch-chronograph-top-gun.jpg | `IW389101` | — |  | truncated: attempt 1: empty (no text in response; finish_reason=length) / attempt 2: empty (no text in response; finish_reason=leng |
| 80 | 080_iwc_portugieser-perpetual-calendar-44.jpg | `IW503302` | `3940R-014` |  |  |
| 81 | 081_jlc_reverso-classic-large-small-seconds.jpg | `Q3858520` | `Q2548520` |  |  |
| 82 | 082_jlc_master-ultra-thin-moon.jpg | `Q1368430` | `Q1368420` | yes (look-alike) |  |
| 84 | 084_jlc_master-control-date.jpg | `Q4018420` | `Q1548530` |  |  |
| 85 | 085_jlc_polaris-chronograph.jpg | `Q9028181` | `Q9028180` |  |  |
| 86 | 086_jlc_reverso-tribute-duoface.jpg | `Q3988482` | `Q3978480` |  |  |
| 87 | 087_jlc_master-ultra-thin-perpetual.jpg | `Q1302520` | — |  | truncated: attempt 1: empty (no text in response; finish_reason=length) / attempt 2: empty (no text in response; finish_reason=leng |
| 88 | 088_jlc_rendez-vous-night-day.jpg | `Q3468430` | `Q3448420` | yes (look-alike) |  |
| 89 | 089_jlc_reverso-tribute-chronograph.jpg | `Q389257J` | `Q713257J` |  |  |
| 91 | 091_vc_overseas-self-winding.jpg | `4520V/210A-B128` | `4500V/110A-B128` | yes (look-alike) |  |
| 95 | 095_vc_fiftysix-self-winding.jpg | `4600E/000A-B442` | `4600E/000A-B487` |  |  |
| 97 | 097_vc_historiques-american-1921.jpg | `82035/000R-9359` | `82035/000R-9354` |  |  |
| 98 | 098_vc_overseas-perpetual-calendar-ultra-thin.jpg | `4300V/120R-B064` | `4300V/120R-B547` |  |  |
