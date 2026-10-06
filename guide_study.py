"""Does attaching REFERENCE_FORMATS.md to the prompt change a model's answers?

    python guide_study.py            # reads saved answers, writes results/GUIDE_STUDY.md, $0

Compares every full run of the plain model with every full run of the same model
given the guide (the "guide" option in config.py). It makes no API calls.

The guide prints some answer-key references as examples. On those rows the model
can copy the answer, so every score is also given for the rows the guide does
not print.
"""
from __future__ import annotations

import json
import re
import statistics
import sys
from collections import defaultdict

import bench
import detail_study
import scoring
import vision_test

PLAIN, GUIDED = "deepseek-flash", "deepseek-flash-guide"
GUIDE = bench.ROOT / "REFERENCE_FORMATS.md"
OUT = bench.RESULTS_DIR / "GUIDE_STUDY.md"


def load_runs(model: str, n_rows: int) -> list[dict]:
    """Every full run of `model`, oldest first: {run_id, answers: {row_id: result}}."""
    runs = []
    for meta_path in sorted(bench.RAW_DIR.glob("*/meta.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        folder = meta_path.parent / model
        if model not in meta.get("models", {}) or len(meta["rows"]) < n_rows or not folder.is_dir():
            continue
        answers = {}
        for path in sorted(folder.glob("*_r0.json")):
            rec = json.loads(path.read_text(encoding="utf-8"))
            answers[rec["row_id"]] = rec["result"]
        runs.append({"run_id": meta_path.parent.name, "answers": answers})
    return runs


def printed_in_guide(rows: list[dict]) -> set[int]:
    """Rows whose reference, or an accepted alternative, appears word for word in the guide."""
    text = GUIDE.read_text(encoding="utf-8")
    out = set()
    for r in rows:
        alts = r["also_accept"] if isinstance(r["also_accept"], list) else re.split(r"[|;]", r["also_accept"] or "")
        if any(a.strip() and a.strip() in text for a in [r["reference_number"], *alts]):
            out.add(r["id"])
    return out


def score(run: dict, gt: dict) -> None:
    run["strict"], run["lenient"], run["brand"], run["got"], run["errors"] = set(), set(), set(), {}, 0
    for row_id, res in run["answers"].items():
        row, parsed = gt[row_id], res.get("parsed") or {}
        if res.get("error"):
            run["errors"] += 1
        got = parsed.get("reference_number")
        strict, lenient, _ = scoring.match(row["brand"], row["reference_number"], row["also_accept"], got)
        run["got"][row_id] = got or "-"
        if strict:
            run["strict"].add(row_id)
        if lenient:
            run["lenient"].add(row_id)
        if (parsed.get("brand") or "").lower() == row["brand"].lower():
            run["brand"].add(row_id)


KINDS = ["No answer", "Wrong brand", "Wrong model line", "Right watch, reference not in the brand's format",
         "Right watch, right format, wrong reference"]


def in_format(brand: str, ref: str | None) -> bool:
    ref = (ref or "").strip().upper()
    for b, pattern, _ in vision_test.PATTERNS:
        m = pattern.search(ref) if b == brand else None
        if m and m.start() == 0 and m.end() == len(ref):
            return True
    return False


def miss_kind(row: dict, res: dict) -> str:
    """What went wrong on a missed row. Only the fourth kind is something a format guide can fix."""
    parsed = res.get("parsed") or {}
    if res.get("error") or not parsed:
        return KINDS[0]
    if (parsed.get("brand") or "").lower() != row["brand"].lower():
        return KINDS[1]
    if detail_study.line_right(row["model_family"], parsed.get("model_family")) is False:
        return KINDS[2]
    return KINDS[4] if in_format(row["brand"], parsed.get("reference_number")) else KINDS[3]


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def main() -> int:
    rows, _ = bench.load_rows()
    gt = {r["id"]: r for r in rows}
    plain, guided = load_runs(PLAIN, len(rows)), load_runs(GUIDED, len(rows))
    if not plain or not guided:
        print(f"Need a full run of both {PLAIN} and {GUIDED}; found {len(plain)} and {len(guided)}.")
        return 1
    leaked = printed_in_guide(rows)
    clean = set(gt) - leaked
    runs = [(f"Plain prompt, run {i}", r) for i, r in enumerate(plain, 1)]
    runs += [(f"With guide, run {i}" if len(guided) > 1 else "With guide", r) for i, r in enumerate(guided, 1)]
    for _, r in runs:
        score(r, gt)

    L = ["# Guide study: does attaching the reference guide help?", "",
         f"Model: `{PLAIN}`. Guide: `{GUIDE.name}` ({len(GUIDE.read_text(encoding='utf-8')):,} characters), "
         "added after the standard prompt. Rebuilt by `guide_study.py` from saved answers.", "",
         f"The guide prints the reference of **{len(leaked)} answer-key rows** as examples "
         f"(rows {', '.join(str(i) for i in sorted(leaked))}). The model can copy those, so the "
         f"**{len(clean)} rows the guide does not print** are the fair test.", "",
         "## Scores", "",
         f"| Run | Folder | Exact, all {len(gt)} | Exact, {len(clean)} fair rows | Exact, {len(leaked)} printed rows "
         "| Incl. look-alikes | Brand right | Failed calls |",
         "|---|---|---:|---:|---:|---:|---:|---:|"]
    for label, r in runs:
        L.append(f"| {label} | `{r['run_id']}` | {len(r['strict'])} | {len(r['strict'] & clean)} "
                 f"| {len(r['strict'] & leaked)} | {len(r['lenient'])} | {len(r['brand'])} | {r['errors']} |")

    L += ["", "## What kind of mistake each miss was", "",
          f"All {len(gt)} rows. A guide to reference formats can only fix the fourth kind.", "",
          "| Kind of miss | " + " | ".join(label for label, _ in runs) + " |", "|---|" + "---:|" * len(runs)]
    for kind in KINDS:
        L.append(f"| {kind} | " + " | ".join(
            str(sum(1 for i in gt if i not in r["strict"] and miss_kind(gt[i], r["answers"][i]) == kind))
            for _, r in runs) + " |")

    L += ["", "## Cost and speed", "",
          "| Run | Cost per image | Median time | Slowest 5% start at | Input tokens | of which cached | Output tokens |",
          "|---|---:|---:|---:|---:|---:|---:|"]
    for label, r in runs:
        res = list(r["answers"].values())
        times = sorted(x.get("elapsed_s") or 0 for x in res)
        p95 = times[max(0, -(-95 * len(times) // 100) - 1)]
        costs = [x["cost_usd"] for x in res if x.get("cost_usd") is not None]
        L.append(f"| {label} | ${mean(costs):.4f} | {statistics.median(times):.1f}s | {p95:.1f}s "
                 f"| {mean([x.get('input_tokens') or 0 for x in res]):,.0f} "
                 f"| {mean([x.get('cached_input_tokens') or 0 for x in res]):,.0f} "
                 f"| {mean([x.get('output_tokens') or 0 for x in res]):,.0f} |")

    brands = sorted({r["brand"] for r in rows})
    L += ["", f"## Exact matches by brand, {len(clean)} fair rows", "",
          "| Brand | Fair rows | " + " | ".join(label for label, _ in runs) + " |",
          "|---|---:|" + "---:|" * len(runs)]
    for b in brands:
        ids = {i for i in clean if gt[i]["brand"] == b}
        L.append(f"| {b} | {len(ids)} | " + " | ".join(str(len(r["strict"] & ids)) for _, r in runs) + " |")

    # Row-level changes, guided run against the plain runs.
    g = guided[-1]
    always = set.intersection(*(r["strict"] for r in plain))
    never = set(gt) - set.union(*(r["strict"] for r in plain))
    sometimes = set(gt) - always - never
    L += ["", "## What changed, row by row", "",
          f"The plain runs disagree with each other, so rows are grouped by what the plain prompt did "
          f"across its {len(plain)} runs.", "",
          "| Plain prompt | Rows | Right with guide | of which fair rows |", "|---|---:|---:|---:|",
          f"| Right in every run | {len(always)} | {len(g['strict'] & always)} | "
          f"{len(g['strict'] & always & clean)} of {len(always & clean)} |",
          f"| Right in some runs | {len(sometimes)} | {len(g['strict'] & sometimes)} | "
          f"{len(g['strict'] & sometimes & clean)} of {len(sometimes & clean)} |",
          f"| Wrong in every run | {len(never)} | {len(g['strict'] & never)} | "
          f"{len(g['strict'] & never & clean)} of {len(never & clean)} |"]

    def table(title: str, ids: set[int]) -> None:
        L.extend(["", f"### {title} ({len(ids)})", ""])
        if not ids:
            L.append("None.")
            return
        L.append("| Row | Brand | Expected | " + " | ".join(label for label, _ in runs) + " | Printed in guide |")
        L.append("|---:|---|---|" + "---|" * len(runs) + "---|")
        for i in sorted(ids):
            L.append(f"| {i} | {gt[i]['brand']} | `{gt[i]['reference_number']}` | "
                     + " | ".join(f"`{r['got'].get(i, '-')}`" for _, r in runs)
                     + f" | {'yes' if i in leaked else ''} |")

    table("Gained: wrong in every plain run, right with the guide", g["strict"] & never)
    table("Lost: right in every plain run, wrong with the guide", always - g["strict"])

    by_brand = defaultdict(int)
    for i in leaked:
        by_brand[gt[i]["brand"]] += 1
    L += ["", "## Rows printed in the guide", "",
          ", ".join(f"{b} {n}" for b, n in sorted(by_brand.items())) + "."]

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    print(f"\nWritten to {OUT.relative_to(bench.ROOT)}")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    sys.exit(main())
