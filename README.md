# Specialty Mapper

Maps arbitrary provider specialty labels to **NUCC taxonomy codes** using an LLM.
Two runtime modes — a fast direct-LLM path and a full Hermes agent path — behind a
small FastAPI server and web UI.

This repo contains the **mapping tool** and the master NUCC reference it runs
against. State-specific Medicaid specialty data (the ground-truth research output)
lives in a companion repo, `medicaid-state-specialty-ref`, which this mapper
consumes as evaluation data.

## What It Does

Given free-text specialty labels ("Cardiologist", "Behavioral Health RN", …), the
mapper returns the most specific NUCC code, display name, a confidence score, and a
short rationale.

- **Fast mode** — single LLM call with the NUCC taxonomy embedded in the prompt,
  reasoning disabled. Lowest latency.
- **Agent mode** — Hermes agent with skills and web search for ambiguous cases.

## Repo Layout

```
medicaid-specialty-mapper/
├── README.md
├── PROMOTION_PLAN.md          # GTM / business model
├── EVAL_HARNESS_SPEC.md       # Evaluation harness design
├── data/
│   └── nucc/
│       └── nucc_taxonomy_251.csv   # Master NUCC reference (v25.1, 884 codes)
├── demo/
│   ├── main.py                # FastAPI backend (Fast + Agent modes)
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
the `hermes` CLI on `PATH` for agent mode. Adjust `LLM_BASE_URL` / `LLM_MODEL` in
`demo/main.py` to reconfigure.

## API

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/`            | Web UI |
| `POST` | `/api/map`     | Map specialties (body: `{"text": "...\n..."}`) |
| `POST` | `/api/map?agent=true` | Map via Hermes agent mode |
| `POST` | `/api/reset`   | Reset the agent session |

Response:
```json
{
  "results": [
    {
      "input": "Cardiologist",
      "nucc_code": "208400000X",
      "nucc_name": "Cardiovascular Disease (Cardiology)",
      "confidence": 0.98,
      "notes": "Direct match"
    }
  ],
  "input_count": 1,
  "mode": "fast"
}
```

## Companion Data Repo

`medicaid-state-specialty-ref` holds the verified per-state Medicaid specialty
datasets (11 states) and the NUCC→state crosswalks used to evaluate this mapper.
See that repo's `README.md` and `AGENTS.md` for the data contract and verification
standard.

## References

- [NUCC Provider Taxonomy Code Set](https://www.nucc.org/)
- [NPPES Taxonomy Search](https://npiregistry.cms.hhs.gov/)
