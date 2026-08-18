"""
Specialty Mapper — FastAPI backend.

Mapping model: the LLM matches free-text input to a **NUCC Display Name** only.
The NUCC **code is never produced by the LLM** — it is resolved by direct lookup
in the NUCC dataset (display name → code).

Caching: every mapping is stored in a local SQLite cache (see cache.py). On a
request, recurring inputs are served from the cache and only the *misses* are
sent to the LLM. This gives deterministic output (the LLM is non-deterministic),
a compounding/auditable data asset, and ~1ms lookups vs ~1-2s LLM calls.
"""

import csv
import json
import difflib
import re
import sys
from pathlib import Path

import urllib.request
import urllib.error

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Make the sibling `cache` module importable regardless of launch method
# (uvicorn demo.main:app, direct demo/main.py, or run_server.py).
sys.path.insert(0, str(Path(__file__).resolve().parent))

from cache import (
    batch_lookup,
    store,
    delete as cache_delete,
    stats as cache_stats,
    normalize_input,
    init_cache,
    NUCC_TAXONOMY_VERSION,
)

app = FastAPI(title="Specialty Mapper")

# Paths
PROJECT_DIR = Path(__file__).parent
NUCC_CSV = PROJECT_DIR.parent / "data" / "nucc" / "nucc_taxonomy_251.csv"

# LLM config
LLM_BASE_URL = "http://10.0.0.228:8080/v1"
LLM_MODEL = "qwen-3.6-27b-mtp"
LLM_API_KEY = "***"

# Initialize the mapping cache (idempotent).
init_cache()

# Cache
_nucc_cache = None
_name_index = None  # normalized display name -> row


def load_nucc():
    """Load NUCC taxonomy into memory."""
    global _nucc_cache, _name_index
    if _nucc_cache is not None:
        return _nucc_cache

    rows = []
    name_index = {}
    with open(NUCC_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            key = normalize_name(row.get("Display Name", ""))
            if key and key not in name_index:
                name_index[key] = row
    _nucc_cache = rows
    _name_index = name_index
    return rows


def normalize_name(name: str) -> str:
    """Normalize a display name for deterministic lookup."""
    return re.sub(r"\s+", " ", name).strip().lower()


def resolve_code(display_name: str):
    """Resolve a NUCC Display Name to its code via direct dataset lookup.

    Exact normalized match first, then close fuzzy match (cutoff 0.97) to
    absorb minor spelling/wording drift. Returns the taxonomy row or None.
    """
    global _name_index
    load_nucc()
    if _name_index is None:
        return None
    if not display_name:
        return None
    key = normalize_name(display_name)
    row = _name_index.get(key)
    if row:
        return row
    matches = difflib.get_close_matches(key, _name_index.keys(), n=1, cutoff=0.97)
    if matches:
        return _name_index[matches[0]]
    return None


def build_reference_context() -> str:
    """Build a NUCC display-name reference for the LLM prompt.

    Deliberately omits codes — the LLM outputs display names only, and the
    code is resolved from the dataset server-side.
    """
    nucc = load_nucc()
    lines = ["NUCC Taxonomy Display Names (Name | Classification):"]
    for row in nucc:
        name = row.get("Display Name", "")
        classification = row.get("Classification", "")
        lines.append(f"  {name} | {classification}")
    return "\n".join(lines)


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """Call the LLM API directly (reasoning disabled)."""
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "chat_template_kwargs": {"enable_thinking": False},
        "temperature": 0.1,
        "max_tokens": 8192,
    }

    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LLM_API_KEY}",
    }

    url = f"{LLM_BASE_URL}/chat/completions"
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
    except urllib.error.URLError as e:
        raise HTTPException(status_code=502, detail=f"LLM error: {e}")


def parse_response(text: str) -> list:
    """Parse the LLM response into structured results."""
    text = text.strip()

    if "```" in text:
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            try:
                parsed = json.loads(part)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                continue

    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass

    json_candidates = []
    for match in re.finditer(r'\[', text):
        start = match.start()
        depth = 0
        end = start
        for i, c in enumerate(text[start:], start):
            if c == '[':
                depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        if depth == 0:
            candidate = text[start:end]
            json_candidates.append(candidate)

    for candidate in reversed(json_candidates):
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, list) and len(parsed) > 0:
                return parsed
        except json.JSONDecodeError:
            continue

    fixed = re.sub(r',\s*([}\]])', r'\1', text)
    try:
        parsed = json.loads(fixed)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass

    object_pattern = r'\{[^{}]*"input"[^{}]*\}'
    objects = re.findall(object_pattern, text, re.DOTALL)
    if objects:
        results = []
        for obj_str in objects:
            obj_str = re.sub(r',\s*}', '}', obj_str)
            try:
                obj = json.loads(obj_str)
                results.append(obj)
            except json.JSONDecodeError:
                continue
        if results:
            return results

    raise ValueError(f"Could not parse response as JSON: {text[-300:]}")


class MapRequest(BaseModel):
    text: str


class MapResponse(BaseModel):
    results: list
    input_count: int
    cache_hits: int = 0
    cache_misses: int = 0


def _system_prompt(reference: str) -> str:
    return f"""You are a specialty mapping expert. Map provider specialty labels to NUCC taxonomy display names.

{reference}

Rules:
- Match to the most specific NUCC display name possible.
- "nucc_name" MUST be the exact display name string from the list above.
- These inputs arrive in a healthcare context (e.g. a specialty label on a provider
  record). Bias TOWARD mapping: if the input can reasonably be read as shorthand for a
  provider specialty, role, or practice area — even a loose or partial overlap with a
  taxonomy entry (e.g. "Artist" -> "Art Therapist") — map it to the closest entry and
  set confidence in the 0.5-0.79 ambiguous band.
- Reserve null for inputs with essentially no medical connotation at all (e.g. a
  product, place, or random word like "Gamer"). Set "nucc_name" to null, confidence
  to 0.0, and say in "notes" that it is not a medical specialty.
- Confidence 1.0: exact match or standard synonym
- Confidence 0.8-0.95: clear semantic match
- Confidence 0.5-0.79: plausible but ambiguous
- Confidence <0.5: speculative or no match

Return ONLY a JSON array, no markdown, no explanation."""


def _user_prompt(input_text: str) -> str:
    return f"""Map these specialty labels to NUCC taxonomy display names:

{input_text}

Return a JSON array:
[
  {{"input": "...", "nucc_name": "..." or null, "confidence": 0.95, "notes": "..."}},
  ...
]"""


@app.get("/")
async def serve_frontend():
    return FileResponse(PROJECT_DIR / "static" / "index.html")


@app.post("/api/map")
async def map_specialty(req: MapRequest):
    inputs = [line.strip() for line in req.text.strip().split("\n") if line.strip()]
    if not inputs:
        raise HTTPException(status_code=400, detail="No input text provided")

    # --- Cache pass: serve recurring inputs from the store -----------------
    cached = batch_lookup(inputs)
    hits = cached["hits"]          # normalized key -> cached row
    misses = cached["misses"]      # unique inputs not in cache (first-seen order)

    reference = build_reference_context()
    system_prompt = _system_prompt(reference)

    # --- LLM pass: only the misses go to the model -------------------------
    llm_map = {}                   # normalized key -> result dict
    if misses:
        input_text = "\n".join(f"- {inp}" for inp in misses)
        user_prompt = _user_prompt(input_text)
        try:
            response = call_llm(system_prompt, user_prompt)
            raw_results = parse_response(response)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        # Align each raw result to a normalized key: by echoed input first,
        # then by position in the miss list.
        miss_keys = [normalize_input(m) for m in misses]
        used_keys = set()
        for idx, r in enumerate(raw_results):
            echoed = normalize_input((r.get("input") or "").strip())
            if echoed in miss_keys and echoed not in used_keys:
                key = echoed
            elif idx < len(miss_keys) and miss_keys[idx] not in used_keys:
                key = miss_keys[idx]
            else:
                continue
            used_keys.add(key)
            original = next(
                (m for m in misses if normalize_input(m) == key), key
            )

            # Resolve code via direct dataset lookup — the LLM never supplies codes.
            nucc_name = (r.get("nucc_name") or "").strip()
            row = resolve_code(nucc_name)
            notes = r.get("notes") or ""
            if row:
                res = {
                    "input": original,
                    "nucc_code": row.get("Code", ""),
                    "nucc_name": row.get("Display Name", ""),
                    "confidence": r.get("confidence", 0.0),
                    "notes": notes,
                }
            else:
                flag = ("no match found — needs review" if not nucc_name
                        else f"display name '{nucc_name}' not found in NUCC "
                             f"dataset — needs review")
                res = {
                    "input": original,
                    "nucc_code": None,
                    "nucc_name": nucc_name or None,
                    "confidence": 0.0,
                    "notes": f"{notes}; {flag}" if notes else flag,
                }

            # Persist the mapping so the next identical input is a cache hit.
            store(original, res["nucc_code"], res["nucc_name"],
                  res["confidence"], res["notes"])
            llm_map[key] = res

    # --- Merge: cache hits + LLM results, in original input order ----------
    results = []
    hit_count = 0
    miss_count = 0
    for orig in inputs:
        key = normalize_input(orig)
        if key in hits:
            h = hits[key]
            results.append({
                "input": orig,
                "nucc_code": h["nucc_code"],
                "nucc_name": h["nucc_name"],
                "confidence": h["confidence"],
                "notes": h["notes"],
                "source": "cache",
            })
            hit_count += 1
        elif key in llm_map:
            res = dict(llm_map[key])
            res["input"] = orig
            res["source"] = "llm"
            results.append(res)
            miss_count += 1
        else:
            # LLM did not return a row for this input — flag for review.
            results.append({
                "input": orig,
                "nucc_code": None,
                "nucc_name": None,
                "confidence": 0.0,
                "notes": "no result returned by mapper — needs review",
                "source": "llm",
            })
            miss_count += 1

    return MapResponse(
        results=results,
        input_count=len(inputs),
        cache_hits=hit_count,
        cache_misses=miss_count,
    )


# --- Cache observability / override (additive; not part of the map contract) -

@app.get("/api/cache/stats")
async def get_cache_stats():
    return cache_stats()


@app.get("/api/cache")
async def list_cache(limit: int = 100, offset: int = 0):
    """List cached mappings for the current taxonomy version (most recent first)."""
    import sqlite3
    from cache import _connect
    limit = max(0, min(limit, 1000))
    offset = max(0, offset)
    conn = _connect()
    try:
        rows = conn.execute(
            """
            SELECT input_key, nucc_code, nucc_name, confidence, notes,
                   nucc_version, created_at, updated_at
            FROM mapping_cache
            WHERE nucc_version = ?
            ORDER BY updated_at DESC, input_key ASC
            LIMIT ? OFFSET ?
            """,
            (NUCC_TAXONOMY_VERSION, limit, offset),
        ).fetchall()
    finally:
        conn.close()
    return {
        "entries": [
            {
                "input": r[0], "nucc_code": r[1], "nucc_name": r[2],
                "confidence": r[3], "notes": r[4], "nucc_version": r[5],
                "created_at": r[6], "updated_at": r[7],
            }
            for r in rows
        ],
        "limit": limit,
        "offset": offset,
    }


@app.delete("/api/cache/{input_key}")
async def remove_cache_entry(input_key: str):
    """Override: remove a cached entry so the next request re-maps via the LLM."""
    removed = cache_delete(normalize_input(input_key))
    if not removed:
        raise HTTPException(
            status_code=404,
            detail=f"No cached entry for {input_key!r} in taxonomy "
                   f"v{NUCC_TAXONOMY_VERSION}",
        )
    return {"deleted": True, "input": input_key, "nucc_version": NUCC_TAXONOMY_VERSION}


app.mount("/static", StaticFiles(directory=str(PROJECT_DIR / "static")), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8645)
