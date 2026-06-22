# Agents.md — Operational Guidelines for AI Agents

This document defines the strict structural and procedural invariants for the `medicaid-specialty-mapper` repository. AI agents must adhere to these rules to prevent "research noise" and maintain the project's status as a clean data product.

## 1. Structural Invariants

### State Data Hierarchy
Every state must follow this exact directory structure:
`data/states/<state_code>/` (where `<state_code>` is the 2-letter ISO code, e.g., `tx`, `ny`, `ca`)

### Mandatory File Naming
Within each state directory, files must be named using the following patterns:
- **Catalog:** `<state_code>_medicaid_specialties.csv` (State Category → Definition)
- **Crosswalk:** `<state_code>_taxonomy_crosswalk.csv` (State Category → NUCC Code)
- **Research:** `<state_code>_initial_research.md` (Logic, edge cases, and decision logs)

### Crosswalk Column Convention
Every `*_taxonomy_crosswalk.csv` **MUST** include:
- **`nucc_code`** — The NUCC taxonomy code (e.g., `207Q00000X`). This is the invariant that downstream tooling depends on.
- **`match_confidence`** — One of:
  - `source` — The NUCC code comes from an official state-published mapping (e.g., FL Taxonomy Master List).
  - `best-effort` — The NUCC code was derived via semantic mapping from state specialty categories to NUCC v25.1 (no official crosswalk published).
Other columns are free-form — use whatever naming matches the state's source data.

### Evidence & Sources
- All raw evidence (PDFs, HTML scrapes, TXT dumps) **MUST** be placed in the `sources/` sub-directory: `data/states/<state_code>/sources/`.
- Never place raw source files at the root of the state directory.

## 2. Workflow & Maintenance Rules

### Tracking & Manifests
- **Manifest Update:** Any time a new state is added or a status changes (e.g., `Missing` → `Ready`), the `data/states/manifest.csv` must be updated immediately.
- **Collection Tracker:** The `docs/state-data-collection-tracker.md` is the authoritative source for project progress. Ensure it is synchronized with the filesystem.

### Script Management
- **No Scripts in Data:** Never place Python scripts or shell scripts inside the `data/` directory.
- **Centralized Scripts:** All automation, build, or cleaning scripts must reside in the top-level `/scripts/` directory.

### Taxonomy Ground Truth
- The `data/nucc/` directory contains the master taxonomy reference. 
- **Do not modify** files in this directory unless performing a formal version upgrade (e.g., moving from v25.1 to v26.0).

## 3. Verification Standard

A state is considered **"Verified"** only when:
1. The `*_medicaid_specialties.csv` is complete.
2. The `*_taxonomy_crosswalk.csv` is complete (no `crosswalk_missing.txt` remains).
3. The `*_initial_research.md` documents the source of every mapping.
4. The `sources/` folder contains the original evidence used for the mapping.
5. The `manifest.csv` is updated to `Ready`.

## 4. Cleanup Protocol
If you discover "research residues" (e.g., `temp_file.txt`, `test_script.py`, or inconsistently named files), you are authorized to:
1. Move them to `sources/` if they are evidence.
2. Move them to `/scripts/` if they are tools.
3. Delete them if they are redundant or temporary.
