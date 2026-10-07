"""Can a web search supply the right reference as a candidate? (Serper idea 1, stage 0)

    python search_study.py plan            # what would be searched and what is already saved, $0
    python search_study.py run --yes       # make the searches not yet saved, then write the report
    python search_study.py report          # rebuild results/SEARCH_STUDY.md from saved searches, $0

No model is called. The saved answers of earlier benchmark runs are replayed:
the brand, model line and reference a model gave for a photo are turned into
searches, and the references read out of the results are the candidates. The
question is how often the right reference is among them.

Searches, one Serper credit each (Google results, top 10):

    ref    site:watchbase.com <brand> <answer-key reference>   is the watch on WatchBase at all
    web    <brand> <answer-key reference>                      the same on the open web, only where WatchBase has no page
    line   site:watchbase.com <brand> <model line the model gave>
    guess  site:watchbase.com <brand> <model part of the model's wrong reference>
    open   <brand> <model line> <metal> <strap> reference      open web

Every response is saved under results/serper/ and never fetched twice. That
folder is not in git: it holds third-party search results.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from urllib.parse import urlparse

import bench
import detail_study
import schema
import scoring
import vision_test as vt

ENDPOINT = "https://google.serper.dev/search"
ACCOUNT = "https://google.serper.dev/account"
KEY_NAME = "SERPER_API_KEY"
SERPER_DIR = bench.RESULTS_DIR / "serper"
CACHE_DIR = SERPER_DIR / "cache"
OUT = bench.RESULTS_DIR / "SEARCH_STUDY.md"
GL, HL = "us", "en"

DEFAULT_MODELS = ["claude-opus-5-5", "claude-sonnet-5-5-nothink", "gpt-6.1-sol-low", "deepseek-flash"]
STALE_ROWS = {12}                       # photo replaced after every saved answer was made
KINDS = ["ref", "web", "line", "guess", "open"]
CANDIDATE_KINDS = ["line", "guess", "open"]
KIND_LABEL = {"line": "WatchBase, by the model line the model gave",
              "guess": "WatchBase, by the model part of the model's reference",
              "open": "Open web, by model line, metal and strap"}
SEARCH_NAME = {"Tag Heuer": "TAG Heuer"}
METAL = {"stainless-steel": "steel", "gold": "gold", "platinum": "platinum", "titanium": "titanium",
         "ceramic": "ceramic", "bronze": "bronze"}
STRAP = {"metal": "bracelet", "leather": "leather strap", "rubber": "rubber strap", "fabric": "fabric strap",
         "nylon": "nylon strap"}


# ── building the searches ────────────────────────────────────────────────────

def watchbase_notation(brand: str, ref: str | None) -> str:
    """A reference as WatchBase writes it, where that differs from the brand: IW5017-01, JLC without the Q,
    Rolex without a catalogue suffix."""
    s = (ref or "").strip()
    if brand == "IWC":
        m = re.fullmatch(r"(IW\d{4})-?(\d{2})", s.upper())
        return f"{m.group(1)}-{m.group(2)}" if m else s
    if brand == "Jaeger-LeCoultre":
        return re.sub(r"^(JL)?Q(?=\d)", "", s, flags=re.I)
    if brand == "Rolex":
        return re.sub(r"-\d{4}$", "", re.sub(r"^M(?=\d)", "", s, flags=re.I))
    return s


def model_part(brand: str, ref: str | None) -> str | None:
    """The part of a reference its siblings share, when the brand writes it as a separate, searchable token.
    None for brands whose reference is one unbroken token (Rolex, Breitling, Cartier, JLC, TAG Heuer)."""
    s = (ref or "").strip().upper()
    if brand in ("Vacheron Constantin", "Patek Philippe") and "-" in s:
        return s.rsplit("-", 1)[0]                       # 4600E/000A-B487 -> 4600E/000A, 5711/1A-010 -> 5711/1A
    if brand == "Audemars Piguet" and "." in s:
        return s.split(".", 1)[0]                        # 15202ST.OO.1240ST.01 -> 15202ST
    if brand == "Omega" and len(s.split(".")) == 6:
        return ".".join(s.split(".")[:4])                # 220.10.41.21.03.001 -> 220.10.41.21
    if brand == "IWC":
        m = re.match(r"IW\d{4}", s)
        return m.group(0) if m else None                 # IW500705 -> IW5007
    return None


def clean_line(brand: str, family: str | None) -> str:
    """The model line as the model wrote it, without the brand name and without brackets or quotes."""
    s = re.sub(r"[()\[\]\"'“”‘’]", " ", family or "")
    for alias in sorted([brand.upper(), *vt.ALIASES.get(brand, [])], key=len, reverse=True):
        s = re.sub(re.escape(alias), " ", s, flags=re.I)
    return " ".join(s.split())[:90]


def name_of(brand: str) -> str:
    return SEARCH_NAME.get(brand, brand)


def ref_query(row: dict) -> str:
    return f"site:watchbase.com {name_of(row['brand'])} {watchbase_notation(row['brand'], row['reference_number'])}"


def web_query(row: dict) -> str:
    return f"{name_of(row['brand'])} {row['reference_number']}"


def answer_queries(answer: dict, row: dict) -> dict[str, str]:
    """The candidate searches one saved answer leads to. No guess search when the guess is already right:
    it would be the `ref` search of that row."""
    brand = answer.get("brand")
    if brand not in schema.BRANDS:
        return {}
    out, name, line = {}, name_of(brand), clean_line(brand, answer.get("model_family"))
    if line:
        out["line"] = f"site:watchbase.com {name} {line}"
        extras = [METAL.get(answer.get("case_material"), ""), STRAP.get(answer.get("bracelet_material"), "")]
        out["open"] = " ".join(f"{name} {line} {' '.join(extras)} reference".split())
    guess = answer.get("reference_number")
    if guess and not scoring.match(row["brand"], row["reference_number"], row["also_accept"], guess)[0]:
        out["guess"] = f"site:watchbase.com {name} {model_part(brand, guess) or watchbase_notation(brand, guess)}"
    return out


# ── saved searches ───────────────────────────────────────────────────────────

def cache_path(text: str, num: int):
    key = json.dumps({"q": text, "num": num, "gl": GL, "hl": HL}, sort_keys=True)
    return CACHE_DIR / f"{hashlib.sha1(key.encode()).hexdigest()[:20]}.json"


def saved(text: str, num: int) -> dict | None:
    path = cache_path(text, num)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def results_of(text: str | None, num: int) -> list[dict] | None:
    """The organic results of a saved search; None when it has not been made."""
    if not text:
        return None
    rec = saved(text, num)
    return None if rec is None else (rec["response"].get("organic") or [])


def credits_spent() -> tuple[int, int]:
    """(searches saved, credits they cost) across the whole cache."""
    n = credits = 0
    for path in CACHE_DIR.glob("*.json"):
        rec = json.loads(path.read_text(encoding="utf-8"))
        n += 1
        credits += int(rec["response"].get("credits") or 1)
    return n, credits


# ── reading references out of results ────────────────────────────────────────

def read_candidates(results: list[dict], brand: str) -> list[dict]:
    """References of this brand found in the results, best placed first. A reference in a title or link
    is the page's own watch; one in a snippet is only mentioned there, so it ranks after."""
    found: dict[str, dict] = {}
    for pos, res in enumerate(results, 1):
        link = res.get("link") or ""
        domain = urlparse(link).netloc.removeprefix("www.")
        for where, text in (("title", res.get("title") or ""), ("link", link), ("snippet", res.get("snippet") or "")):
            for b, raw in vt.find_references(text, {brand}):
                if b != brand:
                    continue
                canon = vt.canon(brand, raw)
                rank = (1 if where == "snippet" else 0, pos)
                cur = found.get(canon)
                if cur is None:
                    cur = found[canon] = {"canon": canon, "reference": raw, "rank": rank, "domains": set(),
                                          "title": None}
                cur["domains"].add(domain)
                if rank <= cur["rank"]:
                    cur["rank"] = rank
                    if where != "snippet":
                        cur["title"] = res.get("title")
    return sorted(found.values(), key=lambda c: c["rank"])


def merge(lists: dict[str, list[dict]]) -> list[dict]:
    """One list from several searches: references more searches agree on first, then by placing."""
    merged: dict[str, dict] = {}
    for kind in CANDIDATE_KINDS:
        for c in lists.get(kind) or []:
            m = merged.setdefault(c["canon"], {"canon": c["canon"], "reference": c["reference"], "kinds": [],
                                               "rank": c["rank"], "order": len(merged)})
            m["kinds"].append(kind)
            m["rank"] = min(m["rank"], c["rank"])
    return sorted(merged.values(), key=lambda m: (-len(m["kinds"]), m["rank"], m["order"]))


def hit(row: dict, brand: str, cands: list[dict]) -> tuple[bool, bool]:
    """(right reference is among them, right reference or an accepted look-alike is)."""
    if brand != row["brand"]:
        return False, False
    hits = [vt.same_reference(row["brand"], row["reference_number"], row["also_accept"], c["reference"]) for c in cands]
    return any(h[0] for h in hits), any(h[1] for h in hits)


# ── the study ────────────────────────────────────────────────────────────────

def load_answers(models: list[str]) -> dict[str, dict]:
    latest = {}
    for run in detail_study.load_runs():            # oldest first, so the last full run of a model wins
        latest[run["model"]] = run
    missing = [m for m in models if m not in latest]
    if missing:
        raise SystemExit(f"No full run saved for: {', '.join(missing)}")
    return {m: latest[m] for m in models}


def coverage(rows: list[dict], num: int) -> dict[int, dict]:
    """Per answer-key row: is its reference on WatchBase, and if not, on the open web."""
    out = {}
    for row in rows:
        item = {"wb": None, "wb_listed": None, "wb_title": None, "web": None, "web_domains": []}
        res = results_of(ref_query(row), num)
        if res is not None:
            mine = [c for c in read_candidates(res, row["brand"])
                    if vt.canon(row["brand"], c["reference"]) == vt.canon(row["brand"], row["reference_number"])]
            own_page = [c for c in mine if c["rank"][0] == 0]
            item["wb"] = bool(own_page)              # its own page is in the results
            item["wb_listed"] = bool(mine)           # or another WatchBase page lists it
            item["wb_title"] = own_page[0]["title"] if own_page else None
        res = results_of(web_query(row), num)
        if res is not None:
            mine = [c for c in read_candidates(res, row["brand"])
                    if vt.canon(row["brand"], c["reference"]) == vt.canon(row["brand"], row["reference_number"])]
            item["web"] = bool(mine)
            item["web_domains"] = sorted(mine[0]["domains"]) if mine else []
        out[row["id"]] = item
    return out


def wanted(kind: str, rows: list[dict], answers: dict[str, dict], num: int) -> list[str] | None:
    """Every distinct search of one kind, in a stable order. None for `web` until every `ref` search is saved."""
    if kind == "ref":
        return list(dict.fromkeys(ref_query(r) for r in rows))
    if kind == "web":
        cov = coverage(rows, num)
        if any(cov[r["id"]]["wb"] is None for r in rows):
            return None
        return list(dict.fromkeys(web_query(r) for r in rows if not cov[r["id"]]["wb"]))
    texts = []
    for run in answers.values():
        for row in rows:
            if row["id"] in STALE_ROWS:
                continue
            text = answer_queries(run["answers"].get(row["id"]) or {}, row).get(kind)
            if text:
                texts.append(text)
    return list(dict.fromkeys(texts))


def study(rows: list[dict], answers: dict[str, dict], num: int) -> dict:
    cov = coverage(rows, num)
    out = {"coverage": cov, "models": {}}
    for model, run in answers.items():
        items = []
        for row in rows:
            if row["id"] in STALE_ROWS:
                continue
            a = run["answers"].get(row["id"]) or {}
            brand = a.get("brand")
            own, own_len, _ = scoring.match(row["brand"], row["reference_number"], row["also_accept"],
                                            a.get("reference_number"))
            queries = answer_queries(a, row)
            lists, pending = {}, []
            for kind in CANDIDATE_KINDS:
                if kind == "guess" and own:              # the guess is the answer-key reference: reuse `ref`
                    res = results_of(ref_query(row), num)
                elif kind in queries:
                    res = results_of(queries[kind], num)
                else:
                    continue
                if res is None:
                    pending.append(kind)
                else:
                    lists[kind] = read_candidates(res, brand) if brand in schema.BRANDS else []
            merged = merge(lists)
            found = {k: hit(row, brand, v) for k, v in lists.items()}
            any_exact, any_len = hit(row, brand, merged)
            rank = next((i for i, c in enumerate(merged, 1)
                         if brand == row["brand"] and vt.canon(brand, c["reference"]) == vt.canon(brand, row["reference_number"])), None)
            own_canon = vt.canon(brand, a.get("reference_number")) if brand in schema.BRANDS else ""
            rest = [c for c in merged if c["canon"] != own_canon]
            with_own = 1 if own else next((i + (2 if own_canon else 1) for i, c in enumerate(rest)
                                           if brand == row["brand"] and c["canon"] == vt.canon(brand, row["reference_number"])), None)
            items.append({"row": row["id"], "brand": row["brand"], "truth": row["reference_number"], "with_own": with_own,
                          "answer": a.get("reference_number") or "-", "brand_ok": brand == row["brand"],
                          "own": own, "own_len": own_len, "found": found, "any": any_exact, "any_len": any_len,
                          "sizes": {k: len(v) for k, v in lists.items()}, "size": len(merged), "rank": rank,
                          "pending": pending, "on_watchbase": cov[row["id"]]["wb_listed"]})
        out["models"][model] = items
    return out


# ── report ───────────────────────────────────────────────────────────────────

def _n(items, test) -> int:
    return sum(1 for i in items if test(i))


def to_markdown(rows: list[dict], answers: dict[str, dict], s: dict, num: int) -> str:
    models = list(answers)
    cov = s["coverage"]
    searches, credits = credits_spent()
    done = [r for r in rows if cov[r["id"]]["wb"] is not None]
    on_wb = [r for r in done if cov[r["id"]]["wb"]]
    L = ["# Search study: can a web search supply the right reference?", "",
         "Stage 0 of Serper idea 1 (`FINDINGS.md`, section 4). Rebuilt by `search_study.py report` from saved "
         "searches.", "",
         f"No model was called. The saved answers of earlier full runs were replayed: for each photo, the brand, "
         f"model line and reference the model gave were turned into Google searches through Serper (US, English, "
         f"top {num} results), and the references read out of the results are the candidates. "
         f"{searches} searches are saved; they cost {credits} Serper credits.", "",
         "## Is the watch on WatchBase at all?", "",
         "One search per answer-key reference, limited to watchbase.com.", ""]
    if done:
        listed = [r for r in done if cov[r["id"]]["wb_listed"]]
        L += [f"**The watch's own page came back for {len(on_wb)} of the {len(done)} answer-key references.** "
              f"{len(listed) - len(on_wb)} more are named on another WatchBase page (a family or movement page), "
              f"so WatchBase has them. {len(done) - len(listed)} are not on WatchBase.", "",
              "| Brand | References | Own page found | Listed elsewhere only | Not on WatchBase |",
              "|---|---:|---:|---|---|"]
        for b in schema.BRANDS:
            mine = [r for r in done if r["brand"] == b]
            only = [r for r in mine if cov[r["id"]]["wb_listed"] and not cov[r["id"]]["wb"]]
            miss = [r for r in mine if not cov[r["id"]]["wb_listed"]]
            L.append(f"| {b} | {len(mine)} | {sum(1 for r in mine if cov[r['id']]['wb'])} | "
                     + ", ".join(f"`{r['reference_number']}`" for r in only) + " | "
                     + ", ".join(f"`{r['reference_number']}`" for r in miss) + " |")
        missing = [r for r in done if not cov[r["id"]]["wb"]]
        checked = [r for r in missing if cov[r["id"]]["web"] is not None]
        if checked:
            on_web = [r for r in checked if cov[r["id"]]["web"]]
            L += ["", f"The {len(checked)} references with no page of their own were then searched on the open web "
                      f"(brand and reference, no site limit): **{len(on_web)} of {len(checked)} found.**", "",
                  "| Row | Reference | On the open web | Sites |", "|---:|---|---|---|"]
            for r in checked:
                c = cov[r["id"]]
                L.append(f"| {r['id']} | `{r['reference_number']}` | {'yes' if c['web'] else 'no'} | "
                         f"{', '.join(c['web_domains'][:4])} |")
    else:
        L.append("Not run yet.")

    n_rows = len(s["models"][models[0]]) if models else 0
    L += ["", "## Is the right reference among the candidates?", "",
          f"{n_rows} photos (row 12 is left out: its photo was replaced after the answers were saved). "
          "\"Among the candidates\" means the exact reference, after normalising notation.", "",
          "| | " + " | ".join(models) + " |", "|---|" + "---:|" * len(models)]

    def line(label, test):
        L.append(f"| {label} | " + " | ".join(str(_n(s["models"][m], test)) for m in models) + " |")

    line("The model's own answer is right (the baseline)", lambda i: i["own"])
    for kind in CANDIDATE_KINDS:
        line(f"Right reference among candidates: {KIND_LABEL[kind]}", lambda i, k=kind: i["found"].get(k, (False, False))[0])
    line("Right reference among candidates: any of the three searches", lambda i: i["any"])
    line("**Own answer or any search** (the most a chooser could reach)", lambda i: i["own"] or i["any"])
    line("Same, also counting accepted look-alikes", lambda i: i["own_len"] or i["any_len"])
    def has(i, *kinds):
        return any(i["found"].get(k, (False, False))[0] for k in kinds)

    L += ["", "What each source adds to the model's own answer:", "",
          "| Right reference is the model's own answer, or among the candidates from | " + " | ".join(models) + " |",
          "|---|" + "---:|" * len(models)]
    line("nothing else (own answer only)", lambda i: i["own"])
    line("WatchBase by model line", lambda i: i["own"] or has(i, "line"))
    line("WatchBase by model line and by the model part of the reference", lambda i: i["own"] or has(i, "line", "guess"))
    line("the open web only", lambda i: i["own"] or has(i, "open"))
    line("all three", lambda i: i["own"] or i["any"])
    pending = {m: _n(s["models"][m], lambda i: i["pending"]) for m in models}
    if any(pending.values()):
        L += ["", "Not every search has been made yet. Photos with a search still missing: "
              + ", ".join(f"{m} {n}" for m, n in pending.items()) + "."]
    L += ["", "The guess search was made only for wrong guesses. For a right guess the result of the "
              "answer-key search above is used, which is the same search."]

    L += ["", "## On the photos the model got wrong", "",
          "| | " + " | ".join(models) + " |", "|---|" + "---:|" * len(models)]
    line("Photos the model got wrong", lambda i: not i["own"])
    for kind in CANDIDATE_KINDS:
        line(f"Search has the right reference: {KIND_LABEL[kind]}",
             lambda i, k=kind: not i["own"] and i["found"].get(k, (False, False))[0])
    line("**Search has the right reference: any**", lambda i: not i["own"] and i["any"])
    line("No search has it", lambda i: not i["own"] and not i["any"])
    line("... because the model named the wrong brand or none", lambda i: not i["own"] and not i["any"] and not i["brand_ok"])
    line("... because WatchBase does not have the watch", lambda i: not i["own"] and not i["any"] and i["brand_ok"]
         and i["on_watchbase"] is False)
    line("... although WatchBase has the watch", lambda i: not i["own"] and not i["any"] and i["brand_ok"]
         and i["on_watchbase"])

    L += ["", "## How long is the candidate list?", "",
          "All three searches merged. Order: the model's own answer first, then references that more searches "
          "agree on, then by position in the results. Apart from the model's own answer, this order uses nothing "
          "the model saw in the photo; stage 1 would rank by that.", "",
          "| | " + " | ".join(models) + " |", "|---|" + "---:|" * len(models)]

    def stat(label, fn):
        L.append(f"| {label} | " + " | ".join(fn(s["models"][m]) for m in models) + " |")

    stat("Median number of candidates per photo", lambda it: f"{statistics.median([i['size'] for i in it]):g}")
    stat("Largest", lambda it: str(max(i["size"] for i in it)))
    stat("Photos with no candidate at all", lambda it: str(_n(it, lambda i: i["size"] == 0)))
    for k in (3, 5, 10):
        stat(f"Model's own answer first, then the list: right reference within the first {k}",
             lambda it, k=k: str(_n(it, lambda i: i["with_own"] and i["with_own"] <= k)))

    L += ["", "## By brand", "",
          "Each cell: the model's own answer is right / own answer or any search.", "",
          "| Brand | Photos | " + " | ".join(models) + " |", "|---|---:|" + "---:|" * len(models)]
    for b in schema.BRANDS:
        n = _n(s["models"][models[0]], lambda i: i["brand"] == b)
        cells = []
        for m in models:
            mine = [i for i in s["models"][m] if i["brand"] == b]
            cells.append(f"{_n(mine, lambda i: i['own'])} / {_n(mine, lambda i: i['own'] or i['any'])}")
        L.append(f"| {b} | {n} | " + " | ".join(cells) + " |")

    for m in models:
        wrong = [i for i in s["models"][m] if not i["own"]]
        L += ["", f"## Every photo {m} got wrong ({len(wrong)})", "",
              "| Row | Expected | Model's answer | Found by | Place in list | List size | On WatchBase |",
              "|---:|---|---|---|---:|---:|---|"]
        for i in wrong:
            by = ", ".join(k for k in CANDIDATE_KINDS if i["found"].get(k, (False, False))[0]) or (
                "look-alike only" if i["any_len"] else "-")
            wb = {True: "yes", False: "no", None: "?"}[i["on_watchbase"]]
            L.append(f"| {i['row']} | `{i['truth']}` | `{i['answer']}` | {by} | {i['rank'] or ''} | {i['size']} | {wb} |")

    L += ["", "## Limits", "",
          "- Google's results change. These are the results on the day each search was made; the saved "
          "responses are the record.",
          f"- Only the top {num} results of each search were read.",
          "- The model line and the attributes come from runs made with the benchmark prompt, which asks for one "
          "reference and no dial colour. A prompt written for this pipeline may do better or worse.",
          "- References are read from titles, links and snippets with one pattern per brand, for the ten "
          "benchmark brands only.",
          "- A candidate list that contains the right reference is not an answer. Picking from it is stage 1.",
          "- WatchBase data read through search results is not licensed for use in a product."]
    return "\n".join(L) + "\n"


def write_report(rows: list[dict], answers: dict[str, dict], num: int) -> dict:
    s = study(rows, answers, num)
    OUT.write_text(to_markdown(rows, answers, s, num), encoding="utf-8")
    return s


def print_headline(answers: dict[str, dict], s: dict) -> None:
    for m in answers:
        it = s["models"][m]
        print(f"{m}: own answer right {_n(it, lambda i: i['own'])}, any search has it {_n(it, lambda i: i['any'])}, "
              f"own or search {_n(it, lambda i: i['own'] or i['any'])} of {len(it)}")
    print(f"Report: {bench._rel(OUT)}")


# ── calling Serper ───────────────────────────────────────────────────────────

def api_key() -> str:
    cfg, _ = bench.load_config(required=True)
    return getattr(cfg, KEY_NAME, "") or os.environ.get(KEY_NAME, "")


def balance(key: str) -> str:
    import requests
    try:
        r = requests.get(ACCOUNT, headers={"X-API-KEY": key}, timeout=20)
        return str(r.json().get("balance", "unknown")) if r.status_code == 200 else "unknown"
    except (requests.RequestException, ValueError):
        return "unknown"


def call_serper(key: str, text: str, num: int, timeout: int = 30) -> dict:
    import requests
    body = {"q": text, "gl": GL, "hl": HL, "num": num}
    for attempt in range(5):
        try:
            r = requests.post(ENDPOINT, headers={"X-API-KEY": key, "Content-Type": "application/json"},
                              json=body, timeout=timeout)
        except requests.RequestException as e:
            if attempt == 4:
                return {"error": f"NETWORK: {type(e).__name__}"}
            time.sleep(2 ** attempt)
            continue
        if r.status_code == 200:
            return r.json()
        if r.status_code in (400, 401, 403):
            raise vt.Fatal(f"HTTP {r.status_code}: {r.text[:200]}")
        if r.status_code in (429, 500, 502, 503, 504) and attempt < 4:
            time.sleep(2 ** attempt)
            continue
        return {"error": f"HTTP {r.status_code}: {r.text[:200]}"}
    return {"error": "no response"}


def fetch(key: str, kind: str, texts: list[str], num: int, concurrency: int) -> tuple[int, int, int]:
    """Make the searches and save them. Returns (saved, credits, failed)."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    saved_n = credits = failed = 0

    def work(text: str) -> tuple[str, dict]:
        return text, call_serper(key, text, num)

    def record(text: str, resp: dict) -> None:
        nonlocal saved_n, credits, failed
        if resp.get("error"):
            failed += 1
            print(f"    failed: {resp['error'][:80]} | {text[:70]}", flush=True)
            return
        cache_path(text, num).write_text(json.dumps(
            {"kind": kind, "q": text, "num": num, "fetched_at": datetime.now(timezone.utc).isoformat(),
             "response": resp}, indent=1, ensure_ascii=False), encoding="utf-8")
        saved_n += 1
        credits += int(resp.get("credits") or 1)

    if not texts:
        return 0, 0, 0
    record(*work(texts[0]))                  # alone first: a bad key stops the run after one call
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        for fut in as_completed([pool.submit(work, t) for t in texts[1:]]):
            record(*fut.result())
    return saved_n, credits, failed


# ── commands ─────────────────────────────────────────────────────────────────

def _setup(args):
    rows, problems = bench.load_rows()
    if problems:
        raise SystemExit("\n".join(problems))
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    return rows, load_answers(models)


def _plan(rows, answers, kinds, num) -> dict[str, list[str] | None]:
    plan = {}
    for kind in kinds:
        texts = wanted(kind, rows, answers, num)
        plan[kind] = None if texts is None else [t for t in texts if saved(t, num) is None]
        total = "?" if texts is None else len(texts)
        new = "after `ref`" if texts is None else len(plan[kind])
        print(f"  {kind:<6} searches {total:>4}   not yet saved {new}")
    return plan


def cmd_plan(args) -> int:
    rows, answers = _setup(args)
    print(f"Models: {', '.join(answers)}. One credit per search. No call is made.\n")
    plan = _plan(rows, answers, KINDS, args.num)
    known = sum(len(v) for v in plan.values() if v is not None)
    print(f"\nNew searches: {known}" + (" plus the `web` searches" if plan.get("web") is None else ""))
    n, credits = credits_spent() if CACHE_DIR.exists() else (0, 0)
    print(f"Already saved: {n} searches, {credits} credits.")
    return 0


def cmd_run(args) -> int:
    rows, answers = _setup(args)
    key = api_key()
    if not key:
        print(f"No {KEY_NAME}. Put a key from serper.dev in config.py as {KEY_NAME} = \"...\".")
        return 1
    kinds = [k.strip() for k in args.kinds.split(",") if k.strip()]
    unknown = [k for k in kinds if k not in KINDS]
    if unknown:
        print(f"Unknown kind: {', '.join(unknown)}. Choose from {', '.join(KINDS)}.")
        return 1
    print(f"Models: {', '.join(answers)}. One Serper credit per search, at most {args.max_new} new searches.\n")
    _plan(rows, answers, kinds, args.num)
    if not args.yes:
        if not sys.stdin.isatty():
            print("Not interactive - pass --yes to confirm.")
            return 1
        if input("\nMake these searches? [y/N] ").strip().lower() not in ("y", "yes"):
            print("Cancelled - nothing was sent.")
            return 1
    print(f"\nCredits left before: {balance(key)}")
    budget, total_credits = args.max_new, 0
    try:
        for kind in [k for k in KINDS if k in kinds]:
            texts = wanted(kind, rows, answers, args.num)
            if texts is None:
                print(f"  {kind}: skipped, the `ref` searches are not complete")
                continue
            todo = [t for t in texts if saved(t, args.num) is None][:budget]
            if not todo:
                continue
            done, credits, failed = fetch(key, kind, todo, args.num, args.concurrency)
            budget -= len(todo)
            total_credits += credits
            print(f"  {kind}: {done} saved, {credits} credits" + (f", {failed} failed" if failed else ""), flush=True)
            if budget <= 0:
                print("  Stopped at the limit set by --max-new.")
                break
    except vt.Fatal as e:
        print(f"\nStopped: {e}\nCheck the key and the credit balance, then run again.")
        return 1
    print(f"Credits used in this run: {total_credits}. Credits left: {balance(key)}\n")
    print_headline(answers, write_report(rows, answers, args.num))
    return 0


def cmd_report(args) -> int:
    rows, answers = _setup(args)
    print_headline(answers, write_report(rows, answers, args.num))
    return 0


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description="Replay saved answers through web search (Serper).")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, func, text in (("plan", cmd_plan, "count the searches; no calls"),
                             ("run", cmd_run, "make the searches not yet saved, then report"),
                             ("report", cmd_report, "rebuild the report from saved searches; no calls")):
        sp = sub.add_parser(name, help=text)
        sp.add_argument("--models", default=",".join(DEFAULT_MODELS), help="model names from saved full runs")
        sp.add_argument("--num", type=int, default=10, help="results per search")
        if name == "run":
            sp.add_argument("--kinds", default=",".join(KINDS), help=f"which searches: {', '.join(KINDS)}")
            sp.add_argument("--max-new", type=int, default=700, help="never make more new searches than this")
            sp.add_argument("--concurrency", type=int, default=3)
            sp.add_argument("--yes", action="store_true", help="skip the confirmation question")
        sp.set_defaults(func=func)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
