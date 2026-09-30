"""ChronoBay AI watch-identification benchmark.

    python bench.py validate                        # check the dataset, spends nothing
    python bench.py estimate --all                  # projected cost, no API calls
    python bench.py run --models claude-opus-5-5 --limit 3
    python bench.py run --all --repeats 3
    python bench.py score results/raw/<run_id>      # re-score saved responses, $0

See README.md for what the numbers mean.
"""
from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import importlib
import importlib.util
import json
import math
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import pricing  # noqa: E402
import report  # noqa: E402
import scoring  # noqa: E402
from schema import BRACELET_MATERIALS, BRANDS, CASE_MATERIALS, MOVEMENTS  # noqa: E402

CSV_PATH = ROOT / "dataset" / "ground_truth.csv"
IMAGES_DIR = ROOT / "dataset" / "images"
RESULTS_DIR = ROOT / "results"
RAW_DIR = RESULTS_DIR / "raw"

COLUMNS = ["id", "image_file", "brand", "model_family", "reference_number", "also_accept",
           "movement", "case_material", "bracelet_material", "source_url", "verified"]
MAX_IMAGE_BYTES = 5 * 1024 * 1024  # Anthropic's per-image limit - the strictest of the five
MAX_IMAGE_SIDE = 8000
MIME = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp", "GIF": "image/gif"}

# Rough per-call output tokens for estimates before any real run exists.
EST_OUTPUT_TOKENS = {"anthropic": 1000, "openai": 800, "gemini": 800, "openrouter": 800, "deepseek": 200}
EST_IMAGE_TOKENS = {"deepseek": 1024, "default": 1500}


# ── dataset ──────────────────────────────────────────────────────────────────

def load_rows(path: Path = CSV_PATH) -> tuple[list[dict], list[str]]:
    if not path.exists():
        return [], [f"{path} not found"]
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            return [], [f"ground_truth.csv is missing columns: {', '.join(missing)}"]
        rows, problems = [], []
        for line_no, raw in enumerate(reader, start=2):
            try:
                rid = int(raw["id"])
            except ValueError:
                problems.append(f"line {line_no}: id {raw['id']!r} is not a number")
                continue
            row = {k: (raw[k] or "").strip() for k in COLUMNS}
            row["id"] = rid
            row["also_accept"] = [a.strip() for a in row["also_accept"].split("|") if a.strip()]
            row["verified"] = row["verified"].lower() == "true"
            rows.append(row)
    return rows, problems


def check_image(row: dict) -> tuple[str | None, str | None]:
    """Returns (mime, problem)."""
    from PIL import Image
    path = IMAGES_DIR / row["image_file"]
    if not row["image_file"]:
        return None, "no image_file"
    if not path.exists():
        return None, f"image missing: dataset/images/{row['image_file']}"
    if path.stat().st_size > MAX_IMAGE_BYTES:
        return None, f"{row['image_file']} is over 5 MB"
    try:
        with Image.open(path) as im:
            fmt, size = im.format, im.size
            im.verify()
    except Exception as e:
        return None, f"{row['image_file']} does not open as an image ({e})"
    if fmt not in MIME:
        return None, f"{row['image_file']} is {fmt}; supported: JPEG, PNG, WebP, GIF"
    if max(size) > MAX_IMAGE_SIDE:
        return None, f"{row['image_file']} is {size[0]}x{size[1]}; max side is {MAX_IMAGE_SIDE}px"
    return MIME[fmt], None


def validate(rows: list[dict], problems: list[str]) -> tuple[list[str], list[str]]:
    errors, warnings = list(problems), []
    seen = set()
    for r in rows:
        tag = f"#{r['id']}"
        if r["id"] in seen:
            errors.append(f"{tag}: duplicate id")
        seen.add(r["id"])
        if not r["verified"]:
            errors.append(f"{tag}: verified is not true - confirm the reference before running")
        if not r["reference_number"]:
            errors.append(f"{tag}: reference_number is empty")
        for field, vocab in (("brand", BRANDS), ("movement", MOVEMENTS),
                             ("case_material", CASE_MATERIALS), ("bracelet_material", BRACELET_MATERIALS)):
            if r[field] not in vocab:
                errors.append(f"{tag}: {field} {r[field]!r} is not in the ChronoBay vocabulary")
        _, problem = check_image(r)
        if problem:
            errors.append(f"{tag}: {problem}")
        canon = scoring.canonical(r["brand"], r["reference_number"])
        if any(scoring.canonical(r["brand"], a) == canon for a in r["also_accept"]):
            warnings.append(f"{tag}: also_accept repeats the reference itself")

    by_ref: dict[str, list[int]] = {}
    for r in rows:
        by_ref.setdefault(scoring.canonical(r["brand"], r["reference_number"]), []).append(r["id"])
    for ref, ids in by_ref.items():
        if ref and len(ids) > 1:
            warnings.append(f"reference {ref} appears on rows {', '.join(map(str, ids))} (different images of one watch?)")
    no_source = [r["id"] for r in rows if not r["source_url"]]
    if no_source:
        warnings.append(f"{len(no_source)} rows have no source_url (optional, but it makes the key auditable)")
    return errors, warnings


def print_validation(rows: list[dict], errors: list[str], warnings: list[str]) -> None:
    counts = {b: 0 for b in BRANDS}
    for r in rows:
        counts[r["brand"]] = counts.get(r["brand"], 0) + 1
    print(f"Dataset: {len(rows)} rows in dataset/ground_truth.csv")
    for brand, n in counts.items():
        print(f"  {brand:<22}{n:>4}")
    for w in warnings:
        print(f"  warning: {w}")
    if errors:
        print(f"\nFAILED - {len(errors)} problem(s). Nothing will run until they are fixed:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("\nOK - dataset is ready.")


def select_rows(rows: list[dict], ids: str | None, limit: int | None) -> list[dict]:
    if ids:
        wanted = [int(x) for x in ids.split(",") if x.strip()]
        by_id = {r["id"]: r for r in rows}
        unknown = [i for i in wanted if i not in by_id]
        if unknown:
            sys.exit(f"Unknown row ids: {unknown}")
        return [by_id[i] for i in wanted]
    if not limit:
        return rows
    # Round-robin across brands so a small sample still covers every brand.
    queues = {b: [r for r in rows if r["brand"] == b] for b in BRANDS}
    picked = []
    while len(picked) < min(limit, len(rows)):
        for b in BRANDS:
            if queues[b] and len(picked) < limit:
                picked.append(queues[b].pop(0))
    return picked


# ── config ───────────────────────────────────────────────────────────────────

def load_config(required: bool):
    if (ROOT / "config.py").exists():
        return importlib.import_module("config"), "config.py"
    if required:
        sys.exit("config.py not found. Copy config.example.py to config.py and add your API keys.")
    spec = importlib.util.spec_from_file_location("config_example", ROOT / "config.example.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, "config.example.py (no config.py yet)"


def settings(cfg) -> dict:
    return {"max_output_tokens": getattr(cfg, "MAX_OUTPUT_TOKENS", 16000),
            "timeout_s": getattr(cfg, "REQUEST_TIMEOUT_S", 180)}


def api_key(cfg, provider: str) -> str:
    from providers import KEY_NAMES
    name = KEY_NAMES[provider]
    return getattr(cfg, name, "") or os.environ.get(name, "")


def select_models(cfg, models_arg: str | None, all_models: bool) -> list[tuple[str, dict]]:
    from providers import PROVIDERS
    configured = getattr(cfg, "MODELS", {})
    names = list(configured) if all_models else [m.strip() for m in models_arg.split(",") if m.strip()]
    unknown = [n for n in names if n not in configured]
    if unknown:
        sys.exit(f"Not in config MODELS: {', '.join(unknown)}. Configured: {', '.join(configured) or '(none)'}")
    for n in names:
        if configured[n].get("provider") not in PROVIDERS:
            sys.exit(f"{n}: unknown provider {configured[n].get('provider')!r} (use one of {', '.join(PROVIDERS)})")
    return [(n, configured[n]) for n in names]


# ── estimate ─────────────────────────────────────────────────────────────────

def _openrouter_prices() -> dict:
    import requests
    try:
        data = requests.get("https://openrouter.ai/api/v1/models", timeout=30).json().get("data", [])
    except Exception:
        return {}
    return {m["id"]: m.get("pricing") or {} for m in data}


def _measured_cost_per_call(name: str) -> tuple[float, str] | None:
    candidates = sorted(RESULTS_DIR.glob(f"{report.safe_name(name)}_*.json"), key=lambda p: p.stat().st_mtime)
    for path in reversed(candidates):
        try:
            s = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if s.get("cost_status") == "complete" and s.get("n"):
            return s["cost_usd"] / s["n"], f"measured in {path.name} ({s['n']} calls)"
    return None


def _anthropic_image_tokens(w: int, h: int) -> int:
    scale = min(1.0, 1568 / max(w, h), math.sqrt(1_150_000 / (w * h)))
    return math.ceil((w * scale) * (h * scale) / 750)


def estimate(models: list[tuple[str, dict]], rows: list[dict], repeats: int, prompt: str) -> list[dict]:
    from PIL import Image
    calls = len(rows) * repeats
    prompt_tokens = len(prompt) // 3 + 300  # prompt + schema overhead, rough
    dims = []
    for r in rows:
        with Image.open(IMAGES_DIR / r["image_file"]) as im:
            dims.append(im.size)
    or_prices = None
    out = []
    for name, spec in models:
        prov, model = spec["provider"], spec["model"]
        measured = _measured_cost_per_call(name)
        if measured:
            per_call, basis = measured
        else:
            per_call, basis = None, "no rate available"
            if prov == "anthropic":
                img = sum(_anthropic_image_tokens(w, h) for w, h in dims) / max(len(dims), 1)
            else:
                img = EST_IMAGE_TOKENS.get(prov, EST_IMAGE_TOKENS["default"])
            out_tok = EST_OUTPUT_TOKENS.get(prov, 800)
            if prov == "openrouter":
                if or_prices is None:
                    or_prices = _openrouter_prices()
                p = or_prices.get(model)
                if p:
                    image_price = float(p.get("image") or 0)
                    in_tokens = prompt_tokens + (0 if image_price else img)
                    per_call = (in_tokens * float(p.get("prompt") or 0) + out_tok * float(p.get("completion") or 0)
                                + image_price + float(p.get("request") or 0))
                    basis = f"rough: OpenRouter list prices, ~{int(in_tokens)} in / {out_tok} out tokens"
            else:
                per_call = pricing.cost_usd(prov, model, int(prompt_tokens + img), out_tok)
                if per_call is not None:
                    basis = f"rough: pricing.py rates, ~{int(prompt_tokens + img)} in / {out_tok} out tokens"
                    if prov == "deepseek":
                        basis += " (rate for the current hour)"
        out.append({"model": name, "calls": calls, "per_call": per_call,
                    "total": per_call * calls if per_call is not None else None, "basis": basis})
    return out


def print_estimate(est: list[dict]) -> float | None:
    print(f"{'MODEL':<24}{'CALLS':>6}{'$/IMAGE':>10}{'TOTAL':>10}  BASIS")
    total, unknown = 0.0, False
    for e in est:
        per = f"${e['per_call']:.4f}" if e["per_call"] is not None else "n/a"
        tot = f"${e['total']:.2f}" if e["total"] is not None else "n/a"
        print(f"{e['model'][:23]:<24}{e['calls']:>6}{per:>10}{tot:>10}  {e['basis']}")
        if e["total"] is None:
            unknown = True
        else:
            total += e["total"]
    print(f"{'':<24}{'':>6}{'':>10}{'$' + format(total, '.2f'):>10}  total" + (" (+ models with no rate)" if unknown else ""))
    print("Rough projections until a model has a completed run; after that they use its measured cost.")
    return total


# ── run ──────────────────────────────────────────────────────────────────────

def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_model(run_id: str, name: str, spec: dict, provider_obj, jobs: list[tuple[dict, int]], prompt: str,
              prompt_hash: str, run_dir: Path, concurrency: int, images: dict[int, tuple[str, str]]):
    from providers.base import CONFIG, ProviderResult
    out_dir = run_dir / report.safe_name(name)
    out_dir.mkdir(parents=True, exist_ok=True)
    lock, abort = threading.Lock(), threading.Event()
    records, done = [], 0

    def work(row: dict, rep: int) -> dict:
        if abort.is_set():
            res = ProviderResult(error=CONFIG, error_detail="skipped: an earlier call failed authentication")
        else:
            b64, mime = images[row["id"]]
            res = provider_obj.identify(b64, mime, prompt)
            if res.error == "auth":
                abort.set()
        rec = {"run_id": run_id, "model_name": name, "provider": spec["provider"], "provider_model": spec["model"],
               "mode": provider_obj.mode, "row_id": row["id"], "repeat": rep, "image_file": row["image_file"],
               "prompt_sha256": prompt_hash, "result": res.to_dict()}
        path = out_dir / f"{row['id']:03d}_r{rep}.json"
        path.write_text(json.dumps(rec, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
        return rec

    started = datetime.now(timezone.utc)
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = {pool.submit(work, row, rep): row for row, rep in jobs}
        for fut in as_completed(futures):
            row = futures[fut]
            rec = fut.result()
            res = rec["result"]
            got = (res.get("parsed") or {}).get("reference_number")
            strict, lenient, _ = scoring.match(row["brand"], row["reference_number"], row["also_accept"], got)
            mark = "ok " if strict else ("~  " if lenient else "no ")
            if res.get("error"):
                mark = f"ERR {res['error']}"
            with lock:
                records.append(rec)
                done += 1
                print(f"  [{name}] {done:>3}/{len(jobs)}  #{row['id']:<3} {mark:<14} "
                      f"got {got or '-':<24} expected {row['reference_number']:<22} {res.get('elapsed_s', 0):.1f}s",
                      flush=True)
    return records, started, round(time.perf_counter() - t0, 2)


def cmd_run(args) -> int:
    from providers import PROVIDERS
    cfg, cfg_name = load_config(required=True)
    rows, problems = load_rows()
    errors, warnings = validate(rows, problems)
    if errors:
        print_validation(rows, errors, warnings)
        return 1
    selected = select_rows(rows, args.ids, args.limit)
    models = select_models(cfg, args.models, args.all)
    missing = sorted({f"{spec['provider']} ({n})" for n, spec in models if not api_key(cfg, spec["provider"])})
    if missing:
        print(f"No API key for: {', '.join(missing)}. Add it to config.py or the environment.")
        return 1

    prompt = cfg.PROMPT
    print(f"{len(selected)} images x {args.repeats} pass(es) x {len(models)} model(s)\n")
    total = print_estimate(estimate(models, selected, args.repeats, prompt))
    if not args.yes:
        if not sys.stdin.isatty():
            print("Not interactive - pass --yes to confirm spending.")
            return 1
        if input(f"\nSpend about ${total:.2f} on this run? [y/N] ").strip().lower() not in ("y", "yes"):
            print("Cancelled - nothing was spent.")
            return 1

    images = {}
    for r in selected:
        mime, _ = check_image(r)
        images[r["id"]] = (base64.standard_b64encode((IMAGES_DIR / r["image_file"]).read_bytes()).decode(), mime)

    now = datetime.now(timezone.utc)
    run_id = now.strftime("%Y-%m-%d_%H%M%S")
    run_dir = RAW_DIR / run_id
    run_dir.mkdir(parents=True)
    prompt_hash = _sha256(prompt.encode())
    meta = {"run_id": run_id, "started_at": now.isoformat(), "config": cfg_name, "prompt": prompt,
            "prompt_sha256": prompt_hash, "csv_sha256": _sha256(CSV_PATH.read_bytes()),
            "rows": [r["id"] for r in selected], "repeats": args.repeats, "concurrency": args.concurrency,
            "settings": settings(cfg), "models": {}}
    gt = {r["id"]: r for r in rows}
    jobs = [(row, rep) for rep in range(args.repeats) for row in selected]
    all_records = {}
    for name, spec in models:
        provider_cls = PROVIDERS[spec["provider"]]
        options = {k: v for k, v in spec.items() if k not in ("provider", "model")}
        provider_obj = provider_cls(spec["model"], api_key(cfg, spec["provider"]), options, settings(cfg))
        print(f"\n== {name}  ({spec['provider']} / {spec['model']}, {provider_obj.mode} mode)")
        records, started, wall = run_model(run_id, name, spec, provider_obj, jobs, prompt, prompt_hash,
                                           run_dir, args.concurrency, images)
        meta["models"][name] = {"provider": spec["provider"], "model": spec["model"], "mode": provider_obj.mode,
                                "options": options, "started_at": started.isoformat(), "wall_clock_s": wall,
                                "price": pricing.lookup(spec["provider"], spec["model"])}
        all_records[name] = records
        (run_dir / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    meta["finished_at"] = datetime.now(timezone.utc).isoformat()
    (run_dir / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    summaries = [report.summarize(n, meta["models"][n], all_records[n], gt) for n, _ in models]
    return finish(summaries, gt, now, "", f"run {run_id}", run_dir)


def finish(summaries: list[dict], gt: dict, stamp: datetime, suffix: str, label: str, run_dir: Path) -> int:
    print()
    for s in summaries:
        print(report.headline(s) + "\n")
    written = report.write_reports(RESULTS_DIR, summaries, gt, stamp, suffix, label)
    comparison = [p for p in written if p.name.startswith("comparison_")]
    if len(summaries) > 1 and comparison:
        text = comparison[0].read_text(encoding="utf-8")
        print(text.split("```")[1].strip("\n") + "\n")
    print(f"Raw responses: {_rel(run_dir)}")
    for p in written:
        print(f"Report:        {_rel(p)}")
    return 0


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def cmd_score(args) -> int:
    run_dir = Path(args.raw_dir).resolve()
    meta_path = run_dir / "meta.json"
    if not meta_path.exists():
        print(f"{meta_path} not found - pass a results/raw/<run_id> directory.")
        return 1
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    rows, problems = load_rows()
    if problems:
        print("\n".join(problems))
        return 1
    if meta.get("csv_sha256") and meta["csv_sha256"] != _sha256(CSV_PATH.read_bytes()):
        print("Note: the answer key changed since this run - scoring uses the current ground_truth.csv.")
    gt = {r["id"]: r for r in rows}
    summaries = []
    for name, model_meta in meta["models"].items():
        recs = [json.loads(p.read_text(encoding="utf-8"))
                for p in sorted((run_dir / report.safe_name(name)).glob("*.json"))]
        summaries.append(report.summarize(name, model_meta, recs, gt, raw_match=args.raw_match))
    now = datetime.now(timezone.utc)
    return finish(summaries, gt, now, "_rescore", f"run {meta['run_id']}, re-scored {now:%Y-%m-%d %H:%M} UTC", run_dir)


def cmd_validate(_args) -> int:
    rows, problems = load_rows()
    errors, warnings = validate(rows, problems)
    print_validation(rows, errors, warnings)
    return 1 if errors else 0


def cmd_estimate(args) -> int:
    cfg, cfg_name = load_config(required=False)
    rows, problems = load_rows()
    if problems:
        print("\n".join(problems))
        return 1
    selected = select_rows(rows, args.ids, args.limit)
    models = select_models(cfg, args.models, args.all)
    print(f"Models from {cfg_name}. {len(selected)} images x {args.repeats} pass(es). No API calls are made.\n")
    print_estimate(estimate(models, selected, args.repeats, cfg.PROMPT))
    return 0


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description="ChronoBay AI watch-identification benchmark")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate", help="check the dataset; spends nothing")
    for name, text in (("estimate", "project the cost of a run; no API calls"),
                       ("run", "run models against the dataset")):
        sp = sub.add_parser(name, help=text)
        group = sp.add_mutually_exclusive_group(required=True)
        group.add_argument("--models", help="comma-separated names from config MODELS")
        group.add_argument("--all", action="store_true", help="every model in config MODELS")
        sp.add_argument("--limit", type=int, help="use N images, spread across brands")
        sp.add_argument("--ids", help="comma-separated row ids to use instead of --limit")
        sp.add_argument("--repeats", type=int, default=1, help="passes per image (default 1)")
        if name == "run":
            sp.add_argument("--concurrency", type=int, default=None, help="parallel calls per model")
            sp.add_argument("--yes", action="store_true", help="skip the spend confirmation")
    sp = sub.add_parser("score", help="re-score a saved run from disk; spends nothing")
    sp.add_argument("raw_dir", help="results/raw/<run_id>")
    sp.add_argument("--raw-match", action="store_true", help="byte-identical matching, no normalization")
    args = parser.parse_args()

    if args.cmd == "run" and args.concurrency is None:
        cfg, _ = load_config(required=True)
        args.concurrency = getattr(cfg, "DEFAULT_CONCURRENCY", 4)
    if getattr(args, "repeats", 1) < 1:
        parser.error("--repeats must be at least 1")
    return {"validate": cmd_validate, "estimate": cmd_estimate, "run": cmd_run, "score": cmd_score}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
