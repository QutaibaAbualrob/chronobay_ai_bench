"""Reference-number matching.

strict  — the answer is the ground-truth reference, after normalizing notation:
          uppercase; spaces . - / removed; Rolex catalog form "M126610LN-0001"
          read as "126610LN"; JLC shop code "JLQ1368430" read as "Q1368430".
lenient — strict, OR a look-alike listed in the row's also_accept, OR the same
          watch on a different strap/bracelet, for the brands whose reference
          encodes the strap in a known position (TAG Heuer, Breitling, Omega,
          Audemars Piguet).

raw=True turns every normalization off: byte-identical comparison only.
"""
from __future__ import annotations

import re

_NOISE = re.compile(r"[\s.\-/]")
_REF_PREFIX = re.compile(r"^REF(ERENCE)?\.?\s*(NO\.?|NUMBER)?\s*[:#]?\s*")


def normalize(ref: str | None) -> str:
    return _NOISE.sub("", (ref or "").upper())


def canonical(brand: str, ref: str | None) -> str:
    s = (ref or "").strip().upper()
    s = _REF_PREFIX.sub("", s)
    if brand == "Rolex":
        s = re.sub(r"^M(?=\d)", "", s)
        s = re.sub(r"-\d{4}$", "", s)
    elif brand == "Jaeger-LeCoultre":
        s = re.sub(r"^JL(?=Q)", "", s)
    return normalize(s)


def strap_family(brand: str, ref: str | None) -> str | None:
    """The reference with its strap/bracelet code masked, or None if the brand
    doesn't encode the strap in a fixed position (or the answer doesn't parse)."""
    n = canonical(brand, ref)
    if brand == "Tag Heuer" and re.fullmatch(r"[A-Z0-9]{7}[A-Z]{2}\d{4}", n):
        return n[:7]                              # WBP201A.BA0632 → WBP201A
    if brand == "Breitling" and re.fullmatch(r"[A-Z]{1,2}[0-9A-Z]{7,9}[A-Z]\d[A-Z]\d", n):
        return n[:-2]                             # AB0138211B1A1 → AB0138211B1
    if brand == "Omega" and re.fullmatch(r"\d{14}", n):
        return n[:4] + n[5:]                      # 2nd digit of group 2: 0 bracelet, 2/3 strap
    if brand == "Audemars Piguet":
        m = re.fullmatch(r"(\d{5}[A-Z]{2})([A-Z]{2})([A-Z0-9]{6})(\d{2})", n)
        if m:                                     # 15500ST.OO.1220ST.01 → drop 1220ST
            return m.group(1) + m.group(2) + m.group(4)
    return None


def match(brand: str, truth: str, also_accept: list[str], answer: str | None,
          raw: bool = False) -> tuple[bool, bool, str | None]:
    """Returns (strict, lenient, reason the lenient score accepted a non-strict answer)."""
    if not answer:
        return False, False, None
    if raw:
        if answer == truth:
            return True, True, None
        return False, answer in also_accept, ("look-alike" if answer in also_accept else None)

    got = canonical(brand, answer)
    if got and got == canonical(brand, truth):
        return True, True, None
    if got in {canonical(brand, a) for a in also_accept}:
        return False, True, "look-alike"
    fam = strap_family(brand, answer)
    if fam is not None and fam in {strap_family(brand, r) for r in [truth, *also_accept]}:
        return False, True, "strap variant"
    return False, False, None
