#!/usr/bin/env python3
"""Build tx_medicaid_specialties.csv from extracted HHSC data."""
import csv
import os

# Data extracted from:
# 1. UMCM Chapter 5.28.1 - Access to Network Providers Performance Standards and Specifications (xlsx)
# 2. Network Adequacy Report Dec 2024 - Appendix A (Tables A-1, A-2, A-3)
# Source: https://www.hhs.texas.gov/services/health/medicaid-chip/managed-care-contract-management/texas-medicaid-chip-uniform-managed-care-manual

specialties = [
    # Primary Care / General Services
    {"specialty": "Acute Care Hospital", "category": "General Services", "programs": "STAR, STAR Health, STAR+PLUS, STAR Kids, CHIP, S+P MMP", "travel_time_metro": 45, "travel_time_micro": 45, "travel_time_rural": 45, "provider_count_standard": "Choice of 2", "performance_threshold": "90%", "implementation_date": "2017-03-01"},
    {"specialty": "Nursing Facility", "category": "General Services", "programs": "STAR+PLUS, S+P MMP", "travel_time_metro": "N/A", "travel_time_micro": "N/A", "travel_time_rural": "N/A", "provider_count_standard": "Choice of 2", "performance_threshold": "90%", "implementation_date": "2017-03-01"},
    {"specialty": "Obstetrician/Gynecologist (OB/GYN)", "category": "Primary Care", "programs": "STAR, STAR Health, STAR+PLUS, STAR Kids, CHIP, S+P MMP", "travel_time_metro": 45, "travel_time_micro": 80, "travel_time_rural": 90, "provider_count_standard": "Choice of 2", "performance_threshold": "90%", "implementation_date": "2017-03-01"},
    {"specialty": "Prenatal", "category": "Primary Care", "programs": "STAR, STAR Health, STAR+PLUS, STAR Kids, CHIP, S+P MMP", "travel_time_metro": 15, "travel_time_micro": 30, "travel_time_rural": 40, "provider_count_standard": "Choice of 2", "performance_threshold": "90%", "implementation_date": "2017-03-01"},
    {"specialty": "Primary Care Provider (PCP)", "category": "Primary Care", "programs": "STAR, STAR Health, STAR+PLUS, STAR Kids, CHIP, S+P MMP", "travel_time_metro": 15, "travel_time_micro": 30, "travel_time_rural": 40, "provider_count_standard": "2 with Open Panel", "performance_threshold": "90%", "implementation_date": "2017-03-01"},
    {"specialty": "Therapies (OT/PT/ST)", "category": "Primary Care", "programs": "STAR, STAR Health, STAR+PLUS, STAR Kids, CHIP, S+P MMP", "travel_time_metro": 45, "travel_time_micro": 80, "travel_time_rural": 75, "provider_count_standard": "Choice of 2", "performance_threshold": "90%", "implementation_date": "2017-03-01"},

    # Specialty Care Providers
    {"specialty": "Audiologist", "category": "Specialty Care", "programs": "STAR, STAR Health, STAR+PLUS, STAR Kids, CHIP, S+P MMP", "travel_time_metro": 45, "travel_time_micro": 80, "travel_time_rural": 90, "provider_count_standard": "Choice of 2", "performance_threshold": "90%", "implementation_date": "2018-09-01"},
    {"specialty": "Cardiovascular Disease", "category": "Specialty Care", "programs": "STAR, STAR Health, STAR+PLUS, STAR Kids, CHIP, S+P MMP", "travel_time_metro": 30, "travel_time_micro": 50, "travel_time_rural": 75, "provider_count_standard": "Choice of 2", "performance_threshold": "90%", "implementation_date": "2017-03-01"},
    {"specialty": "Otolaryngologist (ENT)", "category": "Specialty Care", "programs": "STAR, STAR Health, STAR+PLUS, STAR Kids, CHIP, S+P MMP", "travel_time_metro": 45, "travel_time_micro": 80, "travel_time_rural": 90, "provider_count_standard": "Choice of 2", "performance_threshold": "90%", "implementation_date": "2017-03-01"},
    {"specialty": "General Surgeon", "category": "Specialty Care", "programs": "STAR, STAR Health, STAR+PLUS, STAR Kids, CHIP, S+P MMP", "travel_time_metro": 30, "travel_time_micro": 50, "travel_time_rural": 75, "provider_count_standard": "Choice of 2", "performance_threshold": "90%", "implementation_date": "2017-03-01"},
    {"specialty": "Ophthalmologist", "category": "Specialty Care", "programs": "STAR, STAR Health, STAR+PLUS, STAR Kids, CHIP, S+P MMP", "travel_time_metro": 30, "travel_time_micro": 50, "travel_time_rural": 75, "provider_count_standard": "Choice of 2", "performance_threshold": "90%", "implementation_date": "2017-03-01"},
    {"specialty": "Orthopedist", "category": "Specialty Care", "programs": "STAR, STAR Health, STAR+PLUS, STAR Kids, CHIP, S+P MMP", "travel_time_metro": 30, "travel_time_micro": 50, "travel_time_rural": 75, "provider_count_standard": "Choice of 2", "performance_threshold": "90%", "implementation_date": "2017-03-01"},
    {"specialty": "Pediatric Sub-specialty", "category": "Specialty Care", "programs": "STAR, STAR Health, STAR+PLUS, STAR Kids, CHIP", "travel_time_metro": 30, "travel_time_micro": 50, "travel_time_rural": 75, "provider_count_standard": "Choice of 2", "performance_threshold": "90%", "implementation_date": "2017-03-01"},
    {"specialty": "Psychiatrist", "category": "Specialty Care", "programs": "STAR, STAR Health, STAR+PLUS, STAR Kids, CHIP, S+P MMP", "travel_time_metro": 45, "travel_time_micro": 60, "travel_time_rural": 75, "provider_count_standard": "Choice of 2", "performance_threshold": "90%", "implementation_date": "2017-03-01"},
    {"specialty": "Urologist", "category": "Specialty Care", "programs": "STAR, STAR Health, STAR+PLUS, STAR Kids, CHIP, S+P MMP", "travel_time_metro": 45, "travel_time_micro": 60, "travel_time_rural": 75, "provider_count_standard": "Choice of 2", "performance_threshold": "90%", "implementation_date": "2017-03-01"},

    # Behavioral Health Providers
    {"specialty": "Outpatient Mental Health Services", "category": "Behavioral Health", "programs": "STAR, STAR Health, STAR+PLUS, STAR Kids, CHIP, S+P MMP", "travel_time_metro": 45, "travel_time_micro": 45, "travel_time_rural": 90, "provider_count_standard": "Choice of 2", "performance_threshold": "90%", "implementation_date": "2017-03-01"},
    {"specialty": "Mental Health Targeted Case Management (MHTCM) / Mental Health Rehabilitative Services (MHR)", "category": "Behavioral Health", "programs": "STAR, STAR Health, STAR+PLUS, STAR Kids, CHIP, S+P MMP", "travel_time_metro": 45, "travel_time_micro": 45, "travel_time_rural": 90, "provider_count_standard": "Choice of 2", "performance_threshold": "90%", "implementation_date": "2018-09-01"},
    {"specialty": "Substance Use Disorder (SUD) - Outpatient - Chemical Dependency Treatment Facilities", "category": "Behavioral Health", "programs": "STAR, STAR Health, STAR+PLUS, STAR Kids, CHIP, S+P MMP", "travel_time_metro": 45, "travel_time_micro": 45, "travel_time_rural": 90, "provider_count_standard": "Choice of 2", "performance_threshold": "90%", "implementation_date": "2020-09-01"},
    {"specialty": "Substance Use Disorder (SUD) - Outpatient - Opioid Treatment Programs", "category": "Behavioral Health", "programs": "STAR, STAR Health, STAR+PLUS, STAR Kids, CHIP, S+P MMP", "travel_time_metro": 45, "travel_time_micro": 45, "travel_time_rural": 90, "provider_count_standard": "Choice of 2", "performance_threshold": "90%", "implementation_date": "2020-09-01"},

    # Dental Providers
    {"specialty": "Main Dentist", "category": "Dental", "programs": "CMDS, CHIP Dental, STAR Health", "travel_time_metro": 45, "travel_time_micro": 45, "travel_time_rural": 90, "provider_count_standard": "2 with Open Panel", "performance_threshold": "95%", "implementation_date": "2017-03-01"},
    {"specialty": "Endodontist", "category": "Dental", "programs": "CMDS, CHIP Dental, STAR Health", "travel_time_metro": 90, "travel_time_micro": 90, "travel_time_rural": 90, "provider_count_standard": "Choice of 2", "performance_threshold": "90%", "implementation_date": "2017-03-01"},
    {"specialty": "Orthodontist", "category": "Dental", "programs": "CMDS, CHIP Dental, STAR Health", "travel_time_metro": 90, "travel_time_micro": 90, "travel_time_rural": 90, "provider_count_standard": "Choice of 2", "performance_threshold": "90%", "implementation_date": "2017-03-01"},
    {"specialty": "Pediatric Dentist", "category": "Dental", "programs": "CMDS, CHIP Dental, STAR Health", "travel_time_metro": 45, "travel_time_micro": 45, "travel_time_rural": 90, "provider_count_standard": "Choice of 2", "performance_threshold": "90%", "implementation_date": "2017-03-01"},
    {"specialty": "Oral Surgeon", "category": "Dental", "programs": "CMDS, CHIP Dental, STAR Health", "travel_time_metro": 90, "travel_time_micro": 90, "travel_time_rural": 90, "provider_count_standard": "Choice of 2", "performance_threshold": "90%", "implementation_date": "2017-03-01"},

    # Long Term Services & Supports
    {"specialty": "Assisted Living Facility", "category": "LTSS", "programs": "STAR+PLUS, S+P MMP", "travel_time_metro": 45, "travel_time_micro": 80, "travel_time_rural": 75, "provider_count_standard": "Choice of 2", "performance_threshold": "90%", "implementation_date": "2018-09-01"},
    {"specialty": "Attendant Care", "category": "LTSS", "programs": "STAR+PLUS, STAR Kids, STAR Health, S+P MMP", "travel_time_metro": "N/A", "travel_time_micro": "N/A", "travel_time_rural": "N/A", "provider_count_standard": "Choice of 2 in each county", "performance_threshold": "N/A", "implementation_date": "2018-09-01"},
    {"specialty": "CFC Habilitation Services", "category": "LTSS", "programs": "STAR+PLUS, STAR Kids, STAR Health, S+P MMP", "travel_time_metro": "N/A", "travel_time_micro": "N/A", "travel_time_rural": "N/A", "provider_count_standard": "Choice of 2 in each county", "performance_threshold": "N/A", "implementation_date": "2018-09-01"},
    {"specialty": "Consumer Directed Services (CDS)", "category": "LTSS", "programs": "STAR+PLUS, STAR Kids, STAR Health, S+P MMP", "travel_time_metro": "N/A", "travel_time_micro": "N/A", "travel_time_rural": "N/A", "provider_count_standard": "Choice of 2 in each county", "performance_threshold": "N/A", "implementation_date": "2018-09-01"},
    {"specialty": "In-Home Therapies (OT/PT/ST)", "category": "LTSS", "programs": "STAR+PLUS, STAR Kids, STAR Health, S+P MMP", "travel_time_metro": "N/A", "travel_time_micro": "N/A", "travel_time_rural": "N/A", "provider_count_standard": "Choice of 2 in each county", "performance_threshold": "N/A", "implementation_date": "2018-09-01"},
    {"specialty": "In-Home Skilled Nursing", "category": "LTSS", "programs": "STAR+PLUS, S+P MMP", "travel_time_metro": "N/A", "travel_time_micro": "N/A", "travel_time_rural": "N/A", "provider_count_standard": "Choice of 2 in each county", "performance_threshold": "N/A", "implementation_date": "2018-09-01"},
    {"specialty": "Private Duty Nursing", "category": "LTSS", "programs": "STAR Kids, STAR Health", "travel_time_metro": "N/A", "travel_time_micro": "N/A", "travel_time_rural": "N/A", "provider_count_standard": "Choice of 2 in each county", "performance_threshold": "N/A", "implementation_date": "2018-09-01"},

    # Pharmacy
    {"specialty": "Pharmacy (MRSA)", "category": "Pharmacy", "programs": "STAR MRSA, STAR Kids MRSA, STAR+PLUS MRSA, CHIP", "travel_time_metro": 5, "travel_time_micro": 10, "travel_time_rural": 25, "provider_count_standard": "One", "performance_threshold": "75% Metro / 55% Micro / 90% Rural", "implementation_date": "2018-09-01"},
    {"specialty": "Pharmacy (All Other Programs)", "category": "Pharmacy", "programs": "STAR, STAR Health, STAR+PLUS, STAR Kids, S+P MMP", "travel_time_metro": 5, "travel_time_micro": 10, "travel_time_rural": 25, "provider_count_standard": "One", "performance_threshold": "80% Metro / 75% Micro / 90% Rural", "implementation_date": "2018-09-01"},
    {"specialty": "24 Hour Pharmacy", "category": "Pharmacy", "programs": "STAR, STAR Health, STAR+PLUS, STAR Kids, CHIP, S+P MMP", "travel_time_metro": 90, "travel_time_micro": 90, "travel_time_rural": 90, "provider_count_standard": "One", "performance_threshold": "90%", "implementation_date": "2018-09-01"},
    {"specialty": "Mail Order Pharmacy", "category": "Pharmacy", "programs": "STAR, STAR Health, STAR+PLUS, STAR Kids, CHIP, S+P MMP", "travel_time_metro": "N/A", "travel_time_micro": "N/A", "travel_time_rural": "N/A", "provider_count_standard": "One", "performance_threshold": "N/A", "implementation_date": "2018-09-01"},

    # All Other
    {"specialty": "All Other Covered Services", "category": "All Other", "programs": "STAR, STAR Health, STAR+PLUS, STAR Kids, CHIP, CHIP Dental, CMDS, S+P MMP", "travel_time_metro": "N/A", "travel_time_micro": "N/A", "travel_time_rural": "N/A", "provider_count_standard": "One", "performance_threshold": "90%", "implementation_date": "2017-03-01"},
]

# Write CSV
fieldnames = ["specialty", "category", "programs", "travel_time_metro_min", "travel_time_micro_min", "travel_time_rural_min", "provider_count_standard", "performance_threshold", "implementation_date"]

output_path = os.path.join(os.path.dirname(__file__), '..', 'tx_medicaid_specialties.csv')
with open(output_path, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for s in specialties:
        writer.writerow({
            "specialty": s["specialty"],
            "category": s["category"],
            "programs": s["programs"],
            "travel_time_metro_min": s["travel_time_metro"],
            "travel_time_micro_min": s["travel_time_micro"],
            "travel_time_rural_min": s["travel_time_rural"],
            "provider_count_standard": s["provider_count_standard"],
            "performance_threshold": s["performance_threshold"],
            "implementation_date": s["implementation_date"],
        })

print(f"Wrote {len(specialties)} specialties to {output_path}")

from collections import Counter
cats = Counter(s["category"] for s in specialties)
for cat, count in sorted(cats.items()):
    print(f"  {cat}: {count}")
