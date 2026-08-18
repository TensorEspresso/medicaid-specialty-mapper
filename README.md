# Specialty Mapper

Maps arbitrary provider specialty labels to **NUCC taxonomy codes** using an LLM.
A single direct LLM call (reasoning disabled) behind a small FastAPI server and web UI.

This repo contains the **mapping tool** and the master NUCC reference it runs
against. The tool is **NUCC-only**: it maps free-text labels to NUCC display names
and codes. The eval is seeded from the NUCC taxonomy itself (no state data). A
companion repo, `medicaid-state-specialty-ref`, holds verified per-state Medicaid
specialty data for a **parked** state-mapping extension — the tool and its eval do
not read it.

## What It Does

Given free-text specialty labels ("Cardiologist", "Behavioral Health RN", …), the
mapper returns the most specific NUCC display name and code, a confidence score, a
short rationale, and a recommended action under your consumer policy (auto-accept /
review / reject thresholds, tunable live in the UI).

**Mapping model:** the LLM matches each input to a **NUCC Display Name** only (codes
are withheld from the prompt). The **code is then resolved by direct lookup in the
NUCC dataset** — never LLM-generated. Names that don't resolve are flagged for review.

**Mapping store:** every result is persisted to a local SQLite cache
(`demo/mapping_cache.sqlite3`). Recurring inputs are served from the store and only
*misses* go to the LLM. This gives deterministic output (the LLM is
non-deterministic), a compounding/auditable data asset, and ~1ms lookups vs ~1-2s LLM
calls. Entries are tagged with the taxonomy version they were produced under, so a
NUCC version bump invalidates prior-version entries cleanly. Null results are cached
too.

## Repo Layout

```
specialty-mapper/
├── README.md
├── PROMOTION_PLAN.md          # GTM / business model
├── EVAL_HARNESS_SPEC.md       # Evaluation harness design
├── data/
│   └── nucc/
│       └── nucc_taxonomy_251.csv   # Master NUCC reference (v25.1, 883 codes)
├── demo/
│   ├── main.py                # FastAPI backend (LLM call + cache)
│   ├── cache.py               # SQLite mapping store (lookup/store/override)
│   └── static/index.html      # Web UI
├── docs/
│   └── mapper-product.md      # Mapper product spec
├── scripts/
│   ├── run_server.py          # uvicorn runner
│   ├── start_demo.sh
│   └── start_bg.sh
└── reports/                   # Demo output artifacts
```

## Quick Start

```bash
cd demo
python -m uvicorn main:app --host 0.0.0.0 --port 8645
```

Then open `http://localhost:8645`.

The backend expects an LLM endpoint at `http://10.0.0.228:8080/v1` (Qwen 27B) and
nothing else. Adjust `LLM_BASE_URL` / `LLM_MODEL` in `demo/main.py` to reconfigure.

## API

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/`            | Web UI |
| `POST` | `/api/map`     | Map specialties (body: `{"text": "...\n..."}`) |
| `GET`  | `/api/cache/stats` | Cache stats for the current taxonomy version |
| `GET`  | `/api/cache`   | List cached mappings (`?limit=` / `?offset=`) |
| `DELETE` | `/api/cache/{input_key}` | Override: remove an entry to force re-map |

Response:
```json
{
  "results": [
    {
      "input": "Cardiologist",
      "nucc_code": "207RC0000X",
      "nucc_name": "Cardiovascular Disease Physician",
      "confidence": 0.98,
      "notes": "Direct match."
    }
  ],
  "input_count": 1
}
```

**Consumer policy:** the API is policy-agnostic — it reports confidence, never an
action. The web UI adds a Consumer Policy panel with two thresholds (auto-accept ≥ 85%,
reject < 50% by default) that drive a per-row **Recommended Action** column, recomputed
live as you drag the sliders. Rows with no resolved code are always Reject. In
production the thresholds live in the consumer pipeline, not in this mapper.

## Companion Data Repo

`medicaid-state-specialty-ref` holds the verified per-state Medicaid specialty
datasets (11 states) and NUCC→state crosswalks. It is a **parked extension** for
future state-specific mapping — **not** the substrate for this mapper's eval (which
is NUCC-native). See that repo's `README.md` and `AGENTS.md` for its data contract
and verification standard.

## References

- [NUCC Provider Taxonomy Code Set](https://www.nucc.org/)
- [NPPES Taxonomy Search](https://npiregistry.cms.hhs.gov/)
