# AGENTS.md

Operational guidelines for AI agents working in the `specialty-mapper` repository.
This is the **mapping tool** — an LLM-powered service that maps free-text specialty
labels to **NUCC taxonomy codes**. Keep it runnable, self-contained, and NUCC-only.

## Scope Boundary

- **This repo** = the tool (FastAPI demo + web UI) and the master NUCC reference it runs against.
- **Companion data repo** = `medicaid-state-specialty-ref` (per-state Medicaid specialty
  datasets + NUCC→state crosswalks). It is the **ground-truth data product** this tool
  consumes for evaluation.
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
├── EVAL_HARNESS_SPEC.md       # Evaluation harness design (spec, not yet built)
├── data/
│   └── nucc/
│       └── nucc_taxonomy_251.csv   # Master NUCC reference (v25.1, 883 rows) — DO NOT MODIFY
├── demo/
│   ├── main.py                # FastAPI backend (single LLM call)
│   ├── requirements.txt
│   └── static/index.html      # Web UI (single-page, no build step)
├── docs/
│   ├── mapper-product.md      # Product spec + roadmap
│   ├── pricing-research.md
│   └── startup-advice-validated.md
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
| `LLM_BASE_URL`   | `http://10.0.0.228:8080/v1`       | Local Qwen 27B OpenAI-compatible endpoint. |
| `LLM_MODEL`      | `qwen-3.6-27b-mtp`                | |
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

The JSON response shape (`results[]` with `input`, `nucc_code`, `nucc_name`,
`confidence`, `notes`; plus `input_count`) is consumed by the web UI in
`demo/static/index.html`. Changing the shape requires updating both.

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
