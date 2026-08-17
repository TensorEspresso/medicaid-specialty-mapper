# AI-Powered Provider Specialty Mapping
## Capability Demonstration

**Date:** August 17, 2026
**System:** AI Specialty Mapper — NUCC Taxonomy Mapping Engine
**Reference:** NUCC Provider Taxonomy v25.1 (883 codes)
**Scope:** NUCC-only. This build maps free-text specialty labels to **NUCC** display
names and codes. State/Medicaid crosswalks are out of scope for the current build.

> **Note:** Earlier reports in this repo documented a pre-split architecture that also
> produced per-state Medicaid categories. That state stage has been retired from the
> product. This report reflects the current **NUCC-only** behavior, captured live from
> the running service on 2026-08-17.

---

### Executive Summary

This report demonstrates automated mapping of informal provider specialty labels to
**NUCC taxonomy codes** with confidence scoring. The system ingests arbitrary specialty
input — abbreviations, colloquial labels, partial names — and resolves each to an
authoritative NUCC display name and code, with a confidence score and a short rationale.
Items that cannot be resolved to a real NUCC code are flagged for human review, never
guessed.

**Core capability:** Free-text specialty label → NUCC display name → NUCC code +
confidence score + mapping rationale.

---

### Architecture

The pipeline is two stages, and only the first stage touches the LLM:

1. **Label → NUCC Display Name (LLM).** The LLM is shown the full NUCC display-name list
   (codes withheld) and returns, for each input, the best-matching *display name* plus a
   confidence score and notes. This is the only judgment step.
2. **Display Name → Code (deterministic lookup).** The code is **never LLM-generated**.
   It is resolved by direct lookup in the NUCC dataset (normalized exact match, then a
   tight fuzzy fallback for minor drift). An unresolvable name is flagged for review,
   not guessed.

Why: codes are identifiers, not concepts. The LLM does the semantic work (fuzzy label →
canonical name) and the dataset does the exact work (name → code). This removes a whole
failure class (invented or malformed codes) and makes every output deterministically
checkable against the taxonomy file.

**Data lineage:** every mapping traces a verifiable chain —
**Input label** → **NUCC display name** (LLM-selected) → **NUCC code** (dataset lookup,
v25.1). No step is opaque; each link is auditable against the reference file.

---

### Demonstration: 8 Common Provider Labels

Live outputs from the running service (single LLM call, then dataset lookup):

| # | Input Label | NUCC Display Name | NUCC Code | Confidence | Mapping Notes |
|---|---|---|---|---|---|
| 1 | PCP | Family Medicine Physician | 207Q00000X | 0.95 | PCP = Primary Care Physician; Family Medicine is the standard default for general primary care. |
| 2 | OBGYN | Obstetrics & Gynecology Physician | 207V00000X | 1.00 | Standard abbreviation for OB/GYN. |
| 3 | Ortho | Orthopaedic Surgery Physician | 207X00000X | 1.00 | Common shorthand for Orthopedic Surgery. |
| 4 | ENT | Otolaryngology Physician | 207Y00000X | 1.00 | Standard abbreviation for Otolaryngology. |
| 5 | Peds Card | Pediatric Cardiology Physician | 2080P0202X | 1.00 | Shorthand for Pediatric Cardiology. |
| 6 | Peds Onc | Pediatric Hematology & Oncology Physician | 2080P0207X | 0.95 | Shorthand for Pediatric Oncology; grouped under Pediatric Hematology & Oncology in NUCC. |
| 7 | Allergies | Allergy & Immunology Physician | 207K00000X | 0.90 | Refers to the Allergy & Immunology specialty. |
| 8 | Infectious | Infectious Disease Physician | 207RI0200X | 0.95 | Shorthand for Infectious Disease. |

**Results:** 8 of 8 resolved to a real NUCC code. No item was unresolvable or required
the review flag on this set.

---

### Edge Cases the Mapper Handles

- **Abbreviation / colloquial** — `Peds Card`, `ENT`, `Ortho` → exact specialty codes.
- **Subspecialty** — `Peds Card` → the pediatric subspecialty code, not the parent.
- **Grouping** — `Peds Onc` → the combined Hematology & Oncology subspecialty.
- **No match** — an input with essentially no medical connotation (e.g. `Gamer`, a
  product name, a random word) is returned as `nucc_name: null`, confidence 0.0, and
  flagged for review. A `null` name can never be auto-accepted.
- **Unresolvable name** — if the LLM emits a display name not in the taxonomy, the code
  resolves to `null` and the row is flagged `display name '…' not found in NUCC dataset —
  needs review`, never guessed.

---

### Confidence Score Framework

| Score Range | Classification | Meaning |
|---|---|---|
| 1.00 | Exact | Recognized abbreviation or exact display-name match |
| 0.80–0.95 | High | Clear semantic match — synonym, standard abbreviation, near-exact name |
| 0.50–0.79 | Medium | Plausible match with ambiguity — partial/loose overlap |
| < 0.50 | Low | Speculative or no direct match — flagged for human review |

> **Consumer policy is not part of the mapper.** The API is *policy-agnostic*: it
> reports confidence, never an action. How to act on confidence (auto-accept / review /
> reject thresholds) is a **consumer** decision. The web UI exposes tunable thresholds so
> that boundary is visible; in production those thresholds live in the consumer pipeline.

---

### Underlying Reference Data

**NUCC Provider Taxonomy**
- Source: National Uniform Claim Committee, Health Care Provider Taxonomy Code Set
- Version: 25.1 (July 2025)
- Coverage: 883 taxonomy codes across all provider groups
- Fields per code: Grouping, Classification, Specialization, Definition, Notes, Display Name, Section
- Display name ↔ code is a **bijection** (883 display names, 883 codes, zero collisions) —
  the basis for the deterministic code-lookup stage.

---

### Use Cases

- **Provider data normalization** — standardize specialty labels across clearinghouses,
  payer feeds, and direct submissions into a single NUCC taxonomy.
- **Credentialing / recredentialing** — map incoming specialty claims to board-
  certification-aligned NUCC categories for automated validation.
- **Market / network analysis** — aggregate provider supply by standardized NUCC specialty
  across regions, regardless of source label quality.

---

### Technical Notes

- Two-stage model: LLM selects the **display name**; the **code** is resolved by dataset
  lookup and is never LLM-generated.
- Single direct LLM call per batch (reasoning disabled); local Qwen 27B endpoint.
- The original input is preserved alongside each result for audit.
- Unresolvable or no-medical-connotation inputs are surfaced for human review, never
  auto-assigned.
- **Latency:** a batch of 8 labels mapped in ~4.2s wall (~0.53s/label) on the local
  endpoint, captured 2026-08-17.
