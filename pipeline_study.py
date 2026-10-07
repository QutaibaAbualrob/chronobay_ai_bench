"""Photo -> description -> web search -> shortlist. (Serper idea 1, stage 1)

    python pipeline_study.py run --yes                                  # every photo, default model
    python pipeline_study.py run --ids 3,17 --yes                       # a test run on a few photos
    python pipeline_study.py run --resume results/pipeline/<run_id> --yes   # continue a run that stopped
    python pipeline_study.py run --model deepseek-flash --yes           # another model (Anthropic or DeepSeek)
    python pipeline_study.py report [results/pipeline/<run_id>]         # rebuild the reports from saved answers, $0

For each photo:

    1. describe   one model call: brand, model line, what is visible, up to three candidate references
    2. search     three web searches through Serper, built from the model line and the first candidate
    3. rank       code orders the model's candidates and the searched ones; nothing is removed
    4. choose     a second model call sees the photo and the candidate list and ranks up to three

The report compares the model's own first reference with what the pipeline ends
with. Both come from the same describing call, so run-to-run noise does not
enter the comparison.

Model answers are saved under results/pipeline/<run_id>/. Search responses are
shared with search_study.py under results/serper/ (not in git).
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, ValidationError

import bench
import pricing
import report as bench_report
import schema
import scoring
import search_study as ss
import vision_test as vt

PIPE_DIR = bench.RESULTS_DIR / "pipeline"
OUT = bench.RESULTS_DIR / "PIPELINE_STUDY.md"
DEFAULT_MODEL = "claude-sonnet-5-5-nothink"
MAX_TOKENS = 2000              # both answers are short and the model is run without thinking
MAX_CANDIDATES = 15            # most the choosing call is shown
NUM = 10                       # results per search; a free Serper account allows no more
SEARCH_KINDS = ["line", "guess", "open"]

# ── the two answers the model gives ──────────────────────────────────────────

DialColor = Literal["black", "white", "silver", "grey", "blue", "green", "brown", "red", "orange", "yellow",
                    "pink", "purple", "champagne", "salmon", "beige", "mother-of-pearl", "skeleton", "other",
                    "unknown"]
CaseMaterial = Literal["stainless-steel", "yellow-gold", "rose-gold", "white-gold", "two-tone", "platinum",
                       "titanium", "ceramic", "bronze", "other", "unknown"]
Complication = Literal["date", "day-date", "chronograph", "gmt", "moonphase", "power-reserve", "small-seconds",
                       "world-time", "annual-calendar", "perpetual-calendar", "tourbillon"]


class Description(BaseModel):
    """What is visible comes before the references, so the model has looked before it names a number."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    brand: Literal[*schema.BRANDS, schema.UNKNOWN]
    model_line: str
    dial_color: DialColor
    case_material: CaseMaterial
    bracelet_material: Literal[*schema.BRACELET_MATERIALS, schema.UNKNOWN]
    bezel: str
    case_size_mm: float
    complications: list[Complication]
    movement: Literal[*schema.MOVEMENTS, schema.UNKNOWN]
    printed_reference: str
    references: list[str]
    confidence: float


class Choice(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str
    ranking: list[int]
    clear_leader: bool
    none_fit: bool


DESCRIBE_PROMPT = """You are identifying a wristwatch from a single photo, to pre-fill a listing on a luxury watch resale marketplace. A catalogue search will follow your answer, so report exactly what you see and give your best candidates.

Report:
- brand: one of Rolex, Omega, Patek Philippe, Audemars Piguet, Tag Heuer, Breitling, Cartier, IWC, Jaeger-LeCoultre, Vacheron Constantin — or "unknown".
- model_line: the collection and model name the brand uses, with the size when it is part of the name (for example "Portugieser Automatic 42").
- dial_color: the main colour of the dial: black, white, silver, grey, blue, green, brown, red, orange, yellow, pink, purple, champagne, salmon, beige, mother-of-pearl, skeleton, other, or "unknown".
- case_material: stainless-steel, yellow-gold, rose-gold, white-gold, two-tone (steel with gold), platinum, titanium, ceramic, bronze, other, or "unknown".
- bracelet_material: leather, metal, rubber, fabric, nylon, or "unknown".
- bezel: a few words on the bezel, its material or colour and its type (for example "black ceramic dive bezel", "fluted", "smooth steel", "tachymeter"), or "none".
- case_size_mm: your estimate of the case diameter in millimetres, or 0 if you cannot tell.
- complications: every one you can see, from: date, day-date, chronograph, gmt, moonphase, power-reserve, small-seconds, world-time, annual-calendar, perpetual-calendar, tourbillon. An empty list for a time-only watch.
- movement: automatic, manual, quartz, solar, hybrid, or "unknown".
- printed_reference: a reference number you can read in the photo itself (on a card, a tag or the case back), copied exactly; otherwise an empty string. Never copy a serial number.
- references: up to three candidate manufacturer reference numbers for this exact version of the watch, most likely first, each in the brand's own official format (keep its dots, slashes and letters). Always give at least one. Add a second or a third only for versions you cannot rule out from the photo: another dial or strap version, the previous generation, another size. For Rolex give the base reference (126334), not a catalogue suffix.
- confidence: a number from 0.0 to 1.0 — how sure you are that the first reference is exactly right.

Answer as JSON."""

CHOOSE_PROMPT = """You are looking at a photo of a wristwatch, to pre-fill a listing on a luxury watch resale marketplace.

A first look at this photo gave: {brand}, {line}.
A search of watch catalogues and shop pages then returned the candidate references below. After each one is what those pages say about it. That text can be short, cut off or missing. "By its reference code" is what the brand's numbering system says about that reference.

{candidates}

Decide which candidate is the watch in the photo. Compare what you can see (dial colour and layout, hands and markers, case metal, bezel, bracelet or strap, size, complications) with each candidate's description and with what you know about each reference.

Report:
- reason: one sentence naming what you see that decides between the candidates.
- ranking: the numbers of up to three candidates, most likely first.
- clear_leader: true only if something visible in the photo separates your first choice from every other candidate. false if two or more candidates would look the same in this photo.
- none_fit: true if you believe the watch in the photo is none of the candidates. Still give your best ranking.

Answer as JSON."""


# ── what a reference and a catalogue line say about a watch ──────────────────

WHITE, YELLOW, ROSE, TWO, CERAMIC, BRONZE = "white metal", "yellow gold", "rose gold", "two-tone", "ceramic", "bronze"
# Steel, titanium, white gold and platinum look alike in a photo, so they are one group when comparing.
SEEN_METAL = {"stainless-steel": WHITE, "white-gold": WHITE, "platinum": WHITE, "titanium": WHITE,
              "yellow-gold": YELLOW, "rose-gold": ROSE, "two-tone": TWO, "ceramic": CERAMIC, "bronze": BRONZE}
SEEN_STRAP = {"metal": "bracelet", "leather": "strap", "rubber": "strap", "fabric": "strap", "nylon": "strap"}
QUERY_METAL = {"stainless-steel": "steel", "yellow-gold": "yellow gold", "rose-gold": "rose gold",
               "white-gold": "white gold", "two-tone": "steel and gold", "platinum": "platinum",
               "titanium": "titanium", "ceramic": "ceramic", "bronze": "bronze"}
# Dial colours a photo or a catalogue line can easily swap; these never count as a disagreement.
CLOSE_COLOURS = {frozenset(p) for p in (("white", "silver"), ("grey", "silver"), ("grey", "black"),
                                        ("champagne", "yellow"), ("pink", "salmon"), ("beige", "white"),
                                        ("beige", "champagne"), ("beige", "silver"))}
COLOUR_WORDS = [("mother of pearl", "mother-of-pearl"), ("mother-of-pearl", "mother-of-pearl"),
                ("skeleton", "skeleton"), ("openworked", "skeleton"), ("anthracite", "grey"), ("slate", "grey"),
                ("ruthenium", "grey"), ("rhodium", "grey"), ("grey", "grey"), ("gray", "grey"),
                ("black", "black"), ("white", "white"), ("silver", "silver"), ("opaline", "silver"),
                ("blue", "blue"), ("turquoise", "blue"), ("green", "green"), ("olive", "green"),
                ("khaki", "green"), ("brown", "brown"), ("chocolate", "brown"), ("burgundy", "red"),
                ("red", "red"), ("orange", "orange"), ("yellow", "yellow"), ("salmon", "salmon"),
                ("pink", "pink"), ("purple", "purple"), ("champagne", "champagne"), ("beige", "beige"),
                ("cream", "beige"), ("ivory", "beige")]


def decode(brand: str, ref: str | None) -> dict:
    """What a reference's own structure says, using only rules REFERENCE_FORMATS.md marks confirmed, for
    the ten benchmark brands. `metal` is the group used for comparing, `metal_name` the exact reading.
    Anything that does not parse gives nothing."""
    s = (ref or "").strip().upper()
    d: dict = {}

    def metal(name: str | None, group: str | None) -> None:
        if name:
            d["metal_name"] = name
        if group:
            d["metal"] = group

    if brand == "Omega":
        g = s.split(".")
        if len(g) == 6 and all(x.isdigit() for x in g) and len(g[1]) == 2:
            metal(*{"1": ("steel", WHITE), "3": ("steel", WHITE), "2": ("steel and gold", TWO)}.get(g[1][0], (None, None)))
            d["strap"] = "bracelet" if g[1][1] == "0" else "strap"
            d["size"] = g[2]
            dial = {"01": "black", "02": "silver", "03": "blue", "04": "white"}.get(g[4])
            if dial:
                d["dial"] = dial
    elif brand == "Breitling":
        if re.fullmatch(r"[A-Z]{1,2}\d{2}[0-9A-Z]{5,7}[A-Z]\d[A-Z]\d", s):
            metal(*{"A": ("steel", WHITE), "E": ("titanium", WHITE), "R": ("red gold", ROSE),
                    "U": ("steel and gold", TWO)}.get(s[0], (None, None)))
            dial = {"A": "white", "B": "black", "C": "blue", "G": "silver", "K": "red"}.get(s[-4])
            if dial:
                d["dial"] = dial
            strap = {"A1": "bracelet", "E1": "bracelet", "S1": "strap", "P1": "strap", "X1": "strap"}.get(s[-2:])
            if strap:
                d["strap"] = strap
    elif brand == "Jaeger-LeCoultre":
        r = re.sub(r"^(JL)?Q", "", s)
        if len(r) == 7:
            metal(*{"8": ("steel", WHITE), "2": ("pink gold", ROSE)}.get(r[3], (None, None)))
            strap = {"1": "bracelet", "4": "strap", "5": "strap"}.get(r[4])
            if strap:
                d["strap"] = strap
    elif brand == "Vacheron Constantin":
        m = re.match(r"\d{4,5}[A-Z]?/\d{3}([A-Z])-", s)
        if m:
            metal(*{"A": ("steel", WHITE), "R": ("pink gold", ROSE), "G": ("white gold", WHITE),
                    "J": ("yellow gold", YELLOW), "P": ("platinum", WHITE),
                    "M": ("steel and pink gold", TWO)}.get(m.group(1), (None, None)))
    elif brand == "Patek Philippe":
        m = re.match(r"\d{4}(/\d+)?([A-Z]{1,2})-", s)
        if m:
            metal(*{"A": ("steel", WHITE), "J": ("yellow gold", YELLOW), "G": ("white gold", WHITE),
                    "R": ("rose gold", ROSE), "P": ("platinum", WHITE)}.get(m.group(2), (None, None)))
            d["strap"] = "bracelet" if (m.group(1) or "").startswith("/1") else "strap"
    elif brand == "Audemars Piguet":
        p = s.split(".")
        if len(p) == 4 and re.fullmatch(r"\d{5}[A-Z]{2}", p[0]) and p[2]:
            metal(*{"ST": ("steel", WHITE), "TI": ("titanium", WHITE), "PT": ("platinum", WHITE),
                    "BC": ("white gold", WHITE), "OR": ("pink gold", ROSE), "BA": ("yellow gold", YELLOW),
                    "CE": ("black ceramic", CERAMIC)}.get(p[0][5:], (None, None)))
            d["strap"] = "bracelet" if p[2][0].isdigit() else "strap"
    elif brand == "Rolex":
        m = re.match(r"M?(\d{5,6})", s)
        if m:
            # 4 is steel with a white gold bezel, which looks like steel in a photo.
            metal(*{"0": ("steel", WHITE), "4": ("steel with white gold bezel", WHITE), "9": ("white gold", WHITE),
                    "6": ("platinum", WHITE), "1": ("steel and Everose gold", TWO),
                    "3": ("steel and yellow gold", TWO), "5": ("Everose gold", ROSE),
                    "8": ("yellow gold", YELLOW)}.get(m.group(1)[-1], (None, None)))
    elif brand == "Cartier":
        if re.fullmatch(r"W[A-Z0-9][A-Z]{2}\d{4}", s):
            metal(*{"S": ("steel", WHITE), "2": ("steel and gold", TWO), "G": ("gold", None)}.get(s[1], (None, None)))
    elif brand == "Tag Heuer":
        m = re.fullmatch(r"([A-Z]{3}[A-Z0-9]{4})\.?([A-Z]{2})\d{4}", s)
        if m:
            if m.group(1)[5] == "1":
                metal("steel", WHITE)
            strap = {"B": "bracelet", "F": "strap"}.get(m.group(2)[0])
            if strap:
                d["strap"] = strap
    return d


def colour_in(text: str) -> str | None:
    low = text.lower()
    return next((colour for word, colour in COLOUR_WORDS if re.search(rf"\b{re.escape(word)}\b", low)), None)


def read_description(desc: str) -> dict:
    """Metal, dial colour and strap from a WatchBase line of the form `Name Metal / Dial / Strap`."""
    segs = [s.strip() for s in desc.split(" / ")]
    head, d = segs[0].lower(), {}
    steel = "stainless" in head or re.search(r"\bsteel\b", head)
    yellow = "yellow gold" in head or "rolesor yellow" in head
    rose = any(w in head for w in ("pink gold", "rose gold", "red gold", "everose", "sedna"))
    if "rolesor" in head and "white" in head:
        d["metal"] = WHITE
    elif any(w in head for w in ("rolesor", "two-tone", "two tone", "bicolor")) or (steel and (yellow or rose)):
        d["metal"] = TWO
    elif yellow:
        d["metal"] = YELLOW
    elif rose:
        d["metal"] = ROSE
    elif steel or any(w in head for w in ("titanium", "platinum", "white gold")):
        d["metal"] = WHITE
    elif "ceramic" in head:
        d["metal"] = CERAMIC
    elif "bronze" in head:
        d["metal"] = BRONZE
    if len(segs) > 1:
        dial = colour_in(segs[1])
        if dial:
            d["dial"] = dial
        rest = " ".join(segs[1:]).lower()
        if re.search(r"\bbracelet\b", rest):
            d["strap"] = "bracelet"
        elif re.search(r"\b(strap|leather|alligator|rubber|calf|textile|fabric|nato)\b", rest):
            d["strap"] = "strap"
    return d


def ref_spans(text: str, brand: str) -> list[tuple[int, int, str]]:
    """(start, end, canonical reference) for every reference of this brand in a text known to be about
    that brand, so the patterns that need the brand named beside the number apply too."""
    upper, taken, out = text.upper(), [], []
    for b, pattern, _needs in vt.PATTERNS:
        if b != brand:
            continue
        for m in pattern.finditer(upper):
            if any(m.start() < e and s < m.end() for s, e in taken):
                continue
            taken.append((m.start(), m.end()))
            found = vt.find_references(f"{brand} {text[m.start():m.end()]}", {brand})
            if found:
                out.append((m.start(), m.end(), vt.canon(brand, found[0][1])))
    return sorted(out)


def _structured(text: str) -> str | None:
    """A WatchBase line `Name Metal / Dial / Strap`, or None when the text is not one or Google cut it."""
    text = " ".join(text.split()).strip(" ;,:-–")
    return text if " / " in text and 8 <= len(text) <= 160 and not text.endswith(("...", "…")) else None


def watchbase_lines(title: str, snippet: str, brand: str) -> dict[str, str]:
    """{canonical reference: `Name Metal / Dial / Strap`} read from one WatchBase result. The line stands
    in a watch page's title, or directly after a reference in a snippet. Lines standing before a reference
    in brackets are not read: in the first full run that form attached lines to the wrong watch."""
    out: dict[str, str] = {}
    spans = ref_spans(title, brand)
    if len(spans) == 1:
        start, end, canon = spans[0]
        rest = title[:start] + " " + title[end:]
        for alias in sorted([brand, *vt.ALIASES.get(brand, [])], key=len, reverse=True):
            rest = re.sub(re.escape(alias), " ", rest, flags=re.I)
        line = _structured(re.sub(r"\s*[»|]\s*WatchBase.*$", "", rest, flags=re.I).replace(" : ", " "))
        if line:
            out[canon] = line
    for _start, end, canon in ref_spans(snippet, brand):
        line = _structured(re.split(r" ; |\. |\(|\)| \| |・|…|\.\.\.", snippet[end:end + 170], maxsplit=1)[0])
        if line:
            out.setdefault(canon, line)
    return out


def clean_ref(brand: str | None, ref: str | None) -> str:
    """A reference as the model wrote it, without a note added in brackets or after the number."""
    s = (ref or "").strip()
    if brand in schema.BRANDS:
        found = [raw for b, raw in vt.find_references(f"{brand} {s}", {brand}) if b == brand]
        if found:
            return found[0]
    return re.split(r"\s*[(\[]", s, maxsplit=1)[0].strip()


def own_references(d: dict) -> list[str]:
    """The model's own candidates, cleaned, without repeats, at most three."""
    brand, out, seen = d.get("brand"), [], set()
    for ref in d.get("references") or []:
        shown = clean_ref(brand, ref)
        canon = vt.canon(brand, shown) if brand in schema.BRANDS else scoring.normalize(shown)
        if canon and canon not in seen:
            seen.add(canon)
            out.append(shown)
    return out[:3]


def compatible(a: str, b: str) -> bool:
    return a == b or frozenset((a, b)) in CLOSE_COLOURS


def seen_by_model(d: dict) -> dict:
    dial = d.get("dial_color")
    return {"metal": SEEN_METAL.get(d.get("case_material")), "strap": SEEN_STRAP.get(d.get("bracelet_material")),
            "dial": None if dial in ("other", "unknown", None) else dial}


# ── searches and the candidate list ──────────────────────────────────────────

def photo_queries(d: dict) -> dict[str, str]:
    """The three searches for one photo. Same forms as stage 0; the guess search is always made here."""
    brand = d.get("brand")
    if brand not in schema.BRANDS:
        return {}
    out, name, line = {}, ss.name_of(brand), ss.clean_line(brand, d.get("model_line"))
    if line:
        out["line"] = f"site:watchbase.com {name} {line}"
        extras = [QUERY_METAL.get(d.get("case_material"), ""), ss.STRAP.get(d.get("bracelet_material"), "")]
        out["open"] = " ".join(f"{name} {line} {' '.join(extras)} reference".split())
    refs = own_references(d)
    if refs:
        out["guess"] = f"site:watchbase.com {name} {ss.model_part(brand, refs[0]) or ss.watchbase_notation(brand, refs[0])}"
    return out


def gather(d: dict) -> list[dict]:
    """Every candidate for one photo, in the order code ranks them: the model's own references and every
    reference the saved searches returned. Fewest disagreements with the photo first, then the model's own
    order, then how many searches returned the reference as a page of its own, then its place in the results."""
    brand = d.get("brand")
    known = brand in schema.BRANDS
    cands: dict[str, dict] = {}

    def cand(canon: str, shown: str) -> dict:
        return cands.setdefault(canon, {"canon": canon, "reference": shown, "own": None, "kinds": set(),
                                        "pos": 99, "pages": [], "mentions": [], "line": None})

    for i, ref in enumerate(own_references(d), 1):
        cand(vt.canon(brand, ref) if known else scoring.normalize(ref), ref)["own"] = i
    if known:
        for kind, text in photo_queries(d).items():
            for pos, res in enumerate(ss.results_of(text, NUM) or [], 1):
                title, link, snippet = res.get("title") or "", res.get("link") or "", res.get("snippet") or ""
                domain = urlparse(link).netloc.removeprefix("www.")
                strong = {vt.canon(brand, raw): raw for b, raw in vt.find_references(title, {brand}) + vt.find_references(link, {brand}) if b == brand}
                weak = {vt.canon(brand, raw): raw for b, raw in vt.find_references(snippet, {brand}) if b == brand}
                for canon, raw in strong.items():
                    c = cand(canon, raw)
                    c["kinds"].add(kind)
                    c["pos"] = min(c["pos"], pos)
                    c["pages"].append({"domain": domain, "title": title, "snippet": snippet})
                for canon, raw in weak.items():
                    if canon not in strong:
                        cand(canon, raw)["mentions"].append({"domain": domain, "snippet": snippet})
                if domain.endswith("watchbase.com"):
                    for canon, line in watchbase_lines(title, snippet, brand).items():
                        if canon in cands and not cands[canon]["line"]:
                            cands[canon]["line"] = line
    seen = seen_by_model(d)
    for c in cands.values():
        c["decoded"] = decode(brand, c["reference"]) if known else {}
        from_line = read_description(c["line"]) if c["line"] else {}
        if brand == "Rolex":                 # a Rolex reference covers every dial and bracelet; a line is one of them
            from_line = {k: v for k, v in from_line.items() if k == "metal"}
        says = {**from_line, **{k: v for k, v in c["decoded"].items() if k in ("metal", "dial", "strap")}}
        c["against"] = [k for k in ("metal", "dial", "strap")
                        if seen[k] and says.get(k) and not (compatible(seen[k], says[k]) if k == "dial" else seen[k] == says[k])]
    return sorted(cands.values(), key=lambda c: (len(c["against"]), c["own"] or 9, -len(c["kinds"]), c["pos"], c["canon"]))


def _cut(text: str, n: int) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= n else text[:n - 1].rstrip() + "…"


def candidate_line(i: int, c: dict) -> str:
    parts, domains = [], set()
    if c["line"]:
        parts.append(f"WatchBase: {c['line']}")
        domains.add("watchbase.com")
    for page in c["pages"]:
        if page["domain"] not in domains and len(domains) < 3:        # one page per site, at most two more
            domains.add(page["domain"])
            parts.append(f"{page['domain']}: {_cut(page['title'], 90)} - {_cut(page['snippet'], 170)}")
    if not parts and c["mentions"]:
        parts.append(f"named on {c['mentions'][0]['domain']}: {_cut(c['mentions'][0]['snippet'], 170)}")
    dec = c["decoded"]
    code = [dec.get("metal_name") and f"{dec['metal_name']} case", dec.get("strap") and f"on a {dec['strap']}",
            dec.get("dial") and f"{dec['dial']} dial", dec.get("size") and f"{dec['size']} mm"]
    if any(code):
        parts.append("by its reference code: " + ", ".join(x for x in code if x))
    if not parts:
        parts.append("no catalogue page came back for it")
    return f"[{i}] {c['reference']} | " + " | ".join(parts)


def choose_prompt(d: dict, shown: list[dict]) -> str:
    return CHOOSE_PROMPT.format(brand=d.get("brand"), line=d.get("model_line") or "model line not named",
                                candidates="\n".join(candidate_line(i, c) for i, c in enumerate(shown, 1)))


# ── calling the model ────────────────────────────────────────────────────────

class Fatal(Exception):
    """An error every call would repeat (bad key, no credit)."""


PROVIDERS = ("anthropic", "deepseek")
# Rough model cost per photo for both calls, used only for the estimate shown before a run.
# Anthropic: measured on the first Sonnet run. DeepSeek: twice its benchmark cost per call, plus the longer second prompt.
ROUGH_COST = {"anthropic": 0.022, "deepseek": 0.005}

# DeepSeek cannot be held to a schema by its API, so the shape of the answer goes in the prompt
# (as providers/deepseek_provider.py does for the benchmark) and the answer is checked here.
JSON_SHAPE = {
    "Description": '\nReply with ONLY a JSON object — no prose, no code fences — with exactly these keys:\n'
                   '{"brand": "...", "model_line": "...", "dial_color": "...", "case_material": "...", '
                   '"bracelet_material": "...", "bezel": "...", "case_size_mm": 0, "complications": [], '
                   '"movement": "...", "printed_reference": "", "references": ["..."], "confidence": 0.0}\n',
    "Choice": '\nReply with ONLY a JSON object — no prose, no code fences — with exactly these keys:\n'
              '{"reason": "...", "ranking": [candidate numbers, most likely first], "clear_leader": true or false, '
              '"none_fit": true or false}\n',
}
_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)
DIAL_WORDS = {"gray": "grey", "navy": "blue", "anthracite": "grey", "slate": "grey", "cream": "beige",
              "ivory": "beige", "gold": "champagne", "mop": "mother-of-pearl", "openworked": "skeleton"}
BRACELET_WORDS = {"steel": "metal", "bracelet": "metal", "gold": "metal", "titanium": "metal", "alligator": "leather",
                  "crocodile": "leather", "calfskin": "leather", "calf": "leather", "textile": "fabric",
                  "canvas": "fabric", "nato": "nylon"}
MOVEMENT_WORDS = {"self-winding": "automatic", "selfwinding": "automatic", "hand-wound": "manual",
                  "manual-winding": "manual", "hand-winding": "manual"}


def _word(value, allowed: tuple, words: dict, fallback: str) -> str:
    """A free-text value fitted to a fixed list: itself, a known other spelling, or a listed word inside it."""
    s = re.sub(r"[\s_/]+", "-", str(value or "").strip().lower())
    if s in allowed:
        return s
    if s in words:
        return words[s]
    return next((words.get(t, t) for t in s.split("-") if words.get(t, t) in allowed and t not in ("other", "unknown")),
                fallback)


def _case_word(value) -> str:
    s = re.sub(r"[\s_/]+", "-", str(value or "").strip().lower())
    allowed = CaseMaterial.__args__
    if s in allowed:
        return s
    gold, steel = "gold" in s, "steel" in s
    if s in ("two-tone", "bicolor", "bicolour") or (gold and steel):
        return "two-tone"
    if gold:
        return next((v for k, v in (("yellow", "yellow-gold"), ("white", "white-gold"), ("rose", "rose-gold"),
                                    ("pink", "rose-gold"), ("red", "rose-gold")) if k in s), "other")
    return next((v for k, v in (("steel", "stainless-steel"), ("titanium", "titanium"), ("platinum", "platinum"),
                                ("ceramic", "ceramic"), ("bronze", "bronze")) if k in s), "other")


def tidy_description(data: dict) -> dict:
    """An answer that broke the format, fitted to it. Used only when the answer does not validate as it is."""
    brand = str(data.get("brand") or "").upper()
    refs = data.get("references")
    refs = [refs] if isinstance(refs, str) else (refs if isinstance(refs, list) else [])
    size = re.search(r"\d+(\.\d+)?", str(data.get("case_size_mm") or ""))
    comps = data.get("complications") if isinstance(data.get("complications"), list) else []
    try:
        confidence = min(1.0, max(0.0, float(data.get("confidence") or 0)))
    except (TypeError, ValueError):
        confidence = 0.0
    return {
        "brand": next((b for b in schema.BRANDS if vt.names_brand(brand, b)), schema.UNKNOWN),
        "model_line": str(data.get("model_line") or data.get("model_family") or "").strip(),
        "dial_color": _word(data.get("dial_color"), DialColor.__args__, DIAL_WORDS, "other"),
        "case_material": _case_word(data.get("case_material")),
        "bracelet_material": _word(data.get("bracelet_material"), (*schema.BRACELET_MATERIALS, schema.UNKNOWN),
                                   BRACELET_WORDS, schema.UNKNOWN),
        "bezel": str(data.get("bezel") or "none").strip(),
        "case_size_mm": float(size.group(0)) if size else 0.0,
        "complications": [c for c in (re.sub(r"[\s_]+", "-", str(x).strip().lower()) for x in comps)
                          if c in Complication.__args__],
        "movement": _word(data.get("movement"), (*schema.MOVEMENTS, schema.UNKNOWN), MOVEMENT_WORDS, schema.UNKNOWN),
        "printed_reference": str(data.get("printed_reference") or "").strip(),
        "references": [str(r).strip() for r in refs if str(r).strip()],
        "confidence": confidence,
    }


def tidy_choice(data: dict) -> dict:
    ranking = data.get("ranking")
    ranking = ranking if isinstance(ranking, list) else [ranking]
    numbers = [int(m.group(0)) for m in (re.search(r"\d+", str(x)) for x in ranking) if m]
    flag = lambda v: v is True or str(v).strip().lower() == "true"  # noqa: E731
    return {"reason": str(data.get("reason") or "").strip(), "ranking": numbers,
            "clear_leader": flag(data.get("clear_leader")), "none_fit": flag(data.get("none_fit"))}


def read_answer(text: str | None, answer_cls) -> tuple[dict | None, bool, str | None]:
    """(validated answer, whether it had to be tidied to fit, what was wrong when there is no answer)."""
    if not text or not text.strip():
        return None, False, "empty answer"
    body = _FENCE.sub("", text.strip()).strip()
    start, end = body.find("{"), body.rfind("}")
    if start != -1 and end > start:
        body = body[start:end + 1]
    try:
        data = json.loads(body)
    except ValueError as e:
        return None, False, f"invalid JSON: {str(e)[:120]}"
    if not isinstance(data, dict):
        return None, False, "the answer is not a JSON object"
    try:
        return answer_cls.model_validate(data).model_dump(), False, None
    except ValidationError:
        pass
    try:
        tidied = tidy_description(data) if answer_cls is Description else tidy_choice(data)
        return answer_cls.model_validate(tidied).model_dump(), True, None
    except ValidationError as e:
        return None, False, f"the answer does not fit the format: {str(e)[:200]}"


def make_client(cfg, spec: dict):
    st = bench.settings(cfg)
    if spec["provider"] == "deepseek":
        import openai
        from providers.deepseek_provider import BASE_URL
        return openai.OpenAI(api_key=bench.api_key(cfg, "deepseek"), base_url=BASE_URL, max_retries=4,
                             timeout=st["timeout_s"])
    import anthropic
    headers = {"anthropic-workspace-id": st["anthropic_workspace_id"]} if st.get("anthropic_workspace_id") else None
    return anthropic.Anthropic(api_key=bench.api_key(cfg, "anthropic"), max_retries=4, timeout=st["timeout_s"],
                               default_headers=headers)


def ask(client, spec: dict, image: tuple[str, str], prompt: str, answer_cls) -> dict:
    """One call with the photo and a prompt. Returns a record with the validated answer or an error."""
    if spec["provider"] == "deepseek":
        return _ask_deepseek(client, spec, image, prompt, answer_cls)
    return _ask_anthropic(client, spec, image, prompt, answer_cls)


def _ask_deepseek(client, spec: dict, image: tuple[str, str], prompt: str, answer_cls) -> dict:
    """Same request shape as the benchmark's DeepSeek adapter: text first, then the photo, JSON asked for in
    the prompt. The API can return empty content, so an empty or unusable answer is asked for once more;
    both attempts are billed and both are counted."""
    import openai
    from providers.deepseek_provider import MAX_OUTPUT_TOKENS
    messages = [{"role": "user", "content": [
        {"type": "text", "text": prompt + JSON_SHAPE[answer_cls.__name__]},
        {"type": "image_url", "image_url": {"url": f"data:{image[1]};base64,{image[0]}"}}]}]
    rec = {"parsed": None, "raw_text": None, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0,
           "elapsed_s": 0.0, "started_at": datetime.now(timezone.utc).isoformat(), "error": None,
           "attempts": 0, "tidied": False}
    t0, problems = time.perf_counter(), []
    for attempt in (1, 2):
        at = datetime.now(timezone.utc)
        try:
            resp = client.chat.completions.create(model=spec["model"], messages=messages,
                                                  response_format={"type": "json_object"},
                                                  max_tokens=MAX_OUTPUT_TOKENS)
        except (openai.AuthenticationError, openai.PermissionDeniedError) as e:
            raise Fatal(f"{type(e).__name__}: {str(e)[:200]}") from e
        except openai.APIStatusError as e:
            if e.status_code == 402:
                raise Fatal(f"HTTP 402: {str(e)[:200]}") from e
            problems.append(f"HTTP {e.status_code}: {str(e)[:200]}")
            break
        except openai.APIError as e:
            problems.append(f"{type(e).__name__}: {str(e)[:200]}")
            break
        rec["attempts"] = attempt
        usage = resp.usage
        if usage:
            cached = getattr(usage, "prompt_cache_hit_tokens", None) or 0
            rec["input_tokens"] += usage.prompt_tokens
            rec["output_tokens"] += usage.completion_tokens
            cost = pricing.cost_usd("deepseek", spec["model"], usage.prompt_tokens, usage.completion_tokens, cached, at=at)
            rec["cost_usd"] = None if cost is None or rec["cost_usd"] is None else rec["cost_usd"] + cost
        choice = resp.choices[0] if resp.choices else None
        rec["raw_text"], rec["served_model"] = (choice.message.content if choice else None), resp.model
        rec["parsed"], rec["tidied"], problem = read_answer(rec["raw_text"], answer_cls)
        if rec["parsed"] is not None:
            break
        problems.append(f"attempt {attempt}: {problem} (finish_reason={choice.finish_reason if choice else None})")
    rec["elapsed_s"] = round(time.perf_counter() - t0, 3)
    if rec["parsed"] is None:
        rec["error"] = (" | ".join(problems) or "no answer")[:600]
    return rec


def _ask_anthropic(client, spec: dict, image: tuple[str, str], prompt: str, answer_cls) -> dict:
    import anthropic
    output_config: dict = {"format": {"type": "json_schema",
                                      "schema": schema._strip_titles(answer_cls.model_json_schema())}}
    if spec.get("effort"):
        output_config["effort"] = spec["effort"]
    extra = {"thinking": {"type": spec["thinking"]}} if spec.get("thinking") else {}
    rec = {"parsed": None, "raw_text": None, "input_tokens": None, "output_tokens": None, "cost_usd": None,
           "elapsed_s": 0.0, "started_at": datetime.now(timezone.utc).isoformat(), "error": None}
    t0 = time.perf_counter()
    try:
        resp = client.messages.create(
            model=spec["model"], max_tokens=MAX_TOKENS, output_config=output_config, **extra,
            messages=[{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": image[1], "data": image[0]}},
                {"type": "text", "text": prompt}]}])
    except (anthropic.AuthenticationError, anthropic.PermissionDeniedError) as e:
        raise Fatal(f"{type(e).__name__}: {str(e)[:200]}") from e
    except anthropic.APIStatusError as e:
        if e.status_code == 400 and "credit" in str(e).lower():
            raise Fatal(f"HTTP 400: {str(e)[:200]}") from e
        rec["error"] = f"HTTP {e.status_code}: {str(e)[:300]}"
    except anthropic.APIError as e:
        rec["error"] = f"{type(e).__name__}: {str(e)[:300]}"
    rec["elapsed_s"] = round(time.perf_counter() - t0, 3)
    if rec["error"]:
        return rec
    usage = resp.usage
    cached = usage.cache_read_input_tokens or 0
    rec["input_tokens"] = usage.input_tokens + cached + (usage.cache_creation_input_tokens or 0)
    rec["output_tokens"] = usage.output_tokens
    rec["cost_usd"] = pricing.cost_usd("anthropic", spec["model"], rec["input_tokens"], usage.output_tokens, cached)
    rec["served_model"], rec["stop_reason"] = resp.model, resp.stop_reason
    text = "".join(b.text for b in resp.content if b.type == "text")
    rec["raw_text"] = text
    if resp.stop_reason in ("refusal", "max_tokens"):
        rec["error"] = f"stop_reason={resp.stop_reason}"
        return rec
    try:
        rec["parsed"] = answer_cls.model_validate(json.loads(text)).model_dump()
    except (ValueError, ValidationError) as e:
        rec["error"] = f"invalid answer: {str(e)[:300]}"
    return rec


def _load(path: Path) -> dict | None:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _ok(path: Path) -> bool:
    rec = _load(path)
    return bool(rec and rec["result"].get("parsed"))


def _each(todo: list, work, concurrency: int) -> None:
    """Run the first item alone, so a bad key stops the run after one call, then the rest together."""
    if not todo:
        return
    work(todo[0])
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        for fut in as_completed([pool.submit(work, t) for t in todo[1:]]):
            fut.result()


# ── the steps ────────────────────────────────────────────────────────────────

def step_describe(run_dir: Path, rows: list[dict], client, spec: dict, images: dict, concurrency: int) -> None:
    out = run_dir / "describe"
    out.mkdir(exist_ok=True)
    todo = [r for r in rows if not _ok(out / f"{r['id']:03d}.json")]
    print(f"1. Describe: {len(todo)} photos to do, {len(rows) - len(todo)} already saved")
    done = 0

    def work(row: dict) -> None:
        nonlocal done
        res = ask(client, spec, images[row["id"]], DESCRIBE_PROMPT, Description)
        (out / f"{row['id']:03d}.json").write_text(json.dumps(
            {"row_id": row["id"], "image_file": row["image_file"], "result": res}, indent=1, ensure_ascii=False),
            encoding="utf-8")
        done += 1
        p = res["parsed"] or {}
        first = (p.get("references") or ["-"])[0]
        ok = scoring.match(row["brand"], row["reference_number"], row["also_accept"], first)[0]
        mark = f"ERR {res['error'][:40]}" if res["error"] else ("ok " if ok else "no ")
        print(f"   {done:>3}/{len(todo)}  #{row['id']:<3} {mark:<4} first {first:<24} expected {row['reference_number']:<22} "
              f"{res['elapsed_s']:.1f}s", flush=True)

    _each(todo, work, concurrency)


def step_search(run_dir: Path, rows: list[dict]) -> None:
    texts: dict[str, list[str]] = {k: [] for k in SEARCH_KINDS}
    for row in rows:
        rec = _load(run_dir / "describe" / f"{row['id']:03d}.json")
        d = rec and rec["result"].get("parsed")
        for kind, text in (photo_queries(d) if d else {}).items():
            if ss.saved(text, NUM) is None and text not in texts[kind]:
                texts[kind].append(text)
    new = sum(len(v) for v in texts.values())
    print(f"2. Search: {new} new searches (1 Serper credit each); the rest are already saved")
    if not new:
        return
    key = ss.api_key()
    if not key:
        raise Fatal(f"No {ss.KEY_NAME} in config.py")
    credits = 0
    for kind in SEARCH_KINDS:
        saved_n, used, failed = ss.fetch(key, kind, texts[kind], NUM, 3)
        credits += used
        if failed:
            print(f"   {kind}: {failed} searches failed; run again with --resume to retry them")
    print(f"   {credits} credits used, {ss.balance(key)} left")


def step_choose(run_dir: Path, rows: list[dict], client, spec: dict, images: dict, concurrency: int) -> None:
    out, prompts = run_dir / "choose", run_dir / "prompts"
    out.mkdir(exist_ok=True)
    prompts.mkdir(exist_ok=True)
    todo = []
    for row in rows:
        rec = _load(run_dir / "describe" / f"{row['id']:03d}.json")
        d = rec and rec["result"].get("parsed")
        if not d or _ok(out / f"{row['id']:03d}.json"):
            continue
        shown = gather(d)[:MAX_CANDIDATES]
        if len(shown) >= 2:                      # nothing to choose between with fewer
            todo.append((row, d, shown))
    print(f"3. Choose: {len(todo)} photos to do")
    done = 0

    def work(item) -> None:
        nonlocal done
        row, d, shown = item
        prompt = choose_prompt(d, shown)
        (prompts / f"{row['id']:03d}.txt").write_text(prompt, encoding="utf-8")
        res = ask(client, spec, images[row["id"]], prompt, Choice)
        (out / f"{row['id']:03d}.json").write_text(json.dumps(
            {"row_id": row["id"], "candidates": [c["reference"] for c in shown], "result": res}, indent=1,
            ensure_ascii=False), encoding="utf-8")
        done += 1
        p = res["parsed"] or {}
        picks = [shown[i - 1]["reference"] for i in p.get("ranking") or [] if 1 <= i <= len(shown)]
        first = picks[0] if picks else "-"
        ok = scoring.match(row["brand"], row["reference_number"], row["also_accept"], first)[0]
        mark = f"ERR {res['error'][:40]}" if res["error"] else ("ok " if ok else "no ")
        print(f"   {done:>3}/{len(todo)}  #{row['id']:<3} {mark:<4} chose {first:<24} expected {row['reference_number']:<22} "
              f"of {len(shown):>2}  {res['elapsed_s']:.1f}s", flush=True)

    _each(todo, work, concurrency)


# ── scoring ──────────────────────────────────────────────────────────────────

def _right(row: dict, brand: str | None, ref: str | None) -> tuple[bool, bool]:
    """(exact, exact or accepted look-alike) for one reference."""
    if not ref or brand != row["brand"]:
        return False, False
    return vt.same_reference(row["brand"], row["reference_number"], row["also_accept"], ref)


def _any(row: dict, brand: str | None, refs: list[str]) -> tuple[bool, bool]:
    hits = [_right(row, brand, r) for r in refs]
    return any(h[0] for h in hits), any(h[1] for h in hits)


def analyse(run_dir: Path, rows: list[dict]) -> list[dict]:
    items = []
    for row in rows:
        drec = _load(run_dir / "describe" / f"{row['id']:03d}.json")
        crec = _load(run_dir / "choose" / f"{row['id']:03d}.json")
        d = (drec and drec["result"].get("parsed")) or {}
        ch = (crec and crec["result"].get("parsed")) or {}
        brand = d.get("brand")
        own = own_references(d) if d else []
        ranked = gather(d) if d else []
        code = [c["reference"] for c in ranked]
        shown = [clean_ref(brand, s) for s in crec["candidates"]] if crec else code[:MAX_CANDIDATES]
        picks = []
        for i in ch.get("ranking") or []:        # two numbers can be the same reference written twice
            if 1 <= i <= len(shown) and vt.canon(brand or "", shown[i - 1]) not in {vt.canon(brand or "", p) for p in picks}:
                picks.append(shown[i - 1])
        picks = picks[:3]
        if not picks:                           # no choosing call, or it failed: the code order stands
            picks = code[:3]
        if not d or not picks:
            outcome = "not_identified"
        elif ch.get("none_fit"):
            outcome = "not_identified"
        elif ch.get("clear_leader"):
            outcome = "auto_filled"
        else:
            outcome = "choose_one"
        calls = [x["result"] for x in (drec, crec) if x]

        def merged(refs: list[str]) -> list[str]:
            out: list[str] = []
            for r in refs:
                if vt.canon(brand or "", r) not in {vt.canon(brand or "", o) for o in out}:
                    out.append(r)
            return out

        own_then_picks = merged(own[:1] + picks + own[1:])            # the model's own first, then the choosing call's
        switched = merged(picks[:1] + own[:1] + picks[1:]) if ch.get("clear_leader") else own_then_picks
        same_first = bool(own and picks) and vt.canon(brand or "", own[0]) == vt.canon(brand or "", picks[0])
        shown_first_is_own = bool(own and shown) and vt.canon(brand or "", own[0]) == vt.canon(brand or "", shown[0])
        items.append({
            "combo3": _any(row, brand, own_then_picks[:3]), "combo4": _any(row, brand, own_then_picks[:4]),
            "combo5": _any(row, brand, own_then_picks[:5]),
            "switch1": _right(row, brand, switched[0] if switched else None), "same_first": same_first,
            "own_first_moved": bool(crec) and bool(own) and not shown_first_is_own,
            "row": row["id"], "brand": row["brand"], "truth": row["reference_number"], "desc": d, "choice": ch,
            "brand_ok": brand == row["brand"], "own": own, "picks": picks, "outcome": outcome, "n": len(ranked),
            "shown": len(shown), "chose": bool(crec and ch),
            # A choosing call is still owed only when none was made. One that was made and failed is a
            # result: the code order stands for that photo.
            "pending": bool(d) and len(ranked) >= 2 and crec is None,
            "choose_failed": bool(crec) and not ch,
            "own1": _right(row, brand, own[0] if own else None), "own3": _any(row, brand, own),
            "code1": _right(row, brand, code[0] if code else None), "code3": _any(row, brand, code[:3]),
            "pick1": _right(row, brand, picks[0] if picks else None), "pick3": _any(row, brand, picks),
            "avail": _any(row, brand, code), "shown_has": _any(row, brand, shown),
            "cost": sum(x.get("cost_usd") or 0 for x in calls), "time": sum(x.get("elapsed_s") or 0 for x in calls),
            "cost_describe": (drec or {}).get("result", {}).get("cost_usd") or 0,
            "cost_choose": (crec or {}).get("result", {}).get("cost_usd") or 0,
            "error": next((x["error"] for x in calls if x.get("error")), None),
            "tidied": any(x.get("tidied") for x in calls),
            "searches": len(photo_queries(d)) if d else 0,
        })
    return items


# ── report ───────────────────────────────────────────────────────────────────

def _n(items, test) -> int:
    return sum(1 for i in items if test(i))


def to_markdown(meta: dict, rows: list[dict], items: list[dict], pending: list[dict]) -> str:
    n = len(items)
    kind = bench_report.run_kind(n + len(pending), meta["dataset_size"])
    spec = meta["spec"]
    setting = ", ".join(f"{k} {v}" for k, v in spec.items() if k not in ("provider", "model")) or "default settings"
    L = [f"# Pipeline study: describe, search, choose - {kind['label']}", "",
         "Stage 1 of Serper idea 1 (`FINDINGS.md`, section 4). Rebuilt by `pipeline_study.py report` from saved "
         "answers and saved searches.", "",
         f"Run `{meta['run_id']}`, model `{meta['model_name']}` (`{spec['model']}`, {setting}). {n} photos. Each "
         "photo gets one describing call, three web searches, a ranking in code, and one choosing call that "
         f"sees the photo again with up to {MAX_CANDIDATES} candidates.", ""]
    if kind["kind"] == "test":
        L += ["> TEST RUN on part of the photos. Its numbers are not comparable with a full run.", ""]
    if pending:
        L += [f"> **INCOMPLETE.** The run stopped before the choosing call for {len(pending)} photos (rows "
              f"{', '.join(str(i['row']) for i in pending)}). Every table below covers the {n} photos that have "
              "both calls. Continue the run with `--resume` to finish it.", ""]

    def row(label, key):
        L.append(f"| {label} | {_n(items, lambda i: i[key][0])} | {_n(items, lambda i: i[key][1])} |")

    L += ["## Result", "", f"Out of {n} photos.", "",
          "| | Exact reference | Also counting accepted look-alikes |", "|---|---:|---:|"]
    row("Model's own first reference (the baseline, from the same call)", "own1")
    row("**Pipeline's first choice**", "pick1")
    row("Model's own references, up to three, contain it", "own3")
    row("**Pipeline's choices, up to three, contain it**", "pick3")
    row("It was among the candidates shown to the choosing call", "shown_has")
    row("It was available at all: own references or any search (the ceiling)", "avail")
    L += ["", "Code ranking alone, with no second call:", "",
          "| | Exact reference | Also counting accepted look-alikes |", "|---|---:|---:|"]
    row("First in the code order", "code1")
    row("Within the first three of the code order", "code3")

    gained = [i for i in items if i["pick1"][0] and not i["own1"][0]]
    lost = [i for i in items if i["own1"][0] and not i["pick1"][0]]
    L += ["", "## What the pipeline changed", "",
          f"First choice against the model's own first reference: **{len(gained)} gained, {len(lost)} lost**.", ""]
    for title, group in (("Gained: own first reference wrong, pipeline's first choice right", gained),
                         ("Lost: own first reference right, pipeline's first choice wrong", lost)):
        L += [f"### {title} ({len(group)})", ""]
        if not group:
            L += ["None.", ""]
            continue
        L += ["| Row | Expected | Model's own first | Pipeline chose | Reason the model gave |", "|---:|---|---|---|---|"]
        for i in group:
            L.append(f"| {i['row']} | `{i['truth']}` | `{i['own'][0] if i['own'] else '-'}` | "
                     f"`{i['picks'][0] if i['picks'] else '-'}` | {_cut(i['choice'].get('reason', ''), 150).replace('|', '/')} |")
        L.append("")

    L += ["## Outcomes", "",
          "What the seller would see. `auto_filled`: the choosing call said one candidate stands clear. "
          "`choose_one`: it ranked up to three and the seller taps. `not_identified`: it said none fit, or "
          "nothing was read from the photo.", "",
          "| Outcome | Photos | Right reference delivered | Share right |", "|---|---:|---:|---:|"]
    for outcome, key, label in (("auto_filled", "pick1", "filled in is right"),
                                ("choose_one", "pick3", "is among the options"),
                                ("not_identified", "avail", "was available all the same")):
        group = [i for i in items if i["outcome"] == outcome]
        good = _n(group, lambda i: i[key][0])
        share = f"{100 * good / len(group):.0f}%" if group else "-"
        L.append(f"| `{outcome}` | {len(group)} | {good} ({label}) | {share} |")
    L += ["", "Proposed pass marks in `AUTO_LISTING_SPEC.md`, section 10: `auto_filled` right at least 95 times in "
              "100, `choose_one` options contain the right watch at least 95 times in 100, at least 70% of uploads "
              "`auto_filled`."]

    kept = [i for i in items if i["same_first"]]
    changed = [i for i in items if i["chose"] and not i["same_first"]]
    clear = [i for i in items if i["choice"].get("clear_leader")]
    sure = [i for i in items if (i["desc"].get("confidence") or 0) >= 0.8]
    moved = [i for i in items if i["own_first_moved"] and i["own1"][0]]
    L += ["", "## Worked out after the run", "",
          "These combinations were tried on the saved answers after the results were known. They cost nothing, "
          "and they need a fresh set of photos before they can be trusted.", "",
          "| Way of combining the two calls | First choice right | Right one within the options |", "|---|---:|---:|",
          f"| Model's own references only (no search, no second call) | {_n(items, lambda i: i['own1'][0])} | "
          f"{_n(items, lambda i: i['own3'][0])} of three |",
          f"| The choosing call's ranking as it is | {_n(items, lambda i: i['pick1'][0])} | "
          f"{_n(items, lambda i: i['pick3'][0])} of three |",
          f"| Model's own first reference, then the choosing call's picks | {_n(items, lambda i: i['own1'][0])} | "
          f"{_n(items, lambda i: i['combo3'][0])} of three, {_n(items, lambda i: i['combo4'][0])} of four, "
          f"{_n(items, lambda i: i['combo5'][0])} of five |",
          f"| The same, but the choosing call's pick goes first when it says it has a clear leader | "
          f"{_n(items, lambda i: i['switch1'][0])} | {_n(items, lambda i: i['combo3'][0])} of three |",
          "", "When to trust the first choice:", "",
          "| Signal | Photos | First choice right |", "|---|---:|---:|",
          f"| The choosing call kept the model's own first reference | {len(kept)} | {_n(kept, lambda i: i['pick1'][0])} |",
          f"| The choosing call changed it | {len(changed)} | {_n(changed, lambda i: i['pick1'][0])} "
          f"(the model's own first was right on {_n(changed, lambda i: i['own1'][0])}) |",
          f"| The choosing call said it had a clear leader | {len(clear)} | {_n(clear, lambda i: i['pick1'][0])} |",
          f"| Kept the model's own first and said clear leader | {_n(clear, lambda i: i['same_first'])} | "
          f"{_n(clear, lambda i: i['same_first'] and i['pick1'][0])} |",
          f"| The describing call's own confidence was 0.8 or more | {len(sure)} | {_n(sure, lambda i: i['own1'][0])} |",
          ""]
    if moved:
        L += [f"On {len(moved)} photos the list shown to the choosing call had the model's own first reference, "
              "which was right, moved down from first place, because the code order held something against it. "
              f"The choosing call still chose right on {_n(moved, lambda i: i['pick1'][0])} of them"
              + (f"; rows {', '.join(str(i['row']) for i in moved if not i['pick1'][0])} are among the lost."
                 if _n(moved, lambda i: not i['pick1'][0]) else ".")]
    else:
        L += ["The list shown to the choosing call never had a right own first reference moved down from first place."]
    if meta.get("notes"):
        L += ["", "Notes on this run:", ""] + [f"- {note}" for note in meta["notes"]]

    seen = [i for i in items if i["desc"]]
    gt = {r["id"]: r for r in rows}
    case = {"stainless-steel": "stainless-steel", "yellow-gold": "gold", "rose-gold": "gold", "white-gold": "gold",
            "platinum": "platinum", "titanium": "titanium", "ceramic": "ceramic", "bronze": "bronze"}
    L += ["", "## The describing call", "",
          f"Fields the answer key can check, out of {len(seen)} answered photos.", "",
          "| Field | Right |", "|---|---:|",
          f"| Brand | {_n(seen, lambda i: i['brand_ok'])} |",
          f"| Movement | {_n(seen, lambda i: i['desc'].get('movement') == gt[i['row']]['movement'])} |",
          f"| Case material (gold colours counted as gold; two-tone has no match in the key) | "
          f"{_n(seen, lambda i: case.get(i['desc'].get('case_material')) == gt[i['row']]['case_material'])} |",
          f"| Bracelet material | {_n(seen, lambda i: i['desc'].get('bracelet_material') == gt[i['row']]['bracelet_material'])} |",
          "", "Dial colour, bezel, size and complications have no column in the answer key and are not scored.", "",
          f"References given per photo: one {_n(seen, lambda i: len(i['own']) == 1)}, two "
          f"{_n(seen, lambda i: len(i['own']) == 2)}, three {_n(seen, lambda i: len(i['own']) == 3)}."]

    times = sorted(i["time"] for i in items)
    L += ["", "## Cost and speed", "", "| | Per photo |", "|---|---:|",
          f"| Describing call | ${statistics.mean(i['cost_describe'] for i in items):.4f} |",
          f"| Choosing call | ${statistics.mean(i['cost_choose'] for i in items):.4f} |",
          f"| Both calls | ${statistics.mean(i['cost'] for i in items):.4f} |",
          f"| Web searches | {statistics.mean(i['searches'] for i in items):.1f} |",
          f"| Candidates found (median) | {statistics.median(i['n'] for i in items):g} |",
          f"| Model time, both calls, median | {statistics.median(times):.1f}s |",
          f"| Model time, slowest 5% start at | {times[max(0, -(-95 * len(times) // 100) - 1)]:.1f}s |",
          "", f"Model cost of the run: ${sum(i['cost'] for i in items):.2f}. Search time is not included; the "
              "searches were made in a batch between the two calls. A search costs $0.001 at Serper's smallest "
              "paid pack (reported price).",
          f"Photos where the describing call gave no answer: {_n(items, lambda i: not i['desc'])}; they count as "
          f"wrong everywhere. Photos where the choosing call gave no answer: {_n(items, lambda i: i['choose_failed'])}; "
          "for those the code order stands. Photos with no choosing call because there were fewer than two "
          f"candidates: {_n(items, lambda i: bool(i['desc']) and not i['chose'] and not i['choose_failed'])}. "
          f"Photos where an answer broke the format and was tidied to fit: {_n(items, lambda i: i['tidied'])}."]

    L += ["", "## By brand", "", "| Brand | Photos | Own first reference | Pipeline's first choice | Pipeline's three |",
          "|---|---:|---:|---:|---:|"]
    for b in schema.BRANDS:
        mine = [i for i in items if i["brand"] == b]
        if mine:
            L.append(f"| {b} | {len(mine)} | {_n(mine, lambda i: i['own1'][0])} | {_n(mine, lambda i: i['pick1'][0])} | "
                     f"{_n(mine, lambda i: i['pick3'][0])} |")

    wrong = [i for i in items if not i["pick1"][0]]
    L += ["", f"## Every photo where the first choice is wrong ({len(wrong)})", "",
          "| Row | Expected | Pipeline's choices | Outcome | Right one in its three | Shown to it | Available |",
          "|---:|---|---|---|---|---|---|"]
    yes = lambda v: "yes" if v else "no"  # noqa: E731
    for i in wrong:
        L.append(f"| {i['row']} | `{i['truth']}` | " + ", ".join(f"`{p}`" for p in i["picks"]) +
                 f" | {i['outcome']} | {yes(i['pick3'][0])} | {yes(i['shown_has'][0])} | {yes(i['avail'][0])} |")

    L += ["", "## Limits", "",
          "- One pass on 100 photos taken from the web. A seller's own photo is harder.",
          "- The comparison inside this run is fair: both numbers come from the same describing call. Comparing "
          "with other runs is not, because the prompt is different.",
          "- The search forms and the ranking rule were fixed before the run and not tuned on these photos.",
          "- Google's results change; the saved searches are the record.",
          "- WatchBase data read through search results is not licensed for use in a product.",
          "- `clear_leader` is the model's own judgement. It decides between `auto_filled` and `choose_one`."]
    return "\n".join(L) + "\n"


def write_report(run_dir: Path, rows: list[dict]) -> list[dict]:
    meta = json.loads((run_dir / "meta.json").read_text(encoding="utf-8"))
    by_id = {r["id"]: r for r in rows}
    selected = [by_id[i] for i in meta["rows"]]
    every = analyse(run_dir, selected)
    pending = [i for i in every if i["pending"]]
    items = [i for i in every if not i["pending"]]
    text = to_markdown(meta, selected, items, pending)
    (run_dir / "report.md").write_text(text, encoding="utf-8")
    n = len(items)
    print(f"\n{meta['model_name']} - {n} photos" + (f" ({len(pending)} more still need the choosing call)" if pending else ""))
    print(f"  Own first reference right     {_n(items, lambda i: i['own1'][0]):>3}")
    print(f"  Pipeline's first choice right {_n(items, lambda i: i['pick1'][0]):>3}")
    print(f"  Own three contain it          {_n(items, lambda i: i['own3'][0]):>3}")
    print(f"  Pipeline's three contain it   {_n(items, lambda i: i['pick3'][0]):>3}")
    print(f"  Available at all (ceiling)    {_n(items, lambda i: i['avail'][0]):>3}")
    print(f"  Model cost ${sum(i['cost'] for i in every):.2f}")
    print(f"Report: {bench._rel(run_dir / 'report.md')}")
    return items


def write_index(rows: list[dict]) -> None:
    """results/PIPELINE_STUDY.md: one line per run, side by side. The detail is in each run's report.md."""
    by_id = {r["id"]: r for r in rows}
    L = ["# Pipeline study: describe, search, choose", "",
         "Stage 1 of Serper idea 1 (`FINDINGS.md`, section 4). Rebuilt by `pipeline_study.py report` from saved "
         "answers and saved searches.", "",
         "Each photo gets one describing call (brand, model line, what is visible, up to three references), three "
         f"web searches, a ranking in code, and one choosing call that sees the photo again with up to "
         f"{MAX_CANDIDATES} candidates. \"Own\" is what the model gave in the describing call; \"pipeline\" is what "
         "comes out at the end. Both are from the same run, so they can be compared.", "",
         "| Run | Model | Photos with both calls | Own first reference right | Pipeline's first choice right | "
         "Own three contain it | Pipeline's three contain it | Available at all | Model cost per photo |",
         "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    notes = []
    for meta_path in sorted(PIPE_DIR.glob("*/meta.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        every = analyse(meta_path.parent, [by_id[i] for i in meta["rows"] if i in by_id])
        items = [i for i in every if not i["pending"]]
        if not items:
            continue
        kind = bench_report.run_kind(len(every), meta["dataset_size"])
        n = len(items)

        def cell(key: str) -> str:
            return f"{_n(items, lambda i: i[key][0])} ({100 * _n(items, lambda i: i[key][0]) / n:.0f}%)"

        L.append(f"| [{meta['run_id']}](pipeline/{meta['run_id']}/report.md) | {meta['model_name']} | {n} of {len(every)} | "
                 f"{cell('own1')} | {cell('pick1')} | {cell('own3')} | {cell('pick3')} | {cell('avail')} | "
                 f"${statistics.mean(i['cost'] for i in items):.4f} |")
        if kind["kind"] == "test":
            notes.append(f"`{meta['run_id']}` is a test run on part of the photos.")
        if len(items) < len(every):
            notes.append(f"`{meta['run_id']}` is incomplete: {len(every) - len(items)} photos have no choosing call. "
                         "Its counts cover only the photos that have both calls.")
        notes += [f"`{meta['run_id']}`: {note}" for note in meta.get("notes", [])]
    L += ["", "Counts are exact references. Runs with different numbers of photos compare by the percentages."]
    if notes:
        L += ["", "## Read before comparing", ""] + [f"- {n}" for n in notes]
    L += ["", "## What the columns mean", "",
          "- **Own first reference right**: the first reference of the describing call. This is the model with "
          "no search and no second call.",
          "- **Pipeline's first choice right**: the first reference after search and the choosing call.",
          "- **Own three / pipeline's three contain it**: the right reference is among up to three options, which "
          "is what a seller would be shown to tap.",
          "- **Available at all**: the right reference was among the model's own references or anything the "
          "searches returned. Nothing can do better than this without another source."]
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"Comparison of runs: {bench._rel(OUT)}")


# ── commands ─────────────────────────────────────────────────────────────────

def cmd_run(args) -> int:
    cfg, _ = bench.load_config(required=True)
    rows, problems = bench.load_rows()
    errors, _warnings = bench.validate(rows, problems)
    if errors:
        print("\n".join(errors[:20]))
        return 1
    if args.resume:
        run_dir = Path(args.resume).resolve()
        meta = json.loads((run_dir / "meta.json").read_text(encoding="utf-8"))
        by_id = {r["id"]: r for r in rows}
        selected, name, spec = [by_id[i] for i in meta["rows"]], meta["model_name"], meta["spec"]
    else:
        name = args.model
        spec = dict(getattr(cfg, "MODELS", {}).get(name) or {})
        if spec.get("provider") not in PROVIDERS:
            print(f"{name} is not an Anthropic or DeepSeek model in config.py. This script calls only those two.")
            return 1
        selected = bench.select_rows(rows, args.ids, args.limit)
    if not bench.api_key(cfg, spec["provider"]):
        print(f"No API key for {spec['provider']} in config.py or the environment.")
        return 1
    kind = bench_report.run_kind(len(selected), len(rows))
    print(f"{kind['label']}: {name}, two model calls and up to three searches per photo.")
    print(f"Estimated cost: roughly ${ROUGH_COST[spec['provider']] * len(selected):.2f} for the model and up to "
          f"{3 * len(selected)} Serper credits (fewer where a search is already saved).")
    if not args.yes:
        if not sys.stdin.isatty():
            print("Not interactive - pass --yes to confirm spending.")
            return 1
        if input("Run it? [y/N] ").strip().lower() not in ("y", "yes"):
            print("Cancelled - nothing was spent.")
            return 1
    if not args.resume:
        now = datetime.now(timezone.utc)
        run_id = now.strftime("%Y-%m-%d_%H%M%S") + kind["suffix"]
        run_dir = PIPE_DIR / run_id
        run_dir.mkdir(parents=True)
        meta = {"run_id": run_id, "started_at": now.isoformat(), "model_name": name, "spec": spec,
                "rows": [r["id"] for r in selected], "dataset_size": len(rows),
                "describe_prompt": DESCRIBE_PROMPT, "choose_prompt": CHOOSE_PROMPT,
                "max_candidates": MAX_CANDIDATES, "results_per_search": NUM,
                "csv_sha256": bench._sha256(bench.CSV_PATH.read_bytes())}
        (run_dir / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Run folder: {bench._rel(run_dir)}\n")

    images = {}
    for r in selected:
        mime, _ = bench.check_image(r)
        images[r["id"]] = (base64.standard_b64encode((bench.IMAGES_DIR / r["image_file"]).read_bytes()).decode(), mime)
    client = make_client(cfg, spec)
    try:
        step_describe(run_dir, selected, client, spec, images, args.concurrency)
        step_search(run_dir, selected)
        step_choose(run_dir, selected, client, spec, images, args.concurrency)
    except (Fatal, vt.Fatal) as e:
        print(f"\nStopped: {e}\nWhat was saved is kept. Fix the cause and continue with --resume {bench._rel(run_dir)}")
        return 1
    write_report(run_dir, rows)
    write_index(rows)
    return 0


def cmd_report(args) -> int:
    rows, problems = bench.load_rows()
    if problems:
        print("\n".join(problems))
        return 1
    runs = [Path(args.run_dir).resolve()] if args.run_dir else sorted(p.parent for p in PIPE_DIR.glob("*/meta.json"))
    if not runs:
        print("No run under results/pipeline/.")
        return 1
    for run_dir in runs:
        write_report(run_dir, rows)
    write_index(rows)
    return 0


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description="Describe, search, choose: the auto-listing pipeline on the photos.")
    sub = parser.add_subparsers(dest="command", required=True)
    sp = sub.add_parser("run", help="call the model and Serper, then report")
    sp.add_argument("--model", default=DEFAULT_MODEL, help="an Anthropic or DeepSeek model name from config.py")
    sp.add_argument("--limit", type=int, help="only N photos, spread across brands")
    sp.add_argument("--ids", help="only these row ids, e.g. 3,17,42")
    sp.add_argument("--resume", help="continue this run folder; only what is missing is done")
    sp.add_argument("--concurrency", type=int, default=4)
    sp.add_argument("--yes", action="store_true", help="skip the confirmation question")
    sp.set_defaults(func=cmd_run)
    sp = sub.add_parser("report", help="rebuild the report from saved answers and searches; no calls")
    sp.add_argument("run_dir", nargs="?", help="results/pipeline/<run_id>; default: every run")
    sp.set_defaults(func=cmd_report)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
