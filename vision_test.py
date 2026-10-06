"""Google Cloud Vision web detection as a source of candidate references.

    python vision_test.py run --limit 3                  # smallest real call
    python vision_test.py run                            # every image, as it is
    python vision_test.py run --variant altered          # photos changed so they are not copies of web images
    python vision_test.py score results/vision/<run_id>  # re-score saved responses, $0

Answers one question: when Google is shown a watch photo, how often does its
answer contain the right reference number?

Web detection finds pages that already host the same image, so the result
depends on whether the photo is on the web. The dataset photos came from the
web; a seller's own photo did not. The report therefore splits every number by
"Google found a copy of this photo" / "it did not", and `--variant altered`
re-runs the test on rotated, warped, cropped copies that Google should no
longer recognise as copies.
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import os
import random
import re
import statistics
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import bench
import scoring

ENDPOINT = "https://vision.googleapis.com/v1/images:annotate"
VISION_DIR = bench.RESULTS_DIR / "vision"
PRICE_PER_IMAGE = 0.0035          # USD after the first 1,000 units per month
FREE_UNITS_PER_MONTH = 1000
PRICE_VERIFIED = "2026-10-06"     # https://cloud.google.com/vision/pricing
KEY_NAME = "GOOGLE_VISION_API_KEY"

# ── reading references out of text ───────────────────────────────────────────

ALIASES = {
    "Rolex": ["ROLEX"],
    "Omega": ["OMEGA"],
    "Patek Philippe": ["PATEK"],
    "Audemars Piguet": ["AUDEMARS", "PIGUET"],
    "Tag Heuer": ["TAG HEUER", "TAGHEUER", "TAG-HEUER", "HEUER"],
    "Breitling": ["BREITLING"],
    "Cartier": ["CARTIER"],
    "IWC": ["IWC"],
    "Jaeger-LeCoultre": ["JAEGER", "LECOULTRE", "JLC"],
    "Vacheron Constantin": ["VACHERON"],
}

_B = r"(?<![A-Z0-9])"      # not preceded by a letter or digit
_E = r"(?![A-Z0-9])"       # not followed by one
_ROLEX_SUFFIX = r"(?:LN|LV|LB|BLRO|BLNR|CHNR|GRNR|VTNR|NR|RBR|TBR|SABR|SARU|SATS|DB)"

# (brand, pattern on UPPERCASED text, where the brand name must appear for the match to count)
#   "none"  - the format is distinctive enough on its own
#   "any"   - the brand must be named somewhere in Google's answer for this image
#   "same"  - the brand must be named in the same title, label or URL
PATTERNS = [
    ("Rolex", re.compile(_B + r"M?(\d{6})\s?(" + _ROLEX_SUFFIX + r")(?:-\d{4})?" + _E), "any"),
    ("Rolex", re.compile(_B + r"M?(\d{6})()(?:-\d{4})?" + _E), "same"),
    ("Omega", re.compile(r"(?<!\d)(\d{3})\.(\d{2})\.(\d{2})\.(\d{2})\.(\d{2})\.(\d{3})(?!\d)"), "none"),
    ("Omega", re.compile(r"(?<!\d)(\d{3})[\s-]?(\d{2})[\s-]?(\d{2})[\s-]?(\d{2})[\s-]?(\d{2})[\s-]?(\d{3})(?!\d)"), "same"),
    ("Patek Philippe", re.compile(_B + r"(\d{4})(?:[/-](\d{1,4}))?([A-Z]{1,2})-(\d{3})" + _E), "any"),
    ("Audemars Piguet", re.compile(_B + r"(\d{5}[A-Z]{2})[.\s-]?([A-Z0-9]{2})[.\s-]?([A-Z0-9]{6})[.\s-]?(\d{2})" + _E), "none"),
    ("Tag Heuer", re.compile(_B + r"([A-Z]{3}(?=[A-Z0-9]{0,3}\d)[A-Z0-9]{4})\.([A-Z]{2}\d{4})" + _E), "none"),
    ("Tag Heuer", re.compile(_B + r"([A-Z]{3}(?=[A-Z0-9]{0,3}\d)[A-Z0-9]{4})[\s-]?([A-Z]{2}\d{4})" + _E), "any"),
    ("Breitling", re.compile(_B + r"([A-Z]{1,2}\d{2}[0-9A-Z]{5,7}[A-Z]\d[A-Z]\d)" + _E), "none"),
    ("Cartier", re.compile(_B + r"(?:CR)?(W(?=[A-Z0-9]*\d[A-Z0-9]*\d)[A-Z0-9]{7})" + _E), "any"),
    ("IWC", re.compile(_B + r"(IW\d{4})-?(\d{2})" + _E), "none"),
    ("Jaeger-LeCoultre", re.compile(_B + r"Q(\d{6}[0-9A-Z])" + _E), "any"),
    ("Jaeger-LeCoultre", re.compile(_B + r"(\d{6}[0-9A-Z])" + _E), "same"),
    ("Vacheron Constantin", re.compile(_B + r"(\d{4,5}[A-Z]?)[/-]([0-9A-Z]{4})-([A-Z]?\d{3,4})" + _E), "any"),
]

_TAGS = re.compile(r"<[^>]+>")
_NON_ALNUM = re.compile(r"[^A-Z0-9]")


def canon(brand: str, ref: str | None) -> str:
    """scoring.canonical plus two notations seen on the web: JLC without its Q, Cartier with a CR prefix."""
    s = scoring.canonical(brand, ref)
    if brand == "Jaeger-LeCoultre":
        s = re.sub(r"^Q(?=\d)", "", s)
    elif brand == "Cartier":
        s = re.sub(r"^CR(?=W)", "", s)
    return s


def same_reference(brand: str, truth: str, also: list[str], candidate: str) -> tuple[bool, bool]:
    """(exact, exact-or-accepted-look-alike). The second uses the answer key's also_accept and the strap rule."""
    got = canon(brand, candidate)
    if not got:
        return False, False
    if got == canon(brand, truth):
        return True, True
    if got in {canon(brand, a) for a in also}:
        return False, True
    return False, scoring.match(brand, truth, also, candidate)[1]


def names_brand(text_upper: str, brand: str) -> bool:
    return any(a in text_upper for a in ALIASES[brand])


def pools(web: dict) -> dict[str, list[str]]:
    """The text Google returned, grouped by where it came from."""
    pages = web.get("pagesWithMatchingImages") or []
    urls = [p.get("url", "") for p in pages]
    for key in ("fullMatchingImages", "partialMatchingImages", "visuallySimilarImages"):
        urls += [i.get("url", "") for i in web.get(key) or []]
    for p in pages:
        for key in ("fullMatchingImages", "partialMatchingImages"):
            urls += [i.get("url", "") for i in p.get(key) or []]
    return {
        "titles": [_TAGS.sub("", p.get("pageTitle") or "") for p in pages if p.get("pageTitle")],
        "entities": [e.get("description") or "" for e in web.get("webEntities") or [] if e.get("description")],
        "labels": [b.get("label") or "" for b in web.get("bestGuessLabels") or [] if b.get("label")],
        "urls": [u for u in urls if u],
    }


def find_references(text: str, named_anywhere: set[str]) -> list[tuple[str, str]]:
    """(brand, reference as written) for every reference-shaped token in one piece of text."""
    upper = text.upper()
    found, taken = [], []
    for brand, pattern, needs in PATTERNS:
        if needs == "any" and brand not in named_anywhere:
            continue
        if needs == "same" and not names_brand(upper, brand):
            continue
        for m in pattern.finditer(upper):
            if any(m.start() < e and s < m.end() for s, e in taken):
                continue                      # a more specific pattern already read this text
            taken.append((m.start(), m.end()))
            if brand == "Rolex":
                raw = m.group(1) + (m.group(2) or "")
            elif brand == "Omega":
                raw = ".".join(m.groups())
            elif brand == "Patek Philippe":
                raw = m.group(1) + (f"/{m.group(2)}" if m.group(2) else "") + f"{m.group(3)}-{m.group(4)}"
            elif brand == "Audemars Piguet":
                raw = ".".join(m.groups())
            elif brand == "Tag Heuer":
                raw = f"{m.group(1)}.{m.group(2)}"
            elif brand == "IWC":
                raw = m.group(1) + m.group(2)
            elif brand == "Jaeger-LeCoultre":
                raw = "Q" + m.group(1)
            elif brand == "Vacheron Constantin":
                raw = f"{m.group(1)}/{m.group(2)}-{m.group(3)}"
            else:
                raw = m.group(1)
            found.append((brand, raw))
    return found


def candidates(pool: dict[str, list[str]], sources=("titles", "entities", "labels")) -> list[dict]:
    """References found in the given text sources, most often mentioned first."""
    everything = " ".join(t for texts in pool.values() for t in texts).upper()
    named = {b for b in ALIASES if names_brand(everything, b)}
    counts: Counter = Counter()
    first_seen: dict[tuple[str, str], tuple[int, str]] = {}
    order = 0
    for source in sources:
        for text in pool.get(source, []):
            seen_here = set()
            for brand, raw in find_references(text, named):
                key = (brand, canon(brand, raw))
                if key in seen_here:
                    continue
                seen_here.add(key)
                counts[key] += 1
                if key not in first_seen:
                    first_seen[key] = (order, raw)
                    order += 1
    ranked = sorted(counts, key=lambda k: (-counts[k], first_seen[k][0]))
    return [{"brand": b, "reference": first_seen[(b, c)][1], "mentions": counts[(b, c)]} for b, c in ranked]


def contains(texts: list[str], brand: str, refs: list[str]) -> bool:
    """Is any of these references written anywhere in the text, whatever the punctuation?"""
    flat = _NON_ALNUM.sub("", " ".join(texts).upper())
    return any(c and c in flat for c in (canon(brand, r) for r in refs))


# ── one image ────────────────────────────────────────────────────────────────

def analyse(row: dict, response: dict) -> dict:
    out = {"row_id": row["id"], "image_file": row["image_file"], "brand": row["brand"],
           "truth": row["reference_number"], "error": None}
    if response.get("error"):
        err = response["error"]
        out["error"] = f"{err.get('status') or err.get('code')}: {err.get('message', '')}"[:300]
        return out
    web = response.get("webDetection") or {}
    pool = pools(web)
    pages = web.get("pagesWithMatchingImages") or []
    full = len(web.get("fullMatchingImages") or []) + sum(len(p.get("fullMatchingImages") or []) for p in pages)
    partial = len(web.get("partialMatchingImages") or []) + sum(len(p.get("partialMatchingImages") or []) for p in pages)
    truth, also, brand = row["reference_number"], row["also_accept"], row["brand"]
    all_text = pool["titles"] + pool["entities"] + pool["labels"] + pool["urls"]
    found = candidates(pool)
    hits = [same_reference(brand, truth, also, c["reference"]) if c["brand"] == brand else (False, False)
            for c in found]
    out.update({
        "copy": "exact" if full else ("partial" if partial or pages else "none"),
        "full_matches": full, "partial_matches": partial, "pages": len(pages),
        "similar": len(web.get("visuallySimilarImages") or []),
        "brand_named": names_brand(" ".join(pool["titles"] + pool["entities"] + pool["labels"]).upper(), brand),
        "present_titles": contains(pool["titles"], brand, [truth]),
        "present_labels": contains(pool["entities"] + pool["labels"], brand, [truth]),
        "present_urls": contains(pool["urls"], brand, [truth]),
        "present_anywhere": contains(all_text, brand, [truth]),
        "present_anywhere_lenient": contains(all_text, brand, [truth, *also]),
        "candidates": found[:5],
        "top1": bool(hits[:1]) and hits[0][0],
        "top3": any(h[0] for h in hits[:3]),
        "top3_lenient": any(h[1] for h in hits[:3]),
        "best_guess": "; ".join(pool["labels"])[:120],
        "entities": pool["entities"][:4],
    })
    return out


# ── summary and report ───────────────────────────────────────────────────────

MEASURES = [
    ("present_anywhere", "Right reference appears anywhere in Google's answer"),
    ("present_titles", "... in a page title"),
    ("present_labels", "... in Google's own labels (entities, best guess)"),
    ("present_urls", "... only in a URL"),
    ("top3", "Right reference among the top 3 extracted"),
    ("top1", "Right reference is the first one extracted"),
    ("top3_lenient", "Top 3, also counting accepted look-alikes"),
    ("brand_named", "Brand named"),
]


def _count(items: list[dict], key: str) -> int:
    if key == "present_urls":
        return sum(i["present_anywhere"] and not i["present_titles"] and not i["present_labels"] for i in items)
    return sum(bool(i[key]) for i in items)


def summarise(items: list[dict]) -> dict:
    ok = [i for i in items if not i["error"]]
    groups = {"all": ok, "exact": [i for i in ok if i["copy"] == "exact"],
              "partial": [i for i in ok if i["copy"] == "partial"], "none": [i for i in ok if i["copy"] == "none"]}
    table = {g: {"n": len(rows), **{m[0]: _count(rows, m[0]) for m in MEASURES}} for g, rows in groups.items()}
    brands = {}
    for b in bench.BRANDS:
        rows = [i for i in ok if i["brand"] == b]
        if rows:
            brands[b] = {"n": len(rows), "present_anywhere": _count(rows, "present_anywhere"),
                         "top3": _count(rows, "top3"), "exact_copies": sum(i["copy"] == "exact" for i in rows)}
    return {"images": len(items), "errors": len(items) - len(ok), "table": table, "brands": brands,
            "median_pages": statistics.median([i["pages"] for i in ok]) if ok else 0}


def _cell(v: int, n: int) -> str:
    return f"{v} of {n}" if n else "-"


def to_markdown(meta: dict, items: list[dict], s: dict) -> str:
    t = s["table"]
    variant = meta["variant"]
    out = [f"# Google Vision web detection - {variant} photos - {meta['kind_label']}", "",
           f"Run {meta['run_id']}, {meta['started_at'][:16].replace('T', ' ')} UTC. {s['images']} images, "
           f"one WEB_DETECTION call each (maxResults {meta['max_results']}). Errors: {s['errors']}.", ""]
    if variant == "original":
        out += ["> These photos came from the web, so Google can find the pages they were taken from. A seller's "
                "own photo is on no page. Read the **No copy found** column, or the `altered` run, as the guide "
                "to real uploads.", ""]
    else:
        out += ["> Each photo was rotated, warped, cropped and re-coloured before it was sent, to stand in for a "
                "photo that is not on the web. This is an approximation of a seller's own photo, not the real "
                "thing. The **Exact copy found** column shows how many Google still recognised.", ""]
    out += ["| | All | Exact copy found | Partial copy only | No copy found |", "|---|---:|---:|---:|---:|",
            f"| Images | {t['all']['n']} | {t['exact']['n']} | {t['partial']['n']} | {t['none']['n']} |"]
    for key, label in [(m[0], m[1]) for m in MEASURES]:
        out.append(f"| {label} | " + " | ".join(_cell(t[g][key], t[g]["n"]) for g in ("all", "exact", "partial", "none")) + " |")
    out += ["",
            "- **Exact copy found**: Google reported at least one identical image on the web.",
            "- **Partial copy only**: no identical image, but a page with a cropped or edited version.",
            "- **No copy found**: no matching page at all. Only Google's own labels are returned.",
            "- **Top 3 extracted**: reference-shaped text read from page titles and labels, most mentioned first. "
            "This is the candidate list the pipeline would pass on.",
            "- Notation is ignored when comparing (dots, dashes, Rolex `-0001`, JLC `Q`, Cartier `CR`).",
            "", "## By brand", "",
            "| Brand | Images | Exact copies found | Right reference anywhere | In top 3 |", "|---|---:|---:|---:|---:|"]
    for b, v in s["brands"].items():
        out.append(f"| {b} | {v['n']} | {v['exact_copies']} | {v['present_anywhere']} | {v['top3']} |")
    out += ["", "## Every image", "",
            "| # | Expected | Copy | Pages | Top 3 extracted | In top 3 | Google's best guess |",
            "|---:|---|---|---:|---|:-:|---|"]
    for i in items:
        if i["error"]:
            out.append(f"| {i['row_id']} | `{i['truth']}` | error | | {i['error'][:80]} | | |")
            continue
        top = ", ".join(f"`{c['reference']}`" for c in i["candidates"][:3]) or "none"
        mark = "yes" if i["top3"] else ("look-alike" if i["top3_lenient"] else "no")
        out.append(f"| {i['row_id']} | `{i['truth']}` | {i['copy']} | {i['pages']} | {top} | {mark} | "
                   f"{i['best_guess'].replace('|', '/')} |")
    return "\n".join(out) + "\n"


def write_report(run_dir: Path, meta: dict, rows: list[dict]) -> dict:
    by_id = {r["id"]: r for r in rows}
    items = []
    for rid in meta["rows"]:
        path = run_dir / "responses" / f"{rid:03d}.json"
        response = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {
            "error": {"status": "MISSING", "message": "no saved response"}}
        items.append(analyse(by_id[rid], response))
    s = summarise(items)
    (run_dir / "report.md").write_text(to_markdown(meta, items, s), encoding="utf-8")
    (run_dir / "report.json").write_text(json.dumps({"meta": meta, "summary": s, "items": items}, indent=2,
                                                    ensure_ascii=False), encoding="utf-8")
    return s


def print_summary(s: dict, run_dir: Path) -> None:
    t = s["table"]
    print(f"\n{'':<52}{'ALL':>10}{'EXACT COPY':>12}{'PARTIAL':>10}{'NO COPY':>10}")
    print(f"{'Images':<52}{t['all']['n']:>10}{t['exact']['n']:>12}{t['partial']['n']:>10}{t['none']['n']:>10}")
    for key, label in [(m[0], m[1]) for m in MEASURES]:
        print(f"{label[:51]:<52}" + "".join(
            f"{_cell(t[g][key], t[g]['n']):>{w}}" for g, w in (("all", 10), ("exact", 12), ("partial", 10), ("none", 10))))
    if s["errors"]:
        print(f"Errors: {s['errors']}")
    print(f"\nReport:        {bench._rel(run_dir / 'report.md')}")
    print(f"Raw responses: {bench._rel(run_dir / 'responses')}")


# ── altered copies ───────────────────────────────────────────────────────────

def _solve(a: list[list[float]], b: list[float]) -> list[float]:
    n = len(b)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(m[r][col]))
        m[col], m[pivot] = m[pivot], m[col]
        for r in range(n):
            if r != col:
                f = m[r][col] / m[col][col]
                m[r] = [x - f * y for x, y in zip(m[r], m[col])]
    return [m[i][n] / m[i][i] for i in range(n)]


def _perspective(src: list[tuple[float, float]], dst: list[tuple[float, float]]) -> list[float]:
    """Coefficients for PIL's PERSPECTIVE transform mapping output corners (dst) back to input corners (src)."""
    a, b = [], []
    for (x, y), (u, v) in zip(dst, src):
        a.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.append(u)
        a.append([0, 0, 0, x, y, 1, -v * x, -v * y]); b.append(v)
    return _solve(a, b)


def altered_copy(path: Path, seed: int) -> bytes:
    """The same watch, no longer the same picture: rotated, warped, cropped, re-coloured, re-compressed.
    Never mirrored, which would reverse the text on the dial."""
    from PIL import Image, ImageEnhance, ImageFilter
    rng = random.Random(seed)
    im = Image.open(path).convert("RGB")
    im.thumbnail((1600, 1600))
    w, h = im.size
    j = lambda frac: rng.uniform(0.02, frac)  # noqa: E731
    src = [(w * j(0.07), h * j(0.07)), (w * (1 - j(0.07)), h * j(0.07)),
           (w * (1 - j(0.07)), h * (1 - j(0.07))), (w * j(0.07), h * (1 - j(0.07)))]
    dst = [(0, 0), (w, 0), (w, h), (0, h)]
    im = im.transform((w, h), Image.PERSPECTIVE, _perspective(src, dst), Image.BICUBIC)
    im = im.rotate(rng.choice([-1, 1]) * rng.uniform(5, 9), resample=Image.BICUBIC, expand=False,
                   fillcolor=im.getpixel((2, 2)))
    cx, cy = w * rng.uniform(0.04, 0.08), h * rng.uniform(0.04, 0.08)
    im = im.crop((int(cx), int(cy), int(w - cx), int(h - cy)))
    im = ImageEnhance.Brightness(im).enhance(rng.uniform(0.88, 1.12))
    im = ImageEnhance.Contrast(im).enhance(rng.uniform(0.9, 1.12))
    im = ImageEnhance.Color(im).enhance(rng.uniform(0.85, 1.1))
    im = im.filter(ImageFilter.GaussianBlur(0.7))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=84)
    return buf.getvalue()


# ── calling the API ──────────────────────────────────────────────────────────

class Fatal(Exception):
    """An error that will repeat for every image (bad key, API switched off, billing)."""


def call_vision(key: str, image: bytes, max_results: int, timeout: int = 60) -> dict:
    import requests
    body = {"requests": [{"image": {"content": base64.standard_b64encode(image).decode()},
                          "features": [{"type": "WEB_DETECTION", "maxResults": max_results}]}]}
    for attempt in range(4):
        try:
            r = requests.post(ENDPOINT, headers={"X-goog-api-key": key}, json=body, timeout=timeout)
        except requests.RequestException as e:
            if attempt == 3:
                return {"error": {"status": "NETWORK", "message": str(e)[:300]}}
            time.sleep(2 ** attempt)
            continue
        if r.status_code == 200:
            responses = r.json().get("responses") or [{}]
            return responses[0]
        try:
            err = r.json().get("error", {})
        except ValueError:
            err = {"message": r.text[:300]}
        err.setdefault("status", f"HTTP {r.status_code}")
        if r.status_code in (400, 401, 403):
            raise Fatal(f"{err.get('status')}: {err.get('message', '')}")
        if r.status_code in (429, 500, 502, 503, 504) and attempt < 3:
            time.sleep(2 ** attempt)
            continue
        return {"error": err}
    return {"error": {"status": "UNKNOWN", "message": "no response"}}


# ── commands ─────────────────────────────────────────────────────────────────

def cmd_run(args) -> int:
    cfg, _ = bench.load_config(required=True)
    key = getattr(cfg, KEY_NAME, "") or os.environ.get(KEY_NAME, "")
    if not key:
        print(f"No {KEY_NAME}. Create an API key in a Google Cloud project that has the Cloud Vision API "
              f"enabled, and put it in config.py as {KEY_NAME} = \"...\".")
        return 1
    rows, problems = bench.load_rows()
    errors, _warnings = bench.validate(rows, problems)
    if errors:
        print("\n".join(errors[:20]))
        return 1
    selected = bench.select_rows(rows, args.ids, args.limit)
    full = len(selected) == len(rows)
    kind_label = f"FULL RUN ({len(selected)} images)" if full else f"TEST RUN ({len(selected)} of {len(rows)} images)"
    print(f"{kind_label}: {len(selected)} web detection calls on {args.variant} photos.")
    print(f"Cost: free within the first {FREE_UNITS_PER_MONTH:,} calls of the month, otherwise "
          f"${len(selected) * PRICE_PER_IMAGE:.2f} (price checked {PRICE_VERIFIED}).")
    if not args.yes:
        if not sys.stdin.isatty():
            print("Not interactive - pass --yes to confirm.")
            return 1
        if input("Run it? [y/N] ").strip().lower() not in ("y", "yes"):
            print("Cancelled - nothing was sent.")
            return 1

    now = datetime.now(timezone.utc)
    run_id = now.strftime("%Y-%m-%d_%H%M%S") + f"_{args.variant}" + ("_full" if full else f"_test-{len(selected)}img")
    run_dir = VISION_DIR / run_id
    (run_dir / "responses").mkdir(parents=True)
    if args.variant == "altered":
        (run_dir / "altered").mkdir()
    meta = {"run_id": run_id, "started_at": now.isoformat(), "variant": args.variant, "kind_label": kind_label,
            "max_results": args.max_results, "rows": [r["id"] for r in selected],
            "csv_sha256": bench._sha256(bench.CSV_PATH.read_bytes())}
    (run_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    def work(row: dict) -> tuple[dict, dict]:
        path = bench.IMAGES_DIR / row["image_file"]
        if args.variant == "altered":
            image = altered_copy(path, seed=row["id"])
            (run_dir / "altered" / row["image_file"]).write_bytes(image)
        else:
            image = path.read_bytes()
        return row, call_vision(key, image, args.max_results)

    done = 0

    def record(row: dict, response: dict) -> None:
        nonlocal done
        (run_dir / "responses" / f"{row['id']:03d}.json").write_text(
            json.dumps(response, indent=2, ensure_ascii=False), encoding="utf-8")
        done += 1
        a = analyse(row, response)
        state = f"ERR {a['error'][:60]}" if a["error"] else (
            f"copy:{a['copy']:<8} pages:{a['pages']:<3} top3:{'yes' if a['top3'] else 'no '}")
        print(f"  {done:>3}/{len(selected)}  #{row['id']:<3} {row['reference_number']:<22} {state}", flush=True)

    try:
        # The first image goes alone: a bad key or a disabled API stops the run after one call.
        record(*work(selected[0]))
        with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
            for fut in as_completed([pool.submit(work, r) for r in selected[1:]]):
                record(*fut.result())
    except Fatal as e:
        print(f"\nStopped: {e}\nFix the key or the project settings and run again.")
        return 1
    print_summary(write_report(run_dir, meta, rows), run_dir)
    return 0


def cmd_score(args) -> int:
    run_dir = Path(args.run_dir).resolve()
    meta_path = run_dir / "meta.json"
    if not meta_path.exists():
        print(f"{meta_path} not found - pass a results/vision/<run_id> directory.")
        return 1
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    rows, problems = bench.load_rows()
    if problems:
        print("\n".join(problems))
        return 1
    print_summary(write_report(run_dir, meta, rows), run_dir)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Test Google Cloud Vision web detection on the watch photos.")
    sub = parser.add_subparsers(dest="command", required=True)
    sp = sub.add_parser("run", help="call the API and report")
    sp.add_argument("--variant", choices=["original", "altered"], default="original")
    sp.add_argument("--limit", type=int, help="only N images, spread across brands")
    sp.add_argument("--ids", help="only these row ids, e.g. 3,17,42")
    sp.add_argument("--max-results", type=int, default=30)
    sp.add_argument("--concurrency", type=int, default=4)
    sp.add_argument("--yes", action="store_true", help="skip the confirmation question")
    sp.set_defaults(func=cmd_run)
    sp = sub.add_parser("score", help="re-score saved responses, no API calls")
    sp.add_argument("run_dir", help="results/vision/<run_id>")
    sp.set_defaults(func=cmd_score)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
