"""How reliably does a model fill the watch details from a photo, with no catalog?

    python detail_study.py            # reads saved answers, writes results/DETAIL_STUDY.md, $0

Uses only what the full runs already saved: brand, model line, reference,
movement, case material, bracelet material and the model's confidence. It makes
no API calls. Fields the prompt never asked for (dial colour, case size) cannot
be studied this way.
"""
from __future__ import annotations

import glob
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import bench
import scoring

OUT = bench.RESULTS_DIR / "DETAIL_STUDY.md"
STALE_ROWS = {12}       # photo replaced on 2026-10-05, after every saved answer was made
STRONG = ["claude-opus-5-5", "claude-sonnet-5-5-nothink", "gpt-6.1-sol-low"]
ATTRS = [("movement", "Movement"), ("case_material", "Case material"), ("bracelet_material", "Bracelet material")]

# The model line each answer-key row belongs to: (phrase the answer must contain, phrases it must not).
# Checked in order, so longer names come before the names they contain.
LINES = [
    ("royal oak offshore", []), ("code 11 59", []), ("royal oak", ["offshore"]),
    ("superocean heritage", []), ("superocean", ["heritage"]),
    ("santos dumont", []), ("santos", ["dumont"]),
    ("big pilot", []), ("pilot", ["big pilot"]),
    ("diver 300", []), ("seamaster 300", ["diver"]), ("aqua terra", []), ("planet ocean", []),
    ("master ultra thin", []), ("master control", []),
    ("gmt master", []), ("sea dweller", []), ("yacht master", []), ("oyster perpetual", []),
    ("day date", []), ("datejust", []), ("submariner", []), ("daytona", []), ("explorer", []),
    ("speedmaster", []), ("constellation", []), ("railmaster", []), ("de ville", []),
    ("nautilus", []), ("aquanaut", []), ("calatrava", []), ("annual calendar", []), ("world time", []),
    ("perpetual calendar", []), ("twenty 4", []),
    ("carrera", []), ("monaco", []), ("aquaracer", []), ("formula 1", []), ("link", []), ("autavia", []),
    ("navitimer", []), ("chronomat", []), ("premier", []), ("avenger", []), ("aerospace", []), ("top time", []),
    ("tank", []), ("ballon bleu", []), ("pasha", []), ("panthere", []), ("drive", []), ("calibre", []),
    ("portugieser", []), ("aquatimer", []), ("portofino", []), ("ingenieur", []),
    ("reverso", []), ("polaris", []), ("rendez vous", []),
    ("overseas", []), ("patrimony", []), ("traditionnelle", []), ("fiftysix", []), ("historiques", []),
]


def squash(text: str | None) -> str:
    """Lowercase letters and digits only: 'Santos-Dumont' and 'santos dumont' compare equal."""
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", text.lower())


def line_of(family: str) -> tuple[str, list[str]] | None:
    s = squash(family)
    return next(((p, bad) for p, bad in LINES if squash(p) in s), None)


def line_right(truth_family: str, answer_family: str | None) -> bool | None:
    rule = line_of(truth_family)
    if rule is None:
        return None
    phrase, forbidden = rule
    a = squash(answer_family)
    return squash(phrase) in a and not any(squash(f) in a for f in forbidden)


def pct(a: int, b: int) -> str:
    return f"{100 * a / b:.0f}%" if b else "-"


def load_runs() -> list[dict]:
    """Every full run of every model, oldest first."""
    runs = []
    for meta_path in sorted(glob.glob(str(bench.RAW_DIR / "*_full" / "meta.json"))):
        meta = json.loads(Path(meta_path).read_text(encoding="utf-8"))
        for model in meta["models"]:
            answers = {}
            for f in glob.glob(str(Path(meta_path).parent / model / "*_r0.json")):
                rec = json.loads(Path(f).read_text(encoding="utf-8"))
                answers[rec["row_id"]] = rec["result"].get("parsed") or {}
            runs.append({"run_id": meta["run_id"], "model": model, "answers": answers})
    return runs


def grade(gt: dict, answers: dict) -> dict[int, dict]:
    out = {}
    for rid, g in gt.items():
        a = answers.get(rid) or {}
        ref = scoring.match(g["brand"], g["reference_number"], g["also_accept"], a.get("reference_number"))
        row = {"reference": ref[0], "reference_lenient": ref[1], "brand": a.get("brand") == g["brand"],
               "line": line_right(g["model_family"], a.get("model_family")),
               "confidence": a.get("confidence")}
        for key, _ in ATTRS:
            row[key] = a.get(key) == g[key]
        row["attrs"] = all(row[k] for k, _ in ATTRS)
        row["identity"] = row["brand"] and bool(row["line"]) and row["attrs"]
        out[rid] = row
    return out


def main() -> int:
    rows, problems = bench.load_rows()
    if problems:
        print("\n".join(problems))
        return 1
    gt = {r["id"]: r for r in rows if r["id"] not in STALE_ROWS}
    n = len(gt)
    unmapped = [g["model_family"] for g in gt.values() if line_of(g["model_family"]) is None]
    if unmapped:
        print("No model line rule for:", unmapped)
        return 1
    runs = load_runs()
    latest = {}
    for r in runs:
        latest[r["model"]] = r                      # later runs replace earlier ones
    graded = {m: grade(gt, r["answers"]) for m, r in latest.items()}
    order = sorted(graded, key=lambda m: -sum(v["reference"] for v in graded[m].values()))
    count = lambda m, k: sum(bool(v[k]) for v in graded[m].values())  # noqa: E731

    out = ["# Study: how reliably does a model fill the watch details on its own?", "",
           f"Generated by `detail_study.py` from the saved answers of every full run. No API calls. "
           f"{n} photos: row {', '.join(map(str, sorted(STALE_ROWS)))} is left out because its photo was replaced "
           "after the runs.", "",
           "Each model saw one photo per watch and had no catalog to check against. A field counts as right "
           "only when it equals the answer key; `unknown` counts as wrong.", "",
           "## 1. Accuracy by field", "",
           f"Out of {n} photos, latest full run of each model.", "",
           "| Model | Brand | Model line | Movement | Case material | Bracelet | All three attributes | Reference |",
           "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for m in order:
        out.append(f"| {m} | {count(m, 'brand')} | {count(m, 'line')} | {count(m, 'movement')} | "
                   f"{count(m, 'case_material')} | {count(m, 'bracelet_material')} | {count(m, 'attrs')} | "
                   f"{count(m, 'reference')} |")
    out += ["",
            "- **Model line** is the collection, such as Submariner or Royal Oak Offshore. It counts as right when "
            "the model's wording contains the collection's name and not a different sibling's (for example "
            "\"Royal Oak\" is wrong for a Royal Oak Offshore).",
            "- **Reference** is the exact reference number, for comparison."]

    # 2. listing-level
    out += ["", "## 2. How much of a listing comes out right", "",
            "\"Identity\" means brand, model line and all three attributes together.", "",
            "| Model | Everything right, including the reference | Identity right, reference wrong | "
            "Something in the identity wrong |", "|---|---:|---:|---:|"]
    for m in order:
        g = graded[m].values()
        full = sum(v["identity"] and v["reference"] for v in g)
        partial = sum(v["identity"] and not v["reference"] for v in g)
        out.append(f"| {m} | {full} | {partial} | {n - full - partial} |")
    out += ["", "The middle column is the case the design handles by leaving only the reference empty."]

    # 3. attributes when reference is wrong
    out += ["", "## 3. Do the attributes hold when the reference is wrong?", "",
            "| Model | Reference wrong | Of those: brand right | Model line right | All three attributes right |",
            "|---|---:|---:|---:|---:|"]
    for m in order:
        wrong = [v for v in graded[m].values() if not v["reference"]]
        k = len(wrong)
        out.append(f"| {m} | {k} | {sum(v['brand'] for v in wrong)} | {sum(bool(v['line']) for v in wrong)} | "
                   f"{sum(v['attrs'] for v in wrong)} |")

    # 4. per value
    out += ["", "## 4. Common values against rare ones", "",
            "Most watches in the set are steel, automatic and on a metal bracelet, so a model that always "
            "answered those three would already score well. This table shows each value separately. "
            "Cells are right answers out of the photos with that value.", ""]
    strong = [m for m in STRONG if m in graded]
    for key, label in ATTRS:
        values = Counter(g[key] for g in gt.values())
        top = values.most_common(1)[0]
        out += [f"**{label}.** Always answering `{top[0]}` would score {top[1]} of {n}.", "",
                "| Value in the answer key | Photos | " + " | ".join(strong) + " |",
                "|---|---:|" + "---:|" * len(strong)]
        for value, k in values.most_common():
            ids = [rid for rid, g in gt.items() if g[key] == value]
            out.append(f"| `{value}` | {k} | " + " | ".join(
                str(sum(graded[m][rid][key] for rid in ids)) for m in strong) + " |")
        out.append("")

    # 5. by brand
    out += ["## 5. By brand", "", "All three attributes right, out of the photos for that brand.", "",
            "| Brand | Photos | " + " | ".join(strong) + " |", "|---|---:|" + "---:|" * len(strong)]
    for b in bench.BRANDS:
        ids = [rid for rid, g in gt.items() if g["brand"] == b]
        out.append(f"| {b} | {len(ids)} | " + " | ".join(
            str(sum(graded[m][rid]["attrs"] for rid in ids)) for m in strong) + " |")

    # 6. agreement between the strong models
    out += ["", "## 6. When the strong models agree", "",
            f"Comparing {', '.join(strong)} on the same photo. Agreement could be used as a confidence signal "
            "in place of a model's own confidence number.", "",
            "| Field | All three agree | Right when they agree | They disagree | At least one right when they disagree |",
            "|---|---:|---:|---:|---:|"]
    fields = [("reference", "Reference")] + [(k, lab) for k, lab in ATTRS]
    for key, label in fields:
        agree = right_agree = some_right = 0
        for rid, g in gt.items():
            raw = [latest[m]["answers"].get(rid, {}) for m in strong]
            if key == "reference":
                vals = [scoring.canonical(g["brand"], a.get("reference_number")) for a in raw]
            else:
                vals = [a.get(key) for a in raw]
            rights = [graded[m][rid][key] for m in strong]
            if len(set(vals)) == 1 and vals[0]:
                agree += 1
                right_agree += rights[0]
            else:
                some_right += any(rights)
        out.append(f"| {label} | {agree} | {right_agree} ({pct(right_agree, agree)}) | {n - agree} | "
                   f"{some_right} ({pct(some_right, n - agree)}) |")

    # 7. stability
    repeats = defaultdict(list)
    for r in runs:
        repeats[r["model"]].append(r)
    out += ["", "## 7. Does a model give the same answer twice?", ""]
    twice = {m: rs for m, rs in repeats.items() if len(rs) >= 2}
    if not twice:
        out.append("No model has two full runs, so this cannot be measured yet.")
    for m, rs in twice.items():
        a, b = rs[0], rs[-1]
        ga, gb = grade(gt, a["answers"]), grade(gt, b["answers"])
        out += [f"Only **{m}** has two full runs ({a['run_id']} and {b['run_id']}). "
                "The second run used a larger output limit, so this is an upper bound on the spread, "
                "not a clean repeat.", "",
                "| Field | Same answer in both runs | Right both times | Right once | Wrong both times |",
                "|---|---:|---:|---:|---:|"]
        for key, label in [("reference", "Reference"), ("brand", "Brand")] + [(k, lab) for k, lab in ATTRS]:
            src = "reference_number" if key == "reference" else key
            same = 0
            for rid, g in gt.items():
                va, vb = a["answers"].get(rid, {}).get(src), b["answers"].get(rid, {}).get(src)
                if key == "reference":
                    va, vb = scoring.canonical(g["brand"], va), scoring.canonical(g["brand"], vb)
                same += va == vb and va not in (None, "")
            both = sum(ga[r][key] and gb[r][key] for r in gt)
            once = sum(ga[r][key] != gb[r][key] for r in gt)
            out.append(f"| {label} | {same} | {both} | {once} | {n - both - once} |")
    out += ["", "The strong models have one full run each, so their run-to-run stability is not measured. "
                "`bench.py run --repeats 3` would measure it."]

    # 8. disputed rows
    out += ["", "## 8. Rows where the strong models agree against the answer key", "",
            "When all three give the same different value, the answer key deserves a second look.", "",
            "| Row | Watch | Field | Answer key | All three answered |", "|---:|---|---|---|---|"]
    disputed = 0
    for rid, g in gt.items():
        for key, label in ATTRS:
            vals = {latest[m]["answers"].get(rid, {}).get(key) for m in strong}
            if len(vals) == 1 and (v := next(iter(vals))) and v != g[key]:
                disputed += 1
                out.append(f"| {rid} | {g['brand']} {g['model_family']} | {label} | `{g[key]}` | `{v}` |")
    if not disputed:
        out.append("| | none | | | |")

    out += ["", "## What this study cannot show", "",
            "- **Dial colour and case size.** The prompt never asked for them and the answer key has no such columns.",
            "- **Real seller photos.** These photos came from the web. The app will send five labelled photos "
            "per watch; this study used one.",
            "- **Run-to-run stability of the strong models.** One run each.",
            "- **The answer key's own errors.** Attribute columns were checked less closely than references; "
            "section 8 lists the rows to recheck."]
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out[: out.index("## 2. How much of a listing comes out right")]))
    print(f"\nWrote {bench._rel(OUT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
