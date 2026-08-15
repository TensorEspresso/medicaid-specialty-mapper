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
- Fast mode: single LLM call, reasoning disabled, lowest latency
- Agent mode: full Hermes agent with skill reasoning for ambiguous cases
- Confidence scoring per mapping
- Web UI for interactive use

## Tech Stack

| Layer | Choice | Why |
|-------|--------|-----|
| Backend | Python FastAPI | Clean REST, simple deploy |
| LLM | Local (Qwen 27B) via API | Fast, private, no per-token cost |
| Agent | Hermes Agent CLI | Skill system, web search, session memory |
| Frontend | Single-page HTML/CSS/JS | No build step, instant load |
| Taxonomy | NUCC v25.1 CSV (884 codes) | Canonical, embedded in prompt for fast mode |

## User Flow

```
User enters specialty labels (one per line)
         │
         ▼
  ┌─────────────┐
  │  Fast Mode   │  ◄─── default (fastest, ~8s)
  │  (direct LLM)│      All 884 NUCC codes embedded in prompt
  └──────┬──────┘      No web search, no tool use
         │
         │  (if user enables Agent Mode)
         ▼
  ┌─────────────┐
  │  Agent Mode  │  ◄─── ~26s, handles edge cases
  │  (Hermes)    │      Full agent with skill reasoning
  └──────┬──────┘      Web search for verification
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
      "nucc_code": "208400000X",
      "nucc_name": "Cardiovascular Disease (Cardiology)",
      "confidence": 0.98,
      "notes": "Direct match to NUCC specialty code"
    },
    {
      "input": "Peds psych",
      "nucc_code": "208500000X",
      "nucc_name": "Child/Adolescent Psychiatry",
      "confidence": 0.85,
      "notes": "Colloquial term mapped to child/adolescent psychiatry"
    }
  ],
  "input_count": 2,
  "mode": "fast"
}
```

## Architecture

```
Browser (single-page)
    │
    │  POST /api/map  {"text": "Cardiologist\nPeds psych"}
    │  GET  /api/reset
    ▼
FastAPI server
    │
    ├── Fast mode: LLM API call
    │   └── System prompt: NUCC taxonomy (884 codes)
    │   └── User prompt: specialty labels
    │   └── Response: JSON array
    │
    └── Agent mode: Hermes CLI
        └── hermes chat --resume specialty-mapper -q "..."
        └── Session persists between calls
        └── /api/reset clears session
```

## API

### POST /api/map

Map specialty text to NUCC codes.

- `text`: newline-separated specialty labels
- `agent` (query param, optional): `true` for agent mode

Returns structured results with confidence scores.

### POST /api/reset

Clear the Hermes agent session (removes accumulated context between mappings).

## Performance

| Mode | Typical Latency | Best For |
|------|----------------|----------|
| Fast | ~8s | Bulk mapping, clear labels |
| Agent | ~26s | Ambiguous labels, edge cases |

Latency depends on label count and model load. 10 labels in fast mode ~10-15s.

## Roadmap

- **State-specific mapping profiles** — consume `medicaid-state-specialty-ref` to
  map labels to a target state's Medicaid specialty codes alongside NUCC (the
  "Map To" target select, state data provenance panel, and state-code result
  columns are designed for this and will be re-introduced when it ships).
- Batch CSV upload
- Integration API (webhook, API key auth)
- Custom taxonomy profiles (non-NUCC target taxonomies)
- Confidence threshold filtering for downstream automation
- Evaluation harness — see `EVAL_HARNESS_SPEC.md` (benchmark against the state
  reference crosswalks in `medicaid-state-specialty-ref`)
