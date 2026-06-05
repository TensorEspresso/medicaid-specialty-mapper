# Medicaid State Specialty Reference

State-by-state Medicaid specialty category definitions mapped to NUCC taxonomy. Solves the 50+ different specialty definition problem across state Medicaid programs.

## Problem

Each state Medicaid program defines its own specialty categories for network adequacy, provider enrollment, and MCO contracting. There is no federal standard — 50+ different specialty taxonomies in circulation. This project builds a comprehensive reference that maps each state's categories back to the NUCC Provider Taxonomy Code Set.

## Deliverables Per State

1. **Specialty categories** — Verbatim list of what each state requires, with time/distance standards, provider count requirements, and enrollee-to-provider ratios
2. **Definitions** — What each state category means. Either explicit descriptions from state documents or a NUCC taxonomy crosswalk (which serves as the operational definition)

## Current Progress

| State | Rows | Status | Sources |
|---|---|---|---|
| Pennsylvania | 86 | Verified | CHC Agreement, PA Taxonomy Crosswalk |
| California | 31 | Verified | DHCS APL21-006, ArcGIS Crosswalk |
| New York | 130 | Verified | MCO Guidelines v3.0, PNDS Data Dictionary |

## Structure

```
medicaid-state-specialty-ref/
├── README.md
├── docs/
│   ├── 01-medicaid-state-specialties.md   # Project overview & strategy
│   ├── 02-research-methodology.md          # Data extraction methodology
│   └── 03-state-data-collection-tracker.md # Per-state source/status tracking
└── data/
    ├── nucc/                               # NUCC taxonomy reference
    │   ├── nucc_taxonomy_24_0.pdf
    │   └── nucc_taxonomy_251.csv
    └── states/                             # One directory per state
        ├── pa/
        │   ├── pa_medicaid_specialties.csv
        │   ├── pa_medicaid_specialties.md
        │   ├── pa_taxonomy_crosswalk.csv
        │   └── sources/
        ├── ca/
        │   ├── ca_medicaid_specialties.csv
        │   ├── ca_medicaid_specialties.md
        │   └── sources/
        └── ny/
            ├── ny_medicaid_specialties.csv
            ├── ny_medicaid_specialties.md
            └── sources/
```

## Data Format

CSV schema: `tier,category,specialty,designation_type,specialty_code,provider_count_requirement,travel_time_requirement,enrollees_per_provider,source`

Each state directory contains:
- `<state>_medicaid_specialties.csv` — Machine-readable specialty data
- `<state>_medicaid_specialties.md` — Human-readable reference with context
- `sources/` — Raw source PDFs for offline verification

## Target Use Cases

- Multi-state Medicaid MCOs contracting across state lines
- Provider network adequacy compliance auditing
- State-by-state specialty fragmentation analysis
- NUCC taxonomy normalization pipelines

## Environment

- Local LLM: Qwen3.6-27B via llama.cpp (Office PC: 10.0.0.228:8080)
- Hermes Agent for workflow automation
