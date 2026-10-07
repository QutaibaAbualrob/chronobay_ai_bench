"""A model that searches the web itself. (Idea 5: OpenAI's web search tool, GPT-6 Luna)

    python websearch_study.py run --ids 5,15,25 --yes       # a test run on a few photos
    python websearch_study.py run --yes                     # every photo
    python websearch_study.py run --no-search --yes         # same prompt and model with search switched off
    python websearch_study.py report [results/websearch/<run_id>]   # rebuild the report from saved answers, $0

One call per photo. The model gets the photo, may search the web up to a set
number of times, and answers with a description and up to three references.
There is no search code of ours in this flow and nothing is saved between runs:
every run pays OpenAI's search fee again.

Cost has two parts: the model's tokens, and OpenAI's fee per search. The API
does not report the fee, so it is worked out here from the number of searches.
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
from urllib.parse import urlparse

import bench
import detail_study
import pipeline_study as ps
import pricing
import report as bench_report
import schema
import scoring

WEB_DIR = bench.RESULTS_DIR / "websearch"
DEFAULT_MODEL = "gpt-6-luna"
SEARCH_FEE = 0.01                 # USD per search: $10.00 per 1,000 calls
FEE_CHECKED = "2026-10-06"        # https://developers.openai.com/api/docs/pricing
DEFAULT_MAX_SEARCHES = 3
TIMEOUT_S = 300                   # a call that searches takes longer than one that does not

SEARCH_INTRO = """You are identifying a wristwatch from a single photo, to pre-fill a listing on a luxury watch resale marketplace. You can search the web.

First look at the watch and decide the brand, the model line and what is visible. Then search for the manufacturer's exact reference number of this version: brand catalogue pages, watch databases such as WatchBase and Chrono24, and retailers list references with their dial, metal and strap. Check each candidate against what you see in the photo before you answer."""
PLAIN_INTRO = ps.DESCRIBE_PROMPT.split("\n\n", 1)[0]
FIELDS = ps.DESCRIBE_PROMPT.split("\n\n", 1)[1]          # the same field list as the pipeline's describing call


# Two ways of asking for references. "optional" is the pipeline's wording: a second or third only for
# versions the model cannot rule out. With it GPT-6 Luna gave a single reference on most photos, which
# leaves the seller nothing to tap when that one is wrong. "three" always asks for the two nearest
# alternatives as well.
_OPTIONAL_LINE = next(line for line in FIELDS.split("\n") if line.startswith("- references:"))
_THREE_LINE = ("- references: exactly three manufacturer reference numbers, most likely first, each in the brand's own "
               "official format (keep its dots, slashes and letters). The first is your best match for this exact "
               "version of the watch. The second and third are the two closest alternatives, the versions most "
               "easily confused with it: another dial or strap version, the previous generation, another size."
               "{from_search} For Rolex give the base reference (126334), not a catalogue suffix.")
RULES = ("three", "optional")
RULE_TEXT = {"three": "It was asked for exactly three references: its best match and the two nearest alternatives.",
             "optional": "It was asked for up to three references, a second or third only where it could not rule "
                         "a version out."}
RULE_SHORT = {"three": "always three", "optional": "up to three"}


def build_prompt(search: bool, rule: str = "three") -> str:
    fields = FIELDS
    if rule == "three":
        fields = FIELDS.replace(_OPTIONAL_LINE, _THREE_LINE.format(
            from_search=" Take them from what your search returned where you can." if search else ""))
    return (SEARCH_INTRO if search else PLAIN_INTRO) + "\n\n" + fields


# ── calling the model ────────────────────────────────────────────────────────

class Fatal(Exception):
    """An error every call would repeat."""


RATE_LIMIT_WAITS = 8              # times one photo waits out the tokens-per-minute limit before giving up


def _scrub(error) -> str:
    """An error message without the account's organisation id, which OpenAI prints in rate-limit errors."""
    return re.sub(r"org-[A-Za-z0-9]{6,}", "org-(removed)", str(error))


def ask(client, spec: dict, image: tuple[str, str], prompt: str, max_searches: int, mode: dict) -> dict:
    """One call. `mode["schema"]` says whether the answer format is enforced by the API; if the API refuses
    that together with search, the shape is asked for in the prompt instead, for the rest of the run."""
    import openai
    rec = {"parsed": None, "raw_text": None, "input_tokens": None, "output_tokens": None, "cached_input_tokens": 0,
           "reasoning_tokens": None, "token_cost_usd": None, "searches": 0, "page_opens": 0, "tool_calls": 0,
           "queries": [], "source_domains": [], "elapsed_s": 0.0,
           "started_at": datetime.now(timezone.utc).isoformat(), "error": None, "tidied": False}
    kwargs: dict = {}
    if spec.get("reasoning_effort"):
        kwargs["reasoning"] = {"effort": spec["reasoning_effort"]}
    if max_searches:
        kwargs.update(tools=[{"type": "web_search"}], include=["web_search_call.action.sources"],
                      extra_body={"max_tool_calls": max_searches})
    t0 = time.perf_counter()
    resp, waits = None, 0
    while True:
        text = prompt if mode["schema"] else prompt + ps.JSON_SHAPE["Description"]
        fmt = {"text": {"format": {"type": "json_schema", "name": "watch_identification", "strict": True,
                                   "schema": schema._strip_titles(ps.Description.model_json_schema())}}} if mode["schema"] else {}
        try:
            resp = client.responses.create(
                model=spec["model"], max_output_tokens=16000, **kwargs, **fmt,
                input=[{"role": "user", "content": [
                    {"type": "input_text", "text": text},
                    {"type": "input_image", "image_url": f"data:{image[1]};base64,{image[0]}", "detail": "high"}]}])
            break
        except (openai.AuthenticationError, openai.PermissionDeniedError) as e:
            raise Fatal(f"{type(e).__name__}: {_scrub(e)[:200]}") from e
        except openai.BadRequestError as e:
            message = str(e).lower()
            if mode["schema"] and max_searches and any(w in message for w in ("json_schema", "text.format", "structured")):
                mode["schema"] = False          # the API will not enforce the format while searching
                continue
            raise Fatal(f"HTTP 400: {_scrub(e)[:300]}") from e
        except openai.RateLimitError as e:
            if "insufficient_quota" in str(e):
                raise Fatal(f"No credit on the OpenAI account: {_scrub(e)[:200]}") from e
            # The account's tokens-per-minute limit. A search call carries 15,000 to 30,000 tokens of
            # retrieved text, so a few calls at once reach it. Wait and ask again rather than lose the photo.
            waits += 1
            if waits > RATE_LIMIT_WAITS:
                rec["error"] = f"rate limit after {RATE_LIMIT_WAITS} waits: {_scrub(e)[:200]}"
                break
            time.sleep(min(60, 15 * waits))
        except openai.APIError as e:
            rec["error"] = f"{type(e).__name__}: {_scrub(e)[:300]}"
            break
    rec["rate_limit_waits"] = waits
    rec["elapsed_s"] = round(time.perf_counter() - t0, 3)
    if resp is None:
        rec["error"] = rec["error"] or "no response"
        return rec

    data = resp.to_dict()
    rec["raw_response"] = data
    usage = data.get("usage") or {}
    rec["input_tokens"], rec["output_tokens"] = usage.get("input_tokens"), usage.get("output_tokens")
    rec["cached_input_tokens"] = (usage.get("input_tokens_details") or {}).get("cached_tokens") or 0
    rec["reasoning_tokens"] = (usage.get("output_tokens_details") or {}).get("reasoning_tokens")
    if rec["input_tokens"] is not None:
        rec["token_cost_usd"] = pricing.cost_usd("openai", spec["model"], rec["input_tokens"],
                                                 rec["output_tokens"] or 0, rec["cached_input_tokens"])
    domains: list[str] = []
    for item in data.get("output") or []:
        if item.get("type") != "web_search_call":
            continue
        rec["tool_calls"] += 1
        action = item.get("action") or {}
        if action.get("type") == "search":
            rec["searches"] += 1
            rec["queries"] += [q for q in (action.get("queries") or [action.get("query")]) if q]
            domains += [urlparse(s.get("url") or "").netloc.removeprefix("www.") for s in action.get("sources") or []]
        elif action.get("type") == "open_page":
            rec["page_opens"] += 1
            domains.append(urlparse(action.get("url") or "").netloc.removeprefix("www."))
    rec["source_domains"] = [d for d in dict.fromkeys(domains) if d]
    rec["search_requests"] = billed_searches(rec)
    rec["served_model"], rec["status"] = data.get("model"), data.get("status")
    rec["raw_text"] = resp.output_text
    if data.get("status") == "incomplete":
        rec["error"] = f"incomplete: {(data.get('incomplete_details') or {}).get('reason')}"
        return rec
    rec["parsed"], rec["tidied"], problem = ps.read_answer(rec["raw_text"], ps.Description)
    if rec["parsed"] is None:
        rec["error"] = problem
    return rec


def _answered(run_dir: Path, row_id: int) -> bool:
    path = run_dir / "answers" / f"{row_id:03d}.json"
    return path.exists() and bool(json.loads(path.read_text(encoding="utf-8"))["result"].get("parsed"))


def billed_searches(res: dict) -> int:
    """The number of searches OpenAI counts for one call. The response states it under
    `tool_usage.web_search.num_requests`: one request can hold several queries, and opening a page is not
    one. When that field is missing, the search actions in the output are counted instead."""
    reported = (((res.get("raw_response") or {}).get("tool_usage") or {}).get("web_search") or {}).get("num_requests")
    return reported if isinstance(reported, int) else (res.get("searches") or 0)


# ── run ──────────────────────────────────────────────────────────────────────

def cmd_run(args) -> int:
    import openai
    cfg, _ = bench.load_config(required=True)
    rows, problems = bench.load_rows()
    errors, _warnings = bench.validate(rows, problems)
    if errors:
        print("\n".join(errors[:20]))
        return 1
    if args.resume:                              # continue a run that stopped: same model, prompt and limit
        run_dir = Path(args.resume).resolve()
        meta = json.loads((run_dir / "meta.json").read_text(encoding="utf-8"))
        by_id = {r["id"]: r for r in rows}
        name, spec, searches, prompt = meta["model_name"], meta["spec"], meta["max_searches"], meta["prompt"]
        everything = [by_id[i] for i in meta["rows"]]
        selected = [r for r in everything if not _answered(run_dir, r["id"])]
    else:
        name = args.model
        spec = dict(getattr(cfg, "MODELS", {}).get(name) or {})
        if spec.get("provider") != "openai":
            print(f"{name} is not an OpenAI model in config.py. This script uses OpenAI's own web search.")
            return 1
        everything = selected = bench.select_rows(rows, args.ids, args.limit)
        searches = 0 if args.no_search else args.max_searches
        prompt = build_prompt(bool(searches), args.references)
    key = bench.api_key(cfg, "openai")
    if not key:
        print("No OPENAI_API_KEY in config.py or the environment.")
        return 1
    if not selected:
        print("Every photo of this run already has an answer.")
        write_report(run_dir, rows)
        write_index(rows)
        return 0
    kind = bench_report.run_kind(len(everything), len(rows))
    effort = spec.get("reasoning_effort") or "default"
    print(f"{kind['label']}: {name} ({effort} reasoning effort), "
          + (f"web search on, at most {searches} searches per photo." if searches else "web search off.")
          + (f" {len(selected)} photos still to do." if args.resume else ""))
    if searches:
        print(f"Estimated cost: up to ${len(selected) * searches * SEARCH_FEE:.2f} in search fees "
              f"(${SEARCH_FEE:.2f} a search, checked {FEE_CHECKED}), plus the model's tokens.")
    if not args.yes:
        if not sys.stdin.isatty():
            print("Not interactive - pass --yes to confirm spending.")
            return 1
        if input("Run it? [y/N] ").strip().lower() not in ("y", "yes"):
            print("Cancelled - nothing was spent.")
            return 1

    if not args.resume:
        now = datetime.now(timezone.utc)
        run_id = now.strftime("%Y-%m-%d_%H%M%S") + ("_nosearch" if not searches else "") + kind["suffix"]
        run_dir = WEB_DIR / run_id
        (run_dir / "answers").mkdir(parents=True)
        meta = {"run_id": run_id, "started_at": now.isoformat(), "model_name": name, "spec": spec,
                "max_searches": searches, "references_rule": args.references, "rows": [r["id"] for r in selected],
                "dataset_size": len(rows), "prompt": prompt, "search_fee_usd": SEARCH_FEE,
                "csv_sha256": bench._sha256(bench.CSV_PATH.read_bytes())}
        (run_dir / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Run folder: {bench._rel(run_dir)}\n")

    client = openai.OpenAI(api_key=key, max_retries=2, timeout=TIMEOUT_S)
    mode, done = {"schema": meta.get("format_enforced", True)}, 0

    def work(row: dict) -> dict:
        nonlocal done
        mime, _ = bench.check_image(row)
        image = (base64.standard_b64encode((bench.IMAGES_DIR / row["image_file"]).read_bytes()).decode(), mime)
        res = ask(client, spec, image, prompt, searches, mode)
        (run_dir / "answers" / f"{row['id']:03d}.json").write_text(json.dumps(
            {"row_id": row["id"], "image_file": row["image_file"], "result": res}, indent=1, ensure_ascii=False),
            encoding="utf-8")
        done += 1
        first = (ps.own_references(res["parsed"]) or ["-"])[0] if res["parsed"] else "-"
        ok = scoring.match(row["brand"], row["reference_number"], row["also_accept"], first)[0]
        mark = f"ERR {res['error'][:40]}" if res["error"] else ("ok " if ok else "no ")
        print(f"   {done:>3}/{len(selected)}  #{row['id']:<3} {mark:<4} first {first:<24} expected {row['reference_number']:<22} "
              f"searches {res['searches']}  {res['elapsed_s']:.1f}s", flush=True)
        return res

    try:
        first = work(selected[0])            # alone first: a bad key or a refused request stops the run here
        if searches and first["searches"] > 3 * searches:
            raise Fatal(f"the first photo used {first['searches']} searches although the limit was {searches}")
        with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
            for fut in as_completed([pool.submit(work, r) for r in selected[1:]]):
                fut.result()
    except Fatal as e:
        print(f"\nStopped: {e}\nWhat was saved is kept. Continue with --resume {bench._rel(run_dir)}")
        meta["format_enforced"] = mode["schema"]
        (run_dir / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
        return 1
    meta["format_enforced"] = mode["schema"]
    (run_dir / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    write_report(run_dir, rows)
    write_index(rows)
    return 0


# ── report ───────────────────────────────────────────────────────────────────

def _n(items, test) -> int:
    return sum(1 for i in items if test(i))


def analyse(run_dir: Path, rows: list[dict]) -> list[dict]:
    items = []
    for row in rows:
        path = run_dir / "answers" / f"{row['id']:03d}.json"
        if not path.exists():
            continue
        res = json.loads(path.read_text(encoding="utf-8"))["result"]
        if not res.get("parsed") and not res.get("raw_response"):
            continue        # the call never reached the model (rate limit, no credit): owed, not a wrong answer
        d = res.get("parsed") or {}
        own = ps.own_references(d) if d else []
        brand = d.get("brand")
        requests = billed_searches(res)
        fee = requests * SEARCH_FEE
        items.append({
            "row": row["id"], "brand": row["brand"], "truth": row["reference_number"], "own": own, "desc": d,
            "first": ps._right(row, brand, own[0] if own else None), "three": ps._any(row, brand, own),
            "place": next((k for k, ref in enumerate(own, 1) if ps._right(row, brand, ref)[0]), None),
            "brand_ok": brand == row["brand"], "searches": requests, "n_queries": len(res.get("queries") or []),
            "page_opens": res.get("page_opens") or 0, "tool_calls": res.get("tool_calls") or 0,
            "queries": res.get("queries") or [], "domains": res.get("source_domains") or [],
            "tokens_in": res.get("input_tokens") or 0, "tokens_out": res.get("output_tokens") or 0,
            "token_cost": res.get("token_cost_usd") or 0.0, "fee": fee, "cost": (res.get("token_cost_usd") or 0.0) + fee,
            "time": res.get("elapsed_s") or 0.0, "error": res.get("error"), "tidied": res.get("tidied")})
    return items


def saved_benchmark(rows: list[dict], models: list[str]) -> dict[str, set[int]]:
    """Rows each earlier benchmark run of these models got exactly right, for context."""
    latest = {}
    for run in detail_study.load_runs():
        latest[run["model"]] = run
    out = {}
    for m in models:
        if m in latest:
            out[m] = {r["id"] for r in rows if scoring.match(
                r["brand"], r["reference_number"], r["also_accept"],
                (latest[m]["answers"].get(r["id"]) or {}).get("reference_number"))[0]}
    return out


def to_markdown(meta: dict, rows: list[dict], items: list[dict]) -> str:
    n = len(items)
    kind = bench_report.run_kind(len(meta["rows"]), meta["dataset_size"])
    spec, cap = meta["spec"], meta["max_searches"]
    effort = spec.get("reasoning_effort") or "default"
    L = [f"# Web search study: the model searches for itself - {kind['label']}", "",
         "Idea 5 in `FINDINGS.md`, section 4. Rebuilt by `websearch_study.py report` from saved answers.", "",
         f"Run `{meta['run_id']}`, model `{meta['model_name']}` (`{spec['model']}`, {effort} reasoning effort). "
         + (f"OpenAI's web search tool was on, limited to {cap} searches per photo. " if cap else "Web search was off. ")
         + f"One call per photo. {n} photos. " + RULE_TEXT[meta.get("references_rule", "optional")], ""]
    if kind["kind"] == "test":
        L += ["> TEST RUN on part of the photos. It measures cost and whether the flow works. Its accuracy is not "
              "comparable with a full run: a few photos either way change the figure a lot.", ""]
    owed = [i for i in meta["rows"] if i not in {x["row"] for x in items}]
    if owed:
        L += [f"> **INCOMPLETE.** {len(owed)} of the {len(meta['rows'])} photos have no answer yet (rows "
              f"{', '.join(str(i) for i in owed)}): the run stopped before reaching them, or the call was refused "
              f"for rate limit or lack of credit. Every table below covers the {n} photos that have an answer. "
              "Continue the run with `--resume`.", ""]
    if meta.get("notes"):
        L += ["Notes on this run:", ""] + [f"- {note}" for note in meta["notes"]] + [""]
    L += ["## Result", "", f"Out of {n} photos.", "",
          "| | Exact reference | Also counting accepted look-alikes |", "|---|---:|---:|",
          f"| First reference is right | {_n(items, lambda i: i['first'][0])} | {_n(items, lambda i: i['first'][1])} |",
          f"| Its references, up to three, contain it | {_n(items, lambda i: i['three'][0])} | {_n(items, lambda i: i['three'][1])} |",
          f"| Brand right | {_n(items, lambda i: i['brand_ok'])} | |",
          "", f"Where the right reference stands in its list: first {_n(items, lambda i: i['place'] == 1)}, second "
              f"{_n(items, lambda i: i['place'] == 2)}, third {_n(items, lambda i: i['place'] == 3)}, not in it "
              f"{_n(items, lambda i: i['place'] is None)}. References given per photo: one "
              f"{_n(items, lambda i: len(i['own']) == 1)}, two {_n(items, lambda i: len(i['own']) == 2)}, three "
              f"{_n(items, lambda i: len(i['own']) == 3)}, none {_n(items, lambda i: not i['own'])}."]
    earlier = saved_benchmark([r for r in rows if r["id"] in {i["row"] for i in items}],
                              ["gpt-6-luna-nothink", "gpt-6-luna-xhigh", "deepseek-flash", "claude-sonnet-5-5-nothink"])
    if earlier:
        L += ["", "For context, the same photos in the saved benchmark runs (one reference, no search, a different "
                  "prompt): " + ", ".join(f"{m} {len(v)}" for m, v in earlier.items()) + " right."]

    times = sorted(i["time"] for i in items)
    fee, tokens = sum(i["fee"] for i in items), sum(i["token_cost"] for i in items)
    L += ["", "## Cost and speed", "", "| | Per photo | This run |", "|---|---:|---:|",
          f"| Searches made | {statistics.mean(i['searches'] for i in items):.1f} | {sum(i['searches'] for i in items)} |",
          f"| Pages opened | {statistics.mean(i['page_opens'] for i in items):.1f} | {sum(i['page_opens'] for i in items)} |",
          f"| Search fee at ${SEARCH_FEE:.2f} a search | ${fee / n:.4f} | ${fee:.2f} |",
          f"| Model tokens | ${tokens / n:.4f} | ${tokens:.2f} |",
          f"| **Total** | **${(fee + tokens) / n:.4f}** | **${fee + tokens:.2f}** |",
          f"| Input tokens | {statistics.mean(i['tokens_in'] for i in items):,.0f} | |",
          f"| Output tokens | {statistics.mean(i['tokens_out'] for i in items):,.0f} | |",
          f"| Time, median | {statistics.median(times):.1f}s | |",
          f"| Time, longest | {times[-1]:.1f}s | |", ""]
    if cap:
        over = _n(items, lambda i: i["searches"] > cap)
        L += ["Photos by number of searches: " + ", ".join(
                  f"{_n(items, lambda i, k=k: i['searches'] == k)} with {k} search{'' if k == 1 else 'es'}"
                  for k in sorted({i['searches'] for i in items})) + ". "
              + (f"{over} photos went over the limit of {cap}." if over else f"No photo went over the limit of {cap}."),
              "",
              "The number of searches is the one OpenAI's API reports for each call "
              "(`tool_usage.web_search.num_requests`). One search can hold several queries "
              f"({sum(i['n_queries'] for i in items)} queries in this run), and opening a page is not counted. The "
              f"fee is that number times ${SEARCH_FEE:.2f}, the listed price; the API does not report an amount in "
              "dollars, so the account's usage page has the last word.",
              f"At this rate all {meta['dataset_size']} photos would cost about "
              f"${(fee + tokens) / n * meta['dataset_size']:.2f}."]
    L += ["", f"Calls that failed: {_n(items, lambda i: i['error'])}. Answers tidied to fit the format: "
              f"{_n(items, lambda i: i['tidied'])}. Answer format enforced by the API: "
              f"{'yes' if meta.get('format_enforced', True) else 'no, it was asked for in the prompt'}."]

    L += ["", "## Every photo", "", "| Row | Expected | Its references | First right | In its three | Searches | "
          "Time | What it searched for |", "|---:|---|---|:-:|:-:|---:|---:|---|"]
    for i in items:
        refs = ", ".join(f"`{r}`" for r in i["own"]) or (f"error: {(i['error'] or '')[:50]}")
        q = "; ".join(i["queries"][:3]).replace("|", "/")
        L.append(f"| {i['row']} | `{i['truth']}` | {refs} | {'yes' if i['first'][0] else 'no'} | "
                 f"{'yes' if i['three'][0] else 'no'} | {i['searches']} | {i['time']:.0f}s | {ps._cut(q, 150)} |")
    sites: dict[str, int] = {}
    for i in items:
        for d in i["domains"]:
            sites[d] = sites.get(d, 0) + 1
    if sites:
        top = sorted(sites.items(), key=lambda kv: -kv[1])[:12]
        L += ["", "Sites its searches returned or it opened, by number of photos: "
              + ", ".join(f"{d} {c}" for d, c in top) + "."]
    L += ["", "## Limits", "",
          "- Nothing is saved between runs. A second run searches again, pays again and may get other results.",
          "- The photos came from the web, so a search can land on the page a photo was taken from.",
          "- One pass. Small differences between runs are noise."]
    return "\n".join(L) + "\n"


def write_report(run_dir: Path, rows: list[dict]) -> None:
    meta = json.loads((run_dir / "meta.json").read_text(encoding="utf-8"))
    by_id = {r["id"]: r for r in rows}
    selected = [by_id[i] for i in meta["rows"]]
    items = analyse(run_dir, selected)
    if not items:
        print("No saved answers in this run.")
        return
    (run_dir / "report.md").write_text(to_markdown(meta, selected, items), encoding="utf-8")
    n = len(items)
    fee, tokens = sum(i["fee"] for i in items), sum(i["token_cost"] for i in items)
    print(f"\n{meta['model_name']} - {n} photos, web search {'on' if meta['max_searches'] else 'off'}")
    print(f"  First reference right        {_n(items, lambda i: i['first'][0]):>3}")
    print(f"  Its three contain it         {_n(items, lambda i: i['three'][0]):>3}")
    print(f"  Searches per photo           {statistics.mean(i['searches'] for i in items):.1f}")
    print(f"  Cost: search fee ${fee:.2f} + tokens ${tokens:.2f} = ${fee + tokens:.2f}  (${(fee + tokens) / n:.4f} a photo)")
    print(f"Report: {bench._rel(run_dir / 'report.md')}")


def write_index(rows: list[dict]) -> None:
    """results/WEBSEARCH_STUDY.md: every run on one page, and search on against search off on shared photos."""
    by_id = {r["id"]: r for r in rows}
    runs = []
    for meta_path in sorted(WEB_DIR.glob("*/meta.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        items = analyse(meta_path.parent, [by_id[i] for i in meta["rows"] if i in by_id])
        if items:
            runs.append((meta, {i["row"]: i for i in items}))
    if not runs:
        return
    L = ["# Web search study: the model searches for itself", "",
         "Idea 5 in `FINDINGS.md`, section 4. Rebuilt by `websearch_study.py report` from saved answers.", "",
         "One call per photo to an OpenAI model. With search on, the model may search the web a limited number "
         "of times before it answers; with search off it answers from the photo alone. The answer is a "
         "description and up to three references.", "",
         "| Run | Model | Search | References asked for | Photos | First reference right | Its three contain it | "
         "Searches per photo | Cost per photo | Time, median |", "|---|---|---|---|---:|---:|---:|---:|---:|---:|"]
    for meta, items in runs:
        it = list(items.values())
        n = len(it)
        effort = meta["spec"].get("reasoning_effort") or "default"
        planned = len(meta["rows"])
        photos = str(n) if n == planned else f"{n} of {planned}"
        L.append(f"| [{meta['run_id']}](websearch/{meta['run_id']}/report.md) | {meta['model_name']} ({effort} effort) | "
                 f"{'on, limit ' + str(meta['max_searches']) if meta['max_searches'] else 'off'} | "
                 f"{RULE_SHORT[meta.get('references_rule', 'optional')]} | {photos} | "
                 f"{_n(it, lambda i: i['first'][0])} ({100 * _n(it, lambda i: i['first'][0]) / n:.0f}%) | "
                 f"{_n(it, lambda i: i['three'][0])} ({100 * _n(it, lambda i: i['three'][0]) / n:.0f}%) | "
                 f"{statistics.mean(i['searches'] for i in it):.1f} | ${statistics.mean(i['cost'] for i in it):.4f} | "
                 f"{statistics.median(i['time'] for i in it):.1f}s |")
    pairs = [(a, b) for a in runs for b in runs
             if a[0]["max_searches"] and not b[0]["max_searches"] and a[0]["spec"] == b[0]["spec"]
             and a[0].get("references_rule", "optional") == b[0].get("references_rule", "optional")
             and set(a[1]) & set(b[1])]
    if pairs:
        L += ["", "## Search on against search off, same photos", "",
              "Same model, same setting and the same way of asking for references. Only the photos both runs "
              "have are counted.", "",
              "| Search on | Search off | References asked for | Photos in both | First right: on | First right: off | "
              "Right with search only | Right without search only | Three contain it: on | Three contain it: off |",
              "|---|---|---|---:|---:|---:|---:|---:|---:|---:|"]
        for (ma, a), (mb, b) in pairs:
            both = sorted(set(a) & set(b))
            on = {r for r in both if a[r]["first"][0]}
            off = {r for r in both if b[r]["first"][0]}
            L.append(f"| `{ma['run_id']}` | `{mb['run_id']}` | {RULE_SHORT[ma.get('references_rule', 'optional')]} | "
                     f"{len(both)} | {len(on)} | {len(off)} | {len(on - off)} | {len(off - on)} | "
                     f"{sum(1 for r in both if a[r]['three'][0])} | {sum(1 for r in both if b[r]['three'][0])} |")
    L += ["", "Counts are exact references. A run on part of the photos is a test run: it shows cost and whether "
              "the flow works, and its accuracy moves a lot with one or two photos.",
          "", "The cost of a search run is the model's tokens plus OpenAI's fee of "
              f"${SEARCH_FEE:.2f} a search (price checked {FEE_CHECKED}), counted from what each response reports."]
    out = bench.RESULTS_DIR / "WEBSEARCH_STUDY.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"All runs side by side: {bench._rel(out)}")


def cmd_report(args) -> int:
    rows, problems = bench.load_rows()
    if problems:
        print("\n".join(problems))
        return 1
    runs = [Path(args.run_dir).resolve()] if args.run_dir else sorted(p.parent for p in WEB_DIR.glob("*/meta.json"))
    if not runs:
        print("No run under results/websearch/.")
        return 1
    for run_dir in runs:
        write_report(run_dir, rows)
    write_index(rows)
    return 0


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description="A model that searches the web itself, on the watch photos.")
    sub = parser.add_subparsers(dest="command", required=True)
    sp = sub.add_parser("run", help="call the model, then report")
    sp.add_argument("--model", default=DEFAULT_MODEL, help="an OpenAI model name from config.py")
    sp.add_argument("--limit", type=int, help="only N photos, spread across brands")
    sp.add_argument("--ids", help="only these row ids, e.g. 5,15,25")
    sp.add_argument("--max-searches", type=int, default=DEFAULT_MAX_SEARCHES, help="most searches per photo")
    sp.add_argument("--no-search", action="store_true", help="the same prompt and model with search off")
    sp.add_argument("--references", choices=RULES, default="three",
                    help="three: always ask for the best match and two alternatives; optional: the pipeline's wording")
    sp.add_argument("--resume", help="continue this run folder; only photos without an answer are done")
    sp.add_argument("--concurrency", type=int, default=2, help="calls at once; more than 2 reaches the tokens-per-minute limit when searching")
    sp.add_argument("--yes", action="store_true", help="skip the confirmation question")
    sp.set_defaults(func=cmd_run)
    sp = sub.add_parser("report", help="rebuild the reports from saved answers; no calls")
    sp.add_argument("run_dir", nargs="?", help="results/websearch/<run_id>; default: every run")
    sp.set_defaults(func=cmd_report)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
