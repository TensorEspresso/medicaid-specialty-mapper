"""Mapping store (cache.py) — deterministic, idempotent, non-destructive.

These tests use a unique throwaway key and delete it at the end, so they never
mutate the live cache's real rows. The store's rules under test are the ones
documented in AGENTS.md:
  - key = normalize_input (lowercase, collapsed whitespace)
  - keyed by (input_key, nucc_version)
  - nulls are valid, cached answers
  - store() upserts; delete() returns True/False
"""
import uuid

import cache

# A key that cannot collide with real labels or prior test runs.
KEY = f"_pytest_{uuid.uuid4().hex}"


def test_normalize_input_collapses_whitespace_and_lowercases():
    assert cache.normalize_input("  Cardio  logist ") == "cardio logist"
    assert cache.normalize_input("Cardiologist\nDermatologist") == "cardiologist dermatologist"
    assert cache.normalize_input("") == ""


def test_store_lookup_delete_round_trip():
    # Miss before storing.
    assert cache.lookup(KEY) is None

    # Store a non-null mapping, then read it back (idempotent lookup: raw or
    # normalized key both work because lookup() normalizes internally).
    cache.store(KEY, "207RC0000X", "Cardiovascular Disease Physician", 0.98, "test")
    row = cache.lookup(KEY)
    assert row is not None
    assert row["input_key"] == cache.normalize_input(KEY)
    assert row["nucc_code"] == "207RC0000X"
    assert row["confidence"] == 0.98
    assert row["nucc_version"] == cache.NUCC_TAXONOMY_VERSION

    # Upsert: storing again updates in place, no duplicate row.
    cache.store(KEY, "207RC0000X", "Cardiovascular Disease Physician", 0.99, "test v2")
    assert cache.lookup(KEY)["confidence"] == 0.99

    # delete() is True for present, False for absent (idempotent key).
    assert cache.delete(KEY) is True
    assert cache.delete(KEY) is False
    assert cache.lookup(KEY) is None


def test_nulls_are_cached_as_valid_answers():
    """A null code is a deliberate answer and must round-trip."""
    null_key = f"_pytest_null_{uuid.uuid4().hex}"
    cache.store(null_key, None, None, 0.0, "no medical connotation")
    row = cache.lookup(null_key)
    assert row is not None
    assert row["nucc_code"] is None
    assert row["confidence"] == 0.0
    cache.delete(null_key)


def test_batch_lookup_separates_hits_and_misses():
    hit_key = f"_pytest_hit_{uuid.uuid4().hex}"
    miss_key = f"_pytest_miss_{uuid.uuid4().hex}"
    cache.store(hit_key, "208500000X", "Gastroenterology Physician", 0.9)

    result = cache.batch_lookup([hit_key, miss_key, hit_key])
    assert hit_key in result["hits"]
    assert miss_key in result["misses"]
    # Duplicate original (hit_key twice) maps to its first-seen twin.
    assert hit_key in result["duplicate_inputs"]

    cache.delete(hit_key)


def test_stats_shape():
    s = cache.stats()
    assert s["nucc_version"] == cache.NUCC_TAXONOMY_VERSION
    assert "cached_current_version" in s
    assert "db_path" in s
