# State Medicaid Specialty Data Collection: Research Methodology

**Created:** 2026-06-04  
**Last Updated:** 2026-06-04  
**Author:** Tensor (AI assistant)

## Overview

This document describes the workflow used to extract PA Medicaid provider specialty categories from government sources. The same methodology applies to other states.

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

## Workflow: PA Medicaid Example

### Step 1: Search for the Official Source

Start with targeted web searches to find the authoritative specialty codes document:

```
Search queries used:
1. "Pennsylvania" "specialty categories" Medicaid "network adequacy" provider list
2. PA HealthChoices provider specialty categories MCO requirements
3. Pennsylvania DHS "high categorical specialties" Medicaid provider list
4. "Provider Type Specialty Codes" Pennsylvania DHS PDF 2024
```

**Result:** Found the official PA DHS "Provider Type Specialty Codes" PDF (Updated 3/28/2024) via Google search results. The search snippets even showed partial content from the PDF.

### Step 2: Attempt Direct Download

```bash
# Try the direct URL from search results
curl -sL "https://www.pa.gov/.../Provider+Type+Specialty+Codes.pdf" -o file.pdf
file file.pdf  # Check what we got
```

**Result:** PA.gov returned a 404 HTML page — the PDF had been removed or moved.

### Step 3: Try the Wayback Machine

```bash
# Check if Internet Archive has a cached copy
curl -sL "https://web.archive.org/cdx/search/cdx?url=...&output=text&fl=timestamp,statuscode&limit=5"
```

**Result:** Wayback Machine had timestamps from 2024 but returned 404 — the archived copy was also gone or blocked.

### Step 4: Pivot to Alternative Source

When the primary source fails, find documents that **reference** the data:

```
Search queries:
1. AmeriHealth Caritas Pennsylvania specialty categories network adequacy requirements
2. Pennsylvania Medicaid managed care network adequacy specialty list "designated specialty"
```

**Result:** Found the **2025 Community HealthChoices Agreement** — a 61-page PA DHS PDF contract that defines network adequacy requirements by specialty. This document contains the specialty list embedded in its network adequacy section.

### Step 5: Download and Extract

```bash
# Download the alternative source
curl -sL "https://www.pa.gov/.../2025-chc-agreement.pdf" -o /tmp/pa_chc_agreement.pdf
file /tmp/pa_chc_agreement.pdf  # Confirmed: PDF document, 2.8MB

# Extract text (requires poppler/pdftotext)
brew install poppler
pdftotext /tmp/pa_chc_agreement.pdf - | grep -i "specialty\|provider type" | head -100
```

### Step 6: Targeted Extraction

Use `grep` with context flags to find the relevant sections:

```bash
# Find the network adequacy specialty list
pdftotext file.pdf - | grep -i -A200 "Network Gap Analysis\|network adequacy\|travel time limits" | \
  grep -i -B1 -A1 "Provider types\|specialist\|surgery\|cardiology\|..." | sort -u

# Find PCP/primary care definitions
pdftotext file.pdf - | grep -i -B3 -A5 "PCP\|primary care\|family practice" | \
  grep -i "PCP\|primary care\|family\|internal\|pediatrician\|physician" | sort -u

# Find facility provider type codes
pdftotext file.pdf - | grep -i -B1 -A3 "specialty code\|provider type\|prov_type" | head -120
```

### Step 7: Cross-Reference with Additional Sources

Search for MCO-specific documents that may have more detail:

```
Search: "AmeriHealth Caritas Pennsylvania" specialty codes
Search: "Advanced Health" provider type specialty codes
```

**Result:** Found Advanced Health 2026 CCO Incentive Measures Binder with provider type/specialty code tables (though this was Oregon HSD data, not PA-specific).

### Step 8: Structure the Data

Compile findings into two formats:

**Markdown reference** (`pa_medicaid_specialties.md`):
- Human-readable documentation
- Organized by tier/category
- Includes source citations and notes
- Facility provider type codes in table format

**CSV data file** (`pa_medicaid_specialties.csv`):
- Machine-readable, one row per specialty
- Columns: `tier, category, specialty, provider_count_requirement, travel_time_requirement`
- Ready for programmatic use (mapping, comparison, API)

### Step 9: Document the Process

Update project research notes with:
- What was found
- What sources worked/failed
- Notes about the state's specialty structure
- File locations

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

### What Doesn't Work
1. **Direct PDF downloads from state sites** — Often behind bot protection, moved, or returning 404
2. **Wayback Machine for PDFs** — Often returns HTML wrappers or 404s for government PDFs
3. **Browser tool for PDFs** — Can't render PDF content; returns 404 or navigation errors
4. **State government search** — PA.gov internal search returned "No results" for specialty codes

### Pitfalls
1. **Assume URLs are stable** — They're not. The PA specialty codes PDF was cited in search results but returned 404
2. **Confuse states** — The Advanced Health document had Oregon HSD data, not PA data. Always verify the state
3. **Miss the BH-MCO layer** — PA has separate behavioral health managed care with its own specialty categories. Don't assume one source covers everything
4. **Tier confusion** — PA has multiple network adequacy tiers with different requirements. Document the tier structure, not just the specialty names

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

### Pennsylvania
- **Program name:** HealthChoices (CHC)
- **Managed care types:** CHC-MCO (physical health), BH-MCO (behavioral health), PH-MCO (physical health for adults), CHIP-MCO (children)
- **Network adequacy tiers:** Tier 1 (2 providers, 30/60 min), Tier 2 (1 + 1 in zone), County-level (LTSS)
- **Facility codes:** Provider Type/Specialty Code format (e.g., 01/11, 03/37)
- **LTSS integration:** Community HealthChoices (CHC) program adds LTSS provider types
- **Official PDF:** Previously at `pa.gov/.../Provider+Type+Specialty+Codes.pdf` (now 404)
- **Working source:** 2025 CHC Agreement at `pa.gov/.../2025-chc-agreement.pdf`

## Future Improvements

- [ ] Build a Python script that automates the `pdftotext` + `grep` extraction
- [ ] Create a template for each state's data file to ensure consistency
- [ ] Add NUCC taxonomy mapping column to CSV (Phase 2)
- [ ] Build a comparison matrix across states
- [ ] Set up monitoring for state bulletin changes
