# Arizona (AZ) Medicaid Specialty Reference

## Source Documents

| Document | File | Description |
|----------|------|-------------|
| ACOM Policy 436 | `ahcccs_network_standards.pdf` | Network Standards - primary source for time/distance and category definitions |
| AHCCCS Provider Type List | `doc_e3_provider_types.pdf` | Reference for provider type codes (e.g., 08 = MD, 19 = NP) |
| PMMIS Reference Subsystem | `codes_values_2026.pdf` | Authoritative source for system codes |

## Verification Status

**9 specialty rows verified via semantic mapping.**

- **All rows** verified by matching AHCCCS categories from ACOM Policy 436 against the NUCC v25.1 taxonomy.
- **Time/distance standards** confirmed for Urban and Rural designations.

## County Size Categories

| Category | Population Density | Counties |
|----------|-------------------|----------|
| Urban | High Density | Maricopa, Pima |
| Rural | Low Density | All other Arizona counties |

## Time & Distance Standards

### By Provider Type

| Provider Type | Urban Standard | Rural Standard |
|---------------|----------------|----------------|
| Primary Care (Adult/Pediatric) | 15 minutes or 10 miles | 40 minutes or 30 miles |
| Hospitals | 60 minutes or 45 miles | 110 minutes or 100 miles |
| Pharmacy | 15 minutes or 10 miles | 40 minutes or 30 miles |

### Specialist Standards by County Size

| County Size | Time or Distance |
|-------------|------------------|
| Urban | 30 minutes or 20 miles |
| Rural | 60 minutes or 40 miles |

## Timely Access Standards

| Provider Type | Standard |
|---------------|----------|
| Primary Care | Within 15 business days of request |
| Specialty Care | Within 30 business days of request |

## AHCCCS Core Specialists

1. PCP Adult
2. PCP Pediatric
3. OB/GYN
4. Adult Cardiology
5. Pediatric Cardiology
6. Hospital
7. Nursing Facility
8. Pharmacy
9. BH Outpatient

## Key Notes

- **Provider Type vs Specialty**: AZ uses a dual-coding system: Provider Type Codes (license/role) and Specialty Codes (clinical focus).
- **PCP Composition**: PCP Adult includes Allopathic/Osteopathic Physicians, Nurse Practitioners, Certified Nurse-Midwives, and Physician Assistants.
- **Cardiology Split**: Cardiology is split into Adult and Pediatric, though they may share internal specialty codes.

## Data Gaps

1. **Official Crosswalk**: No official AHCCCS-to-NUCC mapping file is published; the current crosswalk is a best-effort semantic mapping of AHCCCS policy definitions to NUCC v25.1 taxonomy codes. All `match_confidence` values in `az_taxonomy_crosswalk.csv` are marked `best-effort`. AHCCCS uses internal specialty codes (e.g., 062, 150, 151) with no NUCC codes in source documents.
2. **Granular Specialist Standards**: Detailed time/distance for every single sub-specialty is not explicitly tabulated in ACOM 436 beyond the general "Specialist" tier.
