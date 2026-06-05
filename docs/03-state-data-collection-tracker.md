# State Data Collection Tracker

Tracks data sources, extraction methodology, verification status, and known issues for each state's Medicaid specialty dataset.

## States

### Pennsylvania (PA) — COMPLETE

| Field | Value |
|---|---|
| **Status** | Verified ✓ |
| **Data file** | `data/states/pa/pa_medicaid_specialties.csv` |
| **Doc file** | `data/states/pa/pa_medicaid_specialties.md` |
| **Row count** | 86 data rows |
| **Sources** | CHC Agreement PDF (`pa_chc_agreement.pdf`), PA Taxonomy Crosswalk (`pa_taxonomy_crosswalk.pdf`), NUCC Taxonomy (`taxonomy_24_0.pdf`) |
| **Source URLs** | PA DHCP CHC Agreement; PA taxonomy crosswalk p_002941.pdf; NUCC taxonomy_24_0.pdf |
| **Extraction method** | `pdftotext` + `grep`/`sed` pipelines |
| **Verification** | Multi-pass verification against source PDF text. Codes cross-referenced with NUCC taxonomy. |
| **Known issues** | None |
| **Notes** | First state collected. Established CSV schema and methodology. Behavioral Health separated into BH-MCO tier due to separate managed care agreement. |

### California (CA) — COMPLETE

| Field | Value |
|---|---|
| **Status** | Verified ✓ |
| **Data file** | `data/states/ca/ca_medicaid_specialties.csv` |
| **Doc file** | `data/states/ca/ca_medicaid_specialties.md` |
| **Row count** | 31 data rows |
| **Sources** | APL21-006 Attachment A & B, APL19-002, Network Certification Checklist, CA Taxonomy Crosswalk |
| **Source URLs** | DHCS APL21-006 (Medi-Cal Managed Care Provider Contract); healthlaw.org for supplementary network adequacy rules |
| **Extraction method** | `pdftotext` + `grep`/`sed`; taxonomy crosswalk from `.xls` via `cat -v` + parsing |
| **Verification** | Cross-referenced with CA Medi-Cal network adequacy regulations. Population density tiers verified against source. |
| **Known issues** | Dental services sourced from healthlaw.org (separate managed care delivery system) — not in primary DHCS documents |
| **Notes** | Uses 4-tier population density system (Dense/Medium/Small/Rural) for specialist travel times. Timely access column added (within 10/15 business days). |

### New York (NY) — VERIFIED (Round 2, Aug 2025)

| Field | Value |
|---|---|
| **Status** | Verified ✓ (2 rounds of fixes) |
| **Data file** | `data/states/ny/ny_medicaid_specialties.csv` |
| **Doc file** | `data/states/ny/ny_medicaid_specialties.md` |
| **Row count** | 133 data rows (+3 from MCO v4.0) |
| **Sources** | MCO Service Delivery Networks Guidelines v3.0 + v4.0 (Revised Jan 2025), PNDS Data Dictionary v8.0 + v12 (Aug 2024) |
| **Source URLs** | `https://www.health.ny.gov/health_care/managed_care/managed_care_overview.htm`; Guidelines v4: `/health_care/managed_care/docs/mco_sdn_guidelines_v4.pdf`; Dictionary v12: `/health_care/managed_care/docs/dictionary.pdf` |
| **Extraction method** | `pdftotext` + `grep`/`sed`. curl with Mozilla User-Agent required. PNDS v12 ~24K lines — Tables 1 & 2 extracted via line-range grep with noise filtering. |
| **Verification** | 2-pass verification against PNDS v12 + MCO v4.0. All specialty codes, caseload ratios, and HARP ratios re-verified. |
| **Errors found & fixed** | See below |
| **Notes** | NY uses RPC regions (Northeast, Finger Lakes, NYC, Central, Utica-Adirondack, Mid-Hudson, Western, Long Island, Northern Metro) + Urban/Rural county classification. Program types: Medicaid, CHP, HARP, HIV SNP, MAP, MLTC, PACE, FIDA. |

#### NY Verification Errors — Round 1 (Initial)

| # | Severity | Field | Original | "Fixed" | Correct |
|---|---|---|---|---|---|
| 1 | Critical | Travel time — Primary Care | `10 mi / 30 min` | ✓ Metro: `30 min public transit` / Non-metro: `30 mi / 30 min` | Correct |
| 2 | Critical | Physical Med & Rehab code | `170` | ~~`159`~~ | **`160`** (PNDS v12) |
| 3 | Critical | Plastic Surgery code | `160` | ~~`165`~~ | **`170`** (PNDS v12) |
| 4 | Critical | Pediatric Surgery code | `153` | ~~`156`~~ | **`153`** (PNDS v12 — original was correct) |
| 5 | Minor | OB/GYN code padding | `89` | ~~`089`~~ | **`89`** (PNDS v12 — original was correct) |

#### NY Verification Errors — Round 2 (Aug 2025, vs PNDS v12 + MCO v4.0)

| # | Severity | Field | Wrong Value | Corrected | Source |
|---|---|---|---|---|---|
| 1 | Critical | Physical Med & Rehab code | `159` | **`160`** | PNDS v12 Table 1 |
| 2 | Critical | Plastic Surgery code | `165` | **`170`** | PNDS v12 Table 1 |
| 3 | Critical | Pediatric Surgery code | `156` | **`153`** | PNDS v12 Table 1 |
| 4 | Minor | OB/GYN code | `089` | **`89`** | PNDS v12 Table 1 |
| 5 | Critical | Internal Medicine HARP ratio | `2500-4070` | **`3550`** | MCO v3.0/v4.0 Att 3 |
| 6 | Critical | OB/GYN HARP ratio | `6600-8250` | **`8320-10400`** | MCO v3.0/v4.0 Att 3 |
| 7 | Critical | Pediatrics HARP ratio | `8320-10400` | **`6600-8250`** | MCO v3.0/v4.0 Att 3 |

#### New Entries Added (MCO v4.0)

| Specialty | Tier | Requirement | Source |
|---|---|---|---|
| Emergency Medicine | Specialist | 18,490 pop/pract | MCO v4.0 Att 3 (not in PNDS) |
| Other Licensed Practitioner (OLP) | Behavioral Health | 50% or min 2 per county/region | MCO v4.0 Att 4 |
| Medically Supervised Detoxification | Behavioral Health (OASAS) | 2 per county/region | MCO v4.0 Att 4 |

## Planned States

| State | Priority | Rationale |
|---|---|---|
| TX | High | Largest Medicaid enrollment |
| FL | High | Large enrollment, complex network rules |
| IL | Medium | Major urban/rural split |
| NC | Medium | Growing Medicaid expansion state |

## Methodology Notes

- **CSV schema**: `tier,category,specialty,designation_type,specialty_code,provider_count_requirement,travel_time_requirement,enrollees_per_provider,source`
- **Tier values**: Primary Care, OB/GYN, Specialist, Behavioral Health, Crossover, Dental, Facility, LTSS, HCBS, CFCO, Hemophilia, Ancillary
- **Source PDFs**: Stored in `data/states/<state>/sources/` for offline verification
- **Extraction**: `pdftotext` preferred over Python PDF libraries for reliability. Post-processing with `grep`/`sed` to filter extraction artifacts.
- **Verification**: Minimum 2-pass verification — (1) structural check against source tables, (2) spot-check specific codes/ratios against raw source text.
