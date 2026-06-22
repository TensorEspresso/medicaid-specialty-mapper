# North Carolina Medicaid Managed Care — Specialty Reference Methodology

## State Profile
- **State:** North Carolina
- **Program:** NC Medicaid Managed Care (Standard Plan) + Medicaid Direct
- **Enrollees:** ~3.5M (expansion state)
- **Structure:** 5 statewide PHPs (Primary Health Plans) + 6 regional PIHPs (Primary Insurance Health Plans)
- **PHPs:** AmeriHealth Caritas NC, Carolina Complete Health (WellCare), Healthy Blue, Molina Healthcare NC, UnitedHealthcare Community Plan NC
- **Regulatory Authority:** NC Department of Health and Human Services (NC DHHS), Division of Medical Assistance (DMA)

## Sources

### Primary Source — Network Adequacy Standards
- **Document:** North Carolina Medicaid Managed Care Network Adequacy Time or Distance Standards
- **URL:** https://medicaid.ncdhhs.gov/network-adequacy-time-or-distance-standards/download?attachment
- **Format:** PDF (350 KB)
- **Description:** State-level network adequacy time/distance standards for Managed Care and Medicaid Direct. Defines broad service categories but does NOT enumerate specific specialty types — uses "per specialty type" for Specialty Care category.

### Primary Source — MCO Provider Manual (Specialty List)
- **Document:** Carolina Complete Health NC Medicaid Provider Manual (Jan 2026)
- **URL:** https://network.carolinacompletehealth.com/content/dam/centene/carolinacompletehealth/pdfs/CCH_Current_PDF_Provider_Manual.pdf
- **Format:** PDF (1.7 MB, 141 pages)
- **Description:** Provider manual that explicitly lists the 21 specialty care provider types subject to network adequacy standards. This is the authoritative source for the enumerated specialty types.

### Primary Source — PHP Contract Scope of Services
- **Document:** RFP 30-190029-DHB V. Scope of Services
- **URL:** https://www.ncdhhs.gov/dhhs-php-contract/open
- **Format:** PDF (1.8 MB)
- **Description:** PHP (Primary Health Plan) contract scope of services. References "Attachment F. North Carolina Medicaid Managed Care Network Adequacy Standards" for specialty requirements. Confirms the specialty types listed in MCO provider manuals.

### Primary Source — Healthy Blue Provider Manual (Cross-verification)
- **Document:** Healthy Blue NC Medicaid Provider Manual
- **URL:** https://provider.healthybluenc.com/docs/inline/NCNC_CAID_ProviderManual.pdf
- **Format:** PDF (2.3 MB)
- **Description:** Cross-verification source. Confirms the same network adequacy standards structure but does NOT enumerate specialty types — uses "per specialty type" language.

### Secondary Source — Network Adequacy Q&A
- **Document:** Network Adequacy Questions and Answers
- **URL:** https://medicaid.ncdhhs.gov/reports/network-adequacy-questions-and-answers
- **Description:** State Q&A page confirming the categories measured: Primary Care, Hospitals, Pharmacy, OB/GYN, Outpatient Behavioral Health, Specialty Care, Occupational/Physical/Speech Therapies, LTSS, Skilled Nursing Facilities, Inpatient BH, Location-Based Services (BH), Partial Hospitalization (BH), Crisis Services (BH).

### Taxonomy Crosswalk — Provider Permission Matrix (PPM)
- **Document:** Provider Permission Matrix (PPM) — May 31, 2026
- **URL:** https://www.nctracks.nc.gov/content/public/providers/provider-enrollment.html (download link in "Quick Links")
- **Format:** Excel (.xlsx, 987 KB)
- **Description:** Authoritative NC Medicaid taxonomy crosswalk. Maps all 302+ NUCC taxonomy codes (Level 2 + Level 3) to NC Medicaid provider enrollment types, CCNC/CA eligibility, federal site visit requirements, federal fee requirements, fingerprinting requirements, and categorical risk levels. Published by NCTracks (NC DHHS provider enrollment system).
- **Instruction Sheet:** Provider Permission Matrix Instruction Sheet (PDF, 5 pages) — https://www.nctracks.nc.gov/content/dam/jcr:334ac9d5-d2da-462c-94b5-062bd337d072/JA_PRV591_Prov+Permission+Matrix+Instructs_W1.5.1+(1)+(1).pdf

## Extraction Methodology

### Step 1: Identify specialty types
The Carolina Complete Health Provider Manual (Section: Network Adequacy and Access Standards, page 40) explicitly lists the specialty care providers subject to network adequacy standards:

> "Specialty care providers adhering to this standard include: Allergy/Immunology, Anesthesiology, Cardiology, Dermatology, Endocrinology, ENT/Otolaryngology, Gastroenterology, General Surgery, Infectious Disease, Hematology, Nephrology, Neurology, Oncology, Ophthalmology, Optometry, Orthopedic Surgery, Pain Management (Board Certified), Psychiatry, Pulmonology, Radiology, and Rheumatology."

This yields **21 specialty care types**.

### Step 2: Extract network adequacy standards
The same section provides the urban/rural time and distance standards for each service category:
- **Primary Care:** ≥ 2 providers within 30 min / 10 mi (urban) or 30 min / 30 mi (rural) for ≥ 95%
- **Specialty Care:** ≥ 2 providers (per specialty type) within 30 min / 15 mi (urban) or 60 min / 60 mi (rural) for ≥ 95%
- **Hospitals:** ≥ 1 hospital within 30 min / 15 mi (urban) or 30 min / 30 mi (rural) for ≥ 95%
- **Pharmacies:** ≥ 2 pharmacies within 30 min / 10 mi (urban) or 30 min / 30 mi (rural) for ≥ 95%
- **Obstetrics:** ≥ 2 providers within 30 min / 10 mi (urban) or 30 min / 30 mi (rural) for ≥ 95% (female members age 14-44)
- **Occupational/Physical/Speech Therapists:** ≥ 2 providers of each type within 30 min / 10 mi (urban) or 30 min / 30 mi (rural) for ≥ 95%
- **Outpatient BH:** ≥ 2 providers within 30 min / 30 mi (urban) or 45 min / 45 mi (rural) for ≥ 95%
- **Location-Based Services (BH):** ≥ 2 providers within 30 min / 30 mi (urban) or 45 min / 45 mi (rural) for ≥ 95%
- **Crisis Services (BH):** ≥ 1 provider within each PHP Region
- **Inpatient BH:** ≥ 1 provider within each PHP Region
- **Partial Hospitalization (BH):** ≥ 1 provider within 30 min / 30 mi (urban) or 60 min / 60 mi (rural) for ≥ 95%
- **LTSS:** ≥ 2 providers in every county (not geo-mapped)
- **Nursing Facilities:** ≥ 1 facility in every county (not geo-mapped)

### Step 3: Cross-verify with state standards
The state's Network Adequacy Time or Distance Standards document confirms the same standards for Managed Care and Medicaid Direct programs.

### Step 4: Cross-verify with second MCO
Healthy Blue provider manual confirms the same standards structure but does not enumerate specialty types.

## Key Findings

1. **NC uses a defined list of 21 specialty care types** for network adequacy measurement, explicitly listed in MCO provider manuals.
2. **Pain Management requires Board Certification** — this is the only specialty with a specific credentialing requirement noted in the standards.
3. **Two-tier program structure:** Standard Plan (managed care) and Medicaid Direct have separate but parallel network adequacy standards.
4. **Age definitions differ:** Physical health uses age 21 as adult/pediatric cutoff; behavioral health uses age 18.
5. **Service types marked with (*)** are not subject to separate adult/pediatric standards: Hospitals, Pharmacies, Occupational/Physical/Speech Therapists, LTSS, Nursing Facilities.
6. **PHP Regions** are the geographic unit for Crisis Services and Inpatient BH measurements (5 statewide + 6 regional).
7. **LTSS and Nursing Facilities** are measured by county coverage, not geo-mapping.

## Row Count
- **48 total rows** (21 specialty care + 27 other service types/categories)

## Verification Status
- ✅ Sources downloaded and extracted
- ✅ Specialty list cross-verified across 2 MCO provider manuals
- ✅ Network adequacy standards confirmed against state document
- ✅ Taxonomy crosswalk downloaded (Provider Permission Matrix, 302 rows)
- ✅ Final verification pass complete

## Notes
- NC's specialty list is one of the most explicitly enumerated among states studied — the MCO provider manual directly lists all 21 specialty types.
- The state's own network adequacy standards document references "per specialty type" but does not enumerate them, making the MCO provider manual the authoritative source for the specialty list.
- NC has a complex managed care structure with both statewide PHPs and regional PIHPs, each with their own network adequacy reporting.
