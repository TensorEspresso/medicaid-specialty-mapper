# AGENTS.md

Operational guidelines for AI agents working in the `specialty-mapper` repository.
This is the **mapping tool** — an LLM-powered service that maps free-text specialty
labels to **NUCC taxonomy codes**. Keep it runnable, self-contained, and NUCC-only.

## Scope Boundary

- **This repo** = the tool (FastAPI demo + web UI) and the master NUCC reference it runs against.
- **Companion data repo** = `medicaid-state-specialty-ref` (per-state Medicaid specialty
  datasets + NUCC→state crosswalks). It is a **parked extension** for future state-specific
  mapping. The tool and its eval are **NUCC-only** and do **not** read it.
- **Do not** commit state data, research docs, or the state crosswalks here. They belong
  in the data repo.
- **Do not** reintroduce state-specific code paths into the mapper. State mapping is a
  **roadmap feature** (see `docs/mapper-product.md`) that will consume the data repo when
  it ships — until then the mapper targets NUCC only.

## Project Layout

```
specialty-mapper/
├── README.md                  # Human-facing overview
├── AGENTS.md                  # This file — agent guidelines
├── .gitignore
├── PROMOTION_PLAN.md          # GTM / business model (not code)
├── PITCH.md                   # The "we already have a Claude license" objection (not code)
├── EVAL_HARNESS_SPEC.md       # Evaluation harness design (spec, not yet built)
├── pyproject.toml             # Project + pytest config (pythonpath=["demo"], testpaths=["tests"])
├── conftest.py                # Pytest path bootstrap (demo/ on sys.path)
├── tests/                     # Test suite — NUCC bijection invariants + mapping store
│   ├── test_nucc_bijection.py # 883 display names ↔ codes bijection (the eval's answer key)
│   └── test_cache.py          # cache.py rules (key/normalize/upsert/null/delete) — non-destructive
├── data/
│   └── nucc/
│       └── nucc_taxonomy_251.csv   # Master NUCC reference (v25.1, 883 rows) — DO NOT MODIFY
├── demo/
│   ├── main.py                # FastAPI backend (LLM call + cache)
│   ├── cache.py               # SQLite mapping store (demo/mapping_cache.sqlite3)
│   ├── requirements.txt
│   └── static/index.html      # Web UI (single-page, no build step)
├── docs/
│   ├── mapper-product.md      # Product spec + roadmap
│   ├── fde-engagement-plan.md # FDE arc → skill → artifact map + NUCC-only build sequence
│   ├── startup-advice-validated.md
│   └── specialty-mapper-architecture.{svg,png}
├── scripts/
│   ├── run_server.py          # Foreground uvicorn runner
│   ├── start_demo.sh
│   └── start_bg.sh            # Background runner + health check
└── reports/                   # Demo output artifacts (not code)
```

## Hard Config Values (single source: `demo/main.py`)

| Constant         | Value                             | Notes |
|------------------|-----------------------------------|-------|
| `NUCC_CSV`       | `data/nucc/nucc_taxonomy_251.csv` | Resolved relative to `demo/` (parent dir). Do not move the file without updating this. |
| `LLM_BASE_URL`   | `http://localhost:8080/v1`        | Local Qwen 27B via LaunchAgent TCP relay (auto-discovers the Windows box; DHCP IP changes — never hardcode the box IP). |
| `LLM_MODEL`      | `qwen-27B`                        | |
| `LLM_API_KEY`    | `***`                | Placeholder; the local server accepts any non-empty key. |
| **Port**         | **8645**                          | Single port across `run_server.py`, `start_demo.sh`, `start_bg.sh`, and the `__main__` block. Change everywhere if it changes. |

## Mapping Model (two stages)

1. **Input → NUCC Display Name (LLM).** Single direct call; the system prompt embeds the
   full NUCC **display-name** list (codes withheld), reasoning disabled. Lowest latency,
   no external dependencies beyond the LLM endpoint.
2. **Display Name → Code (deterministic lookup).** `resolve_code()` looks the name up in
   `data/nucc/nucc_taxonomy_251.csv` — normalized exact match, then a tight fuzzy fallback
   (cutoff 0.97). **The code is never LLM-generated.** An unresolvable name is flagged for
   review (`nucc_code: null`, confidence 0.0), never guessed.

The system prompt encodes the mapping-bias rule, which is **deliberate** — do not
"simplify" it away:
- Inputs arrive in a healthcare context, so bias **toward** mapping: any loose or
  partial overlap with a clinical entry is mapped to the closest entry at 0.5–0.79
  confidence (e.g. "Artist" → "Art Therapist" @ 0.6).
- `nucc_name: null` (confidence 0.0) is reserved for inputs with essentially **no**
  medical connotation (e.g. "Gamer"). Do not "fix" a null back into a best-effort
  generic match — that was the explicit reason the rule exists.

The JSON response shape (`results[]` with `input`, `nucc_code`, `nucc_name`,
`confidence`, `notes`, `source` — plus `input_count`, `cache_hits`, `cache_misses`)
is consumed by the web UI in `demo/static/index.html`. Changing the shape requires
updating both. `source` is `cache` or `llm` (informational; the UI does not require
it).

## Mapping Store (SQLite cache)

`demo/cache.py` persists every mapping in `demo/mapping_cache.sqlite3` (gitignored).
On `POST /api/map`, recurring inputs are served from the store and only *misses* are
sent to the LLM. Design rules:

- **Key = normalized input** (lowercase, collapsed whitespace). `normalize_input()` is
  the only normalization; `lookup()`/`delete()` normalize internally (idempotent), so
  callers may pass raw or normalized input.
- **Version tag.** Each row is keyed by `(input_key, nucc_version)` where
  `nucc_version` comes from `NUCC_TAXONOMY_VERSION` in `demo/cache.py` (currently
  `25.1`). Bump that constant on a formal NUCC version upgrade and re-point `NUCC_CSV`
  in `demo/main.py`. Prior-version rows become soft-invalidated (a miss) and are
  retained for audit — do not delete them.
- **Nulls are cached.** `nucc_code: null` is a valid, deliberate answer and must stay
  reproducible.
- **All confidences are cached** for determinism; routing on confidence is the
  consumer's job. Override = `DELETE /api/cache/{input}` (operator escape hatch), which
  forces a fresh LLM re-map on the next request.
- **Per-input caching, not per-request.** The LLM is called once per request with all
  misses batched; the store is keyed per input so a label cached in one request is a
  hit in the next, regardless of how it is batched.
- `main.py` imports `cache` as a sibling module; `sys.path.insert(0, <demo dir>)` near
  the top of `main.py` is load-bearing for every launch method — do not remove it.
- The cache DB is **runtime data, not source**: it is gitignored and safe to delete
  (the store rebuilds itself; only the determinism/asset value is reset).

## Consumer Policy (UI only)

The API is **policy-agnostic** — it reports confidence, never an action. Do not add
action/recommendation fields to the `/api/map` response.

The web UI adds a Consumer Policy panel (auto-accept ≥ / reject < sliders, defaults
85% / 50%) that computes a per-row **Recommended Action** client-side and recomputes
live on slider change. Rules the UI enforces:
- `nucc_code: null` → always Reject, regardless of thresholds
- sliders clamp so accept ≥ reject always holds

This mirrors the production boundary: thresholds belong in the consumer pipeline, not
in the mapper. If a policy decision ever needs to leave the UI, it goes in the consumer
integration, not in `demo/main.py`.

## Structural Invariants

- The mapper reads **only** `data/nucc/nucc_taxonomy_251.csv` for reference data.
- Do not add a dependency on `medicaid-state-specialty-ref` paths inside the running
  mapper. If evaluation code (the future eval harness) needs the data repo, that is a
  separate concern, not the demo server.
- `reports/` and `demo/static/index.html` are outputs/UI, not part of the API contract.
- Keep the NUCC CSV as-is; do not regenerate, re-sort, or trim it. A formal taxonomy
  version upgrade is the only reason to touch it.

## Run & Verify

```bash
# foreground
python3 -m uvicorn demo.main:app --host 0.0.0.0 --port 8645

# smoke test (fast mode) — expects correct NUCC rows
curl -s -X POST http://localhost:8645/api/map \
  -H 'Content-Type: application/json' \
  -d '{"text": "Cardiologist\nDermatologist"}'
```

After any change to `demo/main.py`:
1. `python3 -c "import ast,pathlib; ast.parse(pathlib.Path('demo/main.py').read_text())"` — syntax.
2. Boot the server and hit `GET /` and `POST /api/map` to confirm 200s and valid JSON.
3. Confirm `data/nucc/nucc_taxonomy_251.csv` still resolves (883 data rows) —
   `build_reference_context()` should yield one context line per code.

## Conventions

- **No build step.** The UI is a single self-contained `index.html`. Don't introduce a
  bundler.
- **No secrets in commits** beyond the local placeholder API key above.
- When you discover research residues or temp scripts: move evidence to the **data
  repo**, tools to `scripts/`, delete the rest.
- Update `README.md` and `docs/mapper-product.md` when behavior changes.
