# gpt-6.1-sol-low — FULL RUN (100 images)

```
gpt-6.1-sol-low   -   FULL RUN (100 images)   -   2026-10-05 09:33 UTC   [schema mode]
========================================================================
Accuracy (strict)    70/100   (70.0%)
Accuracy (lenient)   77/100   (77.0%)
Brand correct        100/100   (100.0%)
Confidence >= 0.8    73 answers, 59 strictly right (80.8%)
Cost                 $0.7019   (rates verified 2026-10-05)
Time                 98.3s total | mean 7.17s | median 5.97s | p95 14.69s
Errors               0
```

Provider `openai`, model `gpt-6.1-sol`, options `{"reasoning_effort": "low"}`.

**Strict**: the exact reference (notation normalized). **Lenient**: also counts look-alikes listed in `also_accept` and the same watch on a different strap/bracelet. Errors count as failures.

## By brand

| Brand | Images | Strict | Lenient |
|---|---:|---:|---:|
| Audemars Piguet | 10 | 6 (60.0%) | 7 (70.0%) |
| Breitling | 10 | 5 (50.0%) | 5 (50.0%) |
| Cartier | 10 | 6 (60.0%) | 7 (70.0%) |
| IWC | 10 | 6 (60.0%) | 6 (60.0%) |
| Jaeger-LeCoultre | 10 | 5 (50.0%) | 7 (70.0%) |
| Omega | 10 | 8 (80.0%) | 8 (80.0%) |
| Patek Philippe | 10 | 10 (100.0%) | 10 (100.0%) |
| Rolex | 10 | 7 (70.0%) | 9 (90.0%) |
| Tag Heuer | 10 | 8 (80.0%) | 8 (80.0%) |
| Vacheron Constantin | 10 | 9 (90.0%) | 10 (100.0%) |

## Not strictly correct (30)

| # | Image | Expected | Got | Lenient | Error |
|---:|---|---|---|---|---|
| 2 | 002_rolex_cosmograph-daytona.jpg | `126500LN` | `116500LN-0002` | yes (look-alike) |  |
| 5 | 005_rolex_day-date-40.jpg | `228238` | `218238` |  |  |
| 8 | 008_rolex_yacht-master-40.jpg | `126622` | `116622-0003` | yes (look-alike) |  |
| 12 | 012_omega_seamaster-diver-300m.jpg | `210.30.42.20.01.010` | `210.90.42.20.01.001` |  |  |
| 17 | 017_omega_speedmaster-dark-side-of-the-moon.jpg | `311.92.44.51.01.007` | `311.92.44.51.01.003` |  |  |
| 31 | 031_ap_royal-oak-selfwinding-41.jpg | `15500ST.OO.1220ST.01` | `15400ST.OO.1220ST.03` |  |  |
| 32 | 032_ap_royal-oak-jumbo-extra-thin.jpg | `16202ST.OO.1240ST.01` | `15202ST.OO.1240ST.01` | yes (look-alike) |  |
| 34 | 034_ap_royal-oak-chronograph-41.jpg | `26240ST.OO.1320ST.02` | `26315ST.OO.1256ST.02` |  |  |
| 38 | 038_ap_royal-oak-selfwinding-41-rose-gold.jpg | `15510OR.OO.1320OR.01` | `15500OR.OO.1220OR.01` |  |  |
| 41 | 041_tagheuer_carrera-chronograph.jpg | `CBN2A1B.BA0643` | `CAR201Z.BA0714` |  |  |
| 46 | 046_tagheuer_aquaracer-professional-200-solargraph.jpg | `WBP1190.BZ0003` | `WBP1310.BA0005` |  |  |
| 51 | 051_breitling_navitimer-b01-chronograph-43.jpg | `AB0138211B1A1` | `AB0138241C1A1` |  |  |
| 52 | 052_breitling_superocean-automatic-42.jpg | `A17375211B1S1` | `A17376211B1S1` |  |  |
| 54 | 054_breitling_premier-b01-chronograph-42.jpg | `AB0145211G1P1` | `AB0145331G1P1` |  |  |
| 55 | 055_breitling_avenger-automatic-gmt-45.jpg | `A32395101C1X1` | `A32397101C1X1` |  |  |
| 57 | 057_breitling_navitimer-automatic-41.jpg | `A17326211B1P1` | `A17326241B1P1` |  |  |
| 62 | 062_cartier_tank-must-large.jpg | `WSTA0041` | `W5200013` |  |  |
| 64 | 064_cartier_tank-louis-cartier.jpg | `WGTA0011` | `W1560017` |  |  |
| 66 | 066_cartier_pasha-de-cartier-41.jpg | `WSPA0009` | `W31044M7` |  |  |
| 67 | 067_cartier_panthere-de-cartier-medium.jpg | `WSPN0007` | `WSPN0006` | yes (look-alike) |  |
| 72 | 072_iwc_portugieser-automatic-42.jpg | `IW501701` | `IW500701` |  |  |
| 75 | 075_iwc_pilot-s-watch-chronograph-41.jpg | `IW388101` | `IW377714` |  |  |
| 76 | 076_iwc_aquatimer-automatic-42.jpg | `IW328802` | `IW329001` |  |  |
| 80 | 080_iwc_portugieser-perpetual-calendar-44.jpg | `IW503302` | `IW503402` |  |  |
| 81 | 081_jlc_reverso-classic-large-small-seconds.jpg | `Q3858520` | `Q3858522` |  |  |
| 82 | 082_jlc_master-ultra-thin-moon.jpg | `Q1368430` | `Q1368420` | yes (look-alike) |  |
| 85 | 085_jlc_polaris-chronograph.jpg | `Q9028181` | `Q9028180` |  |  |
| 86 | 086_jlc_reverso-tribute-duoface.jpg | `Q3988482` | `Q3978480` |  |  |
| 88 | 088_jlc_rendez-vous-night-day.jpg | `Q3468430` | `Q3448430` | yes (look-alike) |  |
| 91 | 091_vc_overseas-self-winding.jpg | `4520V/210A-B128` | `4500V/110A-B128` | yes (look-alike) |  |
