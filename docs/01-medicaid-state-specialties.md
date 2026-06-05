# Medicaid State Specialty Category Reference

**Status:** Idea / Research  
**Created:** 2026-06-04  
**Last Updated:** 2026-06-04

## Problem

Each state Medicaid program defines its own specialty categories for network adequacy and provider enrollment. These categories:

- **Vary by state** — 50+ different sets of specialty definitions
- **Don't align with NUCC** — States may use NUCC, CMS categories, or their own inventions
- **Have unclear definitions** — Even when category names match, the meaning differs
- **Change over time** — States update requirements regularly

**Example inconsistency:**
- State A: "Internal Medicine" includes cardiology, gastroenterology, etc.
- State B: "Internal Medicine" is generalists only; cardiology is separate
- State C: Uses "Cardiovascular Disease" as a distinct category

## Why This Hurts

1. **Multi-state health plans** — Must maintain 50+ different specialty mappings. Manual, error-prone, expensive.
2. **Providers in multiple states** — Need different specialty classifications per state. Often self-report incorrectly.
3. **Network adequacy reporting** — Each state has different timely-access ratios by specialty. Wrong mapping = wrong ratios = compliance risk.
4. **Contracting & recruitment** — "Does this provider's specialty count toward our adequacy requirement in this state?" Answer depends on state-specific definitions.
5. **QHP/ACA marketplace** — States define specialty requirements for exchange plans, which may differ from Medicaid requirements in the same state.

## Opportunity

**Product:** Comprehensive reference service that maps state Medicaid specialty categories to NUCC taxonomy, with documented definitions and inconsistencies flagged.

**Deliverables per state (2 required):**
1. **Specialty categories** — Verbatim list of what each state requires, with time/distance and timely access standards
2. **Definitions** — What each state category means. Can be explicit descriptions from state documents OR a NUCC taxonomy crosswalk (which serves as the operational definition)

**What it provides:**
1. Specialty categories + definitions (per above)
2. Cross-state comparison — Side-by-side view of how states differ
3. Change tracking — Alerts when states update their requirements

**Target customers:**
- Multi-state Medicaid managed care organizations (MCOs)
- TPAs serving Medicaid clients
- Provider enrollment/credentialing vendors
- Health information organizations (HIOs)
- Consulting firms advising health plans on Medicaid contracts

**Pricing models:**
- Subscription: $10K-50K/year per organization (based on state count)
- API access: $0.05-0.20 per lookup
- Custom reporting: $5K-20K per project

## Competitive Landscape

| Player | What they do | Gap |
|---|---|---|
| State Medicaid agencies | Publish requirements in manuals, bulletins | Fragmented, hard to compare, not machine-readable |
| CMS | Sets federal baseline | Doesn't standardize state-level categories |
| Consulting firms | Manual research for clients | Expensive ($150-300/hr), slow, not scalable |
| Data vendors | Some have partial mappings | Incomplete, outdated, expensive |

**White space:** No comprehensive, up-to-date, machine-readable reference exists. Current approach is manual research by staff who "know the states they work in."

## Technical Approach

**Phase 1: Research & Data Collection**
- Pick 3-5 starter states (prioritize by: data availability, complexity, customer interest)
- Extract specialty categories from:
  - State Medicaid provider manuals
  - CMS-1584 reports (network adequacy)
  - State bulletin notices
  - MCO contract requirements
- Map each state category → NUCC taxonomy codes
- Document definitions, quirks, edge cases

**Phase 2: Reference Database**
- Structured dataset: `state` → `specialty_category` → `nucc_codes[]` → `definition` → `source`
- Version control for changes over time
- Searchable API: "What NUCC codes map to 'Internal Medicine' in Texas?"

**Phase 3: AI-Powered Mapping**
- Given provider NUCC code + state → return mapped specialty category
- Explain reasoning: "NUCC code 207RC0000X (Cardiovascular Disease) maps to 'Cardiology' in State X because..."
- Flag ambiguities: "This provider's specialty could map to Category A or B in State Y"

**Phase 4: Continuous Updates**
- Monitor state Medicaid bulletins for changes
- Alert customers when mappings shift
- Incorporate user corrections

## Data Sources (TBD)

- State Medicaid provider manuals (PDF, web)
- CMS-1584 network adequacy reports
- State bulletin notices
- MCO contract templates
- NCQA accreditation requirements (state-specific)
- ACA exchange specialty requirements (for QHP comparison)

## Data Collection Progress

### Pennsylvania (PA) — COMPLETE
**Source:** 2025 Community HealthChoices Agreement (PA DHS)
**Extracted:** 2026-06-04
**Deliverables:**
- ✅ Specialty categories — 86 rows, verified against CHC Agreement
- ✅ Definitions — `pa_taxonomy_crosswalk.csv` (252 rows: state code + specialty → NUCC)

**Data files:**
- `data/states/pa/pa_medicaid_specialties.csv` — Machine-readable CSV
- `data/states/pa/pa_taxonomy_crosswalk.csv` — NUCC crosswalk
- `data/states/pa/pa_medicaid_specialties.md` — Human-readable reference

**Notes:**
- Official PA DHS "Provider Type Specialty Codes" PDF (Updated 3/28/2024) now returns 404
- Data extracted from 2025 CHC Agreement network adequacy requirements instead
- PA uses tiered network adequacy: Tier 1 (2 providers within 30/60 min), Tier 2 (1 + 1 in zone), County-level
- PA has separate BH-MCO (Behavioral Health Managed Care Organization) for mental health/SUD
- PA has CHC-MCO (Community HealthChoices) for LTSS integration
- Facility provider type/specialty codes documented (e.g., 01/11 = Private Psychiatric Hospital)

### California (CA) — COMPLETE
**Source:** DHCS APL21-006 Attachments A/B + ArcGIS taxonomy crosswalk
**Extracted:** 2026-06-04
**Deliverables:**
- ✅ Specialty categories — 32 rows, 24 verified against DHCS APL21-006
- ✅ Definitions — `ca_taxonomy_crosswalk.csv` (863 rows: NUCC → DHCS NA Group/Category)

**Data files:**
- `data/states/ca/ca_medicaid_specialties.csv` — Machine-readable CSV
- `data/states/ca/sources/ca_taxonomy_crosswalk.csv` — NUCC crosswalk
- `data/states/ca/ca_medicaid_specialties.md` — Human-readable reference

**Notes:**
- CA uses **county density tiers** (Dense/Medium/Small/Rural) instead of provider count requirements
- Time/distance standards vary by county: Dense (15mi/30min), Medium (30mi/60min), Small (45mi/75min), Rural (60mi/90min)
- Primary care: 10 miles or 30 minutes (all counties)
- 16 core specialist categories listed (Cardiology, Nephrology, Dermatology, Neurology, etc.)
- Behavioral health/SUD integrated into main standards (unlike PA's separate BH-MCO)
- Telehealth exception: up to 15% of network can be telehealth providers
- Alternative Access Standards available at ZIP-Code level (up to 3 years)
- CA DHCS website behind Cloudflare — official PDFs not downloadable via curl
- Taxonomy crosswalk publicly available on ArcGIS (`networks-gis.dhcs.ca.gov`)
- CA plans submit NUCC taxonomy codes directly in 274 file submissions
- DHCS reviews 274 files hierarchically: Provider Group Network Role Code → Licensure Type Code → 274 File Format Indicator → Facility Type Code → Institutional Facility Type Code → Taxonomy
- Separate managed care systems for: specialty mental health (county MHPs), dental, substance use (DMC-ODS)
- Appointment access standards: Urgent (48-96h), Primary care (10 business days), Specialty (15 business days)

### Other States — TODO
- [ ] Identify next 3-5 starter states
- [ ] Prioritize by: data availability, complexity, customer interest

## Open Questions

1. Which states are highest priority? (Population, complexity, customer interest)
2. How frequently do states update requirements?
3. What's the legal/public status of state Medicaid manuals? (Copyright, attribution)
4. Can we automate change detection (monitoring state bulletins)?
5. What format do customers want? (API, CSV, web app, embedded component?)
6. How do we handle territories (PR, VI, GU, etc.)?
7. Should we include QHP/ACA exchange requirements alongside Medicaid?

## References

- CMS Medicaid Provider Enrollment: (link TBD)
- State Medicaid Manuals: (links per state, TBD)
- CMS-1584 Network Adequacy Reports: (link TBD)
- NCQA Medicaid Accreditation: (link TBD)
- ACA Exchange Requirements: (link TBD)
