"""Turn saved results into numbers: per-model summaries, markdown/json reports,
and the cross-model comparison. Everything here reads saved records only — it
never calls a provider, so re-scoring costs nothing."""
from __future__ import annotations

import json
import math
import re
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import pricing
import scoring

HIGH_CONFIDENCE = 0.8

MODE_NOTES = {
    "prompt": "prompt mode: JSON asked for in the prompt, not enforced by the API — invalid/empty JSON "
              "is counted as an error, not as a wrong identification",
}
PROVIDER_NOTES = {
    "deepseek": "DeepSeek caps each image at 1,024 tokens (images are scaled to ~1300x1300 px) — less detail "
                "than the other providers get, which matters for reading small engraved text. Its score reflects "
                "that limit as much as model capability. Its price also doubles at peak hours "
                "(01-04 and 06-10 UTC, weekdays); cost uses the rate in force when each request started.",
}


def safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-")


def _pct(n: int, d: int) -> str:
    return f"{100 * n / d:.1f}%" if d else "n/a"


def _p95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


def summarize(model_name: str, model_meta: dict, records: list[dict], gt: dict[int, dict],
              raw_match: bool = False) -> dict:
    items = []
    for rec in sorted(records, key=lambda r: (r["repeat"], r["row_id"])):
        row = gt.get(rec["row_id"])
        res = rec["result"]
        parsed = res.get("parsed") or {}
        answer = parsed.get("reference_number")
        if row is None:
            strict = lenient = False
            reason, brand_ok = None, False
        else:
            strict, lenient, reason = scoring.match(row["brand"], row["reference_number"], row["also_accept"],
                                                    answer, raw=raw_match)
            brand_ok = parsed.get("brand") == row["brand"]
        items.append({
            "row_id": rec["row_id"], "repeat": rec["repeat"], "image_file": rec["image_file"],
            "brand": row["brand"] if row else None,
            "expected": row["reference_number"] if row else None,
            "got": answer, "strict": strict, "lenient": lenient, "lenient_reason": reason,
            "brand_ok": brand_ok, "confidence": parsed.get("confidence"),
            "error": res.get("error"), "error_detail": res.get("error_detail"),
            "elapsed_s": res.get("elapsed_s"), "cost_usd": res.get("cost_usd"),
            "input_tokens": res.get("input_tokens"), "output_tokens": res.get("output_tokens"),
        })

    repeats = sorted({i["repeat"] for i in items})
    passes = []
    for rep in repeats:
        in_pass = [i for i in items if i["repeat"] == rep]
        passes.append({"repeat": rep, "n": len(in_pass),
                       "strict": sum(i["strict"] for i in in_pass),
                       "lenient": sum(i["lenient"] for i in in_pass)})

    n = len(items)
    costs = [i["cost_usd"] for i in items]
    known = [c for c in costs if c is not None]
    if not items or not known:
        cost_status = "unavailable"
    elif len(known) < len(costs):
        cost_status = "partial"
    else:
        cost_status = "complete"
    elapsed = [i["elapsed_s"] for i in items if i["elapsed_s"] is not None]

    per_brand = defaultdict(lambda: [0, 0, 0])
    for i in items:
        b = per_brand[i["brand"] or "?"]
        b[0] += 1
        b[1] += i["strict"]
        b[2] += i["lenient"]

    confident = [i for i in items if isinstance(i["confidence"], (int, float)) and i["confidence"] >= HIGH_CONFIDENCE]

    return {
        "model": model_name,
        "provider": model_meta["provider"],
        "provider_model": model_meta["model"],
        "mode": model_meta["mode"],
        "options": model_meta.get("options", {}),
        "started_at": model_meta.get("started_at"),
        "wall_clock_s": model_meta.get("wall_clock_s"),
        "raw_match": raw_match,
        "n": n,
        "images": len({i["row_id"] for i in items}),
        "dataset_size": len(gt),
        "passes": passes,
        "strict": sum(i["strict"] for i in items),
        "lenient": sum(i["lenient"] for i in items),
        "brand_ok": sum(i["brand_ok"] for i in items),
        "cost_usd": round(sum(known), 6) if known else None,
        "cost_status": cost_status,
        "cost_source": next((r["result"].get("cost_source") for r in records if r["result"].get("cost_source")), None),
        "price_warning": pricing.staleness_warning(model_meta["provider"], model_meta["model"]),
        "price_verified": (pricing.lookup(model_meta["provider"], model_meta["model"]) or {}).get("last_verified"),
        "time": {
            "mean_s": round(statistics.mean(elapsed), 3) if elapsed else None,
            "median_s": round(statistics.median(elapsed), 3) if elapsed else None,
            "p95_s": round(_p95(elapsed), 3) if elapsed else None,
        },
        "errors": dict(Counter(i["error"] for i in items if i["error"])),
        "per_brand": {k: {"n": v[0], "strict": v[1], "lenient": v[2]} for k, v in sorted(per_brand.items())},
        "high_confidence": {"threshold": HIGH_CONFIDENCE, "n": len(confident),
                            "strict": sum(i["strict"] for i in confident)},
        "items": items,
    }


def _accuracy_line(s: dict, key: str) -> str:
    line = f"{s[key]}/{s['n']}   ({_pct(s[key], s['n'])})"
    if len(s["passes"]) > 1:
        rates = [100 * p[key] / p["n"] for p in s["passes"] if p["n"]]
        line += (f"   mean of {len(rates)} passes {statistics.mean(rates):.1f}%, "
                 f"range {min(rates):.1f}-{max(rates):.1f}%")
    return line


def _cost_line(s: dict) -> str:
    if s["cost_status"] == "unavailable":
        if s["price_verified"]:
            return "unavailable - no call returned token usage (every call failed)"
        return "unavailable (no rate for this model in pricing.py)"
    text = f"${s['cost_usd']:.4f}"
    if s["cost_source"] == "reported":
        text += "   (charged amount reported by OpenRouter)"
    elif s["price_verified"]:
        text += f"   (rates verified {s['price_verified']})"
    if s["cost_status"] == "partial":
        text += "   PARTIAL — some calls have no cost"
    if s["price_warning"]:
        text += f"   WARNING: {s['price_warning']}"
    return text


def _time_line(s: dict) -> str:
    t = s["time"]
    if t["mean_s"] is None:
        return "n/a"
    total = f"{s['wall_clock_s']:.1f}s total | " if s.get("wall_clock_s") else ""
    return f"{total}mean {t['mean_s']:.2f}s | median {t['median_s']:.2f}s | p95 {t['p95_s']:.2f}s"


def _errors_line(s: dict) -> str:
    if not s["errors"]:
        return "0"
    parts = ", ".join(f"{v} {k}" for k, v in sorted(s["errors"].items(), key=lambda kv: -kv[1]))
    return f"{sum(s['errors'].values())} ({parts})"


def run_kind(images: int, dataset_size: int) -> dict:
    """A run over only part of the answer key is a TEST run: it shows that a model works,
    but its accuracy is not comparable with a full run."""
    if images >= dataset_size:
        return {"kind": "full", "label": f"FULL RUN ({images} images)", "suffix": "_full"}
    return {"kind": "test", "label": f"TEST RUN ({images} of {dataset_size} images)",
            "suffix": f"_test-{images}img"}


def _kind(s: dict, dataset_size: int | None = None) -> dict:
    return run_kind(s.get("images", s["n"]), dataset_size or s.get("dataset_size") or s.get("images", s["n"]))


TEST_WARNING = ("**TEST RUN** — only {images} of the {size} images. It checks that the model works; "
                "don't compare its accuracy with full runs.")


def headline(s: dict) -> str:
    started = (s.get("started_at") or "")[:16].replace("T", " ")
    title = f"{s['model']}   -   {_kind(s)['label']}   -   {started} UTC   [{s['mode']} mode]"
    hc = s["high_confidence"]
    lines = [
        title,
        "=" * min(len(title), 72),
        f"Accuracy (strict)    {_accuracy_line(s, 'strict')}",
        f"Accuracy (lenient)   {_accuracy_line(s, 'lenient')}",
        f"Brand correct        {s['brand_ok']}/{s['n']}   ({_pct(s['brand_ok'], s['n'])})",
        f"Confidence >= {hc['threshold']}    {hc['n']} answers, {hc['strict']} strictly right "
        f"({_pct(hc['strict'], hc['n'])})",
        f"Cost                 {_cost_line(s)}",
        f"Time                 {_time_line(s)}",
        f"Errors               {_errors_line(s)}",
    ]
    if s["raw_match"]:
        lines.append("Matching             --raw-match: byte-identical comparison, no normalization")
    return "\n".join(lines)


def to_markdown(s: dict, gt: dict[int, dict]) -> str:
    kind = _kind(s)
    out = [f"# {s['model']} — {kind['label']}", ""]
    if kind["kind"] == "test":
        out += ["> " + TEST_WARNING.format(images=s.get("images", s["n"]), size=s.get("dataset_size")), ""]
    out += ["```", headline(s), "```", ""]
    notes = [MODE_NOTES.get(s["mode"]), PROVIDER_NOTES.get(s["provider"])]
    notes = [n for n in notes if n]
    if notes:
        out += [f"> {n}" for n in notes] + [""]
    out += [
        f"Provider `{s['provider']}`, model `{s['provider_model']}`"
        + (f", options `{json.dumps(s['options'])}`" if s["options"] else "") + ".",
        "",
        "**Strict**: the exact reference (notation normalized). **Lenient**: also counts look-alikes listed in "
        "`also_accept` and the same watch on a different strap/bracelet. Errors count as failures.",
        "",
        "## By brand", "", "| Brand | Images | Strict | Lenient |", "|---|---:|---:|---:|",
    ]
    for brand, b in s["per_brand"].items():
        out.append(f"| {brand} | {b['n']} | {b['strict']} ({_pct(b['strict'], b['n'])}) "
                   f"| {b['lenient']} ({_pct(b['lenient'], b['n'])}) |")

    failed = [i for i in s["items"] if not i["strict"]]
    out += ["", f"## Not strictly correct ({len(failed)})", "",
            "| # | Image | Expected | Got | Lenient | Error |", "|---:|---|---|---|---|---|"]
    for i in failed:
        rep = f" (pass {i['repeat'] + 1})" if len(s["passes"]) > 1 else ""
        got = f"`{i['got']}`" if i["got"] else "—"
        lenient = f"yes ({i['lenient_reason']})" if i["lenient"] else ""
        err = f"{i['error']}: {(i['error_detail'] or '')[:120]}" if i["error"] else ""
        out.append(f"| {i['row_id']}{rep} | {i['image_file']} | `{i['expected']}` | {got} | {lenient} | "
                   f"{err.replace('|', '/')} |")
    return "\n".join(out) + "\n"


def comparison_markdown(run_label: str, summaries: list[dict]) -> str:
    ranked = sorted(summaries, key=lambda s: (-(s["strict"] / s["n"] if s["n"] else 0), s["model"]))
    out = [f"# Comparison — {run_label}", ""]
    s0 = summaries[0] if summaries else None
    if s0 and _kind(s0)["kind"] == "test":
        out += ["> " + TEST_WARNING.format(images=s0.get("images", s0["n"]), size=s0.get("dataset_size")), ""]
    out += ["```",
           f"{'MODEL':<26}{'STRICT':>8}{'LENIENT':>9}{'COST':>11}{'$/IMAGE':>10}{'MEAN':>8}{'P95':>8}  MODE"]
    for s in ranked:
        cost = f"${s['cost_usd']:.4f}" if s["cost_usd"] is not None else "n/a"
        per = f"${s['cost_usd'] / s['n']:.4f}" if s["cost_usd"] is not None and s["n"] else "n/a"
        flag = " !" if (s["mode"] == "prompt" or s["provider"] in PROVIDER_NOTES
                        or s["cost_status"] != "complete" or s["price_warning"]) else ""
        mean = f"{s['time']['mean_s']:.2f}s" if s["time"]["mean_s"] is not None else "n/a"
        p95 = f"{s['time']['p95_s']:.2f}s" if s["time"]["p95_s"] is not None else "n/a"
        out.append(f"{s['model'][:25]:<26}{_pct(s['strict'], s['n']):>8}{_pct(s['lenient'], s['n']):>9}"
                   f"{cost:>11}{per:>10}{mean:>8}{p95:>8}  {s['mode']}{flag}")
    out.append("```")

    notes = []
    for s in ranked:
        if s["mode"] == "prompt":
            parse_errors = s["errors"].get("schema-parse", 0) + s["errors"].get("empty", 0)
            misses = s["n"] - s["strict"]
            notes.append(f"**{s['model']}** — {MODE_NOTES['prompt']}. {parse_errors} of its {misses} misses "
                         f"were invalid or empty JSON rather than wrong answers.")
        if s["provider"] in PROVIDER_NOTES:
            notes.append(f"**{s['model']}** — {PROVIDER_NOTES[s['provider']]}")
        if s["cost_status"] != "complete":
            notes.append(f"**{s['model']}** — cost {s['cost_status']}.")
        if s["price_warning"]:
            notes.append(f"**{s['model']}** — {s['price_warning']}.")
        if s["errors"]:
            notes.append(f"**{s['model']}** — errors: {_errors_line(s)}; each counts as a failure.")
    if notes:
        out += ["", "## Read before comparing", ""] + [f"- {n}" for n in notes]
    out += ["", "Strict = exact reference (notation normalized). Lenient = also look-alikes listed in the "
                "answer key and strap/bracelet variants of the same watch. One pass per image unless noted: "
                "these models are non-deterministic, so a single pass carries unmeasured spread, and numbers "
                "from different sessions or prompt versions are not comparable."]
    return "\n".join(out) + "\n"


def unique_path(path: Path) -> Path:
    """Never overwrite: add _2, _3 … when a report of that name exists."""
    if not path.exists():
        return path
    k = 2
    while (candidate := path.with_name(f"{path.stem}_{k}{path.suffix}")).exists():
        k += 1
    return candidate


def write_run_reports(folder: Path, summaries: list[dict], gt: dict[int, dict], run_label: str) -> list[Path]:
    """One folder per run: summary.md (all models, ranked) + <model>.md/.json each."""
    folder.mkdir(parents=True, exist_ok=True)
    written = []
    if summaries:
        comp = unique_path(folder / "summary.md")
        comp.write_text(comparison_markdown(run_label, summaries), encoding="utf-8")
        written.append(comp)
    for s in summaries:
        md = unique_path(folder / f"{safe_name(s['model'])}.md")
        md.write_text(to_markdown(s, gt), encoding="utf-8")
        js = unique_path(folder / f"{safe_name(s['model'])}.json")
        js.write_text(json.dumps(s, indent=2, ensure_ascii=False), encoding="utf-8")
        written += [md, js]
    return written


def _load_run_summaries(results_dir: Path) -> list[tuple[Path, dict]]:
    found = []
    for path in (results_dir / "runs").glob("*/*.json"):
        try:
            s = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if "strict" in s and "model" in s:
            found.append((path, s))
    return found


def _run_time(s: dict) -> str:
    return (s.get("rescored_at") or s.get("started_at") or "")[:16].replace("T", " ")


def build_index(results_dir: Path, dataset_size: int) -> Path:
    """results/REPORT.md — the one file to open. Rebuilt from runs/ after every run
    or re-score; it only summarizes and links, the detailed reports never change."""
    found = _load_run_summaries(results_dir)
    rel = lambda p: p.relative_to(results_dir).as_posix()  # noqa: E731

    # Latest result per model; a run over the whole dataset beats a smaller smoke test.
    latest: dict[str, tuple[Path, dict]] = {}
    for path, s in found:
        key = (s.get("images", 0) >= dataset_size, _run_time(s))
        cur = latest.get(s["model"])
        if cur is None or key > (cur[1].get("images", 0) >= dataset_size, _run_time(cur[1])):
            latest[s["model"]] = (path, s)
    ranked = sorted(latest.values(), key=lambda ps: -(ps[1]["strict"] / ps[1]["n"] if ps[1]["n"] else 0))

    out = ["# ChronoBay watch-identification benchmark", "",
           f"Updated {datetime.now():%Y-%m-%d %H:%M}. {dataset_size} watches in the answer key. "
           "This page is rebuilt after every run; the detailed reports it links to are never changed.", "",
           "## Latest result per model", ""]
    if not ranked:
        out.append("No runs yet.")
    else:
        out += ["| Model | Exact reference | Incl. look-alikes | Brand right | Cost / image | Median time "
                "| Errors | Images | Run | Detailed report |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---|---|"]
        for path, s in ranked:
            per = f"${s['cost_usd'] / s['n']:.4f}" if s.get("cost_usd") is not None and s["n"] else "n/a"
            med = f"{s['time']['median_s']:.1f}s" if s["time"].get("median_s") is not None else "n/a"
            errs = sum(s["errors"].values())
            images = f"{s.get('images', s['n'])}" + (f" x{len(s['passes'])}" if len(s["passes"]) > 1 else "")
            tag = ""
            if _kind(s, dataset_size)["kind"] == "test":
                images = f"{s.get('images', s['n'])} of {dataset_size}"
                tag = " (TEST RUN only)"
            out.append(f"| **{s['model']}**{tag} | **{_pct(s['strict'], s['n'])}** ({s['strict']}/{s['n']}) "
                       f"| {_pct(s['lenient'], s['n'])} | {_pct(s['brand_ok'], s['n'])} | {per} | {med} | {errs} "
                       f"| {images} | {_run_time(s)} | [{s['model']}.md]({rel(path.with_suffix('.md'))}) |")

        brands = sorted({b for _, s in ranked for b in s["per_brand"]})
        out += ["", "## Exact reference by brand", "",
                "| Brand | " + " | ".join(s["model"] for _, s in ranked) + " |",
                "|---|" + "---:|" * len(ranked)]
        for b in brands:
            cells = []
            for _, s in ranked:
                pb = s["per_brand"].get(b)
                cells.append(f"{pb['strict']}/{pb['n']}" if pb else "—")
            out.append(f"| {b} | " + " | ".join(cells) + " |")

        notes = []
        for _, s in ranked:
            if s["mode"] == "prompt":
                notes.append(f"**{s['model']}** — {MODE_NOTES['prompt']}.")
            if s["provider"] in PROVIDER_NOTES:
                notes.append(f"**{s['model']}** — {PROVIDER_NOTES[s['provider']]}")
            if s.get("price_warning"):
                notes.append(f"**{s['model']}** — {s['price_warning']}.")
        if notes:
            out += ["", "## Read before comparing", ""] + [f"- {n}" for n in notes]

    out += ["", "## What the columns mean", "",
            "- **Exact reference** — the model named the exact reference number (notation normalized: case, "
            "spaces and `. - /` ignored). This is the headline number.",
            "- **Incl. look-alikes** — also counts references a photo can't tell apart (another size, the "
            "previous generation — listed per watch in the answer key) and the same watch on another strap.",
            "- **Errors** — calls with no usable answer (timeouts, refusals, empty or invalid JSON). "
            "They count as misses and are listed in the detailed report.",
            "- A single pass per image carries unmeasured spread; results from different prompts or sessions "
            "are not directly comparable."]

    runs: dict[str, list[tuple[Path, dict]]] = {}
    for path, s in found:
        runs.setdefault(path.parent.name, []).append((path, s))
    sections = {
        "full": ["", "## Full runs", "", f"Every image in the answer key ({dataset_size}). Compare these."],
        "test": ["", "## Test runs", "",
                 "A subset of the images, to check that a model or setting works before paying for a full run. "
                 "Not comparable with full runs — a few images say little about accuracy."],
    }
    for kind_name, header in sections.items():
        folders = [f for f in sorted(runs, reverse=True) if _kind(runs[f][0][1], dataset_size)["kind"] == kind_name]
        out += header + [""]
        if not folders:
            out.append("None yet.")
            continue
        out += ["| Run | Models | Images | Summary | Detailed reports |", "|---|---|---:|---|---|"]
        for folder in folders:
            items = sorted(runs[folder], key=lambda ps: ps[1]["model"])
            s0 = items[0][1]
            rescore = " (re-score)" if s0.get("rescored_at") else ""
            links = ", ".join(f"[{s['model']}]({rel(p.with_suffix('.md'))})" for p, s in items)
            summary = results_dir / "runs" / folder / "summary.md"
            summary_link = f"[summary](runs/{folder}/summary.md)" if summary.exists() else ""
            images = s0.get("images", s0["n"])
            images = f"{images} of {dataset_size}" if kind_name == "test" else f"{images}"
            out.append(f"| {folder}{rescore} | {', '.join(s['model'] for _, s in items)} | {images} "
                       f"| {summary_link} | {links} |")

    index = results_dir / "REPORT.md"
    index.write_text("\n".join(out) + "\n", encoding="utf-8")
    return index
