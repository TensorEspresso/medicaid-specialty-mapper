#!/usr/bin/env python3
"""
Build Michigan Medicaid specialty data:
1. Create taxonomy crosswalk from DIFS codes + BCBSM mapping + NUCC taxonomy
2. Create mi_medicaid_specialties.csv
"""

import csv
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
SOURCES = os.path.join(BASE, "sources")
NUCC_CSV = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(BASE))), "data", "nucc", "nucc_taxonomy_251.csv")

# ============================================================
# PHASE 2: Build taxonomy crosswalk
# ============================================================

# DIFS Individual Provider Specialty Types (51 codes from DIFS Appendix 9.1.1)
DIFS_INDIVIDUAL = {
    "001": ("General Practice", "Primary Care"),
    "002": ("Family Medicine", "Primary Care"),
    "003": ("Internal Medicine", "Primary Care"),
    "004": ("Geriatrics", "Primary Care"),
    "005": ("Primary Care - PA", "Primary Care"),
    "006": ("Primary Care - Advanced Reg NP", "Primary Care"),
    "007": ("Allergy and Immunology", "Specialist"),
    "008": ("Cardiology", "Specialist"),
    "010": ("Chiropractor", "Ancillary"),
    "011": ("Dermatology", "Specialist"),
    "012": ("Endocrinology", "Specialist"),
    "013": ("ENT/Otolaryngology", "Specialist"),
    "014": ("Gastroenterology", "Specialist"),
    "015": ("General Surgery", "Specialist"),
    "016": ("Gynecology (OB/GYN)", "OB/GYN"),
    "017": ("Infectious Diseases", "Specialist"),
    "018": ("Nephrology", "Specialist"),
    "019": ("Neurology", "Specialist"),
    "020": ("Neurosurgery", "Specialist"),
    "021": ("Oncology - Medical & Surgical", "Specialist"),
    "022": ("Oncology - Radiation", "Specialist"),
    "023": ("Ophthalmology", "Specialist"),
    "025": ("Orthopedic Surgery", "Specialist"),
    "026": ("Physical Medicine & Rehabilitation", "Specialist"),
    "027": ("Plastic Surgery", "Specialist"),
    "028": ("Podiatry", "Specialist"),
    "029": ("Psychiatry", "Behavioral Health"),
    "030": ("Pulmonology", "Specialist"),
    "031": ("Rheumatology", "Specialist"),
    "033": ("Urology", "Specialist"),
    "034": ("Vascular Surgery", "Specialist"),
    "035": ("Cardiothoracic Surgery", "Specialist"),
    "037": ("Emergency Medicine", "Specialist"),
    "049": ("Physical Therapy", "Ancillary"),
    "050": ("Occupational Therapy", "Ancillary"),
    "051": ("Speech Therapy", "Ancillary"),
    "101": ("Primary Care - Pediatric", "Primary Care"),
    "102": ("Social Worker", "Behavioral Health"),
    "103": ("Psychologist", "Behavioral Health"),
    "105": ("Marriage & Family Therapist", "Behavioral Health"),
    "106": ("Addiction (SUD) Counselor", "Behavioral Health"),
    "107": ("Counselor (Mental Health & Professional)", "Behavioral Health"),
    "108": ("Behavioral Health - Advanced Practice RN", "Behavioral Health"),
    "201": ("Dental - General", "Dental"),
    "202": ("Dental - Orthodontist", "Dental"),
    "203": ("Dental - Periodontist", "Dental"),
    "204": ("Dental - Endodontist", "Dental"),
    "206": ("Dental - Prosthodontist", "Dental"),
    "P201": ("Pediatric Dental", "Dental"),
    "800": ("Addiction Medicine Physician", "Behavioral Health"),
    "801": ("Behavioral Analyst", "Behavioral Health"),
}

# DIFS Facility Specialty Types (15 codes from DIFS Appendix 9.1.2)
DIFS_FACILITY = {
    "040": ("Acute Inpatient Hospitals", "Facility"),
    "041": ("Cardiac Surgery Program", "Facility"),
    "042": ("Cardiac Catheterization Services", "Facility"),
    "043": ("Critical Care Services - ICU", "Facility"),
    "045": ("Surgical Services (ASC/Outpatient)", "Facility"),
    "046": ("Skilled Nursing Facilities", "Facility"),
    "047": ("Diagnostic Radiology", "Facility"),
    "048": ("Mammography", "Facility"),
    "052": ("Inpatient Psychiatry", "Facility"),
    "057": ("Outpatient Infusion/Chemotherapy", "Facility"),
    "072": ("Substance Abuse Rehabilitation Facility", "Facility"),
    "076": ("Mental Health Residential Treatment Facility", "Facility"),
    "080": ("Urgent Care", "Facility"),
    "P072": ("Children's Substance Abuse Rehabilitation Facility", "Facility"),
    "P076": ("Children's Residential Treatment Facility", "Facility"),
}

# DIFS Additional Provider Specialties (Section 4.1)
DIFS_ADDITIONAL = {
    "Anesthesiology": "Specialist",
    "Outpatient Dialysis": "Facility",
    "DME": "Ancillary",
    "Home Health": "Facility",
    "Home Infusion": "Facility",
    "Hospice": "Facility",
    "Laboratory": "Facility",
    "Midwife": "Primary Care",
    "Optometry": "Specialist",
    "Pathology": "Specialist",
    "Oral & Maxillofacial Surgery": "Specialist",
    "Ambulance": "Facility",
    "Pharmacy": "Ancillary",
}

# BCBSM mapping (extracted from bcbsm_taxonomy.txt)
# Provider Specialty -> NUCC Taxonomy Code
BCBSM_MAP = {
    "Addiction Medicine": "207RA0401X",
    "Allergy and Immunology": "207K00000X",
    "Anesthesiology": "207L00000X",
    "Audiologist": "231H00000X",
    "Cardiovascular Disease": "207RC0000X",
    "Certified Registered Nurse Anesthetist": "367500000X",
    "Chiropractor": "111N00000X",
    "Clinical Psychologist": "103TC0700X",
    "Dermatology": "207N00000X",
    "Dentist": "122300000X",
    "Dentist - Endodontist": "1223D0002X",
    "Dentist - Orthodontist": "1223D0003X",
    "Dentist - Periodontist": "1223D0004X",
    "Dentist - Prosthodontist": "1223P0700X",
    "Dentist - Pediatric": "1223D0001X",
    "Dentist - Oral Surgeon": "1223D0005X",
    "Dentist - General": "122300000X",
    "Dentist - Public Health": "1223D0001X",
    "Dental Therapist": "125J00000X",
    "Emergency Medicine": "207P00000X",
    "Endocrinology": "207RD0001X",
    "ENT/Otolaryngology": "207600000X",
    "Family Medicine": "207Q00000X",
    "General Practice": "208D00000X",
    "Gastroenterology": "207RG0001X",
    "General Surgery": "208600000X",
    "Geriatric Medicine": "207RG1001X",
    "Gynecology/OB-GYN": "2085A0100X",
    "Infectious Disease": "207RI0001X",
    "Internal Medicine": "207R00000X",
    "Nephrology": "207RN0001X",
    "Neurology": "207X00000X",
    "Neurosurgery": "207T00000X",
    "Oncology - Medical": "207RM0001X",
    "Oncology - Radiation": "2085R0001X",
    "Ophthalmology": "207W00000X",
    "Orthopedic Surgery": "207X00000X",
    "Neurology": "2084N0400X",
    "Physical Medicine and Rehabilitation": "208100000X",
    "Physical Therapist": "225100000X",
    "Occupational Therapist": "225300000X",
    "Speech Therapist": "235Z00000X",
    "Plastic Surgery": "208200000X",
    "Podiatry": "213E00000X",
    "Preventive Medicine": "2083P0500X",
    "Psychiatry and Neurology": "2084P0800X",
    "Psychiatrist": "2084P0800X",
    "Pulmonary Disease": "207RP1001X",
    "Radiology": "2085R0202X",
    "Radiology - Diagnostic": "2085R0202X",
    "Rheumatology": "207RR0001X",
    "Social Worker": "104100000X",
    "Thoracic Surgery": "208G00000X",
    "Urology": "208800000X",
    "Vascular Surgery": "208900000X",
    "Cardiothoracic Surgery": "208G00000X",
    "Physician Assistant": "363A00000X",
    "Nurse Practitioner": "363L00000X",
    "Certified Nurse Midwife": "363C00000X",
    "Clinical Nurse Specialist": "364S00000X",
    "Marriage and Family Therapist": "101Y00001X",
    "Licensed Professional Counselor": "101YP0300X",
    "Certified Social Worker": "104100000X",
    "Dietitian": "154W00000X",
    "Optometrist": "151S00000X",
    "Pharmacist": "333600000X",
    "Home Health Agency": "261H00000X",
    "Hospice": "261H00000X",
    "Ambulance": "341600000X",
    "Laboratory": "831100000X",
    "DME Supplier": "332B00000X",
}

# Load NUCC taxonomy
nucc_codes = {}
with open(NUCC_CSV, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        code = row.get("Code", "").strip()
        if code:
            nucc_codes[code] = row

# Build crosswalk
crosswalk_rows = []

# Map DIFS individual codes to NUCC
difs_to_nucc = {
    "001": "208D00000X",  # General Practice
    "002": "207Q00000X",  # Family Medicine
    "003": "207R00000X",  # Internal Medicine
    "004": "207RG1001X",  # Geriatrics
    "005": "363A00000X",  # Primary Care - PA
    "006": "363L00000X",  # Primary Care - Advanced Reg NP
    "007": "207K00000X",  # Allergy and Immunology
    "008": "207RC0000X",  # Cardiology
    "010": "111N00000X",  # Chiropractor
    "011": "207N00000X",  # Dermatology
    "012": "207RD0001X",  # Endocrinology
    "013": "207600000X",  # ENT/Otolaryngology
    "014": "207RG0001X",  # Gastroenterology
    "015": "208600000X",  # General Surgery
    "016": "2085A0100X",  # Gynecology (OB/GYN)
    "017": "207RI0001X",  # Infectious Diseases
    "018": "207RN0001X",  # Nephrology
    "019": "2084N0400X",  # Neurology (subspecialty of Psychiatry & Neurology)
    "020": "207T00000X",  # Neurosurgery
    "021": "207RM0001X",  # Oncology - Medical & Surgical
    "022": "2085R0001X",  # Oncology - Radiation
    "023": "207W00000X",  # Ophthalmology
    "025": "207X00000X",  # Orthopedic Surgery — NOTE: NUCC 207X = Orthopaedic Surgery
    "026": "208100000X",  # Physical Medicine & Rehabilitation
    "027": "208200000X",  # Plastic Surgery
    "028": "213E00000X",  # Podiatry
    "029": "2084P0800X",  # Psychiatry
    "030": "207RP1001X",  # Pulmonology
    "031": "207RR0001X",  # Rheumatology
    "033": "208800000X",  # Urology
    "034": "208900000X",  # Vascular Surgery
    "035": "208G00000X",  # Cardiothoracic Surgery
    "037": "207P00000X",  # Emergency Medicine
    "049": "225100000X",  # Physical Therapy
    "050": "225300000X",  # Occupational Therapy
    "051": "235Z00000X",  # Speech Therapy
    "101": "208000000X",  # Primary Care - Pediatric (Pediatrics)
    "102": "104100000X",  # Social Worker
    "103": "103TC0700X",  # Psychologist
    "105": "101Y00001X",  # Marriage & Family Therapist
    "106": "101YP2500X",  # Addiction (SUD) Counselor
    "107": "101YP0300X",  # Counselor (Mental Health & Professional)
    "108": "363L00000X",  # Behavioral Health - Advanced Practice RN
    "201": "122300000X",  # Dental - General
    "202": "1223D0003X",  # Dental - Orthodontist
    "203": "1223D0004X",  # Dental - Periodontist
    "204": "1223D0002X",  # Dental - Endodontist
    "206": "1223P0700X",  # Dental - Prosthodontist
    "P201": "1223D0001X", # Pediatric Dental
    "800": "207RA0401X",  # Addiction Medicine Physician
    "801": "101YP2500X",  # Behavioral Analyst
}

for difs_code, (name, category) in DIFS_INDIVIDUAL.items():
    nucc_code = difs_to_nucc.get(difs_code, "")
    nucc_info = nucc_codes.get(nucc_code, {})
    crosswalk_rows.append({
        "source": "DIFS",
        "source_code": difs_code,
        "source_name": name,
        "source_category": category,
        "nucc_code": nucc_code,
        "nucc_grouping": nucc_info.get("Grouping", ""),
        "nucc_classification": nucc_info.get("Classification", ""),
        "nucc_specialization": nucc_info.get("Specialization", ""),
        "nucc_definition": nucc_info.get("Definition", ""),
        "match_confidence": "high" if nucc_code else "none",
    })

for difs_code, (name, category) in DIFS_FACILITY.items():
    crosswalk_rows.append({
        "source": "DIFS",
        "source_code": difs_code,
        "source_name": name,
        "source_category": category,
        "nucc_code": "",
        "nucc_grouping": "",
        "nucc_classification": "",
        "nucc_specialization": "",
        "nucc_definition": "",
        "match_confidence": "none",
    })

# Write crosswalk
crosswalk_path = os.path.join(BASE, "mi_taxonomy_crosswalk.csv")
with open(crosswalk_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "source", "source_code", "source_name", "source_category",
        "nucc_code", "nucc_grouping", "nucc_classification", "nucc_specialization",
        "nucc_definition", "match_confidence"
    ])
    writer.writeheader()
    writer.writerows(crosswalk_rows)

print(f"Crosswalk written: {len(crosswalk_rows)} rows to {crosswalk_path}")

# ============================================================
# PHASE 3: Build mi_medicaid_specialties.csv
# ============================================================

# MDHHS Network Adequacy Standards table data
# Format: specialty, large_metro_time, large_metro_dist, metro_time, metro_dist,
#         micro_time, micro_dist, rural_time, rural_dist, ceac_time, ceac_dist
mdhhs_specialties = [
    # Primary Care
    ("Primary Care - Adult", "Primary Care", "Primary Care - Adult", "10 min / 5 mi", "15 min / 10 mi", "30 min / 20 mi", "40 min / 30 mi", "70 min / 60 mi", "", "1:500 (except Kalkaska 1:692, Missaukee 1:873, Schoolcraft 1:806; all other counties 1:650)", "MDHHS Network Adequacy Standards"),
    ("Primary Care - Pediatric", "Primary Care", "Primary Care - Pediatric", "10 min / 5 mi", "15 min / 10 mi", "30 min / 20 mi", "40 min / 30 mi", "70 min / 60 mi", "", "1:500", "MDHHS Network Adequacy Standards"),
    # OB/GYN
    ("Gynecology, OB/GYN", "OB/GYN", "Gynecology, OB/GYN", "10 min / 5 mi", "15 min / 10 mi", "30 min / 20 mi", "40 min / 30 mi", "70 min / 60 mi", "", "", "MDHHS Network Adequacy Standards"),
    # Hospital
    ("Hospital", "Facility", "Hospital", "20 min / 10 mi", "30 min / 30 mi", "30 min / 30 mi", "60 min / 60 mi", "110 min / 100 mi", "", "", "MDHHS Network Adequacy Standards"),
    # Specialists
    ("Cardiology", "Specialist", "Cardiology", "20 min / 10 mi", "30 min / 30 mi", "30 min / 30 mi", "60 min / 60 mi", "95 min / 85 mi", "", "", "MDHHS Network Adequacy Standards"),
    ("Neurology", "Specialist", "Neurology", "20 min / 10 mi", "30 min / 30 mi", "30 min / 30 mi", "60 min / 60 mi", "110 min / 100 mi", "", "", "MDHHS Network Adequacy Standards"),
    ("Oncology - Medical, Surgical", "Specialist", "Oncology - Medical, Surgical", "20 min / 10 mi", "30 min / 30 mi", "30 min / 30 mi", "60 min / 60 mi", "110 min / 100 mi", "", "", "MDHHS Network Adequacy Standards"),
    ("Oncology - Radiation", "Specialist", "Oncology - Radiation", "30 min / 15 mi", "60 min / 40 mi", "100 min / 75 mi", "110 min / 90 mi", "145 min / 130 mi", "", "", "MDHHS Network Adequacy Standards"),
    ("Orthopedics/Orthopedic Surgery", "Specialist", "Orthopedics/Orthopedic Surgery", "20 min / 10 mi", "30 min / 30 mi", "30 min / 30 mi", "60 min / 60 mi", "95 min / 85 mi", "", "", "MDHHS Network Adequacy Standards"),
    # Therapy
    ("Occupational Therapy", "Ancillary", "Occupational Therapy", "20 min / 10 mi", "45 min / 30 mi", "80 min / 60 mi", "75 min / 60 mi", "110 min / 100 mi", "", "", "MDHHS Network Adequacy Standards"),
    ("Physical Therapy", "Ancillary", "Physical Therapy", "20 min / 10 mi", "45 min / 30 mi", "80 min / 60 mi", "75 min / 60 mi", "110 min / 100 mi", "", "", "MDHHS Network Adequacy Standards"),
    ("Speech Therapy", "Ancillary", "Speech Therapy", "20 min / 10 mi", "45 min / 30 mi", "80 min / 60 mi", "75 min / 60 mi", "110 min / 100 mi", "", "", "MDHHS Network Adequacy Standards"),
    # Behavioral Health (in MDHHS physical health standards)
    ("Outpatient Clinical Behavioral Health - Adult", "Behavioral Health", "Outpatient Clinical Behavioral Health - Adult", "10 min / 5 mi", "15 min / 10 mi", "30 min / 20 mi", "40 min / 30 mi", "70 min / 60 mi", "", "", "MDHHS Network Adequacy Standards"),
    ("Outpatient Clinical Behavioral Health - Pediatric", "Behavioral Health", "Outpatient Clinical Behavioral Health - Pediatric", "10 min / 5 mi", "15 min / 10 mi", "30 min / 20 mi", "40 min / 30 mi", "70 min / 60 mi", "", "", "MDHHS Network Adequacy Standards"),
    ("Psychiatry - Adult", "Behavioral Health", "Psychiatry - Adult", "20 min / 10 mi", "45 min / 30 mi", "60 min / 45 mi", "75 min / 60 mi", "110 min / 100 mi", "", "", "MDHHS Network Adequacy Standards"),
    ("Psychiatry - Pediatric", "Behavioral Health", "Psychiatry - Pediatric", "20 min / 10 mi", "45 min / 30 mi", "60 min / 45 mi", "75 min / 60 mi", "110 min / 100 mi", "", "", "MDHHS Network Adequacy Standards"),
    # Dental
    ("Dentistry: General Dentist", "Dental", "Dentistry: General Dentist", "30 min / 15 mi", "30 min / 30 mi", "30 min / 30 mi", "40 min / 40 mi", "120 min / 120 mi", "", "1:650 (except Kalkaska 1:692, Missaukee 1:873, Schoolcraft 1:806)", "MDHHS Network Adequacy Standards"),
    ("Dentistry: Endodontics", "Dental", "Dentistry: Endodontics", "30 min / 15 mi", "60 min / 60 mi", "60 min / 60 mi", "120 min / 120 mi", "120 min / 120 mi", "", "", "MDHHS Network Adequacy Standards"),
    ("Dentistry: Oral Surgery", "Dental", "Dentistry: Oral Surgery", "30 min / 15 mi", "60 min / 60 mi", "60 min / 60 mi", "120 min / 120 mi", "120 min / 120 mi", "", "", "MDHHS Network Adequacy Standards"),
    ("Dentistry: Periodontics", "Dental", "Dentistry: Periodontics", "30 min / 15 mi", "60 min / 60 mi", "60 min / 60 mi", "120 min / 120 mi", "120 min / 120 mi", "", "", "MDHHS Network Adequacy Standards"),
    ("Dentistry: Prosthodontics", "Dental", "Dentistry: Prosthodontics", "30 min / 15 mi", "60 min / 60 mi", "60 min / 60 mi", "120 min / 120 mi", "120 min / 120 mi", "", "", "MDHHS Network Adequacy Standards"),
    # Pharmacy
    ("Pharmacy", "Ancillary", "Pharmacy", "10 min / 5 mi", "15 min / 10 mi", "30 min / 20 mi", "40 min / 30 mi", "40 min / 30 mi", "", "", "MDHHS Network Adequacy Standards"),
]

# DIFS additional specialties (Section 4.1) - all max 30-min travel time
difs_additional_specialties = [
    ("Anesthesiology", "Specialist", "Anesthesiology", "30 min", "30 min", "30 min", "30 min", "30 min", "", "", "DIFS Network Adequacy Guidance"),
    ("Outpatient Dialysis", "Facility", "Outpatient Dialysis", "30 min", "30 min", "30 min", "30 min", "30 min", "", "", "DIFS Network Adequacy Guidance"),
    ("DME", "Ancillary", "Durable Medical Equipment", "30 min", "30 min", "30 min", "30 min", "30 min", "", "", "DIFS Network Adequacy Guidance"),
    ("Home Health", "Facility", "Home Health", "30 min", "30 min", "30 min", "30 min", "30 min", "", "", "DIFS Network Adequacy Guidance"),
    ("Home Infusion", "Facility", "Home Infusion", "30 min", "30 min", "30 min", "30 min", "30 min", "", "", "DIFS Network Adequacy Guidance"),
    ("Hospice", "Facility", "Hospice", "30 min", "30 min", "30 min", "30 min", "30 min", "", "", "DIFS Network Adequacy Guidance"),
    ("Laboratory", "Facility", "Laboratory", "30 min", "30 min", "30 min", "30 min", "30 min", "", "", "DIFS Network Adequacy Guidance"),
    ("Midwife", "Primary Care", "Certified Nurse Midwife", "30 min", "30 min", "30 min", "30 min", "30 min", "", "", "DIFS Network Adequacy Guidance"),
    ("Optometry", "Specialist", "Optometry", "30 min", "30 min", "30 min", "30 min", "30 min", "", "", "DIFS Network Adequacy Guidance"),
    ("Pathology", "Specialist", "Pathology", "30 min", "30 min", "30 min", "30 min", "30 min", "", "", "DIFS Network Adequacy Guidance"),
    ("Oral & Maxillofacial Surgery", "Specialist", "Oral & Maxillofacial Surgery", "30 min / 15 mi", "45 min / 30 mi", "80 min / 60 mi", "90 min / 75 mi", "125 min / 110 mi", "", "", "DIFS Network Adequacy Guidance (SADP)"),
]

# DIFS full individual provider specialty types with time/distance (Section 4.3)
difs_full_specialties = [
    ("Allergy and Immunology", "Specialist", "Allergy and Immunology", "30 min / 15 mi", "45 min / 30 mi", "80 min / 60 mi", "90 min / 75 mi", "125 min / 110 mi", "007", "", "DIFS Network Adequacy Guidance"),
    ("Cardiology", "Specialist", "Cardiology", "20 min / 10 mi", "30 min / 20 mi", "50 min / 35 mi", "75 min / 60 mi", "95 min / 85 mi", "008", "", "DIFS Network Adequacy Guidance"),
    ("Cardiothoracic Surgery", "Specialist", "Cardiothoracic Surgery", "30 min / 15 mi", "60 min / 40 mi", "100 min / 75 mi", "110 min / 90 mi", "145 min / 130 mi", "035", "", "DIFS Network Adequacy Guidance"),
    ("Chiropractor", "Ancillary", "Chiropractor", "30 min / 15 mi", "45 min / 30 mi", "80 min / 60 mi", "90 min / 75 mi", "125 min / 110 mi", "010", "", "DIFS Network Adequacy Guidance"),
    ("Dermatology", "Specialist", "Dermatology", "20 min / 10 mi", "45 min / 30 mi", "60 min / 45 mi", "75 min / 60 mi", "110 min / 100 mi", "011", "", "DIFS Network Adequacy Guidance"),
    ("Emergency Medicine", "Specialist", "Emergency Medicine", "20 min / 10 mi", "45 min / 30 mi", "80 min / 60 mi", "75 min / 60 mi", "110 min / 100 mi", "037", "", "DIFS Network Adequacy Guidance"),
    ("Endocrinology", "Specialist", "Endocrinology", "30 min / 15 mi", "60 min / 40 mi", "100 min / 75 mi", "110 min / 90 mi", "145 min / 130 mi", "012", "", "DIFS Network Adequacy Guidance"),
    ("ENT/Otolaryngology", "Specialist", "ENT/Otolaryngology", "30 min / 15 mi", "45 min / 30 mi", "80 min / 60 mi", "90 min / 75 mi", "125 min / 110 mi", "013", "", "DIFS Network Adequacy Guidance"),
    ("Gastroenterology", "Specialist", "Gastroenterology", "20 min / 10 mi", "45 min / 30 mi", "60 min / 45 mi", "75 min / 60 mi", "110 min / 100 mi", "014", "", "DIFS Network Adequacy Guidance"),
    ("General Surgery", "Specialist", "General Surgery", "20 min / 10 mi", "30 min / 20 mi", "50 min / 35 mi", "75 min / 60 mi", "95 min / 85 mi", "015", "", "DIFS Network Adequacy Guidance"),
    ("Infectious Diseases", "Specialist", "Infectious Diseases", "30 min / 15 mi", "60 min / 40 mi", "100 min / 75 mi", "110 min / 90 mi", "145 min / 130 mi", "017", "", "DIFS Network Adequacy Guidance"),
    ("Nephrology", "Specialist", "Nephrology", "30 min / 15 mi", "45 min / 30 mi", "80 min / 60 mi", "90 min / 75 mi", "125 min / 110 mi", "018", "", "DIFS Network Adequacy Guidance"),
    ("Neurology", "Specialist", "Neurology", "20 min / 10 mi", "45 min / 30 mi", "60 min / 45 mi", "75 min / 60 mi", "110 min / 100 mi", "019", "", "DIFS Network Adequacy Guidance"),
    ("Neurosurgery", "Specialist", "Neurosurgery", "30 min / 15 mi", "60 min / 40 mi", "100 min / 75 mi", "110 min / 90 mi", "145 min / 130 mi", "020", "", "DIFS Network Adequacy Guidance"),
    ("Oncology-Medical, Surgical", "Specialist", "Oncology-Medical, Surgical", "20 min / 10 mi", "45 min / 30 mi", "60 min / 45 mi", "75 min / 60 mi", "110 min / 100 mi", "021", "", "DIFS Network Adequacy Guidance"),
    ("Oncology-Radiation", "Specialist", "Oncology-Radiation", "30 min / 15 mi", "60 min / 40 mi", "100 min / 75 mi", "110 min / 90 mi", "145 min / 130 mi", "022", "", "DIFS Network Adequacy Guidance"),
    ("Ophthalmology", "Specialist", "Ophthalmology", "20 min / 10 mi", "30 min / 20 mi", "50 min / 35 mi", "75 min / 60 mi", "95 min / 85 mi", "023", "", "DIFS Network Adequacy Guidance"),
    ("Orthopedic Surgery", "Specialist", "Orthopedic Surgery", "20 min / 10 mi", "30 min / 20 mi", "50 min / 35 mi", "75 min / 60 mi", "95 min / 85 mi", "025", "", "DIFS Network Adequacy Guidance"),
    ("Physical Medicine and Rehabilitation", "Specialist", "Physical Medicine and Rehabilitation", "30 min / 15 mi", "45 min / 30 mi", "80 min / 60 mi", "90 min / 75 mi", "125 min / 110 mi", "026", "", "DIFS Network Adequacy Guidance"),
    ("Plastic Surgery", "Specialist", "Plastic Surgery", "30 min / 15 mi", "60 min / 40 mi", "100 min / 75 mi", "110 min / 90 mi", "145 min / 130 mi", "027", "", "DIFS Network Adequacy Guidance"),
    ("Podiatry", "Specialist", "Podiatry", "20 min / 10 mi", "45 min / 30 mi", "60 min / 45 mi", "75 min / 60 mi", "110 min / 100 mi", "028", "", "DIFS Network Adequacy Guidance"),
    ("Psychiatry", "Behavioral Health", "Psychiatry", "20 min / 10 mi", "45 min / 30 mi", "60 min / 45 mi", "75 min / 60 mi", "110 min / 100 mi", "029", "", "DIFS Network Adequacy Guidance"),
    ("Pulmonology", "Specialist", "Pulmonology", "20 min / 10 mi", "45 min / 30 mi", "60 min / 45 mi", "75 min / 60 mi", "110 min / 100 mi", "030", "", "DIFS Network Adequacy Guidance"),
    ("Rheumatology", "Specialist", "Rheumatology", "30 min / 15 mi", "60 min / 40 mi", "100 min / 75 mi", "110 min / 90 mi", "145 min / 130 mi", "031", "", "DIFS Network Adequacy Guidance"),
    ("Urology", "Specialist", "Urology", "20 min / 10 mi", "45 min / 30 mi", "60 min / 45 mi", "75 min / 60 mi", "110 min / 100 mi", "033", "", "DIFS Network Adequacy Guidance"),
    ("Vascular Surgery", "Specialist", "Vascular Surgery", "30 min / 15 mi", "60 min / 40 mi", "100 min / 75 mi", "110 min / 90 mi", "145 min / 130 mi", "034", "", "DIFS Network Adequacy Guidance"),
]

# DIFS facility specialty types with time/distance (Section 4.4)
difs_facility_specialties = [
    ("Acute Inpatient Hospitals", "Facility", "Acute Inpatient Hospitals", "20 min / 10 mi", "45 min / 30 mi", "80 min / 60 mi", "75 min / 60 mi", "110 min / 100 mi", "040", "", "DIFS Network Adequacy Guidance"),
    ("Cardiac Catheterization Services", "Facility", "Cardiac Catheterization Services", "30 min / 15 mi", "60 min / 40 mi", "160 min / 120 mi", "145 min / 120 mi", "155 min / 140 mi", "042", "", "DIFS Network Adequacy Guidance"),
    ("Cardiac Surgery Program", "Facility", "Cardiac Surgery Program", "30 min / 15 mi", "60 min / 40 mi", "160 min / 120 mi", "145 min / 120 mi", "155 min / 140 mi", "041", "", "DIFS Network Adequacy Guidance"),
    ("Critical Care Services - ICU", "Facility", "Critical Care Services - ICU", "20 min / 10 mi", "45 min / 30 mi", "160 min / 120 mi", "145 min / 120 mi", "155 min / 140 mi", "043", "", "DIFS Network Adequacy Guidance"),
    ("Diagnostic Radiology", "Facility", "Diagnostic Radiology", "20 min / 10 mi", "45 min / 30 mi", "80 min / 60 mi", "75 min / 60 mi", "110 min / 100 mi", "047", "", "DIFS Network Adequacy Guidance"),
    ("Inpatient/Residential Behavioral Health Facility", "Facility", "Inpatient/Residential Behavioral Health Facility", "30 min / 15 mi", "70 min / 45 mi", "100 min / 75 mi", "90 min / 75 mi", "155 min / 140 mi", "052", "", "DIFS Network Adequacy Guidance"),
    ("Mammography", "Facility", "Mammography", "20 min / 10 mi", "45 min / 30 mi", "80 min / 60 mi", "75 min / 60 mi", "110 min / 100 mi", "048", "", "DIFS Network Adequacy Guidance"),
    ("Outpatient Infusion/Chemotherapy", "Facility", "Outpatient Infusion/Chemotherapy", "20 min / 10 mi", "45 min / 30 mi", "80 min / 60 mi", "75 min / 60 mi", "110 min / 100 mi", "057", "", "DIFS Network Adequacy Guidance"),
    ("Skilled Nursing Facilities", "Facility", "Skilled Nursing Facilities", "20 min / 10 mi", "45 min / 30 mi", "80 min / 60 mi", "75 min / 60 mi", "95 min / 85 mi", "046", "", "DIFS Network Adequacy Guidance"),
    ("Surgical Services (ASC/Outpatient)", "Facility", "Surgical Services (ASC/Outpatient)", "20 min / 10 mi", "45 min / 30 mi", "80 min / 60 mi", "75 min / 60 mi", "110 min / 100 mi", "045", "", "DIFS Network Adequacy Guidance"),
    ("Urgent Care", "Facility", "Urgent Care", "20 min / 10 mi", "45 min / 30 mi", "80 min / 60 mi", "75 min / 60 mi", "110 min / 100 mi", "080", "", "DIFS Network Adequacy Guidance"),
    ("Substance Abuse Rehabilitation Facility", "Facility", "Substance Abuse Rehabilitation Facility", "", "", "", "", "", "072", "", "DIFS Network Adequacy Guidance"),
    ("Mental Health Residential Treatment Facility", "Facility", "Mental Health Residential Treatment Facility", "", "", "", "", "", "076", "", "DIFS Network Adequacy Guidance"),
    ("Children's Substance Abuse Rehabilitation Facility", "Facility", "Children's Substance Abuse Rehabilitation Facility", "", "", "", "", "", "P072", "", "DIFS Network Adequacy Guidance"),
    ("Children's Residential Treatment Facility", "Facility", "Children's Residential Treatment Facility", "", "", "", "", "", "P076", "", "DIFS Network Adequacy Guidance"),
]

# PIHP Behavioral Health specialties (from PIHP document)
pihp_adult_services = [
    ("Assertive Community Treatment", "Behavioral Health", "Assertive Community Treatment (ACT)", "", "", "", "", "", "H0039", "1:30,000 (Team to Medicaid Enrollee)", "PIHP Network Adequacy Standards"),
    ("Crisis Residential Programs", "Behavioral Health", "Crisis Residential Programs", "", "", "", "", "", "H0018", "16 beds per 500,000 Total Population", "PIHP Network Adequacy Standards"),
    ("Opioid Treatment Programs", "Behavioral Health", "Opioid Treatment Programs", "", "", "", "", "", "H0020", "1:35,000 (Provider to Medicaid Enrollee)", "PIHP Network Adequacy Standards"),
    ("Psychosocial Rehabilitation (Clubhouses)", "Behavioral Health", "Psychosocial Rehabilitation Programs (Clubhouses)", "", "", "", "", "", "H2030", "1:45,000 (Provider to Medicaid Enrollee)", "PIHP Network Adequacy Standards"),
    ("Inpatient Psychiatric", "Behavioral Health", "Inpatient Psychiatric", "", "", "", "", "", "0100/0114/0124/0134/0154", "", "PIHP Network Adequacy Standards"),
    ("Community Living Supports", "Behavioral Health", "Community Living Supports", "", "", "", "", "", "H2015", "FY25 informational only", "PIHP Network Adequacy Standards"),
    ("Skill Building", "Behavioral Health", "Skill Building", "", "", "", "", "", "H2014", "FY25 informational only", "PIHP Network Adequacy Standards"),
    ("Partial Hospitalization Programs", "Behavioral Health", "Partial Hospitalization Programs", "", "", "", "", "", "0912/0913", "", "PIHP Network Adequacy Standards"),
    ("Targeted Case Management", "Behavioral Health", "Targeted Case Management", "", "", "", "", "", "T1017", "FY25 informational only", "PIHP Network Adequacy Standards"),
    ("Pre-Admission Screen", "Behavioral Health", "Pre-Admission Screen", "", "", "", "", "", "T1023", "FY25 informational only", "PIHP Network Adequacy Standards"),
    ("Outpatient Clinical Mental Health", "Behavioral Health", "Outpatient Clinical Mental Health", "", "", "", "", "", "90832/90834/90837", "FY25 informational only", "PIHP Network Adequacy Standards"),
]

pihp_youth_services = [
    ("Crisis Residential Programs (Youth)", "Behavioral Health", "Crisis Residential Programs (Youth)", "", "", "", "", "", "H0018", "8-12 beds per 500,000 Total Population", "PIHP Network Adequacy Standards"),
    ("Home-Based Services", "Behavioral Health", "Home-Based Services", "", "", "", "", "", "H0036", "1:2,000 (Provider to Medicaid Enrollee)", "PIHP Network Adequacy Standards"),
    ("Intensive Care Coordination with Wraparound (ICCW)", "Behavioral Health", "Intensive Care Coordination with Wraparound", "", "", "", "", "", "H2021", "1:5,000 (Provider to Medicaid Enrollee)", "PIHP Network Adequacy Standards"),
    ("Intensive Crisis Stabilization Services", "Behavioral Health", "Intensive Crisis Stabilization Services (Mobile Response)", "", "", "", "", "", "H2011HT", "FY25 informational only", "PIHP Network Adequacy Standards"),
    ("Respite Services", "Behavioral Health", "Respite Services", "", "", "", "", "", "T1005/H0045/S5151", "FY25 informational only", "PIHP Network Adequacy Standards"),
    ("Parent Support Partners", "Behavioral Health", "Parent Support Partners", "", "", "", "", "", "S5111-WP", "FY25 informational only", "PIHP Network Adequacy Standards"),
    ("Youth Peer Supports", "Behavioral Health", "Youth Peer Supports", "", "", "", "", "", "H0038-WT", "FY25 informational only", "PIHP Network Adequacy Standards"),
    ("Autism Diagnostic Evaluations", "Behavioral Health", "Autism Diagnostic Evaluations", "", "", "", "", "", "90791/90792/96110/etc", "FY25 informational only", "PIHP Network Adequacy Standards"),
    ("Autism Services", "Behavioral Health", "Autism Services", "", "", "", "", "", "97151-97158/0373T", "FY25 informational only", "PIHP Network Adequacy Standards"),
]

# Build the final CSV
csv_rows = []

# MDHHS specialties (primary source for Medicaid)
for row in mdhhs_specialties:
    csv_rows.append({
        "tier": row[1],
        "category": row[1],
        "specialty": row[2],
        "designation_type": "MDHHS CHCP",
        "specialty_code": "",
        "provider_count_requirement": "Min 2 (Large Metro & Metro)" if row[0] in ("Primary Care - Adult", "Primary Care - Pediatric", "Gynecology, OB/GYN", "Hospital") else "",
        "travel_time_requirement": f"Large Metro: {row[3]}; Metro: {row[4]}; Micro: {row[5]}; Rural: {row[6]}; CEAC: {row[7]}",
        "enrollees_per_provider": row[8],
        "source": row[9],
    })

# DIFS additional specialties (applies to all HMOs including Medicaid)
for row in difs_additional_specialties:
    csv_rows.append({
        "tier": row[1],
        "category": row[1],
        "specialty": row[2],
        "designation_type": "DIFS (all HMOs)",
        "specialty_code": "",
        "provider_count_requirement": "",
        "travel_time_requirement": f"Max 30-min travel time regardless county designation" if "30 min" == row[3] else f"Large Metro: {row[3]}; Metro: {row[4]}; Micro: {row[5]}; Rural: {row[6]}; CEAC: {row[7]}",
        "enrollees_per_provider": row[8],
        "source": row[9],
    })

# DIFS full individual specialties (commercial but referenced for Medicaid)
for row in difs_full_specialties:
    csv_rows.append({
        "tier": row[1],
        "category": row[1],
        "specialty": row[2],
        "designation_type": "DIFS (all HMOs)",
        "specialty_code": row[7],
        "provider_count_requirement": "",
        "travel_time_requirement": f"Large Metro: {row[3]}; Metro: {row[4]}; Micro: {row[5]}; Rural: {row[6]}; CEAC: {row[7]}",
        "enrollees_per_provider": row[8],
        "source": row[9],
    })

# DIFS facility specialties
for row in difs_facility_specialties:
    csv_rows.append({
        "tier": row[1],
        "category": row[1],
        "specialty": row[2],
        "designation_type": "DIFS (all HMOs)",
        "specialty_code": row[7],
        "provider_count_requirement": "",
        "travel_time_requirement": f"Large Metro: {row[3]}; Metro: {row[4]}; Micro: {row[5]}; Rural: {row[6]}; CEAC: {row[7]}" if row[3] else "",
        "enrollees_per_provider": row[8],
        "source": row[9],
    })

# PIHP Adult behavioral health services
for row in pihp_adult_services:
    csv_rows.append({
        "tier": row[1],
        "category": "PIHP Adult",
        "specialty": row[2],
        "designation_type": "PIHP BH",
        "specialty_code": row[7],
        "provider_count_requirement": "",
        "travel_time_requirement": "Inpatient/Partial: Large Metro 30 min/15 mi, Metro 70 min/45 mi, Micro 100 min/75 mi, Rural 90 min/75 mi, CEAC 155 min/140 mi; All Other: Large Metro 20 min/10 mi, Metro 45 min/30 mi, Micro 70 min/53 mi, Rural 75 min/60 mi, CEAC 118 min/105 mi",
        "enrollees_per_provider": row[8],
        "source": row[9],
    })

# PIHP Youth behavioral health services
for row in pihp_youth_services:
    csv_rows.append({
        "tier": row[1],
        "category": "PIHP Youth",
        "specialty": row[2],
        "designation_type": "PIHP BH",
        "specialty_code": row[7],
        "provider_count_requirement": "",
        "travel_time_requirement": "Inpatient/Partial: Large Metro 30 min/15 mi, Metro 70 min/45 mi, Micro 100 min/75 mi, Rural 90 min/75 mi, CEAC 155 min/140 mi; All Other: Large Metro 20 min/10 mi, Metro 45 min/30 mi, Micro 70 min/53 mi, Rural 75 min/60 mi, CEAC 118 min/105 mi",
        "enrollees_per_provider": row[8],
        "source": row[9],
    })

# Write CSV
csv_path = os.path.join(BASE, "mi_medicaid_specialties.csv")
fieldnames = ["tier", "category", "specialty", "designation_type", "specialty_code",
              "provider_count_requirement", "travel_time_requirement", "enrollees_per_provider", "source"]

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(csv_rows)

print(f"\nCSV written: {len(csv_rows)} data rows to {csv_path}")
print(f"Breakdown:")
tier_counts = {}
for r in csv_rows:
    t = r["tier"]
    tier_counts[t] = tier_counts.get(t, 0) + 1
for t, c in sorted(tier_counts.items()):
    print(f"  {t}: {c}")
