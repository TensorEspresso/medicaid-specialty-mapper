# Tensor Automata — Healthcare Provider Specialty Data

AI-powered provider specialty mapping and normalization for healthcare data operations.

## What This Is

Two complementary components:

**1. Specialty Mapper (Tool)** — AI-powered mapper that takes arbitrary/inconsistent provider specialty labels and maps them to NUCC taxonomy codes with confidence scoring. Uses local LLM (Qwen3.6-27B) for semantic matching.

**2. State Medicaid Reference (Data)** — Verified state-by-state Medicaid specialty category definitions mapped to NUCC taxonomy. 11 states completed with source documentation.

Together: the mapper handles the "messy input" problem; the state reference handles the "which specialty counts where" problem. Both target the same customers (health plans, TPAs, provider data vendors).

## Problem

Provider specialty data is messy and inconsistent:

- **Unstructured input** — Free text, abbreviations, internal codes, garbage (`"Peds"`, `"Cardio"`, `"007"`, `"Misc"`)
- **No standard mapping** — Different systems use different taxonomies (NUCC, CMS, AMA, internal payer codes)
- **50+ state definitions** — Each Medicaid program defines its own specialty categories that don't align with NUCC or each other
- **Manual processes** — Current solutions are either expensive enterprise platforms or human error-prone

## Solution

**Mapper:**
1. Takes provider data with arbitrary specialty labels
2. Maps to NUCC taxonomy codes using LLM semantic matching
3. Uses context (credentials, practice description, state) to disambiguate
4. Outputs confidence score + recommended mapping
5. Flags low-confidence items for human review

**State Reference:**
1. Extracts specialty categories from state Medicaid manuals, CMS-1584 reports, MCO contracts
2. Maps each state category → NUCC taxonomy codes
3. Documents definitions, quirks, edge cases
4. Version-controlled for changes over time

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
| Illinois | 9 | Verified (broad only, .md) | MCPAR, EQRO, HFS2243i |
| North Carolina | 48 | Verified | CCH Provider Manual, NCTracks PPM |
| Ohio | 178 (3 programs) | Verified | MCO/MCOP/OhioRISE Agreements 2026 |
| Georgia | 61 | Verified | MCO Contracts, NAAR Reports |
| Michigan | 94 | Verified | MDHHS Standards, FY26 CHCP Contract |

Full tracking: [State Data Collection Tracker](docs/state-data-collection-tracker.md)

## Go-to-Market

**Defacto Health** — Data vendor we buy from. They collect from FHIR APIs nationwide; provider specialties come through as free text. We know the two founders professionally.

Approach: Demonstrate first (run mapper on sample), show before/after, let them propose engagement. Don't offer free work.

## Target Customers

- Health plans (commercial, Medicare Advantage, Medicaid managed care)
- TPAs (Third Party Administrators)
- Provider data management vendors
- Multi-state Medicaid MCOs
- Credentialing/enrollment vendors

## Pricing Models

**Mapper:**
- Per-provider: $1-5 per provider mapped
- API: $0.01-0.10 per mapping request
- Retainer: $1,500-$5,000/month for ongoing runs

**State Reference:**
- Standalone data: $200-500 per state, $2K-5K multi-state bundle
- Subscription API: $10K-25K/year (at 20+ states)
- Consulting deliverable: $3K-10K per state bundled

Full pricing research: [docs/pricing-research.md](docs/pricing-research.md)

## Competitive Landscape

| Player | What they do | Gap |
|--------|-------------|-----|
| NUCC | Maintains taxonomy | No mapping tooling, just reference data |
| Availity / Change Healthcare | Data clearinghouses | Expensive, opaque, not always accurate |
| State Medicaid agencies | Publish requirements | Fragmented, not machine-readable |
| Consulting firms | Manual research | $150-300/hr, slow, not scalable |

**White space:** No dedicated AI-powered mapping service exists. No comprehensive, up-to-date state specialty reference exists.

## Differentiator

**Local inference** — No data leaves the client's network. No API costs. Deterministic latency. HIPAA-compliant by design. Real differentiator for healthcare where data privacy is non-negotiable.

## Structure

```
medicaid-specialty-mapper/
├── README.md                          # This file
├── agents.md                          # AI agent guidelines
├── demo/                              # Interactive web demo for prospects
│   ├── main.py                        # FastAPI backend (fast + agent modes)
│   ├── static/
│   │   └── index.html                 # Single-page frontend
│   └── requirements.txt               # Python dependencies
├── docs/
│   ├── mapper-product.md              # Mapper product definition & GTM
│   ├── startup-advice-validated.md    # Startup research (validated)
│   ├── pricing-research.md            # Pricing models & benchmarks
│   ├── state-data-collection-tracker.md
│   └── research-methodology.md
├── data/
│   ├── nucc/                          # NUCC taxonomy reference (v25.1, 884 codes)
│   └── states/                        # One directory per state
│       ├── az/, ca/, fl/, ga/, il/, mi/, nc/, ny/, oh/, pa/, tx/
│       │   ├── *_medicaid_specialties.csv
│       │   ├── *_taxonomy_crosswalk.csv
│       │   └── sources/               # Raw source PDFs
└── reports/                           # Demo outputs
```

**Mapper skill:** Hermes skill (`specialty-mapper` in `~/.hermes/skills/`). Reads from `data/` above.

**Demo:** Interactive web frontend in `demo/` — two modes (fast + agent). Run with `~/.hermes/hermes-agent/venv/bin/python3 main.py` on port 8645.

## Environment

- Local LLM: Qwen3.6-27B via llama.cpp (Office PC: 10.0.0.228:8080)
- Hermes Agent for workflow automation
- NUCC taxonomy: Version 25.1 (July 2025), 884 codes

## Next Steps

- [ ] Test with Defacto sample data (100-200 providers)
- [ ] Prepare before/after demo for Defacto founders
- [ ] Reach out to Defacto founders
- [ ] Add 5 more states to reference (priority: WA, MA, CO, NV, NJ)
- [ ] Complete NY and TX crosswalks
- [ ] Check Quest employment agreement for conflict-of-interest clauses

## References

- [NUCC Provider Taxonomy Code Set](https://www.nucc.org/)
- [NPPES Taxonomy Search](https://npiregistry.cms.hhs.gov/)
- Defacto Health: (website/link TBD)
