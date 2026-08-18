"""
Mapping cache for the Specialty Mapper.

Stores LLM-derived mappings in a local SQLite database so recurring inputs are
served from the cache instead of the LLM.

Value:
- Determinism: the same normalized input always returns the same mapping
  (the LLM is non-deterministic even at low temperature; the cache freezes
  the first result so a data pipeline sees stable answers).
- Compounding data asset: every real-world label that has been mapped becomes
  a persistent, versioned, auditable entry.
- Performance: cache lookup is ~1ms vs ~1-2s per LLM call. At claim-pipeline
  scale with high label repetition, hit rates are typically 80-95%.

Design:
- Key = normalized input (lowercase, collapsed whitespace).
- Each row is tagged with the NUCC taxonomy version it was produced under.
  On taxonomy version bump, rows from the old version are treated as a MISS
  (soft invalidation) so the LLM re-derives them; the old rows are retained
  for audit and are only overwritten by a new same-version result.
- Null results (no medical connotation) are cached too — a null is a valid,
  deliberate answer and should be reproducible.
- Confidence is stored as produced. Low-confidence entries are cached for
  determinism; a consumer pipeline can still route on the stored confidence.
  A manual override is an operator concern (edit/delete the row) and is not
  exposed via the API in this version.
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

_DB_PATH = Path(__file__).parent / "mapping_cache.sqlite3"

# Bumped here on a formal NUCC taxonomy version upgrade (keep in sync with the
# CSV filename in main.py, e.g. nucc_taxonomy_251.csv -> v25.1 -> "25.1").
NUCC_TAXONOMY_VERSION = "25.1"


def _connect():
    conn = sqlite3.connect(_DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def init_cache():
    """Create tables if they do not exist."""
    conn = _connect()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS mapping_cache (
                input_key   TEXT NOT NULL,
                nucc_code   TEXT,
                nucc_name   TEXT,
                confidence  REAL NOT NULL,
                notes       TEXT,
                nucc_version TEXT NOT NULL,
                created_at  TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at  TEXT NOT NULL DEFAULT (datetime('now')),
                PRIMARY KEY (input_key, nucc_version)
            );
            CREATE TABLE IF NOT EXISTS cache_meta (
                key   TEXT PRIMARY KEY,
                value TEXT
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def normalize_input(text: str) -> str:
    """Normalize a free-text input into a cache key."""
    return re.sub(r"\s+", " ", (text or "")).strip().lower()


def _row_to_dict(row) -> dict:
    (input_key, nucc_code, nucc_name, confidence, notes, nucc_version,
     created_at, updated_at) = row
    return {
        "input_key": input_key,
        "nucc_code": nucc_code,
        "nucc_name": nucc_name,
        "confidence": confidence,
        "notes": notes,
        "nucc_version": nucc_version,
        "created_at": created_at,
        "updated_at": updated_at,
    }


def lookup(normalized_input: str) -> dict | None:
    """Return the cached mapping for an input under the current taxonomy
    version, or None (a miss, including stale-version rows).

    The argument is normalized internally (idempotently), so callers may pass
    raw or already-normalized input.
    """
    key = normalize_input(normalized_input)
    conn = _connect()
    try:
        row = conn.execute(
            """
            SELECT input_key, nucc_code, nucc_name, confidence, notes,
                   nucc_version, created_at, updated_at
            FROM mapping_cache
            WHERE input_key = ? AND nucc_version = ?
            """,
            (key, NUCC_TAXONOMY_VERSION),
        ).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        conn.close()


def batch_lookup(inputs: list[str]) -> dict:
    """Look up many inputs at once.

    Returns:
        {
            "hits":  {normalized_input: cached_dict, ...},
            "misses": [original_input, ...],  # unique, in first-seen order
            "duplicate_inputs": {original_input: canonical_original, ...},
        }
    """
    conn = _connect()
    try:
        # Dedupe by normalized key; keep the first-seen original for each key.
        orig_by_key = {}    # normalized key -> first-seen original
        key_order = []      # normalized keys in first-seen order
        for orig in inputs:
            key = normalize_input(orig)
            if key not in orig_by_key:
                orig_by_key[key] = orig
                key_order.append(key)

        # Duplicate inputs: each repeated original maps to its first-seen twin.
        duplicate_inputs = {}
        seen = set()
        for orig in inputs:
            key = normalize_input(orig)
            if key in seen:
                duplicate_inputs[orig] = orig_by_key[key]
            else:
                seen.add(key)

        keys = key_order
        placeholders = ",".join("?" * len(keys)) if keys else "NULL"
        rows = []
        if keys:
            rows = conn.execute(
                f"""
                SELECT input_key, nucc_code, nucc_name, confidence, notes,
                       nucc_version, created_at, updated_at
                FROM mapping_cache
                WHERE input_key IN ({placeholders}) AND nucc_version = ?
                """,
                keys + [NUCC_TAXONOMY_VERSION],
            ).fetchall()

        hits = {_row_to_dict(r)["input_key"]: _row_to_dict(r) for r in rows}

        # Misses are the unique originals whose normalized key is not cached.
        misses = [orig_by_key[key] for key in key_order if key not in hits]

        return {"hits": hits, "misses": misses, "duplicate_inputs": duplicate_inputs}
    finally:
        conn.close()


def store(original_input: str, nucc_code, nucc_name, confidence: float,
          notes: str = "") -> dict:
    """Upsert a mapping for an input under the current taxonomy version.

    Returns the stored row as a dict.
    """
    key = normalize_input(original_input)
    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO mapping_cache
                (input_key, nucc_code, nucc_name, confidence, notes,
                 nucc_version)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT (input_key, nucc_version) DO UPDATE SET
                nucc_code    = excluded.nucc_code,
                nucc_name    = excluded.nucc_name,
                confidence   = excluded.confidence,
                notes        = excluded.notes,
                updated_at   = datetime('now')
            """,
            (key, nucc_code, nucc_name, float(confidence), notes or "",
             NUCC_TAXONOMY_VERSION),
        )
        conn.commit()
        row = conn.execute(
            """
            SELECT input_key, nucc_code, nucc_name, confidence, notes,
                   nucc_version, created_at, updated_at
            FROM mapping_cache
            WHERE input_key = ? AND nucc_version = ?
            """,
            (key, NUCC_TAXONOMY_VERSION),
        ).fetchone()
        return _row_to_dict(row)
    finally:
        conn.close()


def delete(normalized_input: str) -> bool:
    """Remove a cached entry under the current taxonomy version (override).

    The argument is normalized internally (idempotently)."""
    key = normalize_input(normalized_input)
    conn = _connect()
    try:
        cur = conn.execute(
            "DELETE FROM mapping_cache WHERE input_key = ? AND nucc_version = ?",
            (key, NUCC_TAXONOMY_VERSION),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def stats() -> dict:
    """Return cache statistics for the current taxonomy version."""
    conn = _connect()
    try:
        total = conn.execute(
            "SELECT COUNT(*) FROM mapping_cache WHERE nucc_version = ?",
            (NUCC_TAXONOMY_VERSION,),
        ).fetchone()[0]
        nulls = conn.execute(
            "SELECT COUNT(*) FROM mapping_cache WHERE nucc_version = ? AND nucc_code IS NULL",
            (NUCC_TAXONOMY_VERSION,),
        ).fetchone()[0]
        stale = conn.execute(
            "SELECT COUNT(*) FROM mapping_cache WHERE nucc_version != ?",
            (NUCC_TAXONOMY_VERSION,),
        ).fetchone()[0]
        version = conn.execute(
            "SELECT value FROM cache_meta WHERE key = 'taxonomy_version'"
        ).fetchone()
        return {
            "nucc_version": NUCC_TAXONOMY_VERSION,
            "cached_current_version": total,
            "cached_nulls_current_version": nulls,
            "stale_other_versions": stale,
            "db_path": str(_DB_PATH),
        }
    finally:
        conn.close()
