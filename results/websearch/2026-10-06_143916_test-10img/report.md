# Web search study: the model searches for itself - TEST RUN (10 of 100 images)

Idea 5 in `FINDINGS.md`, section 4. Rebuilt by `websearch_study.py report` from saved answers.

Run `2026-10-06_143916_test-10img`, model `gpt-6-luna` (`gpt-6-luna`, default reasoning effort). OpenAI's web search tool was on, limited to 3 searches per photo. One call per photo. 10 photos. It was asked for up to three references, a second or third only where it could not rule a version out.

> TEST RUN on part of the photos. It measures cost and whether the flow works. Its accuracy is not comparable with a full run: a few photos either way change the figure a lot.

## Result

Out of 10 photos.

| | Exact reference | Also counting accepted look-alikes |
|---|---:|---:|
| First reference is right | 9 | 9 |
| Its references, up to three, contain it | 9 | 9 |
| Brand right | 10 | |

Where the right reference stands in its list: first 9, second 0, third 0, not in it 1. References given per photo: one 10, two 0, three 0, none 0.

For context, the same photos in the saved benchmark runs (one reference, no search, a different prompt): gpt-6-luna-nothink 7, gpt-6-luna-xhigh 5, deepseek-flash 5, claude-sonnet-5-5-nothink 6 right.

## Cost and speed

| | Per photo | This run |
|---|---:|---:|
| Searches made | 1.6 | 16 |
| Pages opened | 0.2 | 2 |
| Search fee at $0.01 a search | $0.0160 | $0.16 |
| Model tokens | $0.0021 | $0.02 |
| **Total** | **$0.0181** | **$0.18** |
| Input tokens | 20,447 | |
| Output tokens | 1,006 | |
| Time, median | 20.9s | |
| Time, longest | 69.2s | |

Photos by number of searches: 7 with 1 search, 3 with 3 searches. No photo went over the limit of 3.

The number of searches is the one OpenAI's API reports for each call (`tool_usage.web_search.num_requests`). One search can hold several queries (50 queries in this run), and opening a page is not counted. The fee is that number times $0.01, the listed price; the API does not report an amount in dollars, so the account's usage page has the last word.
At this rate all 100 photos would cost about $1.81.

Calls that failed: 0. Answers tidied to fit the format: 0. Answer format enforced by the API: yes.

## Every photo

| Row | Expected | Its references | First right | In its three | Searches | Time | What it searched for |
|---:|---|---|:-:|:-:|---:|---:|---|
| 5 | `228238` | `228238` | yes | yes | 1 | 11s | site:rolex.com watches day-date 40 yellow gold champagne dial 228238; Rolex 228238 champagne dial yellow gold baton dial reference |
| 15 | `131.10.39.20.02.001` | `131.10.39.20.02.001` | yes | yes | 1 | 10s | site:omegawatches.com Constellation 39 mm silver dial 131.10.39.20.02.001; Omega Constellation silver dial star at 6 Roman bezel reference 39mm Co-Ax… |
| 25 | `5396R-011` | `5396R-011` | yes | yes | 3 | 38s | site:patek.com 5205R annual calendar ivory dial reference; Patek Philippe 5205R reference cream dial black strap annual calendar rose gold; Patek Phi… |
| 35 | `26574ST.OO.1220ST.02` | `26574ST.OO.1220ST.02` | yes | yes | 1 | 14s | site:audemarspiguet.com "26574ST" blue dial; Audemars Piguet Royal Oak Perpetual Calendar blue dial 26574ST reference official; AP Royal Oak Perpetua… |
| 45 | `WBN2110.BA0639` | `WBN2110.BA0639` | yes | yes | 1 | 11s | TAG Heuer Carrera black dial date at 6 automatic steel bracelet reference textured dial; TAG Heuer Carrera date 6 o'clock black dial WAR211A referenc… |
| 55 | `A32395101C1X1` | `A32395101C1X1` | yes | yes | 3 | 28s | site:breitling.com Avenger Automatic GMT 45 blue dial fabric strap reference A32320101C1X1; Breitling Avenger Automatic GMT 45 blue dial reference te… |
| 65 | `WSSA0022` | `WSSA0046` | no | no | 3 | 31s | Cartier Santos Dumont platinum white dial blue alligator strap reference silver dial 2024; site:cartier.com Santos-Dumont platinum blue strap referen… |
| 75 | `IW388101` | `IW388101` | yes | yes | 1 | 69s | site:iwc.com IW388101 blue dial leather Pilot's Watch Chronograph 41; IWC Pilot's Watch Chronograph 41 blue dial black leather reference IW388101; IW… |
| 85 | `Q9028181` | `Q9028181` | yes | yes | 1 | 60s | Jaeger-LeCoultre blue dial chronograph steel bracelet tachymeter Polaris reference blue; site:jaeger-lecoultre.com Polaris Chronograph blue dial stee… |
| 95 | `4600E/000A-B442` | `4600E/000A-B442` | yes | yes | 1 | 12s | site:vacheron-constantin.com 4600E/000A-B487 silver dial; Vacheron Constantin 4600E/000A-B487 silver date black alligator 40mm; Vacheron Constantin F… |

Sites its searches returned or it opened, by number of photos: reddit.com 10, youtube.com 9, en.wikipedia.org 8, chrono24.com 7, watchcharts.com 5, everywatch.com 4, it.wikipedia.org 4, tourneau.com 4, watchesofswitzerland.com 4, laurentfinewatches.com 3, de.wikipedia.org 3, es.wikipedia.org 3.

## Limits

- Nothing is saved between runs. A second run searches again, pays again and may get other results.
- The photos came from the web, so a search can land on the page a photo was taken from.
- One pass. Small differences between runs are noise.
