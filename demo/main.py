"""
Specialty Mapper Demo — FastAPI backend for Defacto demo.
Two modes:
  - Fast mode (default): Direct LLM call, reasoning disabled (~8s)
  - Agent mode: Full Hermes agent with skill reasoning (~26s)
"""

import csv
import json
import subprocess
import threading
from pathlib import Path
from typing import Optional

import urllib.request
import urllib.error

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="Specialty Mapper Demo")

# Paths (relative to parent project root)
PROJECT_DIR = Path(__file__).parent
PROJECT_ROOT = PROJECT_DIR.parent
NUCC_CSV = PROJECT_ROOT / "data" / "nucc" / "nucc_taxonomy_251.csv"
STATES_DIR = PROJECT_ROOT / "data" / "states"

# LLM config (from Hermes config)
LLM_BASE_URL = "http://10.0.0.228:8080/v1"
LLM_MODEL = "qwen-3.6-27b-mtp"
LLM_API_KEY = "***"

# Hermes session for agent mode
HERMES_SESSION = "specialty-mapper"
_session_lock = threading.Lock()

# Cache for reference data
_nucc_cache = None


def load_nucc():
    """Load NUCC taxonomy into memory."""
    global _nucc_cache
    if _nucc_cache is not None:
        return _nucc_cache

    rows = []
    with open(NUCC_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    _nucc_cache = rows
    return rows


def load_state_specialties(state: str):
    """Load a state's Medicaid specialties into memory."""
    state_dir = STATES_DIR / state.lower()
    csv_file = list(state_dir.glob("*_medicaid_specialties.csv"))[0]
    rows = []
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def load_state_crosswalk(state: str):
    """Load a state's NUCC crosswalk if available."""
    state_dir = STATES_DIR / state.lower()
    csv_files = list(state_dir.glob("*_taxonomy_crosswalk.csv"))
    if not csv_files:
        return []
    rows = []
    with open(csv_files[0], "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def get_available_states():
    """Discover available states from the data directory."""
    if not STATES_DIR.exists():
        return []
    states = []
    for d in sorted(STATES_DIR.iterdir()):
        if d.is_dir():
            state_code = d.name.upper()
            csv_files = list(d.glob("*_medicaid_specialties.csv"))
            if csv_files:
                states.append(state_code)
    return states


def build_reference_context(target: str) -> str:
    """Build a compact reference context for the LLM prompt."""
    nucc = load_nucc()

    if target == "nucc":
        lines = ["NUCC Taxonomy Reference (Code | Display Name | Classification):"]
        for row in nucc:
            code = row.get("Code", "")
            name = row.get("Display Name", "")
            classification = row.get("Classification", "")
            lines.append(f"  {code} | {name} | {classification}")
        return "\n".join(lines)
    else:
        try:
            state_specs = load_state_specialties(target)
            crosswalk = load_state_crosswalk(target)
        except (IndexError, FileNotFoundError):
            return f"No reference data available for state {target}"

        lines = [f"{target} State Medicaid Specialty Reference:"]

        # Include full NUCC taxonomy — don't filter by crosswalk, so the LLM can map
        # to subspecialty codes that exist in NUCC but aren't in the state crosswalk.
        lines.append(f"\nNUCC Taxonomy Reference ({len(nucc)} entries):")
        for row in nucc:
            code = row.get("Code", "")
            name = row.get("Display Name", "")
            classification = row.get("Classification", "")
            lines.append(f"  {code} | {name} | {classification}")

        if state_specs:
            first_row = state_specs[0] if state_specs else {}
            has_tier = "tier" in first_row
            # Check if specialty_code column actually has values (OH has the column but it's empty)
            has_specialty_code = "specialty_code" in first_row
            code_col_has_values = any(
                row.get("specialty_code", "").strip()
                for row in state_specs
            ) if has_specialty_code else False
            code_col = "specialty_code" if (has_specialty_code and code_col_has_values) else "specialty"

            if has_tier:
                header = f"\nState Specialty Categories (Tier | Category | {code_col.title().replace('_', ' ')}):"
                if code_col == "specialty":
                    header += "\n  Note: specialty name is the identifier (no numeric code column)"
                lines.append(header)
                for row in state_specs[:50]:
                    tier = row.get("tier", "")
                    category = row.get("category", "")
                    code = row.get(code_col, "")
                    lines.append(f"  {tier} | {category} | {code}")
            else:
                header = f"\nState Specialty Categories (Category | {code_col.title().replace('_', ' ')}):"
                if code_col == "specialty":
                    header += "\n  Note: specialty name is the identifier (no numeric code column)"
                lines.append(header)
                for row in state_specs[:50]:
                    category = row.get("category", "")
                    code = row.get(code_col, "")
                    lines.append(f"  {category} | {code}")

        if crosswalk:
            lines.append(f"\nNUCC Crosswalk ({len(crosswalk)} mappings):")
            # Dynamically pick columns — OH uses different names than MI
            first_cw = crosswalk[0] if crosswalk else {}
            cw_keys = list(first_cw.keys())
            # Pick relevant columns, skipping verbose ones like 'definition'/'nucc_definition'
            verbose_keys = {"nucc_definition", "definition", "notes"}
            cw_cols = [k for k in cw_keys if k not in verbose_keys]
            for row in crosswalk[:100]:
                vals = [row.get(k, "").strip() for k in cw_cols]
                vals = [v for v in vals if v]
                if vals:
                    lines.append("  " + " | ".join(vals))

        return "\n".join(lines)


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """Call the LLM API directly (fast mode — reasoning disabled)."""
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


def call_hermes(prompt: str) -> str:
    """Call Hermes Agent with session reuse (agent mode)."""
    with _session_lock:
        result = subprocess.run(
            ["hermes", "chat", "--resume", HERMES_SESSION, "-q", prompt],
            capture_output=True,
            text=True,
            timeout=120,
        )

    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Hermes error: {result.stderr[:500]}")

    return result.stdout


def parse_response(text: str) -> list:
    """Parse LLM or Hermes response into structured results."""
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

    import re
    json_candidates = []
    for match in re.finditer(r'\\[', text):
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

    fixed = re.sub(r',\\s*([}\\]])', r'\\1', text)
    try:
        parsed = json.loads(fixed)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass

    object_pattern = r'\\{[^{}]*\"input\"[^{}]*\\}'
    objects = re.findall(object_pattern, text, re.DOTALL)
    if objects:
        results = []
        for obj_str in objects:
            obj_str = re.sub(r',\\s*}', '}', obj_str)
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
    target: str
    state: Optional[str] = None


class MapResponse(BaseModel):
    results: list
    target: str
    input_count: int
    mode: str


@app.get("/")
async def serve_frontend():
    return FileResponse(PROJECT_DIR / "static" / "index.html")


@app.get("/api/states")
async def list_states():
    return {"states": get_available_states()}


@app.get("/api/state-info/{state}")
async def state_info(state: str):
    """Return source provenance metadata for a state."""
    state_dir = STATES_DIR / state.lower()
    meta_file = state_dir / "metadata.json"
    if not meta_file.exists():
        raise HTTPException(status_code=404, detail=f"No source info for state {state}")
    with open(meta_file, "r", encoding="utf-8") as f:
        return json.loads(f.read())


@app.post("/api/reset")
async def reset_session():
    result = subprocess.run(
        ["hermes", "sessions", "delete", "--yes", HERMES_SESSION],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        if "not found" not in result.stderr.lower():
            raise HTTPException(status_code=500, detail=f"Reset error: {result.stderr[:300]}")
    return {"status": "ok", "message": f"Session '{HERMES_SESSION}' reset. Next agent request will start fresh."}


@app.post("/api/map")
async def map_specialty(
    req: MapRequest,
    agent: bool = Query(default=False, description="Use Hermes agent mode (slower, more reasoning)"),
):
    target = req.target.upper() if req.target.lower() != "nucc" else "nucc"

    inputs = [line.strip() for line in req.text.strip().split("\n") if line.strip()]
    if not inputs:
        raise HTTPException(status_code=400, detail="No input text provided")

    input_text = "\n".join(f"- {inp}" for inp in inputs)
    target_desc = "NUCC taxonomy codes" if target == "nucc" else f"{target} state Medicaid specialty codes"

    prompt = f"""Map the following specialty labels to {target_desc}.

Input specialties:
{input_text}

Rules for State Mapping (if target is a State):
1. First, identify the most appropriate NUCC taxonomy code for the specialty.
2. Use the provided NUCC Crosswalk to find the corresponding State Specialty Code and State Category for that NUCC code.
3. If the NUCC code exists in the crosswalk, use those exact State values.
4. If no crosswalk match exists, map to the State Specialty Categories semantically as a best effort. In this case, explicitly note in the 'notes' field that the state mapping was semantic because no crosswalk match was found.

Rules for NUCC Mapping (if target is 'nucc'):
1. Map directly to the NUCC taxonomy codes.
2. Do NOT mention crosswalks or state mappings in the notes.

Return ONLY a JSON array with this exact structure — no markdown, no explanation before or after:
[
  {{"input": "original text", "nucc_code": "...", "nucc_name": "...", "state_code": "...", "state_category": "...", "confidence": 0.95, "notes": "reasoning"}},
  ...
]

The "nucc_name" field should be the full NUCC Display Name for the matched code (e.g. "Pediatric Hematology & Oncology Physician").

If no good match exists, set confidence to 0.0 and notes to "no match found — needs review"."""

    try:
        if agent:
            response = call_hermes(prompt)
            mode = "agent"
        else:
            reference = build_reference_context(target)

            system_prompt = f"""You are a specialty mapping expert. Map provider specialty labels to standardized taxonomy codes.

{reference}

Rules:
- Match to the most specific code possible.
- If the target is 'NUCC', map directly to the NUCC taxonomy codes. Do NOT mention crosswalks or state mappings in the notes.
- If the target is a State:
    1. First, identify the most appropriate NUCC taxonomy code.
    2. Use the provided NUCC Crosswalk to find the corresponding State Specialty Code and State Category.
    3. If a crosswalk match exists, use those values.
    4. If the state has no numeric specialty codes (uses specialty names as identifiers), use the specialty name as the state_code.
    5. If no crosswalk match exists, map to the State Specialty Categories semantically and note this in the 'notes' field.
- Confidence 1.0: exact match or standard synonym
- Confidence 0.8-0.95: clear semantic match
- Confidence 0.5-0.79: plausible but ambiguous
- Confidence <0.5: speculative or no match

Return ONLY a JSON array, no markdown, no explanation."""

            user_prompt = f"""Map these specialty labels to {target_desc}:

{input_text}

Return a JSON array:
[
  {{"input": "...", "nucc_code": "...", "nucc_name": "...", "state_code": "...", "state_category": "...", "confidence": 0.95, "notes": "..."}},
  ...
]
Include "nucc_name" as the full NUCC Display Name for the matched code."""
            response = call_llm(system_prompt, user_prompt)
            mode = "fast"

        results = parse_response(response)

        return MapResponse(
            results=results,
            target=target,
            input_count=len(inputs),
            mode=mode,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


app.mount("/static", StaticFiles(directory=str(PROJECT_DIR / "static")), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8645)
