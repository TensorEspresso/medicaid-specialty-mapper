# Specialty Mapper

Maps arbitrary provider specialty labels to **NUCC taxonomy codes** using an LLM.
A single direct LLM call (reasoning disabled) behind a small FastAPI server and web UI.

This repo contains the **mapping tool** and the master NUCC reference it runs
against. State-specific Medicaid specialty data (the ground-truth research output)
lives in a companion repo, `medicaid-state-specialty-ref`, which this mapper
consumes as evaluation data.

## What It Does

Given free-text specialty labels ("Cardiologist", "Behavioral Health RN", …), the
mapper returns the most specific NUCC display name and code, a confidence score, a
short rationale, and a recommended action under your consumer policy (auto-accept /
review / reject thresholds, tunable live in the UI).

**Mapping model:** the LLM matches each input to a **NUCC Display Name** only (codes
are withheld from the prompt). The **code is then resolved by direct lookup in the
NUCC dataset** — never LLM-generated. Names that don't resolve are flagged for review.

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
│   ├── main.py                # FastAPI backend (single LLM call)
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
datasets (11 states) and the NUCC→state crosswalks used to evaluate this mapper.
See that repo's `README.md` and `AGENTS.md` for the data contract and verification
standard.

## References

- [NUCC Provider Taxonomy Code Set](https://www.nucc.org/)
- [NPPES Taxonomy Search](https://npiregistry.cms.hhs.gov/)
