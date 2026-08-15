# Specialty Mapper — Product

Maps arbitrary provider specialty labels to **NUCC taxonomy codes** using LLM
reasoning. Matches fuzzy/colloquial specialty names to standardized NUCC entries.

> **Scope note (post-split):** The mapper targets **NUCC only** in the current build.
> State-specific Medicaid mapping is a **data product** — per-state specialty
> categories and NUCC→state crosswalks live in the companion
> `medicaid-state-specialty-ref` repo. State mapping is a future feature of this
> mapper (see Roadmap) that will consume that data repo as input.

## Core Features

- Map free-text specialty labels ("Cardiologist", "Behavioral Health", …) to the correct NUCC code
- Display-name-first model: the LLM returns the best-matching **NUCC Display Name** only; the
  **code is resolved by direct dataset lookup** (never LLM-generated). Unresolvable names are
  flagged for review, not guessed.
- Single direct LLM call: full display-name list embedded in the prompt, reasoning disabled
- Confidence scoring per mapping
- Web UI for interactive use

## Tech Stack

| Layer | Choice | Why |
|-------|--------|-----|
| Backend | Python FastAPI | Clean REST, simple deploy |
| LLM | Local (Qwen 27B) via API | Fast, private, no per-token cost |
| Frontend | Single-page HTML/CSS/JS | No build step, instant load |
| Taxonomy | NUCC v25.1 CSV (884 codes) | Canonical; display names embedded in the prompt, codes resolved by lookup |

## User Flow

```
User enters specialty labels (one per line)
         │
         ▼
  ┌─────────────┐
  │ Direct LLM   │  ~8s, all 884 NUCC display names embedded in prompt
  └──────┬──────┘  No web search, no tool use
         │  → matched display name per input
         ▼
  ┌──────────────────┐
  │ Dataset lookup    │  display name → code (deterministic,
  └──────┬───────────┘  codes never LLM-generated)
         │
         ▼
  Structured JSON response
  (code, name, confidence, notes)
         │
         ▼
  Results table with confidence bars
```

## Response Format

```json
{
  "results": [
    {
      "input": "Cardiologist",
      "nucc_code": "207RC0000X",
      "nucc_name": "Cardiovascular Disease Physician",
      "confidence": 0.95,
      "notes": "Direct specialty match."
    },
    {
      "input": "Peds psych",
      "nucc_code": "2084P0804X",
      "nucc_name": "Child & Adolescent Psychiatry",
      "confidence": 0.95,
      "notes": "Colloquial term mapped to child/adolescent psychiatry"
    }
  ],
  "input_count": 2
}
```

## Consumer Policy (UI)

The API is **policy-agnostic**: it reports confidence, never an action. *How* to act on
confidence is a consumer decision, so the demo makes that policy visible and tunable in
the UI:

| Tier | Condition | Action |
|------|-----------|--------|
| Green | `confidence ≥ auto-accept threshold` (default 0.85) | Auto-accept |
| Yellow | `reject threshold ≤ confidence < accept threshold` | Flag for human review |
| Red | `confidence < reject threshold` (default 0.50) | Reject |

- Two sliders (auto-accept ≥ / reject <) recompute the **Recommended Action** column
  live — no re-mapping — so the demo shows that policy is the consumer's, not the
  model's.
- Rows with `nucc_code: null` are always Reject, regardless of thresholds: an
  unresolvable name can never be auto-accepted.
- In production these thresholds live in the consumer pipeline; the mapper keeps
  reporting confidence only.

## Architecture

```
Browser (single-page)
    │
    │  POST /api/map  {"text": "Cardiologist\nPeds psych"}
    ▼
FastAPI server
    └── LLM API call
        ├── System prompt: NUCC display names (884, codes withheld)
        ├── User prompt: specialty labels
        └── Response: JSON array of {input, nucc_name, confidence, notes}

    └── Code resolution (server-side)
        ├── normalized exact match on Display Name
        ├── tight fuzzy fallback (cutoff 0.97) for minor drift
        └── unresolvable → flagged for review
```

## API

### POST /api/map

Map specialty text to NUCC codes.

- `text`: newline-separated specialty labels

Returns structured results with confidence scores.

## Performance

Typical latency ~8s for a small batch; scales with label count and model load.
10 labels ~10-15s.

## Roadmap

- **State-specific mapping profiles** — consume `medicaid-state-specialty-ref` to
  map labels to a target state's Medicaid specialty codes alongside NUCC.
- Batch CSV upload
- Integration API (webhook, API key auth)
- Custom taxonomy profiles (non-NUCC target taxonomies)
- Confidence threshold filtering for downstream automation
- Evaluation harness — see `EVAL_HARNESS_SPEC.md` (benchmark against the state
  reference crosswalks in `medicaid-state-specialty-ref`)
