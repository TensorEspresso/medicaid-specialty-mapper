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
| **Crosswalk** | `data/states/ca/sources/ca_taxonomy_crosswalk.csv` — 863 rows (NUCC taxonomy codes mapped to DHCS NA groups/categories) |
| **Sources** | APL21-006 Attachment A & B, APL19-002, Network Certification Checklist, CA Taxonomy Crosswalk |
| **Source URLs** | DHCS APL21-006 (Medi-Cal Managed Care Provider Contract); healthlaw.org for supplementary network adequacy rules |
| **Extraction method** | `pdftotext` + `grep`/`sed`; taxonomy crosswalk from `.xls` via `cat -v` + parsing |
| **Verification** | Cross-referenced with CA Medi-Cal network adequacy regulations. Population density tiers verified against source. |
| **Known issues** | Dental services sourced from healthlaw.org (separate managed care delivery system) — not in primary DHCS documents |
| **Notes** | Uses 4-tier population density system (Dense/Medium/Small/Rural) for specialist travel times. Timely access column added (within 10/15 business days). |

### Texas (TX) — INCOMPLETE (Missing Crosswalk)

| Field | Value |
|---|---|
| **Status** | Incomplete (Crosswalk Missing) |
| **Data file** | `data/states/tx/tx_medicaid_specialties.csv` |
| **Doc file** | `data/states/tx/tx_medicaid_specialties.md` |
| **Row count** | 36 data rows |
| **Sources** | UMCM Ch 5.28.1 Performance Standards (xlsx), Network Capacity Layout (xlsx), Network Adequacy Report Dec 2024 (PDF) |
| **Source URLs** | UMCM parent: `https://www.hhs.texas.gov/services/health/medicaid-chip/managed-care-contract-management/texas-medicaid-chip-uniform-managed-care-manual`; Standards xlsx: `/documents/laws-regulations/handbooks/umcm/5-28-1.xlsx`; Network adequacy PDF: `/documents/medicaid-managed-care-provider-network-adequacy-dec-2024.pdf` |
| **Extraction method** | `openpyxl` for xlsx files; `pdftotext` for PDF appendix tables |
| **Verification** | Cross-referenced xlsx Standards and Specifications sheet with PDF Appendix A (Tables A-1, A-2, A-3). All 36 specialties verified across both sources. |
| **Known issues** | None |
| **Notes** | Uses 3-tier county system (Metro/Micro/Rural). 16 MCOs + 3 DMOs. Dental carved out to DMOs (except STAR Health). LTSS in-home services use "choice of 2 per county" standard. SB 760 framework. Telemedicine providers excluded from network adequacy counts. |

### New York (NY) — INCOMPLETE (Missing Crosswalk)

| Field | Value |
|---|---|
| **Status** | Incomplete (Crosswalk Missing) |
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

## Illinois (IL) — COMPLETE (Broad Categories)

| Field | Value |
|---|---|
| **Status** | Verified ✓ |
| **Data file** | None — no granular specialty taxonomy available |
| **Doc file** | `data/states/il/il_medicaid_specialties.md` |
| **Row count** | N/A — IL uses 9 broad provider categories, not a specialty-by-specialty list |
| **Sources** | MCPAR CY24 (194 pages), EQRO Report 2022-2023 (622 pages), HFS2243i Enrollment Form, MCO Manual, Network Standards PDF, HealthChoice IL RFP 26-478 (BidBuy), 837P Taxonomy Table (42 codes), 837I Taxonomy Table (32 codes), COS Crosswalk xlsx (9 LTC codes), Access-to-Care Standards, MCO Model Contract (2018-24-001), Access Monitoring Review Plan (2016), Transparency Glossary, Chapter 100 General Handbook, YouthCare Specialty Plan Contract |
|| **Source URLs** | HFS: `https://www.hfs.illinois.gov/medicalproviders/handbooks.html`; MCO Manual: `/medicalproviders/handbooks/ManagedCareProviderManual.pdf`; Network Standards: `/medicalproviders/handbooks/NetworkStandards.pdf`; HFS2243i: `/medicalproviders/handbooks/HFS2243i.pdf`; MCPAR CY24: `/hfs site:illinois.gov mcpar`; EQRO: `/hfs site:illinois.gov eqro`; RFP: `https://bidbuy.illinois.gov` (26-478HFS-MEDPR-B-49167); 837P Taxonomy: `/content/dam/soi/en/web/hfs/sitecollectiondocuments/837ptaxonomytableupdate91018final.pdf`; 837I Taxonomy: `/content/dam/soi/en/web/hfs/sitecollectiondocuments/appendix4837itaxonomy.pdf` |
|| **Extraction method** | `pdftotext` + `grep`/`sed` on MCPAR Topic V (Network Adequacy), EQRO reports, HFS2243i Provider Type tables, 837P/837I Taxonomy crosswalks |
|| **Verification** | Cross-referenced MCPAR, EQRO, HFS2243i, MCO Manual, Network Standards, RFP, AND 837P/837I Taxonomy crosswalks. Confirmed: IL has COS-to-Taxonomy crosswalks for billing/enrollment ONLY — NOT for network adequacy. No granular specialty taxonomy exists for network adequacy. |
|| **Known issues** | **No granular specialty list exists for network adequacy.** IL Medicaid managed care uses 9 broad provider categories for network adequacy. HFS2243i references "Attachment D-1" for Provider Specialty, but the attachment was not published separately. MCO contract exhibits (RFP 26-478) also use the same broad categories. **IL DOES publish COS-to-Taxonomy crosswalks (837P/837I) for billing/enrollment — these are NOT network adequacy specialty lists.** |
| **Notes** | See below. |

### IL Provider Categories (from MCPAR Topic V + HFS2243i)

| # | Category | Access Standard | Region | Population | Monitoring |
|---|---|---|---|---|---|
| 1 | Primary Care | 5 wks routine / 3 wks non-serious | Statewide | Adult & pediatric | Secret/Revealed Shopper Calls (Annual) |
| 2 | OB/GYN | 2 wks (1st trimester) / 1 wk (2nd trimester) | Statewide | Adult & pediatric | Secret/Revealed Shopper Calls (Annual) |
| 3 | Specialist — Urban | 60 miles or 60 minutes | Urban | Adult & pediatric | Geomapping (Annual) |
| 4 | Specialist — Rural | 90 miles or 90 minutes | Rural | Adult & pediatric | Geomapping (Annual) |
| 5 | Behavioral Health | Percentage of provider availability | Statewide | Adult & pediatric | Secret/Revealed Shopper Calls (As needed) |
| 6 | Dental | 30 miles or 30 minutes | Statewide | Adult & pediatric | Geomapping (Annual) |
| 7 | Hospital | 30 miles or 30 minutes | Statewide | Adult & pediatric | Geomapping (Annual) |
| 8 | Pharmacy — Urban | 15 miles or 15 minutes | Urban | Adult & pediatric | Geomapping (Annual) |
| 9 | Pharmacy — Rural | 60 miles or 60 minutes | Rural | Adult & pediatric | Geomapping (Annual) |

### IL Provider Types (from HFS2243i)

| Code | Provider Type | Category of Service |
|---|---|---|
| 010 | Physicians | Physicians |
| 011 | Dentists | Dentists |
| 012 | Optometrists | Optometrists |
| 013 | Podiatrists | Podiatrists |
| 014 | Chiropractors | Chiropractors |
| 016 | Advanced Practical Nurses | Advanced Practical Nurses |
| 022 | Physical Therapists | Physical Therapists |
| 023 | Occupational Therapists | Occupational Therapists |
| 024 | Speech Therapists | Speech Therapists |
| 025 | Audiologists | Audiologists |
| 031 | General Hospitals | Hospitals |
| 032 | Psychiatric Hospitals | Hospitals |

### Key Findings

- **No specialty-by-specialty taxonomy for network adequacy** — Unlike PA (86 specialties), CA (31), TX (36), NY (133), or FL (64), IL uses only 9 broad categories for network adequacy. "Specialist" is a single catch-all category with urban/rural splits.
- **MCOs**: 5 health plans + YouthCare Specialty Plan (for youth with serious emotional disturbances). Managed Long Term Services and Supports (MLTSS) via separate MMPs.
- **Monitoring**: EQRO (HSAG) conducts annual Network Access Verification (NAV) / Time-Distance Studies (TDS), quarterly Provider File Layout (PFL) reviews, and revealed Access and Availability Surveys (AAS).
- **Documented gaps** (Dec 2024): Pharmacies and oral surgeons in select rural counties. All other categories met standards. Corrective Action Plans (CAP) required for non-compliance.
- **Specific specialty gaps noted in EQRO**: Allergy and immunology specialists, oral surgery specialists.
- **HFS2243i "Attachment D-1"** references Provider Specialty mapping but was never published as a standalone document. The enrollment form itself only lists the 12 broad provider types above.
- **COS-to-Taxonomy crosswalks exist for billing ONLY** — IL publishes 837P (42 codes) and 837I (32 codes) crosswalks mapping Category of Service to NUCC Taxonomy for claim routing. These are NOT network adequacy specialty lists. The "specialties" visible (Anesthesiology, Radiology, etc.) determine claim routing, not network adequacy monitoring.
- **EQRO Specialist Analysis**: HFS requests ad-hoc analysis of specific specialist categories (allergy/immunology, audiology, endocrinology, neurosurgery, oral surgery, pulmonology) but these are NOT official published network adequacy categories — they're requested by HFS for EQRO validation on a case-by-case basis
- **2016 Access Monitoring Review Plan**: Identified 5 specialties for analysis based on utilization (Anesthesiology, Cardiology, Endocrinology, Oncology, Pediatrics) — pre-dates current managed care expansion
- **Transparency Glossary**: Defines "Primary Care Provider" as physicians, FQHCs, RHCs, NPs, hospital-based clinics, local health departments, school-based clinics, and WHCPs

### Why No CSV

Illinois does not publish a granular specialty taxonomy for Medicaid managed care network adequacy. The state's approach is intentionally broad — "Specialist" covers all specialty services under a single umbrella with uniform access standards (60/90 mi/min by region). Creating a CSV would require inventing specialty categories that the state does not recognize, which contradicts the project's primary-source methodology. The documentation above captures the complete IL framework.

## Florida (FL) — COMPLETE

| Field | Value |
|---|---|
| **Status** | Verified ✓ |
| **Data file** | `data/states/fl/fl_medicaid_specialties.csv` |
| **Doc file** | `data/states/fl/fl_medicaid_specialties.md` |
| **Row count** | 64 data rows |
| **Crosswalk** | `data/states/fl/fl_specialty_taxonomy_crosswalk.csv` — FL Taxonomy Master List (TML), 1,100 rows (59 provider types, 233 specialty codes, 531 taxonomy codes) |
| **Sources** | Exhibit II-A MMA Program (Oct 2025, 143 pages), Dental Attachment II Core Contract Provisions (Oct 2025, 255 pages), FL Taxonomy Master List (TML) from portal.flmmis.com |
| **Source URLs** | AHCA SMMC Plans: `https://ahca.myflorida.com/medicaid/statewide-medicaid-managed-care/2025-2030-smmc-plans.html`; Exhibit II-A: `/content/download/27249/file/Exhibit%20II-A%20Managed%20Medical%20Assistance%20(MMA)%20Program%20Oct%202025.pdf`; Dental: `/content/download/27252/file/Attachment%20II_Core%20Contract%20Provisions%20October%202025.pdf`; TML: `http://portal.flmmis.com/FLPublic/Portals/0/StaticContent/Public/MANAGED%20CARE/prvpm192_01.zip` |
| **Extraction method** | `pymupdf` PDF text extraction → Table 4 (MMA, pages 65-68) + Table 4 (Dental, pages 82-83) → CSV via Python script. TML downloaded from zip, extracted CSV used as-is. |
| **Verification** | Direct PDF text extraction verified against source. All 64 specialties transcribed from Table 4. Crosswalk: 63/64 matched to NUCC taxonomy (LPHA unmatched — FL-specific). |
| **Known issues** | Feb 2025 version of Exhibit II-A is 1 page (stub). Oct 2025 version is authoritative. AHCA site is a SPA — browser navigation required (curl fails on some URLs). Licensed Practitioners of the Healing Arts (LPHA) has no NUCC taxonomy equivalent. |
| **Notes** | Uses regional provider ratios + urban/rural geographic access standards. Pediatric variants for several specialties. Behavioral health uses unique counting system (BCaBA = 0.5 Lead Analyst). Dental carved out to separate Prepaid Dental program. |

## North Carolina (NC) — COMPLETE

| Field | Value |
|---|---|
| **Status** | Verified ✓ |
| **Data file** | `data/states/nc/nc_medicaid_specialty_reference.csv` |
| **Crosswalk** | `data/states/nc/nc_taxonomy_crosswalk.csv` — Provider Permission Matrix (PPM), 302 rows (NUCC taxonomy Level 2 + Level 3 codes mapped to enrollment types, CCNC/CA eligibility, federal requirements, risk levels) |
| **Doc file** | `data/states/nc/nc_methodology.md` |
| **Row count** | 48 data rows (specialty reference) + 302 rows (taxonomy crosswalk) |
| **Sources** | NC Medicaid Network Adequacy Time or Distance Standards PDF, Carolina Complete Health Provider Manual (Jan 2026), RFP 30-190029-DHB V. Scope of Services, Healthy Blue Provider Manual (cross-verification), NCTracks Provider Permission Matrix (May 2026) |
| **Source URLs** | Standards: `https://medicaid.ncdhhs.gov/network-adequacy-time-or-distance-standards/download?attachment`; CCH Manual: `https://network.carolinacompletehealth.com/content/dam/centene/carolinacompletehealth/pdfs/CCH_Current_PDF_Provider_Manual.pdf`; PHP Contract: `https://www.ncdhhs.gov/dhhs-php-contract/open`; Healthy Blue: `https://provider.healthybluenc.com/docs/inline/NCNC_CAID_ProviderManual.pdf`; PPM: `https://www.nctracks.nc.gov/content/public/providers/provider-enrollment.html` (download in Quick Links) |
| **Extraction method** | `pdftotext` + `grep`/`sed` on CCH Provider Manual (pages 39-44). Specialty list explicitly enumerated in CCH manual. Crosswalk: Excel PPM downloaded from NCTracks, parsed with `openpyxl` → CSV. |
| **Verification** | Cross-verified specialty list (21 types) against Healthy Blue provider manual. Network adequacy standards confirmed against state document. Taxonomy crosswalk sourced from authoritative NCTracks PPM. |
| **Known issues** | State's network adequacy standards document references "per specialty type" but does NOT enumerate them. The authoritative specialty list comes from MCO provider manuals (Carolina Complete Health). |
| **Notes** | NC uses a two-tier program structure: Standard Plan (managed care via 5 statewide PHPs + 6 regional PIHPs) and Medicaid Direct. 21 specialty care types explicitly enumerated. Pain Management requires Board Certification. Age cutoff differs: physical health = 21, behavioral health = 18. PPM covers 302+ taxonomy codes with enrollment type, CCNC/CA eligibility, federal site visit/fee requirements, fingerprinting, and risk level. |

### Ohio (OH) — COMPLETE (June 2026)

| Field | Value |
|---|---|
| **Status** | Verified ✓ |
| **Data file** | `data/states/oh/oh_medicaid_specialties.csv` |
| **Doc file** | `data/states/oh/oh_medicaid_specialties.md` |
| **Row count** | 178 data rows (MCO: 104, MCOP: 42, OhioRISE: 32) |
| **Sources** | MCO Agreement 2026 (Appendix F Tables F.1-F.7), MCOP Agreement 2026 (Tables F.2, F.6), OhioRISE Agreement 2026 (Table F.2), Exception Memo Nov 2025 |
| **Source URLs** | MCO: `dam.assets.ohio.gov/.../2026_01_MCO_Final_1.pdf`; MCOP: `dam.assets.ohio.gov/.../2026_01_Next_Gen_MyCare_Final_PA.pdf`; OhioRISE: `dam.assets.ohio.gov/.../2026_01_OhioRISE_Provider_Agreement_Final_Rates_Combined.pdf`; Exception Memo: `dam.assets.ohio.gov/.../2026_MCO_and_MCOP_Exception_Request_Process_Memo.pdf` |
| **Source note** | Cloudinary URLs require `%20` for spaces in path (not `+` encoding) |
| **Extraction method** | `pdftotext` + Python parsing. MCO Table F.2: 26 specialties × 4 geographic tiers = 104 rows. MCOP Table F.2: 28 CMS specialties + 14 facilities. OhioRISE Table F.2: 8 BH specialty types. |
| **Verification** | Cross-verified MCO T&D values against Exception Memo Appendix B Table B.1: Adult Dental, Hospital, MAT/SUD-Outpatient all match exactly. |
| **Known issues** | Oral Surgery has outlier standards (98min/65mi Metro, 110min/80mi Micro/Rural). Vision/ophthalmology not in MCO T&D table — covered by minimum count only. MCOP time/distance for non-LTSS referenced from MCO standards. **No official NUCC taxonomy crosswalk** — best-effort mapping created using CMS crosswalk (Nov 2017) as reference. OhioRISE uses Ohio-specific provider type codes (37, 42, 47, 52, 84, 95, etc.) not NUCC taxonomy codes. |
| **Notes** | Three separate programs with distinct frameworks. MCO: 26 specialties with time/distance by 4 geographic tiers (Large Metro/Metro/Micro/Rural). MCOP: CMS provider panel (28 specialties + 14 facilities) with county-based minimums for 88 counties. OhioRISE: 8 BH specialty types with distance-only standards. Additional county-based minimums: Tables F.3 (hospitals), F.4 (nursing facilities), F.5 (MAT), F.6 (BH), F.7 (dental/vision). |

### Arizona (AZ) — COMPLETE

| Field | Value |
|---|---|
| **Status** | Verified ✓ |
| **Data file** | `data/states/az/az_medicaid_specialties.csv` |
| **Doc file** | `data/states/az/az_medicaid_specialties.md` |
| **Crosswalk** | `data/states/az/az_taxonomy_crosswalk.csv` |
| **Row count** | 9 data rows |
| **Sources** | ACOM Policy 436 - Network Standards, AHCCCS Provider Types List |
| **Extraction method** | `pdftotext` + Python parsing |
| **Verification** | Verified against ACOM Policy 436 and AHCCCS Provider Type list. Crosswalk built using NUCC v25.1. |
| **Notes** | Uses a system of Provider Type Codes (e.g., 08 for MD) and Specialty Codes (e.g., 062 for Cardiology). Distinct standards for Maricopa/Pima vs Other counties. |

### Michigan (MI) — COMPLETE (June 2026)

| Field | Value |
|---|---|
| **Status** | Verified ✓ |
| **Data file** | `data/states/mi/mi_medicaid_specialties.csv` |
| **Doc file** | `data/states/mi/mi_medicaid_specialties.md` |
| **Crosswalk** | `data/states/mi/mi_taxonomy_crosswalk.csv` — 66 rows (51 individual provider types + 15 facility types mapped to NUCC taxonomy) |
| **Row count** | 94 data rows (MDHHS: 22, DIFS: 52, PIHP: 20) |
| **Sources** | MDHHS Network Adequacy Standards (FY25 CHCP), PIHP Network Adequacy Procedural Document (Jan 2026), DIFS Network Adequacy Guidance (Updated 3.26), BCBSM Taxonomy Code Map |
| **Source URLs** | MDHHS: `michigan.gov/mdhhs/.../Network-Adequacy-and-Timely-Access-Standards.pdf`; PIHP: `michigan.gov/mdhhs/.../PIHP_Network_Adequacy_Standard_Procedural_Document.pdf`; DIFS: `michigan.gov/difs/.../Network_Adequacy_Guidance.pdf` |
| **Extraction method** | `pdftotext` + Python parsing. MDHHS table: direct text extraction from multi-column PDF. DIFS: Appendix 9.1 specialty codes + Section 4.3 time/distance tables. PIHP: direct text extraction. |
| **Verification** | 2-pass verification: (1) structural check — all 94 rows validated against source tables, DIFS codes cross-referenced with Appendix 9.1 (51 individual + 15 facility types). (2) spot-check 11 entries against raw PDF text — all matched. Column alignment fixed: `designation_type` → `source`, DIFS specialty codes moved from `enrollees_per_provider` to `specialty_code`, enrollee ratios moved from `source` to `enrollees_per_provider`. (3) 3rd pass — MDHHS table: all 22 rows spot-checked against PDF (time/distance for 5 county tiers). DIFS Sec 4.1: 10 uniform-30min specialties confirmed. DIFS Sec 4.3: specialty codes verified against Appendix 9.1. PIHP: time/distance + provider-to-enrollee ratios + FY25 informational flags confirmed. **All verified.** |
| **Known issues** | DIFS "Dental" specialty (30/15 to 125/110) is a generic dental standard — MDHHS has more granular dental specialties (General Dentist, Endodontics, Oral Surgery, Periodontics, Prosthodontics). DIFS Oral & Maxillofacial Surgery references SADP standards (Section 6.1) — not included in time/distance table. PIHP FY26 standards are based on FY25 encounter data (Oct 2024 – Sep 2025). Some PIHP services marked "FY25 informational only" — no binding ratio standard yet. |
| **Notes** | Dual-delivery system: MCOs (physical health) + PIHPs (specialty behavioral health). 10 Prosperity Regions. 5 CMS county designations (Large Metro/Metro/Micro/Rural/CEAC) across 83 counties. DIFS Appendix 9.1 defines 51 individual provider specialty types + 15 facility specialty types with unique codes. DIFS Section 4.1 adds 10 specialties with uniform 30-min standard. MDHHS provider-to-enrollee ratios: PC Adult 1:500, PC Pediatric 1:500, General Dentist 1:650 (with county exceptions for Kalkaska/Missaukee/Schoolcraft). PIHP uses two-tier time/distance: Inpatient Psychiatric/Partial Hospitalization vs All Other Services. |

### Georgia (GA) — COMPLETE (June 2026)

| Field | Value |
|---|---|
| **Status** | Verified ✓ |
| **Data file** | `data/states/ga/ga_medicaid_specialties.csv` |
| **Doc file** | `data/states/ga/ga_medicaid_specialties.md` |
| **Crosswalk** | `data/states/ga/ga_taxonomy_crosswalk.csv` — 71 rows (best-effort mapping, no official GA crosswalk found) |
| **Row count** | 62 data rows (PCP: 2, Adult Specialties: 17, Pediatric Specialties: 17, OB/GYN: 1, Behavioral Health: 9, Dental: 2, Other Services: 14) |
| **Sources** | Georgia Families Contract (Figure 1: Geographic Access Standards, Figure 2: Appointment Wait Times), GeoAccess County Detail Reports (Q4 2024), AMRP 2016, Peach State Health Plan Provider Manual |
| **Source URLs** | DCH Network Adequacy: `https://dch.georgia.gov/medicaid-managed-care/network-adequacy`; DCH Archived Reports: `https://dch.georgia.gov/archived-network-adequacy-reports`; Georgia Families CMO Info: `https://medicaid.georgia.gov/programs/all-programs/georgia-families/care-management-organizations-cmo`; AMRP: `https://www.medicaid.gov/sites/default/files/2019-12/ga-amrp-16.pdf` |
| **Extraction method** | `pdftotext` + `grep`/`sed` on GeoAccess reports and AMRP. Standards extracted from Georgia Families Contract (Figure 1) — contract obtained through DCH/Medicaid.gov channels. |
| **Verification** | Crosswalk verified against NUCC v25.1 taxonomy — all 71 codes confirmed valid. Original subagent crosswalk had critical mapping errors (e.g., Adult ENT → Ophthalmology, Adult Nephrology → Dermatology) — corrected with direct NUCC lookup. (2) GA contract Figure 1: all contract provider types spot-checked — PCPs (2 within 8mi/15mi), Pediatricians (2 within 8mi/15mi), Obstetric Providers (2 within 30mi/45mi), Specialists (1 within 30mi/45mi), Dental, Hospitals, Mental Health, Pharmacy, Therapy, Vision — all match. (3) GeoAccess Q4 2024 report: all 62 CSV specialties confirmed present. **All verified.** |
| **Known issues** | **Georgia Families Contract not publicly available as standalone PDF** — the authoritative source (containing Figure 1 and Figure 2) must be obtained through FOIA or CMO channels. **No official NUCC taxonomy crosswalk** — best-effort mapping created. Georgia uses distance-only standards (miles), not time-based. |
| **Notes** | 3 CMOs (Amerigroup, CareSource, Peach State Health Plan). 6 managed care regions (Atlanta, Central, East, North, Southeast, Southwest). 2 county tiers (Urban/Rural). Distance-based standards: PCP 8mi urban/15mi rural, Specialists 30mi urban/45mi rural. Pediatric specialties tracked separately from adult (17 each). No provider-to-enrollee ratios — minimum provider counts within distance. |

## Planned States

| State | Priority | Rationale |
|---|---|---|
| FL | High | ✅ Done — see below |
| IL | Medium | ✅ Done — see below (broad categories only) |
| NC | Medium | ✅ Done — see below |
| OH | High | ✅ Done — see above |

## Methodology Notes

- **CSV schema**: `tier,category,specialty,designation_type,specialty_code,provider_count_requirement,travel_time_requirement,enrollees_per_provider,source`
- **Tier values**: Primary Care, OB/GYN, Specialist, Behavioral Health, Crossover, Dental, Facility, LTSS, HCBS, CFCO, Hemophilia, Ancillary
- **Source PDFs**: Stored in `data/states/<state>/sources/` for offline verification
- **Extraction**: `pdftotext` preferred over Python PDF libraries for reliability. Post-processing with `grep`/`sed` to filter extraction artifacts.
- **Verification**: Minimum 2-pass verification — (1) structural check against source tables, (2) spot-check specific codes/ratios against raw source text.
