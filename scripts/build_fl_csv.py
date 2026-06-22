#!/usr/bin/env python3
"""Build fl_medicaid_specialties.csv from Exhibit II-A MMA Program & Dental Attachment II.

Sources:
1. Exhibit II-A – Managed Medical Assistance (MMA) Program, Update October 1, 2025.
   Table 4: Managed Medical Assistance Provider Network Standards Table (pages 65-68).
   URL: https://ahca.myflorida.com/content/download/27249/file/Exhibit%20II-A%20Managed%20Medical%20Assistance%20(MMA)%20Program%20Oct%202025.pdf

2. Attachment II – Scope of Service, Core Provisions, Dental Health Program, Update October 1, 2025.
   Table 4: Dental Plan Provider Network Standards (pages 82-83).
   URL: https://ahca.myflorida.com/content/download/27252/file/Attachment%20II_Core%20Contract%20Provisions%20October%202025.pdf
"""
import csv
import os

# Data extracted from Exhibit II-A MMA Program, Table 4 (pages 65-68)
# Format: (specialty, category, urban_min, urban_miles, rural_min, rural_miles, provider_ratio, source)
specialties = [
    # Primary Care Providers
    ("Primary Care Providers", "Primary Care", 30, 20, 30, 20, "1:750 enrollees", "Exhibit II-A, Table 4"),

    # Specialists
    ("Allergy", "Specialist", 80, 60, 90, 75, "1:20,000 enrollees", "Exhibit II-A, Table 4"),
    ("Cardiology", "Specialist", 50, 35, 75, 60, "1:3,700 enrollees", "Exhibit II-A, Table 4"),
    ("Cardiology (Pediatric)", "Specialist", 100, 75, 110, 90, "1:16,667 enrollees", "Exhibit II-A, Table 4"),
    ("Cardiovascular Surgery", "Specialist", 100, 75, 110, 90, "1:10,000 enrollees", "Exhibit II-A, Table 4"),
    ("Chiropractic", "Specialist", 80, 60, 90, 75, "1:10,000 enrollees", "Exhibit II-A, Table 4"),
    ("Dermatology", "Specialist", 60, 45, 75, 60, "1:7,900 enrollees", "Exhibit II-A, Table 4"),
    ("Endocrinology", "Specialist", 100, 75, 110, 90, "1:25,000 enrollees", "Exhibit II-A, Table 4"),
    ("Endocrinology (Pediatric)", "Specialist", 100, 75, 110, 90, "1:20,000 enrollees", "Exhibit II-A, Table 4"),
    ("Gastroenterology", "Specialist", 60, 45, 75, 60, "1:8,333 enrollees", "Exhibit II-A, Table 4"),
    ("General Surgery", "Specialist", 50, 35, 75, 60, "1:3,500 enrollees", "Exhibit II-A, Table 4"),
    ("Infectious Diseases", "Specialist", 100, 75, 110, 90, "1:6,250 enrollees", "Exhibit II-A, Table 4"),
    ("Internal Medicine Specialist", "Specialist", 30, 20, 30, 20, "1:3,000 enrollees", "Exhibit II-A, Table 4"),
    ("Midwife", "Specialist", 80, 60, 90, 75, "1:20,000 enrollees", "Exhibit II-A, Table 4"),
    ("Nephrology", "Specialist", 80, 60, 90, 75, "1:11,100 enrollees", "Exhibit II-A, Table 4"),
    ("Nephrology (Pediatric)", "Specialist", 100, 75, 110, 90, "1:39,600 enrollees", "Exhibit II-A, Table 4"),
    ("Neurology", "Specialist", 60, 45, 75, 60, "1:8,300 enrollees", "Exhibit II-A, Table 4"),
    ("Neurology (Pediatric)", "Specialist", 100, 75, 110, 90, "1:22,800 enrollees", "Exhibit II-A, Table 4"),
    ("Neurosurgery", "Specialist", 100, 75, 110, 90, "1:10,000 enrollees", "Exhibit II-A, Table 4"),
    ("Obstetrics/Gynecology", "Specialist", 50, 35, 75, 60, "1:1,500 enrollees", "Exhibit II-A, Table 4"),
    ("Oncology", "Specialist", 80, 60, 90, 75, "1:5,200 enrollees", "Exhibit II-A, Table 4"),
    ("Ophthalmology", "Specialist", 50, 35, 75, 60, "1:4,100 enrollees", "Exhibit II-A, Table 4"),
    ("Optometry", "Specialist", 50, 35, 75, 60, "1:1,700 enrollees", "Exhibit II-A, Table 4"),
    ("Orthopedic Surgery", "Specialist", 50, 35, 75, 60, "1:5,000 enrollees", "Exhibit II-A, Table 4"),
    ("Otolaryngology (ENT)", "Specialist", 80, 60, 90, 75, "1:3,500 enrollees", "Exhibit II-A, Table 4"),
    ("Pediatrics (including Adolescent Medicine)", "Specialist", 50, 35, 75, 60, "1:1,500 enrollees", "Exhibit II-A, Table 4"),
    ("Pharmacy", "Specialist", 15, 10, 15, 10, "1:2,500 enrollees", "Exhibit II-A, Table 4"),
    ("24-Hour Pharmacy", "Specialist", 60, 45, 60, 45, "N/A", "Exhibit II-A, Table 4"),
    ("Podiatry", "Specialist", 60, 45, 75, 60, "1:5,200 enrollees", "Exhibit II-A, Table 4"),
    ("Pulmonology", "Specialist", 60, 45, 75, 60, "1:7,600 enrollees", "Exhibit II-A, Table 4"),
    ("Rheumatology", "Specialist", 100, 75, 110, 90, "1:14,400 enrollees", "Exhibit II-A, Table 4"),
    ("Therapist (Occupational)", "Specialist", 50, 35, 75, 60, "1:1,500 enrollees", "Exhibit II-A, Table 4"),
    ("Therapist, Pediatric (Occupational)", "Specialist", 30, 20, 60, 45, "1:1,500 enrollees", "Exhibit II-A, Table 4"),
    ("Therapist (Speech)", "Specialist", 50, 35, 75, 60, "1:1,500 enrollees", "Exhibit II-A, Table 4"),
    ("Therapist, Pediatric (Speech)", "Specialist", 30, 20, 60, 45, "1:1,500 enrollees", "Exhibit II-A, Table 4"),
    ("Therapist (Physical)", "Specialist", 50, 35, 75, 60, "1:1,500 enrollees", "Exhibit II-A, Table 4"),
    ("Therapist, Pediatric (Physical)", "Specialist", 30, 20, 60, 45, "1:1,500 enrollees", "Exhibit II-A, Table 4"),
    ("Therapist (Respiratory)", "Specialist", 100, 75, 110, 90, "1:8,600 enrollees", "Exhibit II-A, Table 4"),
    ("Therapist, Pediatric (Respiratory)", "Specialist", 60, 45, 75, 60, "1:1,500 enrollees", "Exhibit II-A, Table 4"),
    ("Urology", "Specialist", 60, 45, 75, 60, "1:10,000 enrollees", "Exhibit II-A, Table 4"),

    # Facility / Group / Organization
    ("24/7 Emergency Service Facility", "Facility", 30, 20, 30, 20, "2 per county", "Exhibit II-A, Table 4"),
    ("Durable Medical Equipment / Home Medical Equipment", "Facility", "N/A", "N/A", "N/A", "N/A", "2 per county", "Exhibit II-A, Table 4"),
    ("Home Health Agency", "Facility", "N/A", "N/A", "N/A", "N/A", "2 per county", "Exhibit II-A, Table 4"),
    ("Hospice", "Facility", "N/A", "N/A", "N/A", "N/A", "2 per county", "Exhibit II-A, Table 4"),
    ("Hospitals (Acute Care)", "Facility", 30, 20, 30, 20, "1 bed: 275 enrollees", "Exhibit II-A, Table 4"),
    ("Hospital or Facility with Birth/Delivery Services (including Birthing Center)", "Facility", 30, 20, 30, 20, "1 bed: 275 enrollees", "Exhibit II-A, Table 4"),
    ("Fully Accredited Psychiatric Community Hospital (Adult) / Crisis Stabilization Units", "Facility", "N/A", "N/A", "N/A", "N/A", "1 bed: 2,000 enrollees", "Exhibit II-A, Table 4"),
    ("Fully Accredited Psychiatric Community Hospital (Child) / Crisis Stabilization Units", "Facility", "N/A", "N/A", "N/A", "N/A", "1 bed: 3,000 enrollees", "Exhibit II-A, Table 4"),
    ("Statewide Inpatient Psychiatric Program Providers (Under 21)", "Facility", "N/A", "N/A", "N/A", "N/A", "1 bed: 3,000 enrollees", "Exhibit II-A, Table 4"),
    ("Medication and Methadone Treatment Programs", "Facility", 30, 20, 60, 45, "N/A", "Exhibit II-A, Table 4"),

    # Behavioral Health
    ("Licensed Practitioners of the Healing Arts (LPHA)", "Behavioral Health", 30, 20, 30, 20, "1:1,000 enrollees", "Exhibit II-A, Table 4"),
    ("Board Certified/Eligible Child Psychiatrist", "Behavioral Health", 30, 20, 60, 45, "1:3,500 enrollees", "Exhibit II-A, Table 4"),
    ("Behavioral Health Assistant Analyst (BCaBA)", "Behavioral Health", "N/A", "N/A", "N/A", "N/A", "Counts as 0.5 Lead Analyst", "Exhibit II-A, Table 4"),
    ("Board Certified/Eligible Adult Psychiatrist", "Behavioral Health", 30, 20, 60, 45, "1:375 enrollees", "Exhibit II-A, Table 4"),
    ("Inpatient Substance Abuse Detoxification Units", "Behavioral Health", "N/A", "N/A", "N/A", "N/A", "1 bed: 1,000 enrollees", "Exhibit II-A, Table 4"),
    ("Lead Analyst (BCBA)", "Behavioral Health", "N/A", "N/A", "N/A", "N/A", "1 per 775 enrollees", "Exhibit II-A, Table 4"),
    ("Registered Behavior Technician (RBT)", "Behavioral Health", "N/A", "N/A", "N/A", "N/A", "1 per 125 enrollees", "Exhibit II-A, Table 4"),

    # Dental (from Dental Attachment II, Table 4, pages 82-83)
    ("General Dentist", "Dental", 50, 35, 65, 45, "1:1,500", "Dental Attachment II, Table 4"),
    ("Pediatric Dentist", "Dental", 50, 35, 65, 45, "1:3,000", "Dental Attachment II, Table 4"),
    ("Endodontist", "Dental", 60, 50, 90, 75, "1:5,000", "Dental Attachment II, Table 4"),
    ("Orthodontist", "Dental", 60, 50, 90, 75, "1:38,500", "Dental Attachment II, Table 4"),
    ("Oral Surgeon", "Dental", 60, 50, 90, 75, "1:20,600", "Dental Attachment II, Table 4"),
    ("Periodontist", "Dental", "N/A", "N/A", "N/A", "N/A", "Referral basis", "Dental Attachment II, p.84"),
    ("Prosthodontist", "Dental", "N/A", "N/A", "N/A", "N/A", "Referral basis", "Dental Attachment II, p.84"),
]

# Write CSV
fieldnames = [
    "specialty", "category",
    "travel_time_urban_min", "travel_time_urban_miles",
    "travel_time_rural_min", "travel_time_rural_miles",
    "provider_ratio_standard", "source"
]

output_path = os.path.join(os.path.dirname(__file__), '..', 'fl_medicaid_specialties.csv')
with open(output_path, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for s in specialties:
        writer.writerow({
            "specialty": s[0],
            "category": s[1],
            "travel_time_urban_min": s[2],
            "travel_time_urban_miles": s[3],
            "travel_time_rural_min": s[4],
            "travel_time_rural_miles": s[5],
            "provider_ratio_standard": s[6],
            "source": s[7],
        })

print(f"Wrote {len(specialties)} specialties to {output_path}")

from collections import Counter
cats = Counter(s[1] for s in specialties)
for cat, count in sorted(cats.items()):
    print(f"  {cat}: {count}")
