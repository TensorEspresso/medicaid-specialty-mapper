# Illinois Medicaid Managed Care — Provider Categories & Network Adequacy

## Overview

Illinois Medicaid managed care (HealthChoice Illinois) uses **9 broad provider categories** for network adequacy monitoring, not a granular specialty-by-specialty taxonomy. All specialty services fall under a single "Specialist" umbrella category with uniform urban/rural access standards.

**Program**: HealthChoice Illinois (HCIL)
**Administered by**: Illinois Department of Healthcare and Family Services (HFS)
**MCOs**: 5 health plans + YouthCare Specialty Plan (youth with serious emotional disturbances) + MLTSS MMPs

## Network Adequacy Standards (from MCPAR CY24, Topic V)

### Geographic Access Standards

| Category | Standard | Region | Population | Monitoring |
|---|---|---|---|---|
| Primary Care | 5 weeks routine / 3 weeks non-serious | Statewide | Adult & pediatric | Shopper Calls (Annual) |
| OB/GYN | 2 weeks (1st trimester) / 1 week (2nd trimester) | Statewide | Adult & pediatric | Shopper Calls (Annual) |
| Specialist — Urban | 60 miles or 60 minutes | Urban | Adult & pediatric | Geomapping (Annual) |
| Specialist — Rural | 90 miles or 90 minutes | Rural | Adult & pediatric | Geomapping (Annual) |
| Behavioral Health | % provider availability | Statewide | Adult & pediatric | Shopper Calls (As needed) |
| Dental | 30 miles or 30 minutes | Statewide | Adult & pediatric | Geomapping (Annual) |
| Hospital | 30 miles or 30 minutes | Statewide | Adult & pediatric | Geomapping (Annual) |
| Pharmacy — Urban | 15 miles or 15 minutes | Urban | Adult & pediatric | Geomapping (Annual) |
| Pharmacy — Rural | 60 miles or 60 minutes | Rural | Adult & pediatric | Geomapping (Annual) |

### Provider Types (from HFS2243i Enrollment Form)

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

## Monitoring Framework

- **EQRO (External Quality Review Organization)**: HSAG conducts annual Network Access Verification (NAV) / Time-Distance Studies (TDS)
- **Provider File Layout (PFL)**: MCOs submit quarterly PFLs with provider counts by type, region, and county
- **Access and Availability Surveys (AAS)**: Revealed shopper surveys for appointment wait times
- **Geomapping**: Annual geographic analysis for distance/time standards
- **Corrective Action Plans (CAP)**: Required for MCOs failing to meet standards

## Latest Network Adequacy Results (Dec 2024)

**Compliant**: All categories except:
- **Pharmacies**: Gaps in select rural counties
- **Oral surgeons**: Gaps in select rural counties
- **Allergy and immunology specialists**: Regional gaps noted in EQRO report

## Sources

| Document | Description | Location |
|---|---|---|
| MCPAR CY24 | Managed Care Performance Assessment Report, 194 pages | `data/states/il/sources/il_mcpar_cy24.pdf` |
| EQRO Report 2022-2023 | External Quality Review Organization report, 622 pages | `data/states/il/sources/il_eqro_2022_2023.pdf` |
| HFS2243i | Provider enrollment form with Provider Type/Category tables | `data/states/il/sources/il_hfs2243i.pdf` |
| MCO Manual | General provider reimbursement and policy guide | `data/states/il/sources/il_mco_manual.pdf` |
| Network Standards | 4-page network adequacy standards summary | `data/states/il/sources/il_network_standards.pdf` |
| RFP 26-478 | HealthChoice Illinois Medicaid Managed Care RFP (BidBuy) | Online only |
| 837P Taxonomy Table | COS-to-Taxonomy crosswalk for professional claims (42 codes) | `data/states/il/sources/il_837p_taxonomy.pdf` |
| 837I Taxonomy Table | COS-to-Taxonomy crosswalk for institutional claims (32 codes) | `data/states/il/sources/il_appendix4_837i_taxonomy.pdf` |
| COS Crosswalk (xlsx) | Legacy COS to Taxonomy mapping for LTC facilities (9 codes) | `data/states/il/sources/il_cos_crosswalk.xlsx` |
| Access-to-Care Standards | HealthChoice Illinois Contract exhibit — same 9 broad categories | `data/states/il/sources/il_access_to_care.pdf` |
| MCO Model Contract (2018-24-001) | Defines PCP and Behavioral Health broadly. No specialty breakdown for the 9 categories. | `data/states/il/sources/il_model_contract_admin.pdf` |
| Access Monitoring Review Plan (2016) | Identifies 5 specialties for analysis: Anesthesiology, Cardiology, Endocrinology, Oncology, Pediatrics. Pre-dates current managed care expansion. | `data/states/il/sources/il_access_monitoring_plan.pdf` |
| Transparency Glossary | Defines PCP as physicians, FQHCs, RHCs, NPs, hospital clinics, local health depts, school clinics, WHCPs. | `https://hfs.illinois.gov/info/factsfigures/transparency/transparencyglossary.html` |
| Chapter 100 General Handbook | General provider enrollment guide. No specialty taxonomy. | `https://hfs.illinois.gov/content/dam/soi/en/web/hfs/medicalproviders/handbooks/Chapter100GeneralHandbook.pdf` |
| YouthCare Specialty Plan Contract | Broad category usage only. | `data/states/il/sources/il_youthcare_contract.pdf` |

## Comparison to Other States

| State | Specialty Count | Approach |
|---|---|---|
| PA | 86 | Granular specialty list with caseload ratios |
| NY | 133 | PNDS data dictionary with caseload + HARP ratios |
| FL | 64 | Regional provider ratios + urban/rural geographic standards |
| TX | 36 | Metro/Micro/Rural tier system with provider ratios |
| CA | 31 | 4-tier population density system |
| **IL** | **9** | **Broad categories only — "Specialist" is a single catch-all** |

## Category Descriptions & Guidance

### Primary Care
- **Access standard**: 5 weeks routine / 3 weeks non-serious (shopper calls)
- **Includes**: Family Practice (207Q00000X), Primary Care Clinic (261QP2300X), FQHC (261QF0400X), Rural Health Clinic (261QR1300X), Student Health Center (261QS1000X)
- **Guidance**: HFS uses "current default logic" to route Healthy Kids Services (COS 030) claims to Primary Care without provider action

### OB/GYN
- **Access standard**: 2 weeks (1st trimester) / 1 week (2nd trimester) (shopper calls)
- **Includes**: Obstetrics/Gynecology providers enrolled under Physician Type 010
- **Guidance**: No separate provider type code — falls under Physicians (010) with OB/GYN specialty designation

### Specialist — Urban / Rural
- **Access standard**: 60 mi/60 min (urban) / 90 mi/90 min (rural) (geomapping)
- **Includes**: ALL clinical specialties NOT otherwise categorized (catch-all)
- **Taxonomy codes visible in billing crosswalk**: Anesthesiology (207L00000X), Ophthalmology (207W00000X), Radiology (261QR0200X), MRI (261QM1200X), Mammography (261QR0206X), and all subspecialties
- **Guidance**: No specialty-by-specialty breakdown — all specialists share uniform access standards regardless of clinical specialty

### Behavioral Health
- **Access standard**: % provider availability (shopper calls, as needed)
- **Includes**: Mental Health Clinic/Center (261QM0801X), Adult Mental Health (261QM0850X), Adolescent/Children Mental Health (261QM0855X), Psychologist (103T00000X), Clinical Social Worker (1041C0700X), Substance Abuse Rehab (261QR0405X, 324500000X), Methadone (261QM2800X)
- **Guidance**: YouthCare Specialty Plan serves youth with serious emotional disturbances separately

### Dental
- **Access standard**: 30 mi/30 min (geomapping)
- **Includes**: Dentist (122300000X), Oral/Maxillofacial Surgery (1223X0400X)
- **Guidance**: Oral surgeons show documented gaps in rural counties (Dec 2024)

### Hospital
- **Access standard**: 30 mi/30 min (geomapping)
- **Includes**: General Acute Care (282N00000X), Children's Hospital (282NC2000X), Psychiatric Hospital (283Q00000X), Rehabilitation Hospital (283X00000X), Critical Access (282NC0060X), Rural Hospital (282NR1301X), Chronic Disease (281P00000X), ESRD (261QE0700X), Birthing Center (261QB0400X), ASTC (261QA1903X)
- **Guidance**: FFS hospital billing uses 282N00000X as default; other hospital taxonomy codes permitted

### Pharmacy — Urban / Rural
- **Access standard**: 15 mi/15 min (urban) / 60 mi/60 min (rural) (geomapping)
- **Includes**: Pharmacy (333600000X)
- **Guidance**: Pharmacy gaps documented in rural counties (Dec 2024)

### Allied Health / Therapists
- **Not a separate network adequacy category** — falls under "Specialist" for access monitoring
- **Includes**: Physical Therapist (225100000X), Occupational Therapist (225X00000X), Speech-Language Pathologist (235Z00000X), Audiologist (231H00000X), Chiropractor (111N00000X), Podiatrist (213EG0000X)
- **Guidance**: Early Intervention providers may bill Medical Equipment (COS 041) and Medical Supplies (COS 048) with therapy taxonomy codes

### Nursing
- **Not a separate network adequacy category** — falls under "Primary Care" or "Specialist" depending on role
- **Includes**: Nurse Practitioner (363L00000X), Registered Nurse (163W00000X), Licensed Practical Nurse (164W00000X), Nurse Anesthetist (367500000X), Certified Midwife (367A00000X)
- **Guidance**: NP services bill under COS 016/057; RN services under COS 020; CNA under COS 021

### Transportation
- **Not a separate network adequacy category**
- **Includes**: Ambulance (341600000X), Secured Medical Transport Van (343800000X), Non-Emergency Van (343900000X), Taxi (344600000X), Private Auto (347C00000X)
- **Guidance**: Medicar (COS 052) routes to Secured Van (343800000X) if HCPCS A0130; Service Car (COS 054) routes to Non-Emergency Van (343900000X) if HCPCS A0120

### Facilities / LTC
- **Not a separate network adequacy category** — falls under "Hospital"
- **Includes**: Skilled Nursing (314000000X), ICF-MR (315P00000X), ICF-MI (310500000X), Assisted Living (310400000X), Alzheimer/Dementia (311500000X), Residential Treatment (320600000X, 323P00000X), Home Health (251E00000X), Hospice (251G00000X, 315D00000X)
- **Guidance**: LTC facilities bill under Bill Type 089X (Special Facility - Other) with COS 86-87

## Billing/Enrollment Taxonomy Crosswalk

Illinois publishes **Category of Service (COS) to NUCC Taxonomy** crosswalks for **claim processing and provider enrollment** — NOT for network adequacy. These are administrative mappings used by HFS to route 837P/837I claims to the correct reimbursement category.

| Document | Purpose | Taxonomy Codes | Location |
|---|---|---|---|
| 837P Taxonomy Table | Professional claims routing (physicians, therapists, clinics) | 42 unique codes | `data/states/il/sources/il_837p_taxonomy.pdf` |
| 837I Taxonomy Table | Institutional claims routing (hospitals, facilities) | 32 unique codes | `data/states/il/sources/il_appendix4_837i_taxonomy.pdf` |
| COS Crosswalk (xlsx) | Legacy COS to Taxonomy mapping (LTC facilities) | 9 unique codes | `data/states/il/sources/il_cos_crosswalk.xlsx` |

**Key distinction**: These crosswalks map IL's internal COS codes (001-106+) to NUCC taxonomy codes for billing. They are NOT network adequacy specialty lists. The "specialties" visible in the taxonomy codes (Anesthesiology, Radiology, etc.) are incidental to the billing system — they determine claim routing, not network adequacy monitoring.

**Extracted crosswalks** (for reference):
- `data/states/il/il_billing_taxonomy_837p.csv` — 42 taxonomy codes from 837P table
- `data/states/il/il_cos_crosswalk.csv` — 26 PT/COS/Taxonomy combinations from xlsx

## Notes

- HFS2243i references "Attachment D-1" for Provider Specialty mapping, but this attachment was never published as a standalone document
- The MCO contract exhibits (RFP 26-478) use the same broad categories as MCPAR
- No granular specialty taxonomy exists for network adequacy — confirmed across all reviewed HFS documents, MCO contracts, EQRO reports, and RFP exhibits
- Illinois is the only state in this project that does not publish a specialty-by-specialty list for Medicaid managed care network adequacy
- The COS-to-Taxonomy crosswalks (837P/837I) are for billing/enrollment only — they do NOT define network adequacy specialties
- **EQRO Specialist Analysis**: HFS requests ad-hoc analysis of specific specialist categories (allergy/immunology, audiology, endocrinology, neurosurgery, oral surgery, pulmonology) but these are NOT official published network adequacy categories — they're requested by HFS for EQRO validation on a case-by-case basis
- **2016 Access Monitoring Review Plan**: Identified 5 specialties for analysis based on utilization (Anesthesiology, Cardiology, Endocrinology, Oncology, Pediatrics) — pre-dates current managed care expansion
- **Transparency Glossary**: Defines "Primary Care Provider" as physicians, FQHCs, RHCs, NPs, hospital-based clinics, local health departments, school-based clinics, and WHCPs
