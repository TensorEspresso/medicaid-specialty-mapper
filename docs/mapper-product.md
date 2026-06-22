# Provider Specialty Code Mapping & Normalization

**Status:** Prototype — Hermes skill (`nucc-specialty-mapper`)  
**Created:** 2026-06-04  
**Last Updated:** 2026-06-04

## Problem

Provider specialty data in client systems is messy and inconsistent. Labels can be:

| Input type | Example | Challenge |
|---|---|---|
| NUCC taxonomy code | `207RC0000X` | Clean, direct lookup |
| Abbreviation | "Peds", "Cardio", "FM" | Semantic matching needed |
| Natural language | "Child doctor", "Heart specialist" | LLM understanding required |
| Internal payer code | "007", "SPEC_42" | Needs reference mapping |
| Garbage/unknown | "Misc", "UNK", random text | Flag for human review |

**Root cause:** Different systems use different taxonomies (NUCC, CMS, AMA, internal payer codes) and free-text entries. No single source of truth for mapping between them.

## NUCC Taxonomy (Verified)

- **Format:** 10-character alphanumeric codes (e.g., `207RC0000X` = Cardiovascular Disease)
- **Structure:** Hierarchical — Provider Grouping → Classification → Area of Specialization
- **Source:** [NUCC Provider Taxonomy Code Set](https://www.nucc.org/)
- **Used by:** NPPES, Medicare, most Medicaid programs, commercial payers
- **Download:** CSV available from NUCC site

## CMS HPRID Taxonomy

- **Format:** Alphanumeric, different structure from NUCC
- **Used by:** CMS reporting, some state marketplaces
- **Relationship to NUCC:** Related but not identical — mapping is not 1:1

## Opportunity

**Product:** AI-powered specialty code mapping/normalization service

**What it does:**
1. Takes provider data with arbitrary/inconsistent specialty labels
2. Maps to NUCC taxonomy (and optionally to state Medicaid, commercial payer formats)
3. Uses context (provider name, credentials, practice description, NPI data) to disambiguate
4. Outputs confidence score + recommended mapping
5. Flags low-confidence mappings for human review

**Why AI is uniquely suited:**
- Fundamentally a **semantic matching** problem
- LLMs understand that "Peds" = "Pediatrics" = NUCC code `207Q00000X`
- Rule-based mapping fails on edge cases; AI handles ambiguity
- Can encode domain knowledge: "In Medicaid context, 'General Practice' maps to X, but in Medicare Advantage it maps to Y"

**Target customers:**
- Health plans (commercial, Medicare Advantage, Medicaid managed care)
- TPAs (Third Party Administrators)
- GPOs (Group Purchasing Organizations)
- Provider data management vendors

**Pricing models:**
- Per-provider processing: $1-5 per provider mapped
- Platform subscription: $5K-20K/month for health plans
- API calls: $0.01-0.10 per mapping request

## Competitive Landscape

| Player | What they do | Gap |
|---|---|---|
| NUCC | Maintains the taxonomy | No mapping tooling, just reference data |
| Availity / Change Healthcare | Data clearinghouses with some mapping | Expensive, opaque, not always accurate |
| MediSpa / data vendors | Provider data management platforms | Focus on directory accuracy, not taxonomy mapping |
| Health plans | Manual mapping by staff | Human error, turnover, inconsistent |

**White space:** No dedicated AI-powered mapping service exists. Current solutions are either expensive enterprise platforms or manual processes.

## Technical Approach

**Prototype (MVP):**
- Hermes skill that takes CSV input → outputs mapped NUCC codes with confidence scores
- Uses local LLM (Qwen3.6-27B) for semantic matching
- NUCC taxonomy CSV as reference data
- Output: CSV with added columns (`mapped_nucc_code`, `mapped_specialty_name`, `confidence_score`, `needs_review`)

**V1 Product:**
- Web API endpoint: POST provider data → GET mapped results
- Batch processing: Upload CSV → download mapped CSV
- Confidence scoring with human-in-the-loop for low-confidence items
- State-specific mapping profiles (Medicaid, QHP, Medicare Advantage)

**V2 Product:**
- Real-time API for provider enrollment systems
- Integration with NPPES, Availity, Change Healthcare
- Continuous learning from human corrections
- Multi-taxonomy support (NUCC ↔ CMS ↔ AMA ↔ internal codes)

## Go-to-Market: Defacto Health

**Defacto Health** is a data vendor we buy from. They collect data from FHIR APIs and aggregate it. Their provider specialties come through as **free text** — unstructured, inconsistent, unmapped. Exactly our target problem.

**Relationship:** We know the two founders professionally. Good relationship.

### Approach

**Don't lead with "I'll build this for free."** Lead with demonstration:

1. Build prototype using Defacto sample data we already have access to
2. Run mapper on 100-200 providers
3. Show founders the before/after results
4. Let *them* propose what they want (buy, partner, license, service)

**Conversation frame:**
> "We've been working with your data and noticed the free-text specialties are a pain point. I've been building an AI tool that maps them to NUCC taxonomy automatically. I'd love to run it on a sample of your data and show you what it looks like. No strings — just want to see if it's actually useful."

**Why this works:**
- We control the asset (mapper stays ours)
- They see results, not code
- Low pressure, conversational
- Leaves next move open to them
- Establishes value before pricing

### Alternative paths

- **Partnership:** "We'd like to offer this as an add-on to your data product. You handle sales, we handle tech, we split revenue."
- **Go to their customers:** Approach Defacto's customers (health plans) directly with a sample run on their data.

### Risks & mitigations

| Risk | Mitigation |
|---|---|
| They ask for free ongoing work | "Happy to discuss a paid engagement for ongoing runs" |
| They want to build it internally | "Understandable. Happy to share what we learned or partner" |
| They love it but have no budget | Offer revenue-share on resell to their customers |
| Customers bypass Defacto and come to us | That's a good problem — have pricing ready |

## Next Steps

- [ ] Download NUCC taxonomy CSV from nucc.org
- [ ] Build Hermes skill prototype (CSV in → mapped CSV out)
- [ ] Test with Defacto sample data (100-200 providers)
- [ ] Test with real provider data from Quest Analytics
- [ ] Validate accuracy against known mappings
- [ ] Prepare before/after comparison for Defacto founders
- [ ] Reach out to Defacto founders with demo
- [ ] Build confidence scoring model
- [ ] Document edge cases and failure modes

## Open Questions

1. What's the accuracy bar customers need? (90%? 95%? 99%?)
2. How do we handle providers with multiple specialties?
3. What's the refresh cadence for NUCC taxonomy updates?
4. Can we access real provider data for testing (HIPAA considerations)?
5. What's the willingness to pay for this service?
6. Who are Defacto's biggest customers? (potential direct targets)

## References

- [NUCC Provider Taxonomy Code Set](https://www.nucc.org/)
- [NPPES Taxonomy Search](https://npiregistry.cms.hhs.gov/)
- Defacto Health: (website/link TBD)
- CMS HPRID Taxonomy (link TBD)
- AMA Specialty Taxonomy (link TBD)
