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

### New York (NY) — FIXES APPLIED

| Field | Value |
|---|---|
| **Status** | Verified ✓ (errors corrected) |
| **Data file** | `data/states/ny/ny_medicaid_specialties.csv` |
| **Doc file** | `data/states/ny/ny_medicaid_specialties.md` |
| **Row count** | 130 data rows |
| **Sources** | MCO Service Delivery Networks Guidelines v3.0 (`ny_mco_service_delivery_networks_v3.pdf`), PNDS Data Dictionary (`ny_pnds_data_dictionary.pdf`) |
| **Source URLs** | `https://www.health.ny.gov/health_care/managed_care/managed_care_overview.htm`; Guidelines: `/health_care/managed_care/docs/guidelines_for_mco_service_delivery_networks-v3.0.pdf`; Dictionary: `/health_care/managed_care/docs/dictionary.pdf` |
| **Extraction method** | `pdftotext` + `grep`/`sed`. curl with Mozilla User-Agent required to bypass redirect. PNDS Dictionary ~24K lines — Tables 1 & 2 extracted via line-range grep with noise filtering. |
| **Verification** | Multi-pass verification against PNDS Table 1 source text. Specialist caseload ratios verified against MCO Guidelines Attachment 3. Program types mapped from MCO Guidelines. |
| **Errors found & fixed** | See below |
| **Notes** | NY uses RPC regions (Northeast, Finger Lakes, NYC, Central, Utica-Adirondack, Mid-Hudson, Western, Long Island, Northern Metro) + Urban/Rural county classification. Program types: Medicaid, CHP, HARP, HIV SNP, MAP, MLTC, PACE, FIDA. |

#### NY Verification Errors (Corrected)

| # | Severity | Field | Original | Corrected | Source |
|---|---|---|---|---|---|
| 1 | Critical | Travel time — Primary Care | `10 mi / 30 min` | Metro: `30 min public transit` / Non-metro: `30 mi / 30 min` | MCO Guidelines p.9, Patient to Provider Ratio Guidelines |
| 2 | Critical | Physical Med & Rehabilitation code | `170` | `159` | PNDS Table 1 line ~12895 |
| 3 | Critical | Plastic Surgery code | `160` | `165` | PNDS Table 1 line ~12905 |
| 4 | Critical | Pediatric Surgery code | `153` | `156` | PNDS Table 1 line ~12882 |
| 5 | Minor | OB/GYN code padding | `89` | `089` | PNDS Table 1 — consistent zero-padding |

**Note on Pediatrics code `150`:** Initially flagged for removal. Source confirms `150` = "Pediatric Specialty – All Except Primary Care" is a valid PNDS code (PNDS Dictionary p.6041). **No change needed.**

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
