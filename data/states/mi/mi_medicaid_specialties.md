# Michigan Medicaid Specialty Reference

**State:** Michigan (MI)  
**Program:** CHCP (Comprehensive Health Care Program)  
**Agency:** MDHHS (physical health), PIHPs (specialty behavioral health)  
**Data file:** `data/states/mi/mi_medicaid_specialties.csv` (94 rows)  
**Crosswalk:** `data/states/mi/mi_taxonomy_crosswalk.csv` (66 rows)  
**Last updated:** 2026-06-09  

---

## Program Overview

Michigan's Medicaid managed care program operates under the **Comprehensive Health Care Program (CHCP)** framework, administered by the **Michigan Department of Health and Human Services (MDHHS)**. The state uses a dual-delivery system:

- **MCOs (Managed Care Organizations)** — deliver physical health services
- **PIHPs (Primary Integrated Health Plans)** — deliver specialty behavioral health services

The state is organized into **10 Prosperity Regions**, each served by one or more health plans. Regulatory oversight for HMOs also involves the **Michigan Department of Insurance and Financial Services (DIFS)**, which establishes network adequacy standards applicable to all HMOs (including Medicaid).

---

## County/Tier System

Michigan uses **5 CMS county-based geographic designations** applied across all 83 counties:

| Tier | Definition |
|------|-----------|
| **Large Metro** | Pop ≥1M & density ≥1,000/sq mi; OR pop 500K-999K & density ≥1,500/sq mi; OR any pop & density ≥5,000/sq mi |
| **Metro** | Various pop/density combos (e.g., 1M+ pop & 10-999.9 density/sq mi) |
| **Micro** | Pop 50K-199K & density 10-99.9/sq mi; OR pop 10K-49K & density 50-999.9/sq mi |
| **Rural** | Pop 10K-49K & density 10-49.9/sq mi; OR pop <10K & density 50-999.9/sq mi |
| **CEAC** | Any pop size with density <10 people/sq mi |

**Access compliance thresholds:**
- Large Metro & Metro: ≥90% of beneficiaries within time/distance standards
- Micro, Rural, CEAC: ≥85% of beneficiaries within time/distance standards
- Both time AND distance must be met simultaneously

---

## Specialty Categories

### 1. Physical Health — MDHHS CHCP Standards (22 rows)

MDHHS publishes its own network adequacy standards for Medicaid MCOs with 5-tier time/distance by county designation. These cover:

**Primary Care (3):** Primary Care Adult, Primary Care Pediatric, Certified Nurse Midwife (DIFS)

**OB/GYN (1):** Gynecology, OB/GYN

**Specialists (5):** Cardiology, Neurology, Oncology (Medical/Surgical + Radiation), Orthopedics

**Ancillary (4):** Occupational Therapy, Physical Therapy, Speech Therapy, Pharmacy

**Behavioral Health — MCO (4):** Outpatient Clinical BH Adult, Outpatient Clinical BH Pediatric, Psychiatry Adult, Psychiatry Pediatric

**Dental (5):** General Dentist, Endodontics, Oral Surgery, Periodontics, Prosthodontics

**Facility (1):** Hospital

**Provider count requirement:** Minimum 2 providers in Large Metro and Metro counties for Primary Care, Hospital, and OB/GYN.

**Enrollee ratios:**
- Primary Care Adult: 1:500 (except Kalkaska 1:692, Missaukee 1:873, Schoolcraft 1:806; all other counties 1:650)
- Primary Care Pediatric: 1:500
- General Dentist: 1:650 (except Kalkaska 1:692, Missaukee 1:873, Schoolcraft 1:806)

### 2. DIFS Additional Provider Specialties (10 rows)

DIFS requires these specialties with a **uniform max 30-minute travel time** regardless of county designation:

Anesthesiology, Outpatient Dialysis, Durable Medical Equipment, Home Health, Home Infusion, Hospice, Laboratory, Certified Nurse Midwife, Optometry, Pathology

### 3. DIFS Full Specialty List with Time/Distance (32 rows)

DIFS Appendix 9.1 defines **51 individual provider specialty types** and **15 facility specialty types** (66 total), each with a unique DIFS code. The CSV includes the subset with explicit time/distance standards by county tier:

**Individual providers (26):** Allergy/Immunology (007), Cardiology (008), Cardiothoracic Surgery (035), Chiropractor (010), Dermatology (011), Emergency Medicine (037), Endocrinology (012), ENT/Otolaryngology (013), Gastroenterology (014), General Surgery (015), Infectious Diseases (017), Nephrology (018), Neurology (019), Neurosurgery (020), Oncology Medical/Surgical (021), Oncology Radiation (022), Ophthalmology (023), Orthopedic Surgery (025), PM&R (026), Plastic Surgery (027), Podiatry (028), Psychiatry (029), Pulmonology (030), Rheumatology (031), Urology (033), Vascular Surgery (034), Oral & Maxillofacial Surgery

**Facilities (15):** Acute Inpatient Hospitals (040), Cardiac Surgery Program (041), Cardiac Catheterization Services (042), Critical Care/ICU (043), Surgical Services ASC/Outpatient (045), Skilled Nursing Facilities (046), Diagnostic Radiology (047), Mammography (048), Inpatient Psychiatry (052), Outpatient Infusion/Chemotherapy (057), Substance Abuse Rehabilitation (072), Mental Health Residential Treatment (076), Urgent Care (080), Children's Substance Abuse Rehabilitation (P072), Children's Residential Treatment (P076)

### 4. Behavioral Health — PIHP Specialty Services (20 rows)

PIHPs deliver specialty behavioral health with distinct standards (separate from MCO behavioral health):

**Adult services (11):** Assertive Community Treatment (ACT), Crisis Residential Programs, Opioid Treatment Programs, Psychosocial Rehabilitation (Clubhouses), Inpatient Psychiatric, Community Living Supports, Skill Building, Partial Hospitalization Programs, Targeted Case Management, Pre-Admission Screen, Outpatient Clinical Mental Health

**Children/Youth services (9):** Crisis Residential Programs, Home-Based Services, Intensive Care Coordination with Wraparound (ICCW), Intensive Crisis Stabilization Services (Mobile Response), Respite Services, Parent Support Partners, Youth Peer Supports, Autism Diagnostic Evaluations, Autism Services

**Time/distance standards** are split into two tiers:
- Inpatient Psychiatric & Partial Hospitalization: Large Metro 30/15, Metro 70/45, Micro 100/75, Rural 90/75, CEAC 155/140
- All Other Services: Large Metro 20/10, Metro 45/30, Micro 70/53, Rural 75/60, CEAC 118/105

**Provider-to-enrollee ratios (active):**
- ACT: 1:30,000 (Team to Medicaid Enrollee)
- Psychosocial Rehabilitation: 1:45,000
- Opioid Treatment: 1:35,000
- Crisis Residential (Adult): 16 beds per 500,000 population
- Home-Based (Youth): 1:2,000
- ICCW (Youth): 1:5,000
- Crisis Residential (Youth): 8-12 beds per 500,000 population

**FY25 informational only** (no binding ratio): Community Living Supports, Skill Building, Targeted Case Management, Pre-Admission Screen, Outpatient Clinical Mental Health, ICSS, Respite, Parent Support Partners, Youth Peer Supports, Autism Services

---

## Timely Access Standards

### Physical Health (MDHHS)

| Type of Care | Standard |
|-------------|----------|
| Emergency Services | Immediately, 24/7 |
| Urgent Care | Within 48 hours |
| Routine Care | Within 30 business days |
| Non-Urgent Symptomatic Care | Within 7 business days |
| Specialty Care | Within 6 weeks |
| Acute Specialty Care | Within 5 business days |
| Behavioral Health | Emergency: 6 hours; Urgent: 48 hours; Routine: 10 business days |
| Prenatal (1st/2nd trimester) | Within 7 business days |
| Prenatal (3rd trimester) | Within 3 business days |
| Prenatal (high risk) | Within 3 business days |

### Dental

| Type of Care | Standard |
|-------------|----------|
| Emergency Dental | Immediately, 24/7 |
| Urgent Dental | Within 48 hours |
| Routine Dental | Within 21 business days |
| Preventive Dental | Within 6 weeks |
| Initial Dental Appointment | Within 8 weeks |

### PIHP Behavioral Health

| Service | Standard |
|---------|----------|
| Crisis Residential | Within 24 hours of authorization |
| Inpatient Psychiatric | Within 24 hours of authorization |
| Pre-Admission Screen | Disposition within 3 hours |
| ICSS Mobile Response | 1 hour urban, 2 hours rural |
| ACT | Within 7 business days of assessment |
| ICCW/Home-Based/Respite/PSP/YPS | Within 10 business days of disposition |
| Autism Services (97155) | Within 10 business days of 97151 assessment |

---

## Sources

### Primary Sources

| Source | Document | URL |
|--------|----------|-----|
| MDHHS | Updated Network Adequacy and Timely Access Standards for Medicaid Health Plans (FY25 CHCP) | `https://www.michigan.gov/mdhhs/-/media/Project/Websites/mdhhs/Assistance-Programs/Medicaid-BPHASA/Other-Prov-Specific-Page-Docs/Network-Adequacy-and-Timely-Access-Standards.pdf` |
| MDHHS | Network Adequacy Standards — Medicaid Specialty Behavioral Health Services (Jan 2026) | `https://www.michigan.gov/mdhhs/-/media/Project/Websites/mdhhs/Keeping-Michigan-Healthy/BH-DD/Reporting-Requirements/PIHP_Network_Adequacy_Standard_Procedural_Document.pdf` |
| DIFS | Michigan Network Adequacy Guidance (Updated 3.26) | `https://www.michigan.gov/difs/-/media/Project/Websites/difs/Form/Insurance/HMO/Network_Adequacy_Guidance.pdf` |

### Supplementary Sources

| Source | Document | Notes |
|--------|----------|-------|
| BCBSM | Taxonomy Code Map | Blue Cross Blue Shield of Michigan taxonomy crosswalk — maps BCBSM provider specialty names to NUCC taxonomy codes |
| MDHHS | FY26 CHCP Contract | Contract document confirming CHCP framework |
| MDHHS | Provider Enrollment Typical Matrix | Provider enrollment type reference |

---

## Crosswalk Status

**DIFS → NUCC Taxonomy crosswalk:** 66 rows mapping all 51 individual provider specialty types and 15 facility specialty types to NUCC taxonomy codes.

- 51 rows: high-confidence NUCC taxonomy matches (individual providers)
- 15 rows: no direct NUCC taxonomy equivalent (facility types)
- Source: BCBSM Taxonomy Code Map + NUCC taxonomy v25.1
- File: `data/states/mi/mi_taxonomy_crosswalk.csv`

---

## Data Summary

| Metric | Value |
|--------|-------|
| Total specialty rows | 94 |
| MDHHS CHCP rows | 22 |
| DIFS rows | 52 |
| PIHP BH rows | 20 |
| Crosswalk rows | 66 |
| Counties | 83 (5 CMS designations) |
| Prosperity Regions | 10 |
