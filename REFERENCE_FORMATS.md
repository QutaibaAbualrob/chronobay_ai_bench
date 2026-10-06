# Reference number formats by brand

Researched and re-checked 2026-10-06. Covers the 18 brands on WatchBase's front page, plus Cartier, which
ChronoBay seeds but WatchBase does not list there.

## How each rule was checked

Every rule below was checked twice where possible: against a published guide, and against
real references whose details are known (brand websites, WatchBase page titles, and the 100
references in `dataset/ground_truth.csv`).

| Mark | Meaning |
|---|---|
| **Confirmed** | Stated in a published guide and consistent with the real references checked. |
| **Observed** | No published key found. The rule was read off real references, so exceptions are possible. |
| **Unconfirmed** | One source only, or sources and real references disagree. |

Two tests were run on the rules:

| Test | References | Checks | Agreed |
|---|---:|---:|---:|
| Against the answer key (nine ChronoBay brands, 20 rules) | 100 | 180 | 180 |
| Against references outside the answer key (14 brands) | 90 | 155 | 155 |

- **The answer-key test** independently tests the rules marked Confirmed. The rules marked
  Observed were read off those same references, so for them it only shows there are no
  contradictions.
- **The outside test** used references found on WatchBase and brand or retailer pages on
  2026-10-06. For 133 of its 155 checks the rule already existed before the reference was
  looked at, so the rule had to predict the watch's metal, strap, dial or size. The other 22
  checks are on the references an Observed rule was read from.

Both tests can be re-run for free with `reference_format_check.py`.

Limits of this research:

- Brands do not publish these keys. Guides are written by dealers and collectors.
- Many guide pages refuse automated reading. Guides for Omega, Breitling, Longines, TAG Heuer
  and Patek Philippe were opened and read directly. For the other brands the guide's statement
  comes from a search-result summary of the page.
- Watch details for the outside test come from page titles and listing descriptions.
- A rule that holds on every reference checked can still have exceptions on others.

## At a glance

| Brand | Example | What the reference tells you | What it does not |
|---|---|---|---|
| Rolex | `126610LN` | Model, bezel colour, metal | Dial, bracelet (separate suffix) |
| Tudor | `79030N` | Model, colour, often metal | Strap (separate suffix) |
| Omega | `310.30.42.50.01.002` | Collection, metal, strap, size, movement, dial | |
| Breitling | `AB0138211B1A1` | Metal, calibre, dial colour, strap | Size |
| TAG Heuer | `WBP201A.BA0632` | Series, movement type, metal, strap | Size, dial colour |
| Audemars Piguet | `15500ST.OO.1220ST.01` | Model, metal, bracelet or strap | Dial colour (a version number) |
| Patek Philippe | `5711/1A-010` | Model, metal, bracelet, gem-setting | Dial colour (a version number) |
| Vacheron Constantin | `4520V/210A-B128` | Model, metal, bracelet or strap | Dial colour (a version code) |
| Jaeger-LeCoultre | `Q3858520` | Model, metal, strap | Dial (a version number) |
| IWC | `IW371617` | Model family | Everything else (a version number) |
| Cartier | `WSSA0018` | Metal class, family | Size, dial, strap |
| Longines | `L3.781.4.56.6` | Family, metal, bracelet or strap | Dial needs a per-model table |
| Tissot, Certina | `T137.407.11.041.00` | Family, metal, strap | Dial needs a per-model table |
| Hamilton | `H70455133` | Family, size, strap | Code values differ by family |
| Oris | `01 733 7730 4135-07 8 24 05PEB` | Movement, case, strap type, lug width | |
| Zenith | `03.3100.3600/69.M3100` | Metal, calibre, strap type | Dial needs a per-model table |
| Panerai | `PAM01312` | Nothing | Everything (a catalogue number) |
| A. Lange & Söhne | `191.032` | Model | Everything else (a version number) |

---

## Rolex

**Format:** four to six digits, then optional letters. Rolex's own catalogue adds an `M`
in front and a four-digit suffix: `M126610LN-0001`.

| Part | Meaning | Status |
|---|---|---|
| Leading digits | Model family (`1266` Submariner Date, `1263` Datejust 41) | Confirmed |
| Second-last digit | Bezel type | Unconfirmed in general |
| Last digit | Metal | Confirmed |
| Letters | Bezel colour or gem-setting, abbreviated from French | Confirmed |
| `-0001` suffix | Dial and bracelet combination | Confirmed |

- **Metal digit:** 0 steel, 1 steel and Everose gold, 2 steel and platinum, 3 steel and
  yellow gold, 4 steel and white gold, 5 Everose gold, 6 platinum, 7 14k yellow gold (older
  watches), 8 yellow gold, 9 white gold.
- **Letters:** `LN` black bezel, `LV` green, `LB` blue, `BLRO` blue and red, `BLNR` blue and black.
- **Variants:** watches with the same reference differ only in dial and bracelet.
  `126334-0001` is on an Oyster bracelet and `126334-0002` on a Jubilee; both are the 41 mm
  steel and white gold Datejust.
- **Caveat:** the bezel digit is not a clean code. It fits Datejust-style models (`126334`,
  3 = fluted), but the same digit appears on different bezels: `126600` has a rotating dive
  bezel and `124300` a smooth one, and both have 0. Treat the bezel as unknown unless the
  model is known.
- **Checked on:** the ten answer-key references (metal digit 10 of 10), plus `126331` (steel
  and Everose gold), `228206` (platinum) and `126334` on rolex.com and retailer pages.

## Tudor

**Format:** five digits, then letters. The catalogue form is `M79030N-0001`.

| Part | Meaning | Status |
|---|---|---|
| Five digits | Model | Confirmed |
| Last digit | Follows Rolex's metal digit on the examples checked | Observed |
| Letters | Colour or material | Confirmed for `N`; others Observed |
| `-0001` suffix | Bracelet, strap and dial combination | Confirmed |

- **Letters:** `N` black (noir), `B` blue. `T` appears on titanium Pelagos (`25600TB`) and
  `SG` on the silver Black Bay 58 (`79010SG`).
- **Metal digit, as checked:** `79030N` steel, `79733N` and `79363N` steel and yellow gold,
  `79018V` yellow gold.
- **Variants:** `79230B-0001` is on a bracelet and `79230B-0002` on a strap.

## Omega

**Format:** 14 digits in six groups, `AAA.BB.CC.DD.EE.FFF`, used since 2007. Often written
without the dots.

| Group | Meaning | Status |
|---|---|---|
| `AAA` | Collection | Confirmed |
| `BB` first digit | Case metal | Confirmed for 1, 2, 5, 9; Observed for 3, 6 |
| `BB` second digit | Bracelet or strap | Confirmed |
| `CC` | Case diameter in mm | Confirmed |
| `DD` | Movement type | First digit Confirmed in part; second digit Unconfirmed |
| `EE` | Dial colour | Confirmed |
| `FFF` | Sequence number separating otherwise identical versions | Confirmed |

- **Collections seen:** `310` Speedmaster Moonwatch Professional, `311` other Speedmasters,
  `210` Seamaster Diver 300M, `215` Planet Ocean, `220` Aqua Terra and Railmaster, `234`
  Seamaster 300, `131` Constellation, `424` De Ville Prestige.
- **Case metal:** 1 steel, 2 steel and gold, 5 gold, 9 other (titanium, ceramic). Also seen:
  3 on steel watches with a ceramic or aluminium bezel, 6 on Moonshine gold.
- **Bracelet or strap:** 0 metal bracelet, 2 strap that needs no wildlife-trade permit (rubber,
  fabric, calf), 3 strap that does (alligator).
- **Dial:** 01 black, 02 silver, 03 blue, 04 white, 05 white mother-of-pearl.
- **Movement:** the guide gives 0 mechanical, 1 chronometer, 2 co-axial, 3 chronograph,
  6 quartz, 7 quartz chronograph for the first digit. The checked references use 2 for
  co-axial automatics and 5 for chronographs.
- **Variants:** all inside the reference. The same watch on a strap changes one digit:
  `310.30.42.50.01.002` on a bracelet, `310.32.42.50.01.002` on leather.
- **Older formats:** eight digits such as `3570.50.00` before 2007, and case references such
  as `145.022` before about 1988. Reported by one source each; not checked further.
- **Checked on:** the ten answer-key references (strap digit 10 of 10, metal digit 10 of 10,
  diameter 2 of 2) and eight outside references (27 of 27 checks). Examples: `220.12.41.21.03.001`
  is steel on rubber, `220.23.38.20.03.001` is steel and gold on alligator at 38 mm, and
  `220.52.41.21.03.001` is gold on rubber. All three have the blue dial, code 03.

## Breitling

**Format:** 13 characters with no separators on current watches. Older watches use
`A2332212/B635` with a separate strap code.

| Position | Meaning | Status |
|---|---|---|
| 1 | Case metal | Confirmed |
| 2–3 | Calibre number; 50 and above is quartz | Confirmed |
| 2–4 | `B` plus two digits for in-house calibres (`B01`, `B20`) | Confirmed |
| 4 | Chronometer digit on other calibres; 3 = certified | Confirmed |
| 5–6 | Model | Confirmed |
| 7–8 | Case and bezel finish | Confirmed for older codes; current values Observed |
| 9–11 | Dial; the letter is the colour | Letter Confirmed; digits Observed |
| 12–13 | Strap or bracelet | Observed |

- **Case metal:** `A` steel, `B` steel with gold rider tabs, `E` titanium, `H` rose gold,
  `J` white gold, `K` yellow gold, `L` platinum, `M` black steel, `V` black titanium,
  `X` Breitlight. Also seen on current references: `R` red gold and `U` steel with red gold.
- **Dial colour letter:** `A` white, `B` black, `C` blue, `G` silver, `K` red, `Q` bronze.
  Also seen: `L` green and `O` orange, on one reference each.
- **Strap, as seen on verified references:** `A1` metal bracelet, `E1` titanium bracelet,
  `P1` leather strap, `X1` leather or fabric strap, `S1` rubber strap. `A1` and `S1` were then
  tested on five further references and held.
- **Variants:** dial and strap are both inside the reference. `AB0138211B1A1` is black on a
  bracelet and `AB0138241C1A1` is ice blue on a bracelet.
- **Caveat:** no published key was found for positions 7 to 13 of the current format.
- **Checked on:** the ten answer-key references (metal 10 of 10, strap 10 of 10, quartz 10 of 10)
  and eight outside references (21 of 21 checks).

## TAG Heuer

**Format:** seven characters, a dot, then a strap code: `WBP201A.BA0632`.

| Position | Meaning | Status |
|---|---|---|
| 1 | `W` three-hand watch, `C` chronograph | Confirmed |
| 2–3 | Series | Confirmed |
| 4 | Movement type | Confirmed |
| 5 | Size class | Unconfirmed |
| 6 | Metal | Confirmed for 1; Observed for 8, 9 |
| 7 | Dial version | Confirmed |
| After the dot, letters | Bracelet or strap type | Confirmed |
| After the dot, digits | The specific bracelet or strap | Confirmed |

- **Series seen:** `BN` Carrera, `BS` Carrera Glassbox, `AW` Monaco, `BP` Aquaracer
  Professional, `AZ` Formula 1, `BC` Link, `BE` Autavia.
- **Movement digit:** 1 quartz (including solar), 2 automatic. One guide gives 5 as automatic
  chronometer.
- **Metal digit:** 1 steel. 8 and 9 are titanium on the 2026 Solargraph references.
- **Strap letters:** first letter `B` is a bracelet and `F` a strap. `BA` steel bracelet,
  `FC` leather, `FT` rubber. `BZ` and `BF` are titanium bracelets on the references checked.
- **Variants:** the same watch head on another strap changes only the part after the dot.
- **Caveat:** TAG Heuer revises its code tables from time to time.
- **Checked on:** the ten answer-key references (movement 10 of 10, strap 10 of 10, metal 10 of 10).

## Audemars Piguet

**Format:** four blocks, `15500ST.OO.1220ST.01`.

| Block | Meaning | Status |
|---|---|---|
| Five digits | Model | Confirmed |
| Two letters | Case metal | Confirmed |
| Second block | Bezel or gem-setting; `OO` means plain | Confirmed |
| Third block | Bracelet (digits first) or strap (letter first) | Confirmed |
| Last two digits | Dial version | Confirmed |

- **Case metal:** `ST` steel, `OR` pink gold, `BA` yellow gold, `TI` titanium, `CE` black
  ceramic, `CB` white ceramic, `PT` platinum. `BC` is white gold on the two references checked.
  `CR` is white and pink gold together on one reference.
- **Third block:** `1220ST` is a steel bracelet. `A002CR` is an alligator strap and `A027CA`
  a rubber strap; the last two letters give the strap type.
- **Variants:** the dial is only a version number. `15500ST.OO.1220ST.01` is blue and `.04` is silver.
- **Checked on:** the ten answer-key references (metal 10 of 10, bracelet or strap 10 of 10)
  and six outside references (8 of 8 checks).

## Patek Philippe

**Format:** `5711/1A-010`.

| Part | Meaning | Status |
|---|---|---|
| Four digits | Model | Confirmed |
| Digits after the slash | Bracelet and gem-setting | Confirmed |
| Letter | Case metal | Confirmed |
| Three digits after the hyphen | Dial version | Confirmed |

- **After the slash:** `/1` metal bracelet, `/50` decorated dial, `/200` gem-set case
  (brilliant cut), `/300` gem-set (baguette), `/400` high jewellery. Codes combine:
  `4910/1200A` is a bracelet (`/1`) with a gem-set case (`/200`). No slash means a strap.
- **Metal:** `A` steel, `J` yellow gold, `G` white gold, `R` rose gold, `P` platinum,
  `T` titanium. Two letters mean two metals: `AR` steel and rose gold.
- **Dial version:** `-001` is the first version, `-010` usually the second, `-011` the third.
- **Checked on:** the ten answer-key references (metal 10 of 10, bracelet 3 of 3, strap 7 of 7)
  and seven outside references (9 of 9 checks). `5167/1A-001` is the Aquanaut on a steel
  bracelet and `5167A-001` the same watch on rubber.

## Vacheron Constantin

**Format:** `4520V/210A-B128`. Older references look like `85180/000R-9248`.

| Part | Meaning | Status |
|---|---|---|
| Before the slash | Model | Confirmed |
| Three digits after the slash | `000` strap; other values bracelet | Observed |
| Letter | Case metal | Confirmed |
| After the hyphen | Version: dial and details | Confirmed |

- **Metal:** `A` steel, `R` pink gold, `G` white gold, `J` yellow gold, `P` platinum. `M` is
  steel and pink gold on the two references checked.
- **Variants:** the dial is only a version code. `4520V/210A-B128` is blue and `-B126` is silver.
- **Checked on:** the ten answer-key references (metal 10 of 10, strap or bracelet 10 of 10)
  and nine outside references (metal 9 of 9). The strap rule was not tested outside the
  answer key, because page titles do not state the strap.

## Jaeger-LeCoultre

**Format:** `Q` and seven characters: `Q3858520`. The same reference is also written
without the `Q`, or with dots as `385.85.20`.

| Position | Meaning | Status |
|---|---|---|
| 1–3 | Model | Confirmed |
| 4 | Case metal | Confirmed for 8; Observed for 2 |
| 5 | Bracelet or strap | Confirmed for 1, 4, 5; rest of the table Unconfirmed |
| 6–7 | Dial and version; can include a letter | Confirmed |

- **Metal:** 8 steel, 2 pink gold.
- **Strap, from one collector guide:** 1 matching bracelet, 2 pink gold bracelet, 3 white
  gold bracelet, 4 leather with folding clasp, 5 leather with pin buckle, 6 rubber.
- **Variants:** `Q9008180` is the blue Polaris on a bracelet and `Q9008480` the same watch on
  calf leather. `Q4018420` and `Q4018421` are the same Master Control Date on a tan and a
  black strap.
- **Checked on:** the ten answer-key references (metal 10 of 10, strap 10 of 10) and twelve
  outside references (24 of 24 checks), including one pink gold watch.

## IWC

**Format:** `IW` and six digits: `IW371617`.

| Part | Meaning | Status |
|---|---|---|
| First four digits | Reference family (`3716` Portugieser Chronograph) | Confirmed |
| Last two digits | Version: metal, dial and strap together | Confirmed |

- **Notation:** `IW371617`, `IW3716-17` and `3716-17` are the same watch.
- **Variants:** the version number has no general key. Each family numbers its own versions.
- **Caveat:** neighbouring families are different watches. `3714` and `3716` are two
  generations of the Portugieser Chronograph.

## Cartier

**Format on current watches:** `W`, a metal letter, two letters for the family, four digits:
`WSSA0018`. Cartier's website adds `CR` in front. Older watches use `W` and seven
characters (`W69016Z4`), which describe nothing.

| Part | Meaning | Status |
|---|---|---|
| Second character | Metal class | `S`, `G` and `2` Confirmed; rest of the table Unconfirmed |
| Characters 3–4 | Family | Unconfirmed table; five families Confirmed |
| Four digits | Version: size, dial and strap together | Confirmed |

- **Metal class:** `S` steel, `G` gold, `2` steel and gold. One guide adds `J` jewellery,
  `H` high horology and `P` platinum.
- **Family:** `SA` Santos, `TA` Tank, `PA` Pasha, `PN` Panthère, `NM` Drive. One guide adds
  `BB` Ballon Bleu and others.
- **Checked on:** the eight current-format answer-key references (metal 8 of 8, family 8 of 8)
  and three outside references: `W2SA0009` steel and yellow gold, `WGSA0029` yellow gold,
  `WSSA0029` steel.

## Longines

**Format:** `L3.781.4.56.6`.

| Part | Meaning | Status |
|---|---|---|
| `L` and one digit | Family | Unconfirmed |
| Three digits | Model | Confirmed |
| One digit | Case metal | Confirmed |
| Two digits | Dial | Confirmed; values per model |
| Last digit | Bracelet or strap | Confirmed |

- **Metal:** 0 steel with diamonds, 2 PVD, 3 steel and PVD, 4 steel, 5 steel and gold,
  6 gold, 7 gold with diamonds, 8 pink gold, 9 pink gold with diamonds. The guide does not
  list 1; it is titanium on the one reference checked (`L3.810.1.53.6`).
- **Last digit:** 6 bracelet; 0, 2, 3, 4, 5 and 9 strap; 1 watch head only; 7 and 8 either.
- **Variants:** `L3.781.4.56.6` is the black HydroConquest on a bracelet, `L3.781.4.56.9` the
  same on rubber, and `L3.781.4.96.6` the blue one on a bracelet.
- **Checked on:** twelve WatchBase references across HydroConquest, Spirit and Legend Diver
  (bracelet or strap 12 of 12, metal 8 of 8).

## Tissot and Certina

Both use the same layout. Tissot starts with `T`, Certina with `C`.

**Format:** `T137.407.11.041.00`.

| Group | Meaning | Status |
|---|---|---|
| Letter and three digits | Family (`T137` PRX) | Confirmed |
| Three digits | Movement and size version | Observed |
| Two digits | Case finish, then bracelet or strap | Observed |
| Three digits | Dial | Observed |
| Two digits | Version | Observed |

- **Third group, as seen:** the first digit is the case finish (1 steel, 3 coated) and the
  second the bracelet or strap (1 or 3 bracelet, 6 leather, 7 rubber). So `11` is steel on a
  steel bracelet, `16` steel on leather, `17` steel on rubber, `33` a gold-coloured coating
  on a matching bracelet, and `37` a black coating on rubber.
- **Last group:** `.00` is most common; `.01`, `.02` and `.03` also exist.
- **Variants:** `C032.407.11.051.00` is the Certina DS Action Diver on a bracelet and
  `C032.407.17.051.00` the same watch on rubber.
- **Caveat:** neither brand publishes a key.
- **Checked on:** five Tissot references (PRX and Seastar) and two Certina references.

## Hamilton

**Format:** `H` and eight digits: `H70455133`.

| Position | Meaning | Status |
|---|---|---|
| 1–2 | Family (`70` Khaki Field Auto, `69` Khaki Field Mechanical) | Observed |
| 3 | Case size | Observed |
| 4 | Case metal | Unconfirmed |
| 5 | Movement | Unconfirmed |
| 6 | Strap | Observed |
| 7–8 | Dial | Unconfirmed |

- **Checked on two families:** the third digit is 4 on 38 mm watches in both (`H70455133`,
  `H69439931`) and 5 on the 42 mm `H70555533`. `H70455133` is on a steel bracelet,
  `H70455533` on brown leather and `H70455733` on black leather.
- **Caveat:** the position meanings come from one collector chart. Code values may differ by family.

## Oris

**Format:** `01 733 7730 4135-07 8 24 05PEB`.

| Part | Meaning | Status |
|---|---|---|
| `733` | Movement | Confirmed |
| `7730` | Case | Confirmed |
| `4135` | Case material and dial | Confirmed |
| After the dash | The strap or bracelet | Confirmed |
| `8` / `4` / `5` | Metal bracelet / rubber / leather | Confirmed |
| `24` | Lug width in mm | Confirmed |
| `05` | Strap version | Confirmed |

- **Variants:** the same watch on another strap changes only the part after the dash.
- **Not confirmed:** the meaning of the trailing letters (`PEB`, `EB`).

## Zenith

**Format:** `03.3100.3600/69.M3100`.

| Part | Meaning | Status |
|---|---|---|
| First two digits | Case metal | Observed |
| Four digits | Case | Observed |
| Digits before the slash | Calibre (`3600` El Primero 3600, `670` Elite 670) | Observed |
| Two digits after the slash | Dial | Observed |
| Letter and digits | Strap: `M` metal bracelet, `C` leather or fabric, `R` rubber | Observed |

- **Metal, as checked:** `03` steel, `18` rose gold, `51` steel and rose gold, `95` titanium.
- **Variants:** the white Chronomaster Sport is `/69` in steel, rose gold and two-tone, and
  the black one is `/21`.
- **Checked on:** six references. Most of the rules were read off these same references.

## Panerai

**Format:** `PAM` and five digits: `PAM01312`. **Confirmed.**

- The number is a catalogue number given out roughly in rising order. It encodes nothing
  about size, metal or movement.
- Older watches are usually written with three digits: `PAM 111` is `PAM00111`.
- Every variant has its own number.

## A. Lange & Söhne

**Format:** two groups of three digits: `191.032`. **Observed.**

- The first group is the model (`191` Lange 1). The second is a version number.
- The version follows no fixed code: `191.021` yellow gold, `191.025` platinum, `191.032`
  pink gold, `191.039` white gold, `191.062` platinum, `191.063` pink gold.

---

## Claims that failed the check

These turned up in search results and did not hold against real references. They are
listed so nobody builds on them.

| Claim | What the real references show |
|---|---|
| Breitling strap codes are `A1` steel, `B1` leather, `C1` rubber, `D1` mesh, `E1` fabric | Leather is `P1`, rubber is `S1`, a mesh bracelet is `A1`, and `E1` is a titanium bracelet. |
| Tissot's last group is the strap | `T137.407.11.041.00` (bracelet) and `T137.407.16.051.00` (leather) both end in `.00`. The strap is in the third group. |
| Omega's second movement digit is the number of complications | `210.30.42.20.01.001` has a date and `234.30.41.21.01.001` has none. |
| Patek's `G` is yellow gold | `G` is white gold; `J` is yellow gold. |
| IWC splits as three digits and three digits | IWC and WatchBase write four and two: `IW3716-17`. |
| Zenith's `/69` means 1969 | It is the dial code; the same `/69` is on the white Chronomaster Sport in three metals. |
| Rolex's second-last digit always gives the bezel | `126600` (rotating dive bezel) and `124300` (smooth bezel) both have 0. |

## What this means for ChronoBay

**Writing the same reference several ways.** A lookup has to treat these as equal:

| Brand | Equivalent forms |
|---|---|
| Rolex, Tudor | `126610LN`, `M126610LN-0001` |
| Omega | `310.30.42.50.01.002`, `31030425001002` |
| Jaeger-LeCoultre | `Q3858520`, `3858520`, `385.85.20` |
| IWC | `IW371617`, `IW3716-17` |
| Cartier | `WSSA0018`, `CRWSSA0018` |
| Panerai | `PAM00111`, `PAM111` |
| Audemars Piguet, Vacheron, Patek | With or without dots, slashes and hyphens |

**Where the strap sits.** To treat "same watch, other strap" as one watch, ignore this part:

| Brand | Part that changes with the strap |
|---|---|
| Omega | Fifth digit |
| Breitling | Last two characters |
| TAG Heuer, Oris | Everything after the dot or dash |
| Audemars Piguet | Third block |
| Longines | Last digit |
| Tissot, Certina | Second digit of the third group |
| Jaeger-LeCoultre | Fifth digit |
| Hamilton | Sixth digit |
| Zenith | Everything after the last dot |
| Rolex, Tudor | The `-0001` suffix |

**Fields that can be read from the reference with no catalogue.** Metal for 14 of the 19
brands, and bracelet-or-strap for 13. Dial colour can be read directly only for Omega and
Breitling. Case size can be read directly only for Omega.

**Brands where the reference describes nothing.** Panerai, A. Lange & Söhne, and the version
digits of IWC and Cartier. These need a catalogue for every field.

## Sources

- Rolex: [Chrono24 Magazine](https://www.chrono24.com/magazine/rolex-reference-numbers-what-do-they-mean-p_150741/), [Luxe Watches](https://www.luxewatches.co.uk/guide-the-meaning-of-rolex-reference-numbers/), [rolex.com 126334-0002](https://www.rolex.com/watches/datejust/m126334-0002)
- Tudor: [tudorwatch.com 79733N](https://www.tudorwatch.com/en/watches/black-bay/m79733n-0004), [tudorwatch.com 79018V](https://www.tudorwatch.com/en/watches/black-bay-58/m79018v-0006), [WatchBase 79230B-0001](https://watchbase.com/tudor/black-bay/79230b-0001)
- Omega: [Ottuhr guide](https://ottuhr.com/an-experts-guide-to-omega-reference-numbers/), [omegawatches.com 310.32.42.50.01.002](https://www.omegawatches.com/en-us/watch-omega-speedmaster-moonwatch-professional-co-axial-master-chronometer-chronograph-42-mm-31032425001002), [WatchBase 310.30.42.50.01.002](https://watchbase.com/omega/speedmaster/310-30-42-50-01-002)
- Breitling: [Breitling Source](https://www.breitlingsource.com/articles_refnos.shtml), [Montredo](https://www.montredo.com/breitling-reference-number-101/), [WatchBase AB0138211B1A1](https://watchbase.com/breitling/navitimer/ab0138211b1a1)
- TAG Heuer: [TAG Heuer Enthusiast](http://tagheuerenthusiast.blogspot.com/p/model-codes.html), [TAG Heuer Forums](https://tagheuerforums.com/threads/tag-heuer-model-codes.18513/)
- Audemars Piguet: [Watches Off 5th](https://watchesoff5th.com/blogs/how-to/read-audemars-piguet-reference-numbers), [WatchBase 15500ST](https://watchbase.com/audemars-piguet/royal-oak/15500st-oo-1220st-01)
- Patek Philippe: [Wrist Aficionado guide](https://wristaficionado.com/blogs/news/the-ultimate-guide-to-patek-philippe-reference-numbers-in-2025)
- Vacheron Constantin: [Watch Affinity](https://www.watch-affinity.com/vacheron-constantin-serial-numbers), [WatchBase 4520V](https://watchbase.com/vacheron-constantin/overseas/4520v-210a-b128)
- Jaeger-LeCoultre: [WatchUSeek thread](https://www.watchuseek.com/threads/regarding-jaeger-lecoultre-case-and-catalog-numbers.969851/), [WatchBase 3858520](https://watchbase.com/jaeger-lecoultre/reverso/3858520)
- IWC: [WatchBase IW3714-17](https://watchbase.com/iwc/portugieser/iw3714-17), [IWC forum](https://forum.iwc.com/t/reference-numbers-for-portuguese-chronograph/7947/)
- Cartier: [Luxury Bazaar guide](https://www.luxurybazaar.com/grey-market/cartier-reference-numbers/)
- Longines: [Precision Watches guide](https://precisionwatches.com/journal/an-in-depth-guide-to-longines-reference-numbers/), [WatchBase L3.781.4.56.6](https://watchbase.com/longines/hydroconquest/l3-781-4-56-6)
- Tissot: [WatchMaxx T137.407.16.051.00](https://www.watchmaxx.com/tissot-watch-t137-407-16-051-00), [Jomashop T137.407.11.051.00](https://www.jomashop.com/tissot-prx-powermatic-80-automatic-black-dial-mens-watch-t137-407-11-051-00.html)
- Certina: [WatchBase C032.407.11.051.00](https://watchbase.com/certina/ds-action/c032-407-11-051-00)
- Hamilton: [WatchUSeek product code chart](https://www.watchuseek.com/threads/hamilton-product-code-chart.1598706/), [hamiltonwatch.com H70455733](https://www.hamiltonwatch.com/en-us/h70455733-khaki-field-auto.html)
- Oris: [Oris help centre](https://helpcenter.oris.ch/hc/en-gb/articles/16999065639953-How-do-Oris-reference-numbers-work), [oris.ch Aquis Date](https://www.oris.ch/en-US/product/watch/aquis/aquis-date/01-733-7730-4134-07-8-24-05PEB)
- Zenith: [Topper 18.3100.3600/69.C920](https://topperjewelers.com/products/zenith-chronomaster-sport-rose-gold-18-3100-3600-69-c920), [The 1916 Company 51.3100.3600/69.M3100](https://www.the1916company.com/watches/zenith/chronomaster/chronomaster-51.3100.3600-69.m3100/)
- Panerai: [Watchlounge Panerai database](https://panerai.watchlounge.com/introduction/), [The Hour Markers](https://www.thehourmarkers.com/articles/panerai-reference-numbers-decoded)
- Outside test, examples: [Omega 220.12.41.21.03.001](https://watchbase.com/omega/aqua-terra/220-12-41-21-03-001), [Longines L3.810.4.53.0](https://watchbase.com/longines/spirit/l3-810-4-53-0), [Breitling A17375E71C1S1](https://watchbase.com/breitling/superocean/a17375e71c1s1), [Jaeger-LeCoultre 9008480](https://watchbase.com/jaeger-lecoultre/polaris/9008480), [Vacheron 4500V/000R-B127](https://watchbase.com/vacheron-constantin/overseas/4500v-000r-b127), [Patek 5167/1A-001](https://watchbase.com/patek-philippe/aquanaut/5167-1a-001), [AP 15210BC.OO.A321CR.01](https://watchbase.com/audemars-piguet/code-11-59/15210bc-oo-a321cr-01), [rolex.com 126331](https://www.rolex.com/watches/datejust/m126331-0015), [Hamilton H69439931](https://www.hamiltonwatch.com/en-us/h69439931-khaki-field-mechanical.html)
- A. Lange & Söhne: [alange-soehne.com 191.021](https://www.alange-soehne.com/us-en/timepieces/lange-1/lange-1/lange-1-in-750-yellow-gold-191-021), [191.025](https://www.alange-soehne.com/us-en/timepieces/lange-1/lange-1/lange-1-in-950-platinum-191-025)
