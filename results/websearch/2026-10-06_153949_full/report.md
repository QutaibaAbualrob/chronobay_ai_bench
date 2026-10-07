# Web search study: the model searches for itself - FULL RUN (100 images)

Idea 5 in `FINDINGS.md`, section 4. Rebuilt by `websearch_study.py report` from saved answers.

Run `2026-10-06_153949_full`, model `gpt-6-luna` (`gpt-6-luna`, default reasoning effort). OpenAI's web search tool was on, limited to 3 searches per photo. One call per photo. 90 photos. It was asked for exactly three references: its best match and the two nearest alternatives.

> **INCOMPLETE.** 10 of the 100 photos have no answer yet (rows 67, 78, 83, 88, 89, 91, 92, 95, 98, 100): the run stopped before reaching them, or the call was refused for rate limit or lack of credit. Every table below covers the 90 photos that have an answer. Continue the run with `--resume`.

Notes on this run:

- The run stopped twice. On 2026-10-06 it ended after 82 photos with no error message, most likely because the session that started it closed. 21 of those 82 calls had been refused by the OpenAI limit of 200,000 tokens a minute for this model, with three calls running at once. It was continued on 2026-10-07 with two calls at once and waits on that limit, and stopped at 90 answered photos when the OpenAI account ran out of credit.

## Result

Out of 90 photos.

| | Exact reference | Also counting accepted look-alikes |
|---|---:|---:|
| First reference is right | 61 | 64 |
| Its references, up to three, contain it | 70 | 71 |
| Brand right | 89 | |

Where the right reference stands in its list: first 61, second 5, third 4, not in it 20. References given per photo: one 0, two 0, three 90, none 0.

For context, the same photos in the saved benchmark runs (one reference, no search, a different prompt): gpt-6-luna-nothink 35, gpt-6-luna-xhigh 50, deepseek-flash 41, claude-sonnet-5-5-nothink 66 right.

## Cost and speed

| | Per photo | This run |
|---|---:|---:|
| Searches made | 2.0 | 176 |
| Pages opened | 0.0 | 4 |
| Search fee at $0.01 a search | $0.0196 | $1.76 |
| Model tokens | $0.0023 | $0.21 |
| **Total** | **$0.0218** | **$1.97** |
| Input tokens | 22,424 | |
| Output tokens | 1,113 | |
| Time, median | 27.4s | |
| Time, longest | 136.3s | |

Photos by number of searches: 23 with 1 search, 48 with 2 searches, 19 with 3 searches. No photo went over the limit of 3.

The number of searches is the one OpenAI's API reports for each call (`tool_usage.web_search.num_requests`). One search can hold several queries (554 queries in this run), and opening a page is not counted. The fee is that number times $0.01, the listed price; the API does not report an amount in dollars, so the account's usage page has the last word.
At this rate all 100 photos would cost about $2.18.

Calls that failed: 0. Answers tidied to fit the format: 0. Answer format enforced by the API: yes.

## Every photo

| Row | Expected | Its references | First right | In its three | Searches | Time | What it searched for |
|---:|---|---|:-:|:-:|---:|---:|---|
| 1 | `126610LN` | `126610LN`, `116610LN`, `126610LV` | yes | yes | 1 | 11s | site:rolex.com/watches/submariner m126610ln-0001 Submariner date 41 mm; Rolex Submariner Date black dial 126610LN reference 116610LN WatchBase; Rolex… |
| 2 | `126500LN` | `126500LN`, `116500LN`, `116520` | yes | yes | 1 | 10s | site:rolex.com/watches/cosmograph-daytona 126500LN black dial 40 mm; Rolex 126500LN black dial silver subdials 116500LN reference Daytona official; R… |
| 3 | `126710BLRO` | `126710BLRO`, `116719BLRO`, `16710` | yes | yes | 1 | 13s | site:rolex.com watches gmt-master-ii 126710BLRO Jubilee 40 mm; Rolex GMT-Master II 126710BLRO Pepsi Jubilee reference WatchBase; Rolex GMT Master II… |
| 4 | `126334` | `126334`, `126300`, `116334` | yes | yes | 2 | 17s | site:rolex.com Datejust 41 blue fluted motif dial 126334 Jubilee; Rolex 126334 blue fluted motif dial reference Datejust 41; Rolex Datejust 41 blue m… |
| 5 | `228238` | `228238`, `128238`, `218238` | yes | yes | 2 | 16s | site:rolex.com watches day-date 40 228238 champagne dial yellow gold; Rolex 228238 champagne dial day date 40 reference; Rolex Day-Date 40 champagne… |
| 6 | `124270` | `124270`, `214270`, `224270` | yes | yes | 1 | 10s | site:rolex.com/watches/explorer 124270 224270 Explorer 36 40 black dial; Rolex Explorer blue dial photo 124270 reference 39 mm 214270; Rolex Explorer… |
| 7 | `126600` | `126600`, `116600`, `126603` | yes | yes | 2 | 19s | Rolex Yacht-Master black dial 40 reference black dial platinum bezel 116622; Rolex official Yacht-Master 40 black dial reference 116622 black; Rolex… |
| 8 | `126622` | `126622`, `116622`, `268622` | yes | yes | 2 | 15s | site:rolex.com Yacht-Master 40 rhodium 126622; Rolex Yacht-Master 126622 rhodium dial 116622 reference WatchBase; Rolex 126622 gray dial blue seconds… |
| 9 | `124300` | `126000`, `124300`, `124200` | no | yes | 1 | 45s | site:rolex.com Oyster Perpetual turquoise 41 124300; Rolex turquoise dial Oyster Perpetual photo 124300 126000 reference; Rolex Oyster Perpetual turq… |
| 10 | `124060` | `124060`, `114060`, `14060M` | yes | yes | 1 | 10s | site:rolex.com watches submariner 124060 41 mm; Rolex Submariner 124060 114060 14060M references black no date 41mm |
| 11 | `310.30.42.50.01.002` | `310.30.42.50.01.002`, `310.30.42.50.01.001`, `311.30.42.30.01.005` | yes | yes | 1 | 14s | site:omegawatches.com 310.30.42.50.01.002 Speedmaster Moonwatch; Omega Speedmaster 310.30.42.50.01.001 310.30.42.50.01.002 official reference sapphir… |
| 12 | `210.30.42.20.01.010` | `210.30.42.20.01.010`, `210.32.42.20.01.003`, `210.30.42.20.06.002` | yes | yes | 2 | 36s | site:omegawatches.com Seamaster Diver 300M black dial mesh bracelet 210.30.42.20.01.010; Omega Seamaster Diver 300M black dial mesh bracelet referenc… |
| 13 | `220.10.41.21.03.001` | `220.10.41.21.03.001`, `220.10.38.20.03.001`, `231.10.42.21.03.001` | yes | yes | 2 | 86s | Omega Aqua Terra blue dial horizontal teak 38 mm steel bracelet reference date 6 220.10; Omega Aqua Terra blue teak dial reference steel bracelet 41… |
| 14 | `215.30.44.21.01.001` | `232.30.44.22.01.001`, `232.30.44.22.01.002`, `215.30.44.22.01.001` | no | no | 2 | 110s | site:omegawatches.com 215.30.44.22.01.001 Planet Ocean GMT; Omega Planet Ocean GMT black dial orange GMT hand steel bracelet reference 43.5 215.30.44… |
| 15 | `131.10.39.20.02.001` | `131.10.39.20.02.001`, `131.10.39.20.06.001`, `131.10.39.20.01.001` | yes | yes | 1 | 31s | site:omegawatches.com Constellation 39 mm Master Chronometer silver dial 131.10.39.20.02.001; Omega Constellation Co-Axial Master Chronometer silver… |
| 16 | `234.32.41.21.01.001` | `234.32.41.21.01.001`, `234.30.41.21.01.001`, `233.30.41.21.01.001` | yes | yes | 1 | 56s | site:omegawatches.com Seamaster 300 234.32.41.21.01.001; Omega Seamaster 300 black dial brown leather 234.32.41.21.01.001 WatchBase; Omega Seamaster… |
| 17 | `311.92.44.51.01.007` | `311.92.44.51.01.003`, `311.92.44.51.01.007`, `311.92.44.51.01.004` | no | yes | 2 | 19s | site:omegawatches.com Speedmaster black ceramic grey fabric strap date 6 red Speedmaster reference; Omega Speedmaster black ceramic grey fabric strap… |
| 18 | `210.90.42.20.01.001` | `210.90.42.20.01.001`, `210.92.42.20.01.001`, `210.30.42.20.01.001` | yes | yes | 2 | 60s | site:omegawatches.com 210.90.42.20.01.001 Seamaster 007 Edition mesh bracelet; Omega 210.90.42.20.01.001 WatchBase brown bezel titanium 42; Omega NTT… |
| 19 | `220.10.40.20.01.001` | `220.10.40.20.01.001`, `220.10.40.20.06.001`, `220.10.40.20.03.001` | yes | yes | 1 | 9s | Omega Railmaster vertical brushed grey brown dial beige indices bracelet reference denim dial; Omega Railmaster 220.10.40.20.01.001 dial reference of… |
| 20 | `424.13.40.20.02.001` | `424.13.40.20.02.001`, `424.10.40.20.02.001`, `424.13.40.20.02.002` | yes | yes | 1 | 10s | site:omegawatches.com De Ville Prestige Co-Axial silver dial Roman numerals date 39.5 reference; Omega De Ville Prestige Co-Axial silver dial date Ro… |
| 21 | `5711/1A-010` | `5711/1A-010`, `5711/1A-001`, `5711/1A-011` | yes | yes | 2 | 46s | site:patek.com 5711/1A-010 Nautilus blue dial; Patek Philippe Nautilus 5711/1A-010 blue dial reference WatchBase; Patek Philippe 5711/1A-001 Nautilus… |
| 22 | `5167A-001` | `5167A-001`, `5167R-001`, `5168G-001` | yes | yes | 1 | 70s | site:patek.com 5167A-001 Aquanaut black dial composite strap 40.8; Patek Philippe Aquanaut 5167A-001 grey black dial rubber strap 5167A reference; Pa… |
| 23 | `5227G-010` | `5227G-010`, `5227G-001`, `5227R-001` | yes | yes | 2 | 17s | site:patek.com 5227G-010 black dial Calatrava; Patek Philippe 5227G-010 black dial reference 5227G-010; Patek Philippe black dial date Calatrava whit… |
| 24 | `5712/1A-001` | `5726/1A-001`, `5726/1A-010`, `5726/1A-014` | no | no | 1 | 14s | site:patek.com 5726/1A-001 Nautilus annual calendar black dial; Patek Philippe 5726/1A black dial reference 40.5 WatchBase; Patek Nautilus 5726 black… |
| 25 | `5396R-011` | `5205R-001`, `5205R-010`, `5205G-001` | no | no | 2 | 113s | site:patek.com 5205R-001 rose gold ivory dial reference; Patek Philippe 5205R-001 ivory dial black alligator official reference annual calendar; Pate… |
| 26 | `5230G-001` | `5230G-001`, `5230R-001`, `5130G-001` | yes | yes | 2 | 18s | site:patek.com 5230G World Time grey dial reference; Patek Philippe 5230G-001 grey dial black alligator strap 38.5; Patek Philippe World Time white g… |
| 27 | `5968A-001` | `5968A-001`, `5968G-001`, `5968G-010` | yes | yes | 1 | 10s | site:patek.com 5968A-001 Aquanaut Chronograph black dial; Patek Philippe Aquanaut Chronograph 5968A-001 official reference 5968A 42.2 mm; Patek Phili… |
| 28 | `5270P-001` | `5270P-001`, `5270P-014`, `5270G-014` | yes | yes | 3 | 32s | Patek Philippe salmon dial chronograph Arabic numerals reference salmon 5172G-010 official; site:patek.com 5172G-010 salmon dial chronograph; watch s… |
| 29 | `5196J-001` | `5196J-001`, `5196G-001`, `3796J` | yes | yes | 2 | 23s | site:patek.com 5196J Calatrava small seconds yellow gold; Patek Philippe Calatrava yellow gold small seconds baton markers white dial reference 5196J… |
| 30 | `4910/1200A-001` | `4910/1200A-001`, `4910/1200A-010`, `4910/10A-012` | yes | yes | 2 | 49s | site:patek.com Twenty~4 blue dial diamond bezel steel bracelet 4910 reference; Patek Philippe 4910/10A blue dial diamond bezel reference blue; Patek… |
| 31 | `15500ST.OO.1220ST.01` | `15500ST.OO.1220ST.01`, `15500ST.OO.1220ST.02`, `15510ST.OO.1320ST.01` | yes | yes | 3 | 21s | site:audemarspiguet.com Royal Oak 41 mm blue dial date 15500ST reference; Audemars Piguet Royal Oak blue dial 15500ST.00.1220ST.01 official reference… |
| 32 | `16202ST.OO.1240ST.01` | `15510ST.OO.1320ST.01`, `15500ST.OO.1220ST.01`, `15400ST.OO.1220ST.03` | no | no | 2 | 22s | site:audemarspiguet.com Royal Oak Selfwinding 41 mm blue dial 15510ST.OO.1320ST.07; Audemars Piguet 15510ST blue dial official reference 41 mm; Audem… |
| 33 | `26470ST.OO.A027CA.01` | `26470ST.OO.A027CA.01`, `26470ST.OO.A028CR.01`, `26470ST.OO.A101CR.01` | yes | yes | 2 | 76s | Audemars Piguet Royal Oak Offshore Chronograph blue dial orange hands silver subdials black rubber strap reference; site:audemarspiguet.com Royal Oak… |
| 34 | `26240ST.OO.1320ST.02` | `26331ST.OO.1220ST.02`, `26331ST.OO.1220ST.01`, `26331ST.OO.1220ST.03` | no | no | 2 | 28s | site:audemarspiguet.com 26331ST black dial chronograph reference Royal Oak; Audemars Piguet 26331ST black dial chronograph reference .02 .03; Audemar… |
| 35 | `26574ST.OO.1220ST.02` | `26574ST.OO.1220ST.02`, `26574ST.OO.1220ST.01`, `26574ST.OO.1220ST.03` | yes | yes | 1 | 31s | site:audemarspiguet.com 26574ST blue dial Royal Oak Perpetual Calendar reference; Audemars Piguet 26574ST.OO.1220ST.01 blue dial 41mm perpetual calen… |
| 36 | `15210BC.OO.A002CR.01` | `15210CR.OO.A002CR.01`, `15210CR.OO.A009CR.01`, `15210BC.OO.A002CR.01` | no | yes | 2 | 24s | site:audemarspiguet.com Code 11.59 Selfwinding grey dial 41 mm steel reference; Audemars Piguet Code 11.59 grey dial Arabic numerals steel black alli… |
| 37 | `15720ST.OO.A027CA.01` | `15720ST.OO.A027CA.01`, `15710ST.OO.A027CA.01`, `15720ST.OO.A009CA.01` | yes | yes | 2 | 16s | site:audemarspiguet.com 15710ST blue rubber strap blue dial Royal Oak Offshore Diver; Audemars Piguet 15710ST.OO.A027CA blue dial blue rubber strap 4… |
| 38 | `15510OR.OO.1320OR.01` | `15510OR.OO.1320OR.03`, `15500OR.OO.1220OR.01`, `15510ST.OO.1320ST.06` | no | no | 3 | 35s | site:audemarspiguet.com 37 mm pink gold blue dial Royal Oak selfwinding reference blue dial bracelet; Audemars Piguet Royal Oak 37mm pink gold blue d… |
| 39 | `26405CE.OO.A002CA.01` | `26420TI.OO.A027CA.01`, `26420IO.OO.A009CA.01`, `26238TI.OO.2000TI.01` | no | no | 2 | 96s | site:audemarspiguet.com Royal Oak Offshore chronograph grey dial tachymeter 43 titanium reference; Audemars Piguet 43mm Royal Oak Offshore grey dial… |
| 40 | `15407ST.OO.1220ST.01` | `15407ST.OO.1220ST.02`, `15407ST.OO.1220ST.01`, `15407OR.OO.1220OR.01` | no | yes | 2 | 44s | site:audemarspiguet.com "15407ST" Royal Oak Double Balance Wheel Openworked; Audemars Piguet 15407ST.OO.1220ST.01 reference 15407 alternatives; Royal… |
| 41 | `CBN2A1B.BA0643` | `CBN2A1B.BA0643`, `CBN2A1A.BA0643`, `CBN2A10.BA0643` | yes | yes | 2 | 20s | site:tagheuer.com Carrera Chronograph black dial black ceramic bezel steel bracelet 44mm CBN2A1B BA0643; TAG Heuer Carrera chronograph black ceramic… |
| 42 | `CAW211P.FC6356` | `CAW211P.FC6356`, `CAW2111.FC6183`, `CAW211R.FC6401` | yes | yes | 2 | 131s | site:tagheuer.com CAW211P.FC6356 Monaco Calibre 11 blue; TAG Heuer Monaco Calibre 11 CAW211P.FC6356 references blue dial; TAG Heuer Monaco automatic… |
| 43 | `WBP201A.BA0632` | `WBP201A.BA0632`, `WBP201B.BA0632`, `WBP201C.BA0632` | yes | yes | 1 | 29s | site:tagheuer.com Aquaracer black dial date 6 43mm WBP reference bracelet; TAG Heuer Aquaracer Professional 300 black dial date at 6 WBP202A BA0632 r… |
| 44 | `WAZ1110.BA0875` | `WAJ2110.BA0870`, `WAJ2110.FT6015`, `WAJ1110.BA0871` | no | no | 3 | 74s | site:tagheuer.com Aquaracer black dial bezel numerals 5 10 15 stainless steel bracelet reference; TAG Heuer Aquaracer black dial oversized bezel nume… |
| 45 | `WBN2110.BA0639` | `WAR211A.BA0782`, `WAR211B.BA0782`, `WBN2110.BA0639` | no | yes | 3 | 27s | TAG Heuer Carrera black concentric dial date at 6 steel bracelet reference automatic; site:tagheuer.com Carrera black dial date 6 automatic bracelet… |
| 46 | `WBP1190.BZ0003` | `WBP1190.BZ0003`, `WBP1184.BF0008`, `WBP1180.BF0000` | yes | yes | 3 | 73s | site:tagheuer.com Aquaracer Solargraph grey dial rose gold indices bracelet reference; TAG Heuer Aquaracer Solargraph grey dial rose gold accents ref… |
| 47 | `CBS2212.FC6535` | `CBS2212.FC6535`, `CBS2210.FC6534`, `CBS2212.BA0048` | yes | yes | 2 | 18s | site:tagheuer.com CBS2212.FC6535 blue Carrera Chronograph 39; TAG Heuer Carrera blue chronograph 39mm date at 6 two subdials reference CBS2212.FC6535… |
| 48 | `WBC2110.BA0603` | `WBC2110.BA0603`, `WBC2112.BA0603`, `WBC2111.BA0603` | yes | yes | 2 | 41s | TAG Heuer Link Calibre 5 black dial date steel bracelet reference 41mm WBC2110 official; TAG Heuer Link Calibre 5 black dial automatic reference 39mm… |
| 49 | `WBP201D.FT6197` | `WBP201D.FT6197`, `WBP201A.FT6197`, `WAY108A.FT6141` | yes | yes | 2 | 103s | site:tagheuer.com WBP208D.FT6201 white dial Aquaracer; TAG Heuer Aquaracer white dial black titanium bezel automatic 43 reference white; TAG Heuer Aq… |
| 50 | `CBE2110.FC8226` | `CBE2110.FC8226`, `CBE2110.BA0687`, `CBE2111.BA0687` | yes | yes | 2 | 18s | site:tagheuer.com Autavia Heuer 02 CBE2110.FC8226 black dial 42mm; TAG Heuer Autavia CBE2110.FC8226 reference black dial leather strap alternatives C… |
| 51 | `AB0138211B1A1` | `AB0121211C1A1`, `AB0121211B1A1`, `AB0121211G1A1` | no | no | 3 | 118s | site:breitling.com Navitimer B01 Chronograph 43 blue dial bracelet reference AB0121211C1A1; Breitling Navitimer B01 Chronograph 43 blue dial stainles… |
| 52 | `A17375211B1S1` | `A17364`, `A17392`, `A17367` | no | no | 2 | 53s | Breitling Superocean black dial silver inner ring rubber strap 500m 1650ft reference 44; site:breitling.com Superocean 44 500m 1650ft black dial rubb… |
| 53 | `AB0134101B1A1` | `AB0134101B1A1`, `AB0134101G1A1`, `AB0134101K1A1` | yes | yes | 3 | 26s | site: breitling.com Chronomat B01 42 black dial steel bracelet AB0134101B1A1; Breitling Chronomat B01 42 black dial silver subdials rouleaux bracelet… |
| 54 | `AB0145211G1P1` | `AB0145211G1P1`, `AB0145211G1A1`, `AB0145331K1P1` | yes | yes | 3 | 23s | site: breitling.com Premier B09 Chronograph 40 cream dial reference brown leather; Breitling Premier B09 Chronograph 40 silver dial brown alligator r… |
| 55 | `A32395101C1X1` | `A32320101C1X1`, `A32320101B1X1`, `A32320101C1A1` | no | no | 2 | 21s | site:breitling.com Avenger Automatic GMT 44 blue dial fabric strap reference; Breitling Avenger GMT 44 blue dial blue military strap reference A32320… |
| 56 | `AB2010121B1A1` | `233.32.41.21.01.001`, `233.30.41.21.01.001`, `234.30.41.21.01.001` | no | no | 3 | 136s | Omega Seamaster 300 black dial mesh bracelet 233.30.41.21.01.001 reference; site:omegawatches.com Seamaster 300 41 mm black dial mesh bracelet refere… |
| 57 | `A17326211B1P1` | `A17326211B1P2`, `A17326211B1P1`, `A17326241B1P1` | no | yes | 2 | 21s | site:breitling.com Navitimer 8 Automatic 41 black dial beaded bezel A17314101B1X1; Breitling Navitimer 8 Automatic 41 black dial silver bezel leather… |
| 58 | `E79363101B1E1` | `E76325221B1E1`, `E76325221B1S1`, `V76325221B1V1` | no | no | 2 | 39s | Breitling watch black dial two digital displays titanium bracelet rider tabs reference Aerospace Evo; site:breitling.com watches Aerospace black dial… |
| 59 | `AB01761A1K1X1` | `AB01761A1K1X1`, `AB01761A1K1A1`, `A2531024/K1X1` | yes | yes | 3 | 42s | site:breitling.com Top Time B01 Racing red dial reference; Breitling Top Time B01 Racing red dial AB01772 reference; Breitling Top Time B01 Racing re… |
| 60 | `A32398101B1A1` | `A32398101B1A1`, `A32398101C1A1`, `A32398101A1A1` | yes | yes | 2 | 62s | site:breitling.com Chronomat GMT 40 black dial A32398101B1A1; Breitling Chronomat GMT 40 black dial reference official; Breitling Chronomat GMT 40 re… |
| 61 | `WSSA0018` | `WSSA0018`, `WSSA0029`, `WSSA0030` | yes | yes | 2 | 20s | site:cartier.com Santos de Cartier watch steel automatic date white dial reference large WSSA0018; Cartier Santos de Cartier white dial steel bracele… |
| 62 | `WSTA0041` | `WSTA0030`, `W1018355`, `WSTA0053` | no | no | 3 | 24s | site:cartier.com Tank Must small steel reference WSTA0051 white dial black strap; Cartier Tank Solo small quartz white dial black leather reference 2… |
| 63 | `W69016Z4` | `W69016Z4`, `WSBB0026`, `W69012Z4` | yes | yes | 2 | 101s | Cartier Ballon Bleu de Cartier 42 mm steel silver dial leather strap reference automatic date 42mm; Cartier Ballon Bleu 42mm steel silver guilloche d… |
| 64 | `WGTA0011` | `WGTA0011`, `WGTA0010`, `WGTA0357` | yes | yes | 3 | 30s | Cartier Tank Louis Cartier rose gold guilloche dial brown strap reference; Cartier Tank Louis Cartier rose gold guilloche dial reference "guilloché";… |
| 65 | `WSSA0022` | `WSSA0022`, `WSSA0085`, `WSSA0032` | yes | yes | 2 | 49s | site:cartier.com Santos-Dumont large steel blue alligator strap silver dial WSSA0022; Cartier Santos Dumont silver dial blue strap white gold referen… |
| 66 | `WSPA0009` | `W31074M7`, `W31047M7`, `W31044M7` | no | no | 2 | 58s | Cartier Pasha C white dial steel bracelet blue hands reference 2324; Cartier Pasha 35mm white guilloche dial steel bracelet automatic reference Carti… |
| 68 | `WSTA0065` | `W51008Q3`, `W51011Q3`, `WSTA0065` | no | yes | 2 | 136s | Cartier Tank Française steel white dial Roman numeral bracelet quartz reference medium W51002Q3; Cartier Tank Francaise stainless steel white dial re… |
| 69 | `WSNM0004` | `WSNM0004`, `WSNM0015`, `WSNM0009` | yes | yes | 2 | 21s | Cartier Drive de Cartier small seconds date silver dial steel black alligator reference WSNM; site:cartier.com Drive de Cartier 41 mm small seconds d… |
| 70 | `W7100056` | `W7100056`, `W7100057`, `W7100055` | yes | yes | 2 | 42s | Cartier Calibre de Cartier Diver black dial rubber strap W7100056 reference; Cartier Calibre de Cartier Diver W7100056 small seconds date black bezel… |
| 71 | `IW371617` | `IW371617`, `IW371605`, `IW371446` | yes | yes | 2 | 21s | site:iwc.com Portugieser Chronograph stainless steel bracelet silver dial reference; IWC Portugieser Chronograph bracelet silver dial reference IW; I… |
| 72 | `IW501701` | `IW501701`, `IW501702`, `IW500701` | yes | yes | 2 | 18s | site:iwc.com Portugieser Automatic 42 silver dial gold hands date power reserve reference; IWC Portugieser Automatic 42 white dial gold hands black a… |
| 73 | `IW329301` | `IW329301`, `IW329303`, `IW329304` | yes | yes | 1 | 66s | site:iwc.com "IW3293" Big Pilot's Watch 43 brown calfskin strap; IWC Big Pilot 43 brown strap black dial reference IW329301 IW329303; WatchBase IWC B… |
| 74 | `IW328201` | `IW328201`, `IW328203`, `IW328202` | yes | yes | 1 | 9s | site:iwc.com Mark XX black dial black calfskin strap reference IW328201; IWC Mark XX black dial leather strap IW328201 reference; IWC Mark XX referen… |
| 75 | `IW388101` | `IW377714`, `IW377717`, `IW388101` | no | yes | 1 | 104s | site:iwc.com IW388101 blue dial leather strap Pilot's Watch Chronograph 41; IWC IW388101 blue dial reference alternatives IW388102 official; IWC Pilo… |
| 76 | `IW328802` | `IW328802`, `IW328801`, `IW328803` | yes | yes | 1 | 15s | site:iwc.com Aquatimer Automatic black dial rubber strap 42 reference IW328801; IWC Aquatimer Automatic 42 black dial rubber strap reference 2022; IW… |
| 77 | `IW356501` | `IW356501`, `IW356517`, `IW356502` | yes | yes | 3 | 34s | site:iwc.com Portugieser Automatic 40 silver dial date ring IW358 reference; IWC Portugieser Automatic 40 silver dial date 1 31 central date hand ref… |
| 79 | `IW389101` | `IW388002`, `IW388001`, `IW379901` | no | no | 3 | 49s | site:iwc.com blue camouflage dial Pilot's Watch Chronograph reference IWC; IWC blue camo dial chronograph black ceramic red seconds reference; IWC Pi… |
| 80 | `IW503302` | `IW344202`, `IW344203`, `IW502213` | no | no | 3 | 34s | site:iwc.com Portugieser Perpetual Calendar 44 red gold silver dial brown alligator reference; IWC Portugieser Perpetual Calendar 44 rose gold silver… |
| 81 | `Q3858520` | `Q3858522`, `Q3858520`, `Q2438522` | no | yes | 3 | 96s | Jaeger-LeCoultre Reverso silver dial Arabic numerals small seconds Q reference steel brown strap; site:jaeger-lecoultre.com Reverso Tribute Small Sec… |
| 82 | `Q1368430` | `Q1368430`, `Q1368420`, `Q1362520` | yes | yes | 3 | 47s | site:jaeger-lecoultre.com Master Ultra Thin Moon 39 mm steel silver dial reference 1368420; Jaeger-LeCoultre Master Ultra Thin Moon silver dial black… |
| 84 | `Q4018420` | `Q4018420`, `Q4018421`, `Q1548420` | yes | yes | 1 | 9s | site:jaeger-lecoultre.com Master Control Date silver dial brown leather Q4018420; Jaeger-LeCoultre Master Control Date silver dial brown strap refere… |
| 85 | `Q9028181` | `Q9028180`, `Q9028480`, `Q9028170` | no | no | 3 | 25s | site:jaeger-lecoultre.com blue dial chronograph steel bracelet tachymeter Jaeger-LeCoultre reference; Jaeger-LeCoultre blue dial chronograph bracelet… |
| 86 | `Q3988482` | `Q3978480`, `Q397848J`, `Q397846J` | no | no | 2 | 33s | site:jaeger-lecoultre.com Reverso Tribute Small Seconds blue dial steel reference; Jaeger-LeCoultre Reverso Tribute Small Seconds blue Q3978430 refer… |
| 87 | `Q1302520` | `Q4142520`, `Q4148420`, `Q4148480` | no | no | 2 | 20s | Jaeger-LeCoultre Master Control Calendar pink gold moonphase day month pointer date reference; site:jaeger-lecoultre.com Master Control Calendar pink… |
| 90 | `Q4138420` | `Q4138420`, `Q4132520`, `Q4138480` | yes | yes | 2 | 30s | Jaeger-LeCoultre Master chronograph day month moonphase pulsometer silver dial reference; JLC watch "FOR 30 PULSATIONS" day month chronograph moonpha… |
| 93 | `85180/000R-9248` | `85180/000R-9248`, `85180/000R-B515`, `85180/000G-9230` | yes | yes | 1 | 19s | site:vacheron-constantin.com 85180/000R-9248 Patrimony date pink gold silver dial; Vacheron Constantin Patrimony Self-Winding 40mm pink gold silver d… |
| 94 | `82172/000R-9382` | `82172/000R-9382`, `82172/000R-B402`, `82172/000G-9383` | yes | yes | 2 | 19s | Vacheron Constantin watch silver dial small seconds rose gold railway minute track reference 82172; site:vacheron-constantin.com Patrimony small seco… |
| 96 | `7900V/110A-B334` | `7900V/110A-B334`, `7900V/110A-B333`, `7900V/110A-B546` | yes | yes | 2 | 20s | site:vacheron-constantin.com 7900V/110A-B546 Overseas Dual Time blue dial; Vacheron Constantin Overseas Dual Time 7900V blue dial steel official refe… |
| 97 | `82035/000R-9359` | `82035/000R-9359`, `82035/000G-B735`, `1100S/000R-B430` | yes | yes | 1 | 14s | site:vacheron-constantin.com Historiques American 1921 40 mm 82035/000R-9359; Vacheron Constantin American 1921 white dial 40mm rose gold reference 8… |
| 99 | `4010U/000G-B330` | `4010U/000G-B330`, `4010U/000R-B329`, `4010U/000G-H070` | yes | yes | 2 | 23s | Vacheron Constantin peripheral date scale moon phase dial retrograde date silver reference; Vacheron Constantin moon phase retrograde date 1 31 dial… |

Sites its searches returned or it opened, by number of photos: reddit.com 90, youtube.com 86, en.wikipedia.org 76, it.wikipedia.org 63, chrono24.com 60, es.wikipedia.org 45, therealreal.com 39, hourstriker.com 38, fr.wikipedia.org 32, everywatch.com 30, t3.com 28, watchcharts.com 27.

## Limits

- Nothing is saved between runs. A second run searches again, pays again and may get other results.
- The photos came from the web, so a search can land on the page a photo was taken from.
- One pass. Small differences between runs are noise.
