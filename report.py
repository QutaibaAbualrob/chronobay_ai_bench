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


def headline(s: dict) -> str:
    started = (s.get("started_at") or "")[:16].replace("T", " ")
    title = f"{s['model']}   -   {started} UTC   [{s['mode']} mode]"
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
    out = [f"# {s['model']}", "", "```", headline(s), "```", ""]
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
    out = [f"# Comparison — {run_label}", "", "```",
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


def write_reports(results_dir: Path, summaries: list[dict], gt: dict[int, dict], stamp: datetime,
                  suffix: str = "", run_label: str = "") -> list[Path]:
    written = []
    ts = stamp.strftime("%Y-%m-%d_%H%M")
    for s in summaries:
        base = results_dir / f"{safe_name(s['model'])}_{ts}{suffix}"
        md = unique_path(base.with_suffix(".md"))
        md.write_text(to_markdown(s, gt), encoding="utf-8")
        js = unique_path(base.with_suffix(".json"))
        js.write_text(json.dumps(s, indent=2, ensure_ascii=False), encoding="utf-8")
        written += [md, js]
    if summaries:
        comp = unique_path(results_dir / f"comparison_{ts}{suffix}.md")
        comp.write_text(comparison_markdown(run_label or ts, summaries), encoding="utf-8")
        written.append(comp)
    return written
