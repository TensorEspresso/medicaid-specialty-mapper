# Medicaid Specialty Mapper

AI-powered provider specialty mapping and state Medicaid specialty reference data.

## Overview

Two complementary components:

**1. Specialty Mapper (Tool)** — Maps arbitrary/inconsistent provider specialty labels to NUCC taxonomy codes with confidence scoring. Uses local LLM (Qwen3.6-27B) for semantic matching.

**2. State Medicaid Reference (Data)** — Verified state-by-state Medicaid specialty category definitions mapped to NUCC taxonomy. 11 states completed with source documentation.

Together: the mapper handles the "messy input" problem; the state reference handles the "which specialty counts where" problem.

## Problem

Provider specialty data is messy and inconsistent:

- **Unstructured input** — Free text, abbreviations, internal codes, garbage (`"Peds"`, `"Cardio"`, `"007"`)
- **No standard mapping** — Different systems use different taxonomies (NUCC, CMS, AMA, internal payer codes)
- **50+ state definitions** — Each Medicaid program defines specialty categories that don't align with NUCC or each other
- **Manual processes** — Current solutions are expensive enterprise platforms or error-prone

## Solution

**Mapper:** Takes provider data with arbitrary specialty labels → maps to NUCC taxonomy using LLM semantic matching → outputs confidence score + recommended mapping → flags low-confidence items for human review.

**State Reference:** Extracts specialty categories from state Medicaid manuals, CMS-1584 reports, MCO contracts → maps each state category to NUCC taxonomy codes → documents definitions, quirks, edge cases → version-controlled for changes over time.

## Current Progress

**Mapper:** Prototype phase. Hermes skill (`specialty-mapper`) implemented.

**State Reference:** 11 states verified with source documentation.

| State | Rows | Status | Sources |
|-------|------|--------|---------|
| Arizona | 9 | Verified | AHCCCS/DES Network Standards |
| Pennsylvania | 86 | Verified | CHC Agreement, PA Taxonomy Crosswalk |
| California | 31 | Verified | DHCS APL21-006, ArcGIS Crosswalk |
| Texas | 36 | Verified | UMCM Ch 5.28.1, Network Capacity Layout |
| New York | 133 | Verified | MCO Guidelines v4.0, PNDS Data Dictionary v12 |
| Florida | 64 | Verified | Exhibit II-A MMA, FL Taxonomy Master List |
| Illinois | 9 | Verified (broad only) | MCPAR, EQRO, HFS2243i |
| North Carolina | 48 | Verified | CCH Provider Manual, NCTracks PPM |
| Ohio | 178 (3 programs) | Verified | MCO/MCOP/OhioRISE Agreements 2026 |
| Georgia | 61 | Verified | MCO Contracts, NAAR Reports |
| Michigan | 94 | Verified | MDHHS Standards, FY26 CHCP Contract |

Full tracking: [State Data Collection Tracker](docs/state-data-collection-tracker.md)

## Target Customers

- Health plans (commercial, Medicare Advantage, Medicaid managed care)
- TPAs (Third Party Administrators)
- Provider data management vendors
- Multi-state Medicaid MCOs
- Credentialing/enrollment vendors

## Key Differentiator

**Local inference** — No data leaves the client's network. No API costs. Deterministic latency. HIPAA-compliant by design.

## Structure

```
medicaid-specialty-mapper/
├── README.md              # This file
├── AGENTS.md              # AI agent operational guidelines
├── demo/                  # Interactive web demo for prospects
│   ├── main.py            # FastAPI backend
│   ├── static/index.html  # Single-page frontend
│   └── requirements.txt
├── docs/
│   ├── state-data-collection-tracker.md
│   ├── research-methodology.md
│   ├── mapper-product.md
│   └── pricing-research.md
├── data/
│   ├── nucc/              # NUCC taxonomy v25.1 (884 codes)
│   └── states/            # Per-state directories
│       ├── manifest.csv   # Authoritative state tracking
│       └── <state>/
│           ├── *_medicaid_specialties.csv
│           ├── *_taxonomy_crosswalk.csv
│           └── sources/   # Raw evidence (PDFs)
├── reports/               # Demo outputs
└── scripts/               # Build and automation scripts
```

## Environment

- **Local LLM:** Qwen3.6-27B via llama.cpp
- **Orchestration:** Hermes Agent
- **NUCC taxonomy:** Version 25.1 (July 2025), 884 codes

## Next Steps

- [ ] Test with Defacto sample data (100-200 providers)
- [ ] Prepare before/after demo for Defacto founders
- [ ] Reach out to Defacto founders
- [ ] Add 5 more states (priority: WA, MA, CO, NV, NJ)
- [ ] Complete NY and TX crosswalks
- [ ] Check Quest employment agreement for conflict-of-interest clauses

## References

- [NUCC Provider Taxonomy Code Set](https://www.nucc.org/)
- [NPPES Taxonomy Search](https://npiregistry.cms.hhs.gov/)
