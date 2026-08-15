"""
Specialty Mapper Demo — FastAPI backend.
Maps arbitrary provider specialty labels to NUCC taxonomy codes.

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

# Paths
PROJECT_DIR = Path(__file__).parent
NUCC_CSV = PROJECT_DIR.parent / "data" / "nucc" / "nucc_taxonomy_251.csv"

# LLM config
LLM_BASE_URL = "http://10.0.0.228:8080/v1"
LLM_MODEL = "qwen-3.6-27b-mtp"
LLM_API_KEY = "***"

# Hermes session for agent mode
HERMES_SESSION = "specialty-mapper"
_session_lock = threading.Lock()

# Cache
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


def build_reference_context() -> str:
    """Build a compact NUCC reference context for the LLM prompt."""
    nucc = load_nucc()
    lines = ["NUCC Taxonomy Reference (Code | Display Name | Classification):"]
    for row in nucc:
        code = row.get("Code", "")
        name = row.get("Display Name", "")
        classification = row.get("Classification", "")
        lines.append(f"  {code} | {name} | {classification}")
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

    object_pattern = r'\{[^{}]*\"input\"[^{}]*\}'
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
    mode: str


@app.get("/")
async def serve_frontend():
    return FileResponse(PROJECT_DIR / "static" / "index.html")


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
    return {"status": "ok", "message": f"Session '{HERMES_SESSION}' reset."}


@app.post("/api/map")
async def map_specialty(
    req: MapRequest,
    agent: bool = Query(default=False, description="Use Hermes agent mode"),
):
    inputs = [line.strip() for line in req.text.strip().split("\n") if line.strip()]
    if not inputs:
        raise HTTPException(status_code=400, detail="No input text provided")

    input_text = "\n".join(f"- {inp}" for inp in inputs)

    prompt = f"""Map the following specialty labels to NUCC taxonomy codes.

Input specialties:
{input_text}

Rules:
1. Map to the most specific NUCC taxonomy code possible.
2. Return ONLY a JSON array with this exact structure — no markdown, no explanation before or after:
[
  {{"input": "original text", "nucc_code": "...", "nucc_name": "...", "confidence": 0.95, "notes": "reasoning"}},
  ...
]

The "nucc_name" field should be the full NUCC Display Name for the matched code.
If no good match exists, set confidence to 0.0 and notes to "no match found — needs review"."""

    try:
        if agent:
            response = call_hermes(prompt)
            mode = "agent"
        else:
            reference = build_reference_context()

            system_prompt = f"""You are a specialty mapping expert. Map provider specialty labels to NUCC taxonomy codes.

{reference}

Rules:
- Match to the most specific code possible.
- Confidence 1.0: exact match or standard synonym
- Confidence 0.8-0.95: clear semantic match
- Confidence 0.5-0.79: plausible but ambiguous
- Confidence <0.5: speculative or no match

Return ONLY a JSON array, no markdown, no explanation."""

            user_prompt = f"""Map these specialty labels to NUCC taxonomy codes:

{input_text}

Return a JSON array:
[
  {{"input": "...", "nucc_code": "...", "nucc_name": "...", "confidence": 0.95, "notes": "..."}},
  ...
]"""
            response = call_llm(system_prompt, user_prompt)
            mode = "fast"

        results = parse_response(response)

        return MapResponse(
            results=results,
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
