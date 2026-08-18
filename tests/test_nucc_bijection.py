"""NUCC taxonomy invariants — the keystone fact the eval spec depends on.

The NUCC-native eval (EVAL_HARNESS_SPEC.md) treats the taxonomy itself as the
ground-truth answer key: 883 display names -> their own codes, a verified
bijection. These tests guard that invariant so a taxonomy edit that breaks the
bijection fails the suite instead of silently contaminating Number A.
"""
import csv
import re

import main  # demo.main — safe to import (no network at import time)

NUCC_CSV = main.NUCC_CSV


def _norm(n: str) -> str:
    return re.sub(r"\s+", " ", n or "").strip().lower()


def _rows():
    with open(NUCC_CSV, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_rows_count_is_883():
    assert len(_rows()) == 883


def test_codes_are_distinct():
    codes = [r["Code"] for r in _rows()]
    assert len(codes) == len(set(codes)), "NUCC codes must be unique"


def test_display_name_code_bijection():
    """Every display name maps to exactly one code and vice versa.

    This is what makes the taxonomy a clean self-contained answer key. If a
    display name ever maps to two codes (or a code to two names), the eval's
    ground truth becomes ambiguous and this test is the tripwire.
    """
    name2code, code2name = {}, {}
    for r in _rows():
        n, c = _norm(r["Display Name"]), r["Code"]
        assert n, "blank display name present"
        assert c, "blank code present"
        assert n not in name2code, f"display name maps to >1 code: {n!r}"
        assert c not in code2name, f"code maps to >1 display name: {c!r}"
        name2code[n] = c
        code2name[c] = n
    assert len(name2code) == 883
    assert len(code2name) == 883


def test_resolve_code_round_trips_all_names():
    """resolve_code() must recover every display name via exact normalized
    lookup (link B — deterministic, never LLM)."""
    for r in _rows():
        row = main.resolve_code(r["Display Name"])
        assert row is not None, f"resolve_code failed for {r['Display Name']!r}"
        assert row["Code"] == r["Code"]


def test_resolve_code_fuzzy_absorbs_minor_drift():
    """A small misspelling still resolves (difflib cutoff 0.97)."""
    # Dropping the trailing "t" still lands on "Physical Therapist".
    row = main.resolve_code("Physical Therapis")
    assert row is not None
    assert row["Display Name"] == "Physical Therapist"


def test_resolve_code_link_b_does_not_do_semantic_mapping():
    """resolve_code() is link B only — exact + 0.97 fuzzy, NOT a synonym resolver.

    A colloquial title that isn't a display name (and isn't a near-miss of one)
    returns None: that semantic hop is the LLM's job (link A), which picks the
    display name; the code is then a pure dataset lookup. This is the deliberate
    boundary that keeps link B deterministic.
    """
    assert main.resolve_code("Cardiologist") is None


def test_resolve_code_unknown_returns_none():
    assert main.resolve_code("zzz not a real specialty zzz") is None
    assert main.resolve_code("") is None
