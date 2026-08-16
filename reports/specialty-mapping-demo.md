# AI-Powered Provider Specialty Mapping

## Capability Demonstration

**Date:** June 9, 2026
**System:** AI Specialty Mapper — NUCC Taxonomy Crosswalk Engine

> **Note (post-split):** This report documents the **pre-split architecture** — a single system
> that mapped labels to both NUCC codes *and* state Medicaid categories. The repo was split on
> 2026-06-14: the **state crosswalk** stage described below now lives in the companion
> `medicaid-state-specialty-ref` data repo, and the running mapper is **NUCC-only** (free-text
> label → NUCC display name via LLM → deterministic NUCC code lookup). Read the state-crosswalk
> sections as a record of the prior design, not current behavior.

---

### Executive Summary

This report demonstrates automated mapping of informal provider specialty labels to standardized Medicaid specialty codes with confidence scoring. The system ingests arbitrary specialty input — abbreviations, colloquial labels, partial names — and resolves them to authoritative state Medicaid specialty categories backed by NUCC taxonomy codes.

**Core capability:** Free-text specialty label → State Medicaid code + NUCC taxonomy code + Confidence score + Mapping rationale

---

### Architecture

The mapping pipeline operates in five stages:

1. **Input Ingestion** — Accepts specialty labels in any format: abbreviations (*Ortho, ENT, Peds Card*), colloquial terms (*Allergies, Infectious*), full names, or mixed batches. No preprocessing or normalization required.

2. **NUCC Taxonomy Resolution** — Each input label is matched against the full NUCC taxonomy dataset (883 codes, v25.1) using semantic search across classification, specialization, and definition fields. The system resolves abbreviations to their canonical specialty (e.g., *Peds Card* → *Pediatric Cardiology*) and identifies the most specific NUCC code (preferring Specialization over Classification over Grouping).

3. **State Crosswalk Resolution** — The resolved NUCC code is mapped to the target state's Medicaid specialty category. Two lookup methods:
   - **Official crosswalk** — State-published NUCC-to-specialty mapping where available (e.g., CA's DHCS ArcGIS crosswalk, FL's Taxonomy Master List, NC's Provider Permission Matrix)
   - **Name-matching fallback** — Direct matching of NUCC classification/specialization names against state specialty catalog entries when no official crosswalk exists

4. **Edge Case Handling** — Three special cases detected and handled explicitly:
   - **Subspecialty-to-parent** — e.g., Pediatric Cardiology → Cardiology when the state has no pediatric subspecialty tier
   - **Dual-mapping** — e.g., Pediatric Hematology-Oncology → both Hematology and Oncology categories
   - **No-match flagging** — e.g., Allergy/Immunology when the state has no corresponding category
   Each is scored down appropriately and annotated with reasoning.

5. **Confidence Scoring & Output** — Each mapping receives a 0.0–1.0 confidence score. Output includes: original input, resolved NUCC code, state Medicaid category, tier assignment, confidence score, and mapping rationale. Items below 0.50 are flagged for human review rather than auto-assigned.

### Data Lineage

Every mapping traces a verifiable chain: **Input label** → **NUCC taxonomy code** (with definition from v25.1) → **State Medicaid specialty category** (with source document reference). No step is opaque — each link in the chain is auditable against the underlying reference data.

---

### Demonstration: CA Medi-Cal Specialty Mapping

**Input:** Informal specialty abbreviations as commonly seen in provider data feeds

| # | Input Label | CA Medicaid Category | Tier | NUCC Code | Confidence | Mapping Notes |
|---|---|---|---|---|---|---|
| 1 | PCP | Adult Primary Care | Primary Care | 207Q00000X | 1.00 | Exact match. Pediatric variant → "Pediatric Primary Care" row |
| 2 | OBGYN | OB/GYN Primary Care + Obstetrics and Gynecological Specialty Care | Primary Care / Specialist | 207V00000X | 1.00 | Dual role — counts as both PCP and specialist in CA |
| 3 | Ortho | Orthopedic Surgery | Specialist | 207X00000X | 1.00 | Exact match |
| 4 | ENT | ENT/Otolaryngology | Specialist | 207Y00000X | 1.00 | Exact match |
| 5 | Peds Card | Cardiology/Interventional Cardiology | Specialist | 2080P0202X | 0.75 | Subspecialty → parent category. CA has no pediatric subspecialty tier |
| 6 | Peds Onc | Oncology + Hematology | Specialist | 2080P0207X | 0.70 | Dual-mapped. CA has no pediatric subspecialty; counts toward both categories |
| 7 | Allergies | — (No direct category) | — | 207K00000X | 0.30 | **Flagged for review.** CA Medicaid does not list Allergy/Immunology as a distinct specialist category |
| 8 | Infectious | HIV/AIDS Specialists/Infectious Diseases | Specialist | 207RI0200X | 1.00 | Exact match |

**Results:** 8 of 8 resolved to NUCC taxonomy. 6 of 8 mapped directly to CA Medicaid categories. 1 dual-mapped. 1 flagged for human review.

---

### Confidence Score Framework

| Score Range | Classification | Meaning |
|---|---|---|
| 1.00 | Exact | Input is a recognized abbreviation or matches state specialty name exactly |
| 0.80–0.95 | High | Clear semantic match — synonym, standard abbreviation, or near-exact name |
| 0.50–0.79 | Medium | Plausible match with ambiguity — subspecialty mapped to parent category, or multiple candidates |
| < 0.50 | Low | Speculative or no direct match — flagged for human review |

---

### Underlying Reference Data

**NUCC Taxonomy**
- Source: National Uniform Claim Committee, Health Care Provider Taxonomy Code Set
- Version: 25.1 (July 2025)
- Coverage: 883 taxonomy codes across all provider groups
- Fields per code: Classification, Specialization, Definition, Board certification source

**State Medicaid Crosswalks**
- 9 states with collected specialty data: AZ, CA, FL, IL, NC, NY, OH, PA, TX
- CA: 31 specialty categories across 5 tiers (Primary Care, Specialist, Behavioral Health, Ancillary, LTSS)
- Crosswalk methodology: Official state crosswalk where published; NUCC name-matching fallback where not

---

### Use Cases

**Network Adequacy Analysis** — Ingest provider rosters with free-text specialties and automatically classify against state Medicaid specialty requirements for gap analysis

**Provider Data Normalization** — Standardize specialty labels across multiple data sources (clearinghouses, payer feeds, direct provider submissions) into a single taxonomy

**Recredentialing Workflows** — Map incoming specialty claims to board certification categories for automated validation

**Market Analysis** — Aggregate provider supply by standardized specialty across counties, regardless of source data label quality

---

### Technical Notes

- Subspecialty handling is state-dependent — states with coarse taxonomies (e.g., CA, OH) require parent-category mapping with reduced confidence
- Dual-mapped specialties (e.g., Peds Onc → Oncology + Hematology) are explicitly flagged rather than forced into a single category
- The system preserves the original input alongside the mapped result for audit trails
- Items below 0.50 confidence are surfaced for human review rather than auto-assigned
