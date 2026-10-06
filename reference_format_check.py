"""Test the decoding rules in REFERENCE_FORMATS.md. No API calls.

    python reference_format_check.py

Test 1 runs the rules against the answer key (dataset/ground_truth.csv).
Test 2 runs them against references outside the answer key, whose details were
taken from WatchBase and brand or retailer pages on 2026-10-06.
"""
from __future__ import annotations

import re
from collections import defaultdict

import bench


def answer_key_test() -> tuple[int, int, list[str]]:
    rows, _ = bench.load_rows()
    ok = n = 0
    bad: list[str] = []

    def add(r, rule, expect, actual):
        nonlocal ok, n
        n += 1
        if actual in expect:
            ok += 1
        else:
            bad.append(f"#{r['id']} {r['reference_number']} - {rule}: rule says {expect}, key says {actual}")

    for r in rows:
        ref, b = r["reference_number"], r["brand"]
        case, strap, mov = r["case_material"], r["bracelet_material"], r["movement"]
        non_metal = ("leather", "rubber", "fabric", "nylon")
        if b == "Rolex":
            d = re.match(r"(\d+)", ref).group(1)[-1]
            add(r, "last digit = metal", {"0": ("stainless-steel",), "1": ("stainless-steel", "gold"),
                                           "2": ("stainless-steel", "platinum"), "3": ("stainless-steel", "gold"),
                                           "4": ("stainless-steel", "gold"), "5": ("gold",), "6": ("platinum",),
                                           "8": ("gold",), "9": ("gold",)}[d], case)
        elif b == "Omega":
            g = ref.split(".")
            add(r, "strap digit", ("metal",) if g[1][1] == "0" else non_metal, strap)
            add(r, "metal digit", {"1": ("stainless-steel",), "3": ("stainless-steel",), "9": ("ceramic", "titanium"),
                                    "2": ("stainless-steel", "gold"), "5": ("gold",), "6": ("gold",)}[g[1][0]], case)
            size = re.search(r"\b(3\d|4\d)\b", r["model_family"])
            if size:
                add(r, "diameter", (size.group(1),), g[2])
        elif b == "Patek Philippe":
            m = re.match(r"\d{4}(/\d+)?([A-Z]+)-\d{3}", ref)
            add(r, "metal letter", ({"A": "stainless-steel", "G": "gold", "R": "gold", "J": "gold", "P": "platinum",
                                     "T": "titanium"}[m.group(2)],), case)
            add(r, "slash = bracelet", ("metal",) if m.group(1) else ("leather", "rubber"), strap)
        elif b == "Audemars Piguet":
            p = ref.split(".")
            add(r, "metal letters", ({"ST": "stainless-steel", "OR": "gold", "BC": "gold", "BA": "gold", "CE": "ceramic",
                                      "TI": "titanium", "PT": "platinum"}[p[0][5:]],), case)
            add(r, "third block", ("metal",) if p[2][0].isdigit() else ({"CR": "leather", "CA": "rubber"}.get(p[2][-2:], "?"),), strap)
        elif b == "Tag Heuer":
            head, tail = ref.split(".")
            add(r, "movement digit", {"1": ("quartz", "solar"), "2": ("automatic",)}[head[3]], mov)
            add(r, "strap letters", ("metal",) if tail[0] == "B" else ({"FC": "leather", "FT": "rubber"}[tail[:2]],), strap)
            add(r, "metal digit", ({"1": "stainless-steel", "8": "titanium", "9": "titanium"}.get(head[5], "?"),), case)
        elif b == "Breitling":
            add(r, "metal letter", ({"A": "stainless-steel", "E": "titanium"}[ref[0]],), case)
            add(r, "strap code", {"A1": ("metal",), "E1": ("metal",), "P1": ("leather",), "X1": ("leather", "fabric"),
                                   "S1": ("rubber",)}[ref[-2:]], strap)
            cal = ref[1:3]
            add(r, "quartz calibre", ("quartz",) if cal.isdigit() and int(cal) >= 50 else ("automatic",), mov)
        elif b == "Cartier":
            if re.match(r"W[A-Z]{3}\d{4}$", ref):
                add(r, "metal letter", ({"S": "stainless-steel", "G": "gold"}[ref[1]],), case)
        elif b == "Jaeger-LeCoultre":
            add(r, "metal digit", ({"8": "stainless-steel", "2": "gold"}.get(ref[4], "?"),), case)
            add(r, "strap digit", ({"1": "metal", "4": "leather", "5": "leather"}.get(ref[5], "?"),), strap)
        elif b == "Vacheron Constantin":
            m = re.match(r"\d{4,5}[A-Z]?/(\d{3})([A-Z])-", ref)
            add(r, "metal letter", ({"A": "stainless-steel", "R": "gold", "G": "gold", "J": "gold", "P": "platinum"}[m.group(2)],), case)
            add(r, "000 = strap", ("leather", "rubber") if m.group(1) == "000" else ("metal",), strap)
    return ok, n, bad


# ── Test 2 data: references outside the answer key ───────────────────────────
S, B = "strap", "bracelet"
X = [
    ("Omega", "220.12.41.21.03.001", dict(metal="steel", dial="blue", strap=S, size="41")),
    ("Omega", "220.12.41.21.03.007", dict(metal="steel", dial="blue", strap=S, size="41")),
    ("Omega", "220.23.38.20.03.001", dict(metal="steel+gold", dial="blue", strap=S, size="38")),
    ("Omega", "220.52.41.21.03.001", dict(metal="gold", dial="blue", strap=S, size="41")),
    ("Omega", "310.32.42.50.01.002", dict(metal="steel", dial="black", strap=S)),
    ("Omega", "310.32.42.50.01.001", dict(metal="steel", dial="black", strap=S)),
    ("Omega", "310.30.42.50.04.001", dict(metal="steel", dial="white", strap=B)),
    ("Omega", "310.60.42.50.01.002", dict(metal="gold", dial="black")),
    ("Longines", "L3.810.4.53.0", dict(strap=S)),
    ("Longines", "L3.810.4.53.6", dict(strap=B)),
    ("Longines", "L3.810.4.93.6", dict(strap=B)),
    ("Longines", "L3.810.4.03.6", dict(strap=B)),
    ("Longines", "L3.810.1.53.6", dict(strap=B, metal="titanium")),
    ("Longines", "L3.781.4.56.6", dict(strap=B, metal="steel")),
    ("Longines", "L3.781.4.56.9", dict(strap=S, metal="steel")),
    ("Longines", "L3.781.4.96.6", dict(strap=B, metal="steel")),
    ("Longines", "L3.781.4.96.9", dict(strap=S, metal="steel")),
    ("Longines", "L3.781.4.76.9", dict(strap=S, metal="steel")),
    ("Longines", "L3.781.4.76.6", dict(strap=B, metal="steel")),
    ("Longines", "L3.774.4.50.6", dict(strap=B, metal="steel")),
    ("Breitling", "A17375E71C1S1", dict(metal="steel", dial="blue", strap="rubber")),
    ("Breitling", "A17375E71C1A1", dict(metal="steel", dial="blue", strap=B)),
    ("Breitling", "R17375211B1S1", dict(metal="red gold", dial="black", strap="rubber")),
    ("Breitling", "A17375211B2S1", dict(metal="steel", dial="black", strap="rubber")),
    ("Breitling", "A17375A71A1S1", dict(metal="steel", dial="white")),
    ("Breitling", "A173751C1B1S1", dict(metal="steel", dial="black")),
    ("Breitling", "U173752A1B1S1", dict(metal="steel+gold", dial="black")),
    ("Breitling", "AB0138241C1A1", dict(metal="steel", dial="blue", strap=B)),
    ("Jaeger-LeCoultre", "9008480", dict(metal="steel", strap=S)),
    ("Jaeger-LeCoultre", "9008471", dict(metal="steel", strap=S)),
    ("Jaeger-LeCoultre", "9008170", dict(metal="steel", strap=B)),
    ("Jaeger-LeCoultre", "9068170", dict(metal="steel", strap=B)),
    ("Jaeger-LeCoultre", "9028471", dict(metal="steel", strap=S)),
    ("Jaeger-LeCoultre", "9068180", dict(metal="steel", strap=B)),
    ("Jaeger-LeCoultre", "Q9088180", dict(metal="steel", strap=B)),
    ("Jaeger-LeCoultre", "2548520", dict(metal="steel", strap=S)),
    ("Jaeger-LeCoultre", "2438520", dict(metal="steel", strap=S)),
    ("Jaeger-LeCoultre", "3848420", dict(metal="steel", strap=S)),
    ("Jaeger-LeCoultre", "3842520", dict(metal="pink gold", strap=S)),
    ("Jaeger-LeCoultre", "2538120", dict(metal="steel", strap=B)),
    ("Vacheron Constantin", "4500V/000R-B127", dict(metal="pink gold")),
    ("Vacheron Constantin", "4500V/110R-B705", dict(metal="pink gold")),
    ("Vacheron Constantin", "5500V/000R-B074", dict(metal="pink gold")),
    ("Vacheron Constantin", "4520V/210R-B705", dict(metal="pink gold")),
    ("Vacheron Constantin", "5500V/110A-B075", dict(metal="steel")),
    ("Vacheron Constantin", "4520V/210A-B126", dict(metal="steel")),
    ("Vacheron Constantin", "4520V/210A-B483", dict(metal="steel")),
    ("Vacheron Constantin", "4500V/000M-B127", dict(metal="steel+gold")),
    ("Vacheron Constantin", "5500V/000M-B074", dict(metal="steel+gold")),
    ("Patek Philippe", "5167/1A-001", dict(metal="steel", strap=B)),
    ("Patek Philippe", "5167R-001", dict(metal="rose gold", strap=S)),
    ("Patek Philippe", "5711/1P-010", dict(metal="platinum")),
    ("Patek Philippe", "5711/1A-011", dict(metal="steel")),
    ("Patek Philippe", "5711J-001", dict(metal="yellow gold")),
    ("Patek Philippe", "5711R-001", dict(metal="rose gold")),
    ("Patek Philippe", "5067A-001", dict(metal="steel")),
    ("Audemars Piguet", "15500OR.OO.D002CR.01", dict(metal="pink gold", strap=S)),
    ("Audemars Piguet", "15500OR.OO.1220OR.01", dict(metal="pink gold", strap=B)),
    ("Audemars Piguet", "15210BC.OO.A321CR.01", dict(metal="white gold")),
    ("Audemars Piguet", "15210OR.OO.A002CR.01", dict(metal="pink gold")),
    ("Audemars Piguet", "15500ST.OO.1220ST.04", dict(metal="steel")),
    ("Audemars Piguet", "26530ST.OO.1220ST.01", dict(metal="steel")),
    ("Tudor", "79030N", dict(metal="steel")),
    ("Tudor", "79230B", dict(metal="steel")),
    ("Tudor", "79733N", dict(metal="steel+gold")),
    ("Tudor", "79363N", dict(metal="steel+gold")),
    ("Tudor", "79018V", dict(metal="yellow gold")),
    ("Rolex", "126331", dict(metal="steel+gold")),
    ("Rolex", "228206", dict(metal="platinum")),
    ("Cartier", "W2SA0009", dict(metal="steel+gold")),
    ("Cartier", "WGSA0029", dict(metal="gold")),
    ("Cartier", "WSSA0029", dict(metal="steel")),
    ("Zenith", "03.3100.3600/69.M3100", dict(metal="steel", strap=B)),
    ("Zenith", "03.3100.3600/21.M3100", dict(metal="steel", strap=B)),
    ("Zenith", "18.3100.3600/69.C920", dict(metal="rose gold", strap=S)),
    ("Zenith", "51.3100.3600/69.M3100", dict(metal="steel+gold", strap=B)),
    ("Zenith", "95.9000.670/78.M9000", dict(metal="titanium", strap=B)),
    ("Zenith", "03.2040.4061/69.C496", dict(metal="steel", strap=S)),
    ("Tissot", "T137.407.11.041.00", dict(strap=B)),
    ("Tissot", "T137.407.16.051.00", dict(strap="leather")),
    ("Tissot", "T137.407.33.021.00", dict(strap=B)),
    ("Tissot", "T120.407.17.041.00", dict(strap="rubber")),
    ("Tissot", "T120.407.37.051.00", dict(strap="rubber")),
    ("Certina", "C032.407.11.051.00", dict(strap=B)),
    ("Certina", "C032.407.17.051.00", dict(strap="rubber")),
    ("Hamilton", "H70455133", dict(strap=B, size="38")),
    ("Hamilton", "H70455533", dict(strap="leather", size="38")),
    ("Hamilton", "H70455733", dict(strap="leather", size="38")),
    ("Hamilton", "H70555533", dict(size="42")),
    ("Hamilton", "H69439931", dict(size="38")),
]


def decode(brand, ref):
    d = {}
    if brand == "Omega":
        g = ref.split(".")
        d["metal"] = {"1": "steel", "3": "steel", "2": "steel+gold", "5": "gold", "6": "gold", "9": "other"}[g[1][0]]
        d["strap"] = B if g[1][1] == "0" else S
        d["size"] = g[2]
        d["dial"] = {"01": "black", "02": "silver", "03": "blue", "04": "white"}.get(g[4])
    elif brand == "Longines":
        g = ref.split(".")
        d["metal"] = {"1": "titanium", "4": "steel", "5": "steel+gold", "6": "gold", "8": "pink gold"}.get(g[2])
        d["strap"] = {"6": B, "0": S, "2": S, "3": S, "4": S, "5": S, "9": S}.get(g[4])
    elif brand == "Breitling":
        d["metal"] = {"A": "steel", "E": "titanium", "R": "red gold", "U": "steel+gold"}.get(ref[0])
        d["dial"] = {"A": "white", "B": "black", "C": "blue", "G": "silver", "K": "red"}.get(ref[9])
        d["strap"] = {"A1": B, "E1": B, "S1": "rubber", "P1": "leather", "X1": S}.get(ref[-2:])
    elif brand == "Jaeger-LeCoultre":
        r = ref.lstrip("Q")
        d["metal"] = {"8": "steel", "2": "pink gold"}.get(r[3])
        d["strap"] = {"1": B, "4": S, "5": S}.get(r[4])
    elif brand == "Vacheron Constantin":
        m = re.match(r"\d{4,5}[A-Z]?/\d{3}([A-Z])-", ref)
        d["metal"] = {"A": "steel", "R": "pink gold", "G": "white gold", "J": "yellow gold", "P": "platinum",
                      "M": "steel+gold"}.get(m.group(1))
    elif brand == "Patek Philippe":
        m = re.match(r"\d{4}(/\d+)?([A-Z]+)-", ref)
        d["metal"] = {"A": "steel", "J": "yellow gold", "G": "white gold", "R": "rose gold", "P": "platinum"}.get(m.group(2))
        d["strap"] = B if (m.group(1) or "").startswith("/1") else S
    elif brand == "Audemars Piguet":
        p = ref.split(".")
        d["metal"] = {"ST": "steel", "OR": "pink gold", "BC": "white gold", "BA": "yellow gold"}.get(p[0][5:])
        d["strap"] = B if p[2][0].isdigit() else S
    elif brand in ("Tudor", "Rolex"):
        digit = re.match(r"\d+", ref).group(0)[-1]
        d["metal"] = {"0": "steel", "1": "steel+gold", "3": "steel+gold", "4": "steel+gold", "6": "platinum",
                      "8": "yellow gold"}.get(digit)
    elif brand == "Cartier":
        d["metal"] = {"S": "steel", "G": "gold", "2": "steel+gold"}.get(ref[1])
    elif brand == "Zenith":
        d["metal"] = {"03": "steel", "18": "rose gold", "51": "steel+gold", "95": "titanium"}.get(ref[:2])
        d["strap"] = {"M": B, "C": S, "R": S}.get(ref.rsplit(".", 1)[1][0])
    elif brand in ("Tissot", "Certina"):
        d["strap"] = {"1": B, "3": B, "6": "leather", "7": "rubber"}.get(ref.split(".")[2][1])
    elif brand == "Hamilton":
        d["size"] = {"4": "38", "5": "42"}.get(ref[3])
        d["strap"] = {"1": B, "5": "leather", "7": "leather"}.get(ref[6])
    return d


tally = defaultdict(lambda: [0, 0])
bad = []
for brand, ref, truth in X:
    got = decode(brand, ref)
    for k, v in truth.items():
        t = tally[(brand, k)]
        t[1] += 1
        if got.get(k) == v:
            t[0] += 1
        else:
            bad.append((brand, ref, k, "rule says", got.get(k), "page says", v))
ok1, n1, bad1 = answer_key_test()
print(f"Test 1 - answer key: {ok1} of {n1} checks agree")
for line in bad1:
    print("  MISMATCH", line)
print("Test 2 - references outside the answer key:")
per_brand = defaultdict(lambda: [0, 0, 0])
for brand, ref, truth in X:
    per_brand[brand][2] += 1
for (brand, k), (ok, n) in sorted(tally.items()):
    per_brand[brand][0] += ok
    per_brand[brand][1] += n
for brand, (ok, n, refs) in per_brand.items():
    detail = ", ".join(f"{k} {tally[(brand, k)][0]}/{tally[(brand, k)][1]}" for (b, k) in sorted(tally) if b == brand)
    print(f"  {brand:<20} {refs:>2} refs  {ok}/{n} checks   ({detail})")
print("TOTAL references:", len(X), "| checks:", sum(v[1] for v in tally.values()), "| agree:", sum(v[0] for v in tally.values()))
for b in bad:
    print("MISMATCH", b)

# Checks where the rule was read off this very reference: they show consistency, not a test.
DEFINING = {
    ("Omega", "310.60.42.50.01.002", "metal"), ("Longines", "L3.810.1.53.6", "metal"),
    ("Breitling", "R17375211B1S1", "metal"), ("Breitling", "U173752A1B1S1", "metal"),
    ("Vacheron Constantin", "4500V/000M-B127", "metal"),
    ("Hamilton", "H70455133", "strap"), ("Hamilton", "H70455533", "strap"), ("Hamilton", "H70455733", "strap"),
    ("Hamilton", "H70455133", "size"), ("Hamilton", "H70555533", "size"),
    ("Zenith", "03.2040.4061/69.C496", "metal"), ("Zenith", "03.2040.4061/69.C496", "strap"),
    ("Zenith", "03.3100.3600/69.M3100", "strap"), ("Zenith", "18.3100.3600/69.C920", "metal"),
    ("Zenith", "51.3100.3600/69.M3100", "metal"), ("Zenith", "95.9000.670/78.M9000", "metal"),
    ("Tissot", "T137.407.11.041.00", "strap"), ("Tissot", "T137.407.16.051.00", "strap"),
    ("Tissot", "T137.407.33.021.00", "strap"), ("Certina", "C032.407.17.051.00", "strap"),
    ("Tudor", "79733N", "metal"), ("Tudor", "79018V", "metal"),
}
tests = sum(1 for brand, ref, truth in X for k in truth if (brand, ref, k) not in DEFINING)
defining = sum(1 for brand, ref, truth in X for k in truth if (brand, ref, k) in DEFINING)
print("real tests:", tests, "| rule read off the same reference:", defining)
by = defaultdict(int)
for brand, ref, truth in X:
    for k in truth:
        if (brand, ref, k) not in DEFINING:
            by[brand] += 1
print("real tests by brand:", dict(by))
