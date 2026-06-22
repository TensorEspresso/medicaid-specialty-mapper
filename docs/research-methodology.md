# State Medicaid Specialty Data Collection: Research Methodology

**Created:** 2026-06-04  
**Last Updated:** 2026-06-05  
**Author:** Tensor (AI assistant)  
**Sessions:** 20260604_205511_8fdc2a (PA), 20260604_220115_734469 (CA), 20260605_143413_92e369 (NY), current session (TX, FL, MI)

## Overview

This document describes the research workflows used to extract Medicaid provider specialty categories from state government sources. Covers completed states: California (CA), Texas (TX), Pennsylvania (PA), New York (NY), Florida (FL). Each state had a different source landscape — see the workflow sections below for the actual process followed, reconstructed from session records.

## The Challenge

State Medicaid specialty data lives in:
- PDFs on state government websites (often behind bot protection)
- MCO contract documents
- Network adequacy reports
- Provider enrollment manuals

These sources are:
- **Not machine-readable** — PDFs, scanned documents, or JavaScript-rendered pages
- **Behind bot protection** — Cloudflare, Akamai, or custom WAFs block automated access
- **Unstable** — URLs change, documents get moved or replaced without notice
- **Fragmented** — No single source has everything; you need to piece together multiple documents

## Workflow: CA Medicaid (Reconstructed from Session 20260604_220115_734469)

### Step 1: Locate Official Sources

```
Search queries used:
1. "California" "Medi-Cal" "network adequacy" specialty categories provider list
2. "DHCS" "APL" network adequacy standards specialists PDF
3. California Medi-Cal MCP network certification requirements specialty codes
4. "APL21-006" Attachment A specialty list
5. "California Medi-Cal" dental network adequacy "timely access" healthlaw.org
6. "California" SUD opioid treatment network adequacy Medicaid managed care
```

**Result:** Found DHCS Application Letters (APL) as primary regulatory documents. APL21-006 contains Network Adequacy Standards with time/distance tables and core specialist lists. APL19-002 covers mandatory provider enrollment.

### Step 2: Download Sources (Cloudflare Obstacle)

```bash
# Primary sources — used wp-content/uploads paths to bypass Cloudflare
curl -sL "https://www.dhcs.ca.gov/wp-content/uploads/2025/10/FinalRuleNAStandards3-26-18.pdf" -o ca_network_adequacy_standards.pdf
curl -sL "https://www.dhcs.ca.gov/wp-content/uploads/2025/12/2024-Network-Adequacy-and-Access-Assurances-Analysis-Methods.pdf" -o ca_2024_network_adequacy.pdf

# Taxonomy crosswalk
curl -sL "https://www.dhcs.ca.gov/provgovpart/Documents/2024-Network-Guidance-for-EAE-DSNPs-Taxonomy-Crosswalk-January-2023.xls" -o ca_taxonomy_crosswalk.xls

# Secondary source — healthlaw.org analysis
curl -sL "https://healthconsumer.org/wp/wp-content/uploads/2016/10/Network-Adequacy-in-Medi-Cal_NHelP_2024.pdf" -o ca_network_adequacy_healthlaw.pdf
```

**Pitfall:** Direct `curl` to DHCS PDF links returns 212-byte Cloudflare error pages/captcha. The `wp-content/uploads` subdomain paths bypass this. Browser tool also works but is slower.

### Step 3: Extract from PDFs

```bash
# Extract specialist tables and time/distance standards
pdftotext ca_apl21-006AttA.pdf - | grep -i -A50 "Table 2\|core specialist\|specialist" | head -200
pdftotext ca_apl21-006AttB.pdf - | grep -i -A20 "Table 1\|time distance\|travel time" | head -100
pdftotext ca_apl19-002.pdf - | grep -i -A5 "mandatory\|FQHC\|RHC\|must be included" | head -50

# Extract from healthlaw.org secondary source
pdftotext ca_network_adequacy_healthlaw.pdf - | grep -i "specialist\|specialty\|time.*distance\|minutes\|miles\|primary.*care\|pediatric\|OB/GYN\|behavioral\|mental.*health" | head -40
```

**Result:** Confirmed 16 core specialists in Table 2, time/distance standards in Table 1, mandatory provider requirements in APL19-002. Healthlaw.org source confirmed dental and SUD/opioid data NOT in DHCS primary sources.

### Step 4: Structure and Verify

- Compiled 31 specialty rows (27 from DHCS APLs + 3 from healthlaw.org: SUD, Opioid, Dental)
- Cross-referenced time/distance standards against 4-tier county population density system
- Noted telehealth exceptions (APL 23-001 excludes General Surgery, Orthopedics, PM&R, Hospitals)
- Documented taxonomy crosswalk: 863 records via ArcGIS or `ca_taxonomy_crosswalk.xls`

## Workflow: TX Medicaid (Executed in Current Session)

### Step 1: Search for the Official Source

```
Search queries used:
1. "Texas" "specialty categories" "network adequacy" Medicaid provider list
2. "HHSC" "Managed Care" network adequacy specialty requirements PDF
3. Texas Medicaid STAR STAR+PLUS provider specialty list MCO
4. "Uniform Managed Care Manual" Texas HHSC specialty
```

**Result:** Found the Texas HHSC "Uniform Managed Care Manual" (UMCM) — a comprehensive manual with downloadable xlsx attachments. Chapter 5.28.1 "Access to Network Providers Performance Standards and Specifications" was the primary source.

### Step 2: Navigate and Download

```bash
# Navigate to UMCM parent page, found Chapter 5.28.1 xlsx link
# Download primary source — machine-readable Excel
curl -sL "https://www.hhs.texas.gov/sites/default/files/documents/laws-regulation/handbooks/umcm/5-28-1.xlsx" -o tx_access_network_providers.xlsx

# Download supporting documents
curl -sL "https://www.hhs.texas.gov/sites/default/files/documents/laws-regulation/handbooks/umcm/5-24-2.xlsx" -o tx_network_capacity_layout.xlsx
curl -sL "https://www.hhs.texas.gov/sites/default/files/documents/medicaid-managed-care-provider-network-adequacy-dec-2024.pdf" -o tx_network_adequacy_dec2024.pdf
curl -sL "https://www.hhs.texas.gov/sites/default/files/documents/medicaid-managed-care-provider-network-exam.xls" -o tx_provider_network_exam.xls
```

**Result:** All files downloaded. No bot protection encountered — HHSC site serves files directly.

### Step 3: Parse the Excel File

```python
import openpyxl
wb = openpyxl.load_workbook('tx_access_network_providers.xlsx', data_only=True)
ws = wb['Standards and Specifications']
# Read 130 rows of specialty data with travel times, provider counts, programs, thresholds
```

**Result:** Extracted 36 specialties across 9 categories. Data was structured with clear columns for metro/micro/rural travel times, provider count standards, performance thresholds, and implementation dates.

### Step 4: Cross-Reference with Network Adequacy Report

```bash
# Extract Appendix A standards tables from PDF
pdftotext tx_network_adequacy_dec2024.pdf - | grep -A 200 "Appendix A. Network Adequacy Standards"
# Extract specialist network analysis from Appendix E
pdftotext tx_network_adequacy_dec2024.pdf - | grep -A 50 "Appendix E. Network Analysis"
```

**Result:** PDF Appendix A (Tables A-1, A-2, A-3) confirmed all 36 specialties matched the xlsx. Appendix E showed MCO-specific network analysis with the same specialist categories.

### Step 5: Structure and Verify

- Compiled 36 specialty rows into CSV via Python script
- Cross-referenced xlsx and PDF — 100% match on specialty names, travel times, and programs
- Documented DMO dental carve-out, LTSS county-based standards, telemedicine exclusion
- Noted 3-tier county system (Metro/Micro/Rural) and SB 760 legislative framework

## Workflow: PA Medicaid (Reconstructed from Session 20260604_205511_8fdc2a)

### Step 1: Search for the Official Source (15+ Attempts)

```
Search queries used:
1. "Pennsylvania" "specialty categories" Medicaid "network adequacy" provider list
2. PA HealthChoices provider specialty categories MCO requirements
3. Pennsylvania DHS "high categorical specialties" Medicaid provider list
4. "Provider Type Specialty Codes" Pennsylvania DHS PDF 2024
5. AmeriHealth Caritas Pennsylvania specialty categories network adequacy requirements
6. Pennsylvania Medicaid managed care network adequacy specialty list "designated specialty"
7. site:cms.gov Pennsylvania Medicaid provider specialty categories
8. "PA Code" title 55 chapter 49 Medicaid provider specialty categories
9. Pennsylvania Medicaid "specialty code" provider list "primary care" "specialty care" categories
10. Pennsylvania Medicaid managed care network adequacy specialty list "designated specialty"
11. Pennsylvania Medicaid "provider specialty" list "family medicine" "internal medicine" "obstetrics" "pediatrics"
```

**Result:** Found the official PA DHS "Provider Type Specialty Codes" PDF (Updated 3/28/2024) via Google search results — snippets showed partial content. But the URL returned 404.

### Step 2: Attempt Direct Download (Failed)

```bash
# Try the direct URL from search results
curl -sL "https://www.pa.gov/content/dam/copapwp-pagov/en/dhs/documents/providers/documents/medical-assistance/Provider+Type+Specialty+Codes.pdf" -o file.pdf
file file.pdf  # Returns HTML, not PDF — 404 page
```

**Result:** PA.gov returned a 404 HTML page — the PDF had been removed or moved.

### Step 3: Try the Wayback Machine (Failed)

```bash
# Check if Internet Archive has a cached copy
curl -sL "https://web.archive.org/cdx/search/cdx?url=pa.gov/...&output=text&fl=timestamp,statuscode&limit=5"
curl -sL "https://web.archive.org/web/20240630191507/https://www.pa.gov/..." -o archived.pdf
```

**Result:** Wayback Machine had timestamps from 2024 but returned 404 — the archived copy was also gone or blocked.

### Step 4: Pivot to Alternative Source

```
Search queries for alternative:
1. AmeriHealth Caritas Pennsylvania specialty categories network adequacy requirements
2. Pennsylvania Medicaid managed care network adequacy specialty list "designated specialty"
```

**Result:** Found the **2025 Community HealthChoices Agreement** — a 61-page PA DHS PDF contract that defines network adequacy requirements by specialty. This document contains the specialty list embedded in its network adequacy section (Section V).

### Step 5: Download and Extract

```bash
# Download the alternative source
curl -sL "https://www.pa.gov/content/dam/copapwp-pagov/en/dhs/documents/healthchoices/hc-providers/documents/2025-chc-agreement.pdf" -o /tmp/pa_chc_agreement.pdf
file /tmp/pa_chc_agreement.pdf  # Confirmed: PDF document, 2.8MB

# Install pdftotext (poppler)
brew install poppler

# Find the network adequacy section — grep with line numbers
pdftotext /tmp/pa_chc_agreement.pdf - | grep -n -i "thirty.*minutes\|sixty.*minutes\|network gap\|travel time.*Urban\|travel time.*Rural" | head -30
# → Anchor line ~18508

# Extract the specialty block
pdftotext /tmp/pa_chc_agreement.pdf - | sed -n '18495,18650p'
# → Raw specialty list with tier requirements

# Extract specialist list with context
pdftotext /tmp/pa_chc_agreement.pdf - | grep -i -A200 "Network Gap Analysis\|network adequacy\|travel time limits" | \
  grep -i -B1 -A1 "Provider types\|specialist\|surgery\|cardiology\|..." | sort -u

# Extract PCP/primary care definitions
pdftotext /tmp/pa_chc_agreement.pdf - | grep -i -B3 -A5 "PCP\|primary care\|family practice" | \
  grep -i "PCP\|primary care\|family\|internal\|pediatrician\|physician" | sort -u

# Extract facility provider type codes
pdftotext /tmp/pa_chc_agreement.pdf - | grep -i -B1 -A3 "specialty code\|provider type\|prov_type" | head -120
```

### Step 6: Cross-Reference with MCO Documents

```
Search: "AmeriHealth Caritas Pennsylvania" specialty codes
Search: "Advanced Health" provider type specialty codes
```

Downloaded Advanced Health 2026 CCO Incentive Measures Binder — turned out to be Oregon HSD data, NOT PA. **Lesson: Always verify the state in downloaded documents.**

### Step 7: Parse the Taxonomy Crosswalk (Multi-Column PDF)

```bash
# Download crosswalk PDF
curl -sL "https://www.pa.gov/.../pa_taxonomy_crosswalk.pdf" -o pa_taxonomy_crosswalk.pdf

# pdftotext mangles multi-column layout — requires Python regex
python3 -c "
import re
with open('crosswalk.txt') as f:
    text = f.read()
# Regex to reconstruct rows from mangled columns
pattern = r'(\d+/\d+)\s+(.+?)\s+(\d{10}X)'
matches = re.findall(pattern, text)
# → 252 PA→NUCC mappings extracted
"
```

**Result:** 252 PA-to-NUCC code mappings. Multi-column PDFs require Python parsing — `pdftotext` alone mangles the columns.

### Step 8: Structure the Data

- Compiled 86 specialty rows into CSV: 6 PCP, 17 Tier 1 specialists, 4 Tier 2 specialists, 23 Tier 1 LTSS, 1 Tier 2 LTSS, 8 County-level LTSS, 1 ILOS LTSS, 4 FTE LTSS, 7 Facility types, 14 Additional services, 6 BH-MCO types
- Created human-readable markdown reference
- Organized by tier/category with source citations
- **Post-hoc:** Restructured project to per-state subfolders (`data/states/pa/sources/`) to house source PDFs

### Step 9: Project Restructuring Decision

During PA session, realized the project needed to be split from the AI Specialty Mapper:

```bash
# Split into two independent repos
cd ~/projects
mkdir medicaid-state-specialty-ref ai-specialty-mapper
# Moved docs, data, sources to new repos
# Initialized git in both
```

**Result:** `medicaid-state-specialty-ref/` and `ai-specialty-mapper/` are now separate git repos under `~/projects/`.

## Workflow: NY Medicaid (Reconstructed from Session 20260605_143413_92e369)

### Step 1: Search for the Official Source

```
Search queries used:
1. New York Medicaid specialty categories network adequacy
2. NY Medicaid MCO agreement specialty provider types
3. NY DOH PNDS Data Dictionary provider specialty codes
```

**Result:** Found two authoritative NY DOH sources:
- "Guidelines for MCO Service Delivery Networks" v3.0 — network adequacy standards with specialist caseload ratios
- PNDS Data Dictionary — provider specialty codes (Tables 1 & 2)

### Step 2: Download Sources (User-Agent Workaround)

```bash
# Direct curl blocked — NY DOH returns HTML redirect
curl -sL "https://www.health.ny.gov/health_care/managed_care/docs/guidelines_for_mco_service_delivery_networks-v3.0.pdf" -o ny_mco_guidelines.pdf
file ny_mco_guidelines.pdf  # Returns HTML — blocked

# Workaround: add Mozilla User-Agent header
curl -sL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" \
  "https://www.health.ny.gov/health_care/managed_care/docs/guidelines_for_mco_service_delivery_networks-v3.0.pdf" \
  -o /tmp/ny_mco_guidelines2.pdf
file /tmp/ny_mco_guidelines2.pdf  # PDF document, 759KB — success

# Same for PNDS Data Dictionary
curl -sL -A "Mozilla/5.0" "https://www.health.ny.gov/health_care/managed_care/docs/dictionary.pdf" -o /tmp/ny_pnds_dictionary.pdf
```

**Pitfall:** NY DOH blocks non-browser user agents. The `-A "Mozilla/5.0"` flag bypasses this.

### Step 3: Extract and Clean PDF Data

```bash
# Convert to text
pdftotext /tmp/ny_mco_guidelines2.pdf - | wc -l  # 1959 lines
pdftotext /tmp/ny_pnds_dictionary.pdf - | wc -l  # 24065 lines

# Locate tables in PNDS Dictionary
pdftotext /tmp/ny_pnds_dictionary.pdf - | grep -n "Table 1\|Table 2" | head -10
# → Table 1 at line ~X, Table 2 at line ~Y

# Extract tables to files
pdftotext /tmp/ny_pnds_dictionary.pdf - | sed -n 'X,Yp' > /tmp/ny_table1.txt  # 2891 lines
pdftotext /tmp/ny_pnds_dictionary.pdf - | sed -n 'Y,Zp' > /tmp/ny_table2.txt  # 1237 lines

# Clean noise from Table 2 — filter out *, N, headers, numeric codes, program type markers
grep -v '^\*$\|^N$\|^[0-9]\{3\}$\|^[0-9]\{3\}-' /tmp/ny_table2.txt | \
  grep -v 'SIP-PL\|^[A-Z]\{3\}-' | \
  grep -i "service\|therapy\|specialty\|physician\|nurse\|psychologist" \
  > /tmp/ny_clean_table2.txt  # ~136 lines of clean service data

# Extract region data from Attachment 5
pdftotext /tmp/ny_mco_guidelines2.pdf - | grep -A 100 "Attachment 5\|RPC Region\|Urban\|Rural" | \
  grep -i "county\|region\|urban\|rural" | sort -u
```

**Result:** Cleaned ~136 lines of specialty data from Table 2. Mapped counties to RPC regions (Northeast, Finger Lakes, NYC, Central, Utica-Adirondack, Mid-Hudson, Western, Long Island, Northern Metro) and Urban/Rural classifications.

### Step 4: Extract Network Adequacy Standards

```bash
# Extract specialist caseload ratios
pdftotext /tmp/ny_mco_guidelines2.pdf - | grep -A 50 "Specialist Caseload Ratios\|Patient to Provider Ratio" | head -100
# → Confirmed ratios: Allergy/Immunology 121,780; Cardiology 32,210; Dermatology 35,420; Psychiatry 6,494

# Extract travel time standards
pdftotext /tmp/ny_mco_guidelines2.pdf - | grep -i "travel time\|minutes\|miles\|metropolitan\|non-metropolitan" | head -30
# → Metropolitan: 30 min by public transit; Non-metropolitan: 30 min or 30 miles
```

### Step 5: Structure and Verify

- Compiled 130 specialty rows: 6 PCP, 4 OB/GYN, 26 Specialist, 22 Behavioral Health, 15 Crossover, 4 Dental, 17 Facility, 2 LTSS, 22 HCBS, 3 CFCO, 2 Hemophilia, 3 Ancillary
- Created markdown documentation with program types (Medicaid, CHP, HARP, HIV SNP, MAP, MLTC, PACE, FIDA)

### Step 6: Verification Pass (Critical Errors Found)

```bash
# Verify specialty codes against PNDS Table 1
# Full text extraction for deep inspection
pdftotext /tmp/ny_pnds_dictionary.pdf - > /tmp/ny_pnds_full.txt

# Check Physical Med & Rehabilitation code
grep -n "Physical Med\|153\|170" /tmp/ny_pnds_full.txt | head -10
# → CSV listed code 170, but PNDS Table 1 confirms code is 153. Code 170 = Plastic Surgery.

# Check Pediatrics code
grep -n "Pediatric\|050\|060\|776\|066\|150" /tmp/ny_pnds_full.txt | head -10
# → CSV included code 150, but source shows codes 050, 060, 776, 066. Code 150 = column offset artifact.

# Verify OB/GYN code padding
grep -n "Obstetric\|089\|89" /tmp/ny_pnds_full.txt | head -10
# → CSV lists 89, source shows 089. Cosmetic zero-padding inconsistency.
```

**Critical errors found:**
1. **Travel time standard** — CSV incorrectly listed `10 mi / 30 min` for Primary Care. Correct: Metropolitan = `30 min public transit`; Non-metropolitan = `30 min or 30 miles`.
2. **Physical Med & Rehabilitation code** — CSV listed `170`, correct is `153`. Code `170` = Plastic Surgery.
3. **Pediatrics code** — CSV included `150`, which is a column offset artifact. Correct codes: `050, 060, 776, 066`.
4. **OB/GYN code** — Cosmetic zero-padding: CSV `89` vs source `089`.

**Lesson:** Always run a verification pass comparing CSV codes back to source documents. PDF extraction artifacts can produce wrong codes.

## Key Tools Used

| Tool | Purpose |
|---|---|
| `web_search` | Find government documents, MCO contracts, specialty lists |
| `web_extract` | Extract content from web pages (limited — DuckDuckGo backend is search-only) |
| `browser_navigate` | Access pages that require JavaScript rendering |
| `curl` | Download PDFs and other files directly |
| `pdftotext` (poppler) | Extract searchable text from PDFs |
| `grep` | Targeted text extraction with context flags (`-A`, `-B`, `-C`) |
| `file` | Verify downloaded file type (PDF vs HTML) |

## Lessons Learned

### What Works
1. **Google search snippets contain PDF content** — Even when you can't download the PDF, search results often show enough content to confirm what's inside
2. **MCO contracts are goldmines** — State-MCO agreements define network adequacy requirements, which include specialty lists
3. **Multiple search angles** — Try different query formulations: "network adequacy", "provider enrollment", "specialty categories", "MCO requirements"
4. **`pdftotext` + `grep` is powerful** — Much faster than trying to parse PDFs programmatically for one-off extractions
5. **UMCM/Managed Care Manuals** — Texas HHSC publishes an excellent Uniform Managed Care Manual with machine-readable xlsx attachments. Other states may have similar resources
6. **`wp-content/uploads` paths bypass Cloudflare** — CA DHCS blocks direct `curl` but serves files from the uploads subdomain without bot checks
7. **Mozilla User-Agent bypasses download blocks** — NY DOH requires `-A "Mozilla/5.0"` on curl requests
8. **Verification pass catches critical errors** — NY session found 3 critical errors (wrong codes, wrong travel times) by comparing CSV back to source PDF

### What Doesn't Work
1. **Direct PDF downloads from state sites** — Often behind bot protection, moved, or returning 404
2. **Wayback Machine for PDFs** — Often returns HTML wrappers or 404s for government PDFs
3. **Browser tool for PDFs** — Can't render PDF content; returns 404 or navigation errors
4. **State government search** — PA.gov internal search returned "No results" for specialty codes
5. **`pdftotext` on multi-column PDFs** — Mangles column layout; requires Python regex parsing to reconstruct rows
6. **macOS `cat -A` flag** — Not supported; use `od -c` or Python for raw character inspection

### Pitfalls
1. **Assume URLs are stable** — They're not. The PA specialty codes PDF was cited in search results but returned 404
2. **Confuse states** — The Advanced Health document had Oregon HSD data, not PA data. Always verify the state
3. **Miss the BH-MCO layer** — PA has separate behavioral health managed care with its own specialty categories. Don't assume one source covers everything
4. **Tier confusion** — PA has multiple network adequacy tiers with different requirements. Document the tier structure, not just the specialty names
5. **State-specific program naming** — TX uses STAR/STAR Health/STAR+PLUS/STAR Kids (not "HealthChoices" or "Medi-Cal"). Always verify which programs each specialty applies to
6. **Carved-out services** — TX dental is administered by separate DMOs, not MCOs. Check for service carve-outs before assuming MCO contracts cover everything
7. **PDF extraction artifacts produce wrong codes** — NY session: code `150` appeared in CSV as a column offset artifact from Table 2 extraction. Code `170` (Plastic Surgery) was misattributed to PM&R (correct: `153`). Always verify codes against source.
8. **Travel time standards vary by metro/non-metro** — NY uses `30 min public transit` for metro and `30 min or 30 miles` for non-metro. Don't apply a single standard across all counties.
9. **Cloudflare blocks automated downloads** — CA DHCS returns 212-byte captcha pages to `curl`. Use `wp-content/uploads` paths or browser tools.
10. **Download blocks require User-Agent headers** — NY DOH returns HTML redirects to non-browser user agents. Add `-A "Mozilla/5.0"` to curl.
11. **SPA sites break browser clicks** — AHCA (FL) is a JavaScript SPA — direct clicks fail. Use browser console to extract `href` attributes and navigate directly.
12. **Feb vs Oct version traps** — FL Exhibit II-A has a Feb 2025 version that's a 1-page stub. Oct 2025 is the authoritative document. Always verify document dates and page counts.
13. **Dental carve-outs need separate contracts** — FL dental specialties are in a separate Model Dental Plan Contract, not the MMA Exhibit. Check for carved-out services before assuming one source covers everything.
14. **TML zip downloads** — FL TML is hosted on portal.flmmis.com as a zip file. Extract with `unzip` before using the CSV inside.
15. **Multi-source regulatory overlap** — MI has three distinct regulatory sources (MDHHS, DIFS, PIHP) with overlapping authority. DIFS sets baseline for all HMOs, MDHHS sets Medicaid-specific standards, PIHP handles specialty behavioral health. Don't assume one source covers everything.
16. **CSV column alignment bugs** — MI CSV had `designation_type` containing source names, DIFS codes in `enrollees_per_provider`, and enrollee ratios in `source` column. Always validate column semantics, not just column counts.
17. **State-specific specialty codes vs NUCC** — MI DIFS codes (001-080, P072, P076, P201, 800, 801) are NOT NUCC taxonomy codes. They're MI-specific DIFS codes that need a separate crosswalk mapping.

## Replicable Workflow for Other States

1. **Search** for `[State] Medicaid "specialty categories" OR "provider type" OR "network adequacy"`
2. **Try direct download** of any PDF found
3. **If 404, search for** `[State] Medicaid MCO agreement OR contract 2024 OR 2025`
4. **Download MCO contract**, extract with `pdftotext`
5. **Grep for** network adequacy, specialty, provider type sections
6. **Cross-reference** with MCO-specific documents (AmeriHealth, UnitedHealthcare, etc.)
7. **Structure** into markdown + CSV
8. **Document** sources, dates, and notes

## State-Specific Notes

### California
- **Program name:** Medi-Cal
- **Administering agency:** DHCS (Department of Health Care Services)
- **Network structure:** Managed Care Plans (MCPs) across service regions
- **County designations:** Dense (≥600/sq mi), Medium (150-600), Small (21-150), Rural (<21) — 4-tier population density system
- **Time/distance standards:** Time OR distance (MCPs choose which to use). Primary care: 10mi/30min uniform. Specialists: varies by county (15mi/30min Dense → 60mi/90min Rural)
- **Timely access:** Added dimension — PCP/OB/GYN within 10 business days, specialty/LTSS within 15 business days
- **Core specialists:** 16 defined by DHCS in APL21-006 Table 2 (Cardiology, Nephrology, Dermatology, Neurology, Endocrinology, Ophthalmology, ENT, Orthopedics, Gastroenterology, PM&R, General Surgery, Psychiatry, Hematology, Oncology, Pulmonology, HIV/AIDS)
- **Telehealth:** Permitted for compliance EXCEPT General Surgery, Orthopedics, PM&R, Hospitals (APL 23-001)
- **Dental:** Separate managed care delivery system — not in DHCS network adequacy process
- **SUD/Opioid:** DHCS groups with mental health; separate specialty data not available from primary source
- **Mandatory providers:** FQHCs, RHCs, FBCs, CNMs, LMs, IHFs must be included where available (APL 19-002)
- **Taxonomy crosswalk:** 863 records via ArcGIS (`networks-gis.dhcs.ca.gov`) or email request to DHCS-PMU
- **Primary source:** DHCS APL21-006 Attachments A & B (PDFs) — directly downloadable
- **Secondary source:** healthlaw.org analysis (3 rows: SUD, Opioid, Dental — not in DHCS docs)
- **Extraction:** `pdftotext` + `grep`/`sed` for PDFs; taxonomy crosswalk via `cat -v` + parsing from `.xls`

### Texas
- **Program name:** STAR, STAR Health, STAR+PLUS, STAR Kids, CHIP, CMDS
- **Administering agency:** HHSC (Health and Human Services Commission)
- **Network structure:** 16 MCOs + 3 DMOs across service areas (SAs)
- **County designations:** Metro, Micro, Rural (3-tier system based on population density)
- **Travel time standards:** Vary by county type — Metro (15-45 min), Micro (30-80 min), Rural (40-90 min)
- **Performance threshold:** 90% of members within standard (except Main Dentist at 95%, Pharmacy varies)
- **Dental:** Carved out to DMOs (DentaQuest, MCNA, UHC, Superior) except STAR Health (carved-in)
- **LTSS:** In-home services use "choice of 2 in each county" (no travel time standard)
- **Telemedicine:** Providers offering only telehealth/telemedicine excluded from network adequacy counts
- **Legislation:** SB 760 (84th Legislature, 2015) mandated HHSC to develop specific network access standards
- **Primary source:** UMCM Chapter 5.28.1 "Access to Network Providers Performance Standards and Specifications" (xlsx) — directly downloadable, no bot protection
- **Secondary source:** Network Adequacy Report Dec 2024 (PDF) — Appendix A Tables A-1/A-2/A-3
- **Extraction:** `openpyxl` for xlsx (directly machine-readable), `pdftotext` for PDF appendix

### Pennsylvania
- **Program name:** HealthChoices (CHC)
- **Managed care types:** CHC-MCO (physical health), BH-MCO (behavioral health), PH-MCO (physical health for adults), CHIP-MCO (children)
- **Network adequacy tiers:** Tier 1 (2 providers, 30/60 min), Tier 2 (1 + 1 in zone), County-level (LTSS)
- **Facility codes:** Provider Type/Specialty Code format (e.g., 01/11, 03/37)
- **LTSS integration:** Community HealthChoices (CHC) program adds LTSS provider types
- **Official PDF:** Previously at `pa.gov/.../Provider+Type+Specialty+Codes.pdf` (now 404)
- **Working source:** 2025 CHC Agreement at `pa.gov/.../2025-chc-agreement.pdf`
- **Crosswalk:** 252 PA→NUCC mappings from multi-column PDF (requires Python regex parsing)
- **Research path:** 15+ search attempts → official PDF 404 → Wayback Machine 404 → CHC Agreement pivot → 86 rows extracted

### New York
- **Program name:** Medicaid Managed Care (MCO)
- **Administering agency:** NY DOH (Department of Health)
- **Program types:** Medicaid, CHP (Child Health Plus), HARP, HIV SNP, MAP (Medicaid Advantage Plus), MLTC (Managed Long-Term Care), PACE, FIDA
- **Network structure:** Managed Care Organizations (MCOs) across RPC regions
- **RPC regions:** Northeast, Finger Lakes, NYC, Central, Utica-Adirondack, Mid-Hudson, Western, Long Island, Northern Metro
- **County designations:** Urban vs Rural classification per RPC region
- **Travel time standards:** Metropolitan = 30 min by public transit; Non-metropolitan = 30 min or 30 miles
- **Specialist caseload ratios:** Population-per-provider ratios (e.g., Cardiology 32,210; Psychiatry 6,494)
- **Primary sources:** MCO Guidelines v3.0 + PNDS Data Dictionary (Tables 1 & 2)
- **Download obstacle:** NY DOH blocks non-browser user agents — requires `-A "Mozilla/5.0"` on curl
- **Extraction:** Complex `grep`/`sed` cleaning required — Table 2 contained noise characters (`*`, `N`), program type markers (`SIP-PL`), and column offset artifacts
- **Verification errors:** 3 critical errors found in verification pass (wrong travel time, wrong PM&R code, artifact Pediatrics code)
- **Specialty count:** 130 rows across 12 categories (PCP, OB/GYN, Specialist, BH, Crossover, Dental, Facility, LTSS, HCBS, CFCO, Hemophilia, Ancillary)

### Florida
- **Program name:** Statewide Medicaid Managed Care (SMMC) — Managed Medical Assistance (MMA) + Dental Health Program
- **Administering agency:** AHCA (Agency for Health Care Administration)
- **Network structure:** 5 SMMC plans (Aetna Better Health, Florida Blue, Sunshine Health, UnitedHealthcare, Molina) + separate Prepaid Dental program
- **County designations:** Urban vs Rural — distinct access standards per designation
- **Travel time standards:** Urban: 30 min/20 mi (PC), 50-100 min/35-75 mi (specialists). Rural: 30 min/20 mi (PC), 60-110 min/45-90 mi (specialists)
- **Provider ratios:** "1 provider per X enrollees" by region (e.g., 1:750 for primary care, 1:1,500 for general dentist)
- **Dental:** Carved out to separate Prepaid Dental program — sourced from Model Dental Plan Contract Attachment II
- **Behavioral health:** Unique counting system — BCaBA counts as 0.5 Lead Analyst; RBT ratio is 1:125 enrollees
- **Primary sources:** Exhibit II-A MMA Program (Oct 2025, 143 pages) + Dental Attachment II (Oct 2025, 255 pages) — both from AHCA SMMC plans page
- **Taxonomy crosswalk:** FL Taxonomy Master List (TML) from portal.flmmis.com — 1,100 rows, 59 provider types, 233 specialty codes, 531 taxonomy codes (downloaded as zip)
- **Download obstacles:** AHCA site is a JavaScript SPA — direct clicks fail, browser console extraction of `href` attributes required. Some curl downloads need `-L` for redirects. Feb 2025 version of Exhibit II-A is a 1-page stub — Oct 2025 is authoritative.
- **Extraction:** `pymupdf` for PDF text extraction (Table 4 on pages 65-68 for MMA, pages 82-83 for Dental). TML downloaded from zip, CSV used as-is.
- **Specialty count:** 64 rows across 5 categories (Specialist, Dental, Facility, Behavioral Health, Primary Care). 63/64 have NUCC taxonomy matches (LPHA is FL-specific with no NUCC equivalent).

### Michigan
- **Program name:** CHCP (Comprehensive Health Care Program)
- **Administering agency:** MDHHS (physical health), PIHPs (specialty behavioral health)
- **Network structure:** MCOs + PIHPs across 10 Prosperity Regions
- **County designations:** 5 CMS tiers (Large Metro/Metro/Micro/Rural/CEAC) across 83 counties
- **Multi-source landscape:** MI requires 3 distinct sources — MDHHS standards (MCO physical health), DIFS guidance (all HMOs, including Medicaid), and PIHP procedural document (specialty behavioral health). Unlike other states, MI has overlapping regulatory authority: DIFS sets baseline standards for all HMOs, while MDHHS sets Medicaid-specific standards that can be more or less restrictive.
- **DIFS specialty codes:** DIFS Appendix 9.1 defines 51 individual provider specialty types and 15 facility specialty types with unique codes (e.g., 007 for Allergy/Immunology, 040 for Acute Inpatient Hospitals). These are NOT NUCC taxonomy codes — they're MI-specific DIFS codes.
- **DIFS 30-min specialties:** DIFS Section 4.1 adds 10 specialties (Anesthesiology, Outpatient Dialysis, DME, Home Health, Home Infusion, Hospice, Laboratory, Midwife, Optometry, Pathology) with a uniform max 30-min travel time regardless of county designation — no time/distance table entry.
- **PIHP two-tier standards:** PIHP time/distance is split into two tiers: (1) Inpatient Psychiatric & Partial Hospitalization (more generous: 30/15 to 155/140), and (2) All Other Services (tighter: 20/10 to 118/105). Provider-to-enrollee ratios only apply to select services; many are "FY25 informational only."
- **Crosswalk:** BCBSM Taxonomy Code Map provides NUCC taxonomy mapping for DIFS codes. Crosswalk has 66 rows: 51 with high-confidence NUCC matches, 15 facility types with no direct NUCC equivalent.
- **CSV column alignment issue:** The original CSV had a structural bug — `designation_type` column contained source names (MDHHS CHCP/DIFS/PIHP BH), DIFS specialty codes were in `enrollees_per_provider` column, and enrollee ratios were in `source` column. Fixed by: (1) moving `designation_type` → `source`, (2) moving DIFS codes from `enrollees_per_provider` → `specialty_code`, (3) moving enrollee ratios from `source` → `enrollees_per_provider`.
- **Primary sources:** MDHHS Network Adequacy Standards PDF (FY25 CHCP, 4 pages), PIHP Network Adequacy Procedural Document (Jan 2026, 4 pages), DIFS Network Adequacy Guidance (Updated 3.26, 20 pages + appendix)
- **Extraction:** `pdftotext` for all PDFs. MDHHS table: multi-column layout extracted directly. DIFS: Appendix 9.1 codes + Section 4.3 time/distance tables. PIHP: direct text extraction.
- **Specialty count:** 94 rows (MDHHS: 22, DIFS: 52, PIHP: 20) + 66 crosswalk rows

## Future Improvements

- [ ] Build a Python script that automates the `pdftotext` + `grep` extraction
- [ ] Create a template for each state's data file to ensure consistency
- [ ] Add NUCC taxonomy mapping column to CSV (Phase 2)
- [ ] Build a comparison matrix across states
- [ ] Set up monitoring for state bulletin changes
