# AGENTS.md

Operational guidelines for AI agents working in the `medicaid-specialty-mapper` repository. This is a data product — keep it clean, verified, and structured.

## Project Layout

```
medicaid-specialty-mapper/
├── README.md              # Human-facing project overview
├── AGENTS.md              # This file — agent guidelines
├── .gitignore
├── demo/                  # Interactive web demo for prospects
├── docs/                  # Product docs, pricing research, trackers
├── data/
│   ├── nucc/              # NUCC taxonomy reference (v25.1, 884 codes) — DO NOT MODIFY
│   └── states/            # One directory per state (ISO 2-letter code)
│       ├── manifest.csv   # Authoritative state tracking manifest
│       └── <state>/
│           ├── <state>_medicaid_specialties.csv
│           ├── <state>_taxonomy_crosswalk.csv
│           ├── <state>_initial_research.md
│           ├── metadata.json
│           └── sources/   # Raw evidence (PDFs, HTML, TXT)
├── reports/               # Demo outputs
└── scripts/               # All automation/build scripts
```

## Structural Invariants

### State Data Hierarchy
Every state lives under `data/states/<state_code>/` where `<state_code>` is the lowercase 2-letter ISO code (`tx`, `ny`, `ca`).

### Mandatory File Naming
| File | Pattern | Purpose |
|------|---------|---------|
| Catalog | `<state_code>_medicaid_specialties.csv` | State category → definition |
| Crosswalk | `<state_code>_taxonomy_crosswalk.csv` | State category → NUCC code |
| Research | `<state_code>_initial_research.md` | Logic, edge cases, decision logs |

### Crosswalk Column Requirements
Every `*_taxonomy_crosswalk.csv` **MUST** include:
- **`nucc_code`** — NUCC taxonomy code (e.g., `207Q00000X`). Downstream tooling depends on this column.
- **`match_confidence`** — One of:
  - `source` — From an official state-published mapping.
  - `best-effort` — Derived via semantic mapping to NUCC v25.1.

All other columns are free-form — match the state's source data naming.

### Evidence & Sources
- All raw evidence (PDFs, HTML, TXT) **MUST** go in `data/states/<state_code>/sources/`.
- Never place source files at the state directory root.

## Workflow Rules

### Manifests & Tracking
- **`data/states/manifest.csv`** — Update immediately when adding a state or changing status.
- **`docs/state-data-collection-tracker.md`** — Authoritative progress tracker. Keep synchronized with filesystem.

### Script Management
- **Never** place scripts inside `data/`. All automation, build, and cleanup scripts go in `/scripts/`.

### Taxonomy Ground Truth
- `data/nucc/` contains the master NUCC reference. **Do not modify** unless performing a formal version upgrade.

## Verification Standard

A state is **"Verified"** only when all five conditions are met:

1. `*_medicaid_specialties.csv` is complete.
2. `*_taxonomy_crosswalk.csv` is complete (no `crosswalk_missing.txt` remains).
3. `*_initial_research.md` documents the source of every mapping.
4. `sources/` contains the original evidence used for the mapping.
5. `manifest.csv` status is `Ready`.

## Cleanup Protocol

When you discover research residues (`temp_file.txt`, `test_script.py`, inconsistently named files):

1. **Evidence** → move to `sources/`
2. **Tools** → move to `/scripts/`
3. **Redundant or temporary** → delete
