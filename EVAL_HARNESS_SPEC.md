# Specialty Mapper — Eval Harness Specification

> Phase 1 keystone spec (Draft v3, 2026-08-14 — v3: the scored, ground-truth-labeled dimension is
> **link A, the clean display name**, not the NUCC code. Link B is a deterministic lookup, made
> provably lossless by the verified display-name↔code bijection. v2: two-link answer key,
> data-driven ambiguity classifier, two-axis dataset, behavior-correct scoring, per-tier reporting)
> Produces **Number A** — the portable, citable accuracy number on public-catalog ground truth.
> Companion to `PROMOTION_PLAN.md` §5 Phase 1.

---

## 0. What this produces, and what it can claim

**Produces:** a measured, reproducible **capability profile** for the mapper — performance by
ambiguity tier and by noise class, plus calibration, a failure taxonomy, and cost/latency — in a
standalone report that cites **no proprietary data**.

**Can claim (Number A):**
- "Given a provider specialty label, the system recovers the **intended specialty** (clean
  display name — hence the NUCC code, by the verified display-name↔code bijection) at **X%
  overall** and the following profile: **99% on clean labels, 92% on noisy-but-unambiguous
  labels, 78% on dominant-default ambiguous labels, 61% behavior-correct on
  genuinely-ambiguous labels**."
- "Self-reported confidence is calibrated: accuracy by band is …; **overconfident error rate is
  Y%.**"
- "On genuinely-ambiguous inputs (e.g. `neuro`), the system **does not commit to a single
  specialty with high confidence**; it returns low confidence and surfaces the candidate set, at
  Z%."
- "P% of genuinely-unmappable labels are correctly flagged for manual review."

**Cannot claim (that's Number B, on Quest data):**
- It does **not** measure coverage of the messy labels that *actually* appear in Quest's
  production data. It measures **robustness to controlled label noise + calibration + ambiguity
  handling**, on a reproducible set. The report states this limitation explicitly. Number A
  must not overclaim into Number B's territory.

The headline is the **profile, not the aggregate.** An aggregate ("87%") hides where the system
works and where it doesn't. The per-tier table is the asset.

---

## 1. What is measured: link A only (the display name)

A test case is two links:

```
"gastro" ──[A]──> "Gastroenterology" ──[B]──> 208500000X
   (input)     (clean display name)          (NUCC code)
```

- **[A]** (`gastro → "Gastroenterology"`) is **authored by the LLM.** The model is shown the NUCC
  taxonomy and must *select* the display name the label refers to. Nothing in the data says
  "gastro" means Gastroenterology — that is a judgment. **This is the only dimension we measure
  against a ground-truth-labeled dataset.**
- **[B]** (`"Gastroenterology" → 208500000X`) is a **deterministic lookup** in the taxonomy. No
  judgment. **Not an independent scored dimension.**

**Why scoring link A is provably complete (not just convenient).** In NUCC v25.1, display name ↔
code is a **bijection** (verified: 883 display names, 883 codes, zero name→multi-code collisions,
zero duplicate codes). Display name and code therefore carry *identical* information: picking the
right display name ⟺ producing the right code. Measuring either yields the same number. We
measure the **display name** specifically because it is (1) the authored dimension, (2)
interpretable — a failure reads as "*gastro* → 'Gastroenterology, Nursing' instead of
'Gastroenterology'", not '2086U0000X vs 208500000X' — and (3) free of hidden failure modes: the
lookup cannot fail on a valid name, so nothing hides in the un-scored link.

**Consequence for the pipeline:** the LLM is prompted to emit a **display name** (one of the 883),
plus confidence and a candidate set. The NUCC code is then **derived by lookup** — for the
product and for the run record — but the **scored, ground-truth-labeled dimension is the display
name.** If the model emits a name *not* in the taxonomy, that is a **link-A failure** (the
authoring produced an unresolvable category), not a link-B failure: the lookup never fails on a
valid name.

**The answer key is valid in proportion to the agreement of link A.** The control is to make the
ambiguity of link A a **measured, reproducible property of the taxonomy** (§3.2) and to **score
each case under the rule its ambiguity dictates** (§5).

Ground-truth answer key per case: `{input, expected_name (link A, authored), expected_code (link
B, derived), tier, noise_class, provenance}`. The model's output is a name; we score
name-vs-name.

---

## 2. Architecture: extract the callable core

The mapping logic is currently fused with the FastAPI server. The eval (and Phase 2
productionization) both need a standalone callable. **Step 1 of the build is this extraction:**

```
src/specialty_mapper/
├── __init__.py
├── nucc.py          # load_nucc() — NUCC v25.1 reference (883 display names), hierarchy-aware
│                    #   + resolve_code(name) — the link-B lookup (display name -> code)
├── state.py         # load_state_catalog(), load_state_crosswalk()
├── client.py        # llm_call() — fast mode, structured-output enabled
├── mapper.py        # map_specialty(labels, target, state) -> list[MappingResult]
│                    #   THE core. Demo and eval both call this.
└── parse.py         # parse_json() — single clean parser (replaces the 7-fallback)
```

- `demo/main.py` becomes a thin wrapper that imports from `src/specialty_mapper`.
- **Regression gate:** after extraction, the demo must return semantically-identical results on
  the same inputs before the eval touches anything.

### 2a. The output contract is a display name, not a code
This is a **prompt change from the current demo** (which asks the model to emit codes directly and
hands it the full taxonomy + crosswalk as context). In the tightened design:
- the model is asked to **select the clean NUCC display name** the label refers to (the link-A
  judgment) plus confidence and — where genuinely ambiguous — a candidate set;
- the **code is derived downstream** by `resolve_code(name)` (link B), never authored by the
  model. This is what makes link B a pure lookup and removes it from the scored dimensions.

### 2b. Kill the 7-fallback parser
`parse_response` in `demo/main.py` has **seven** JSON-extraction fallbacks — a symptom of prompt
fragility. Replace with one clean path:
1. `client.llm_call()` requests **structured output** (`response_format: {"type":"json_object"}` —
   llama.cpp supports JSON mode).
2. `parse.py` does a single `json.loads` + **pydantic schema validation** against `MappingResult`.
3. **One failure mode:** "not valid JSON / schema mismatch" → the label is flagged `parse_failed`,
   routed to review. No regex surgery, no depth-counting, no trailing-comma repair.

`parse_success_rate` becomes a first-class metric (§5.1).

### 2c. `MappingResult` schema (the contract)
```python
class MappingResult(BaseModel):
    input: str
    nucc_name: str | None          # THE scored field (link A) — display name, or None => no match
    nucc_code: str | None          # DERIVED from nucc_name via resolve_code (link B); product/record
    state_code: str | None
    state_category: str | None
    confidence: float              # 0.0–1.0, model self-reported
    candidates: list[str] = []     # co-equal DISPLAY NAMES (for genuinely-ambiguous inputs)
    notes: str
    parse_failed: bool = False
    name_unresolvable: bool = False  # nucc_name emitted but not in taxonomy => link-A failure
```

`candidates` (display names, not codes) is the field that makes behavior-correct scoring (§5.3)
possible: on a genuinely ambiguous input, the *correct* output is a low-confidence result **plus a
candidate set of display names**, not a single name/code.

---

## 3. Ground-truth generation

### 3.1 Two orthogonal axes — don't collapse them
The dataset crosses two independent dimensions:

1. **Ambiguity** (from the taxonomy, §3.2): is the referential target (link A) unique? This
   determines **the scoring rule** (§5.2/5.3).
2. **Noise / perturbation class** (from the label, §3.4): case, typo, abbreviation, separator,
   provider-wrapped, no-match. This determines **how hard the input is to parse**.

The headline robustness claim lives at the **intersection** (e.g. *T-unique × typo* = "how well
does it handle noisy labels on unambiguous specialties"). Reporting on one axis alone loses the
other.

### 3.2 Ambiguity is computed from the taxonomy, not opinion — `classify_ambiguity()`
For any input/root, `classify_ambiguity()` walks the NUCC hierarchy and returns a tier. The tier is
defined on the **display-name candidate set** for the root — how many co-equal display names are
plausible. The rule is operational and reproducible (verified against the v25.1 file):

- Collect all taxonomy nodes whose **display name** matches the root, restricted to the target
  grouping (Allopathic & Osteopathic Physicians for physician specialties).
- Inspect the **hierarchy**: are the matching display names a *parent + its subspecialty
  children*, or *co-equal siblings*?

| Tier | Definition | Example | Root display-name fan-out (v25.1) | Scoring rule |
|---|---|---|---|---|
| **T-unique** | One dominant parent display name; other matches are its subspecialty children or adjacent professional codes | `gastro` | 3 (1 parent + pediatric child + nursing) | **exact-match** on the parent display name |
| **T-dominant** | One dominant parent display name + a real subspecialty tree, but the parent is the unambiguous default | `cardio` | 12 (Cardiology + ~5 A&O subspecialties + non-MD) | **exact-match** on the parent display name; subspecialty child = acceptable, logged |
| **T-coequal** | **Two or more co-equal parent display names, none an ancestor of the others** — a genuine judgment fork | `neuro` | 24 (Neurology / Neurological Surgery / Neuropsychology + fan-out) | **behavior-correct** (§5.3) |

**The dominance test (principled, not a count heuristic):** a parent display name P is *dominant*
for a root if every other matching display name in the grouping is either (a) a subspecialty
descendant of P, or (b) an adjacent non-MD professional code. If instead two or more matching
display names are **sibling classifications under a shared grouping with no ancestor relationship
among them**, the root is **T-coequal**. That's the precise line between `cardio` (Cardiology is
the ancestor of Interventional/Nuclear/Pediatric Cardiology → dominant) and `neuro` (Neurology,
Neurological Surgery, Neuropsychology are siblings → coequal).

This classifier is a **reusable component**: it generalizes to any abbreviation, is auditable
("here's why `neuro` is T-coequal: three sibling classifications, no ancestor relationship"), and
turns "my judgment about which abbreviations are ambiguous" into a **measured property of the
data.**

**First state: MI** (clean 66-row `source_name → nucc_code`, mostly 1:1, verified vs MDHHS, home
state + flagship). **OH** is the natural second state but is harder (one `specialty` → multiple
NUCC codes, e.g. "Adult Primary Care" → 3 codes) — save it for the ambiguity tier. **CA/FL**
crosswalks are provider-type-group keyed (863/1082 rows, include hospitals) — poor physician
ground truth, skip for v1.

### 3.3 Two sources of test cases (both honest)
- **Templated (the bulk):** from each clean crosswalk row (invariant link B answer) + a
  deterministic seeded perturbation (§3.4). Link A is authored but **graded by the classifier** —
  templated cases are drawn to land in T-unique/T-dominant so link A is high-agreement.
- **Curated (the tricky tail):** hand-authored T-coequal forks (real dual-mappings), subspecialty-
  to-parent collapses, and genuine no-matches. Tagged `provenance: curated`. The report states the
  mix explicitly (e.g. "145 templated + 35 curated") — methodological transparency is a feature.

### 3.4 Perturbation / noise taxonomy (axis 2)
| Class | Example (from "Family Medicine" → 207Q00000X) |
|---|---|
| `exact` | `Family Medicine` |
| `case` | `family medicine` / `FAMILY MEDICINE` |
| `whitespace` | `  Family Medicine  ` / `Family    Medicine` |
| `abbreviation` | `Fam Med` / `FM` |
| `typo` | `Familly Medicine` / `Cardiologiy` |
| `separator` | `Family Medicine / Internal` / `Cardiology - Interventional` |
| `combined` | `Hematology/Oncology` (dual) |
| `subspecialty` | `Pediatric Cardiology` |
| `legacy` | `Gen Practice` (for "General Practice") |
| `provider_wrapped` | `Dr. Smith - Cardiology` / `Cardiology (Dr. Jones, MD)` |
| `no_match` | `XYZ123` / `Marketing` |

### 3.5 Target composition (MI v1, ~180 total)
Drawn so every (ambiguity tier × key noise class) cell is populated, and no cell dominates:

- **T-unique** (≈40): exact 5, case 4, whitespace 4, abbreviation 6, typo 5, separator 5,
  legacy 4, provider_wrapped 4, subspecialty→parent 3
- **T-dominant** (≈55): abbreviation 10, separator 8, typo 6, subspecialty (child) 8, combined 7,
  provider_wrapped 6, case 5, whitespace 3, exact 2
- **T-coequal** (≈45, ~20 templated forks + 25 curated): `neuro`-type forks 12, dual/parent
  collapses 13, multi-parent subspecialty 12, curated no-match 8
- **No-match (cross-tier)** (≈40, curated + templated): `XYZ123`, `Marketing`, `Dr. Smith`
  (no specialty), etc.
- **Curated total** ≈ 35, tagged `provenance: curated`.

Each case carries **both** `ambiguity_tier` and `noise_class`, plus `seed_lineage` and
`provenance`.

### 3.6 Generator requirements
- **Deterministic:** fixed `seed` in the dataset header. Same seed → same set.
- **Reproducible from data:** `dataset.py` regenerates from crosswalk files + `classify_ambiguity()`
  + a per-class rule table; no hand-edited JSONL by default.
- **Committed + pinned:** `mi_v1.jsonl` committed with a header (seed, state, crosswalk hash,
  generated_at, n_templated, n_curated, tier counts).
- **Verified:** `dataset.py` self-checks every row — `expected_name` exists in the reference;
  `resolve_code(expected_name) == expected_code` (bijection sanity); `expected_state_category`
  exists in the catalog; `ambiguity_tier` matches `classify_ambiguity()` on the case's root (a
  disagreement is a dataset bug, caught at build time).

---

## 4. The run
`run.py`:
1. Load `mi_v1.jsonl`.
2. For each case, call `mapper.map_specialty()`.
3. Record per case: full `MappingResult` (name **and** derived code), latency, tokens in/out,
   model id, prompt version hash.
4. Write `evals/runs/<ts>_<model>/results.jsonl`.

- **Batching:** mirror the demo's batching for a realistic cost/latency profile.
- **Isolation:** the eval runs the *fast* (direct-LLM) path. Agent mode (Hermes `subprocess`) is
  out of scope — it's the architecture Phase 2 cleans up, not what Number A measures.

---

## 5. Metrics (precise definitions)

### 5.1 Core metrics
| Metric | Definition |
|---|---|
| `specialty_name_acc` | % cases where `pred.nucc_name == expected_name` (None==None counts correct). **The primary Number A authoring metric. Computed per tier** (§5.2). By the display-name↔code bijection this equals `nucc_code_acc`. |
| `nucc_code_acc` | % where `pred.nucc_code == expected_code`. Retained for the product view; **asserted equal to `specialty_name_acc`** — a divergence is impossible by the bijection and is therefore a bug, not a separate number. |
| `state_cat_acc` | % where `pred.state_category == expected_state_category`. |
| `acc_by_band` | accuracy within each confidence band: `≥0.9`, `[0.7,0.9)`, `[0.5,0.7)`, `[0.3,0.5)`, `<0.3`. |
| `acc_by_tier` | **`specialty_name_acc` per ambiguity tier (T-unique / T-dominant / T-coequal).** The headline profile. |
| `acc_by_noise` | accuracy per noise class. |
| `acc_by_cell` | accuracy per (ambiguity tier × noise class) intersection. |
| `no_match_recall` | on the no-match class, % correctly flagged (`confidence<0.5` or needs-review). |
| `name_unresolvable_rate` | % where the model emitted a display name **not** in the taxonomy (a link-A failure, distinct from a clean no-match). |
| `false_confident` | % cases with `confidence≥0.8` that are **wrong**. The dangerous failure. |
| `parse_success_rate` | % responses parsed cleanly by the single parser. Measures the 7-fallback fix. |
| **Calibration / ECE** | Expected Calibration Error across bands; confidence-vs-accuracy curve. |
| **Cost/latency** | total tokens, p50/p95 per-label latency, calls per batch. |

### 5.2 Tier-conditional scoring rule (axis 1)
The ambiguity tier **selects the scoring rule**, which is what makes the per-tier number
meaningful instead of a lucky-guess artifact. All scoring is on the **display name** (link A):

- **T-unique / T-dominant → exact-match scoring.** `gastro` must come back as the parent display
  name. (T-dominant: a subspecialty child display name is logged as *acceptable* but not counted
  exact.)
- **T-coequal → behavior-correct scoring** (§5.3).

### 5.3 Behavior-correct scoring (the honesty load-bearing rule)
For a **T-coequal** case, "correct" is **not** "you guessed the right single name." Correct is the
**behavior**:
- `confidence < commit_threshold` (default 0.6, tunable, recorded), **and**
- the candidate set (`MappingResult.candidates`, display names) contains **all** co-equal parent
  display names, and
- it does **not** commit to a single name at high confidence.

If the system **confidently commits to one name** on a T-coequal input, that is a **failure — an
overconfident error — even if it landed on a plausible one**, because in production that is exactly
the dangerous wrong-answer. This is what makes the harness honest on the hard tier rather than
quietly rewarding a lucky guess.

`coequal_behavior_acc` = % T-coequal cases that satisfy the behavior rule. `coequal_overcommit`
= % T-coequal cases that committed at `confidence≥commit_threshold` (the anti-metric).

### 5.4 Headline profile (the artifact)
```
Ambiguity tier    n     scoring rule           result
T-unique          40    exact-match (name)     99%
T-dominant        55    exact-match (name)     92%
T-coequal         45    behavior-correct       61%  (overcommit 9%)
no-match          40    flag-for-review        84%
OVERALL          180    —                      (aggregate shown, not headline)
```
The confidence-band table (§5.1 `acc_by_band`) is the second artifact — it converts
"self-reported confidence" from a *claim* to a *measurement*.

---

## 6. The report (standalone + regression-trackable)
`report.py` emits, per run, under `evals/runs/<ts>_<model>/`:
- `results.jsonl` — full per-case results (name, derived code, confidence, candidates).
- `summary.json` — all §5 metrics + config (model, prompt hash, dataset hash, seed,
  commit_threshold).
- `report.md` — human-readable, leads with the profile.

**`report.md` structure:**
1. **Headline:** the tier profile in one block + overconfident-error rate.
2. **Ambiguity profile** (§5.4 table) — the capability profile.
3. **Noise-class breakdown** — accuracy per perturbation class; worst 3 called out.
4. **Ambiguity × noise matrix** — the intersection cells.
5. **Confidence bands + calibration** — band table + ECE.
6. **The failures** — every failed case, grouped by (tier × class), `predicted name → expected
   name` (for T-coequal: committed name vs the required candidate set).
7. **Cost/latency.**
8. **Methodology & limitation** — how the set was generated (n templated/curated, seed, state,
   the two-link answer key, the display-name↔code bijection, the classifier rule,
   commit_threshold) and the explicit statement that this is a robustness/calibration/ambiguity
   result on a synthetic set, **not** a production-coverage measurement (Number A ≠ Number B).

**Regression tracking (the differentiator):** every run is pinned to (model, prompt hash, dataset
hash) and stored as `results.jsonl`, so a later run diffs cleanly: *"Prompt change X moved
T-dominant exact-match 88% → 92% and did not regress the T-coequal overcommit rate."* The eval is
a **continuous instrument**, not a one-shot screenshot.

---

## 7. Build order (within Phase 1)
1. **Extract core** → `src/specialty_mapper/` (nucc, state, client, mapper, parse). Add
   `resolve_code(name)` (link-B lookup). Thin the demo to a wrapper. **Switch the output contract
   to display name + derived code (§2a).** *Gate: demo output unchanged on the same inputs.*
2. **`nucc.py` hierarchy-aware** + **`classify_ambiguity()`** (matches on **display name**) — the
   data-driven ambiguity tier. *Gate: `gastro`→T-unique, `cardio`→T-dominant, `neuro`→T-coequal,
   and a small audit table of other roots prints correctly.*
3. **Single clean parser** + structured output in `client.py`; add `candidates` (display names) +
   `name_unresolvable` to `MappingResult`. *Gate: `parse_success_rate` is a real number;
   7-fallback deleted.*
4. **`perturb.py`** — generator + noise taxonomy, seeded, deterministic.
5. **`dataset.py`** → generate + self-verify `evals/datasets/mi_v1.jsonl` (display-name existence,
   `resolve_code` bijection sanity, state-category existence, tier matches classifier);
   hand-check a sample.
6. **`run.py` + `score.py`** — tier-conditional scoring on the display name (exact-match vs
   behavior-correct), `commit_threshold`. *Gate: first full run → Number A profile exists;
   `nucc_code_acc == specialty_name_acc` asserted.*
7. **`report.py`** → standalone `report.md` + `summary.json` + `results.jsonl` (all §6 sections).
8. **Iterate:** tune prompt/structured-output to move the profile; every change logged as a new
   run; show ≥1 before/after diff to demonstrate the regression instrument.

Tests (`tests/`): `test_parse.py` (valid / truncated / non-JSON / schema-mismatch → one clean
failure), `test_classify.py` (gastro/cardio/neuro tier + a sibling-vs-ancestor regression
fixture), `test_resolve.py` (display-name↔code bijection: every name resolves, code is unique,
round-trips), `test_perturb.py` (determinism + taxonomy coverage), `test_score.py` (band math,
no_match_recall, ECE, behavior-correct rule on a known T-coequal fixture, code==name equivalence
assertion).

---

## 8. File layout (additions)
```
medicaid-specialty-mapper/
├── src/specialty_mapper/          # NEW — the callable core + eval
│   ├── nucc.py                    # hierarchy-aware reference + resolve_code() + classify_ambiguity()
│   ├── state.py
│   ├── client.py
│   ├── mapper.py
│   ├── parse.py
│   └── eval/{classify,perturb,dataset,run,score,report}.py
├── evals/                          # NEW
│   ├── datasets/mi_v1.jsonl         # committed, seed-pinned, two-axis ground truth
│   └── runs/<ts>_<model>/{results.jsonl,summary.json,report.md}
├── tests/{test_parse,test_classify,test_resolve,test_perturb,test_score}.py
├── demo/                            # unchanged behavior; imports from src/
├── pyproject.toml                   # NEW (matches qhp-specialty-framework standard)
└── data/states/mi/                  # existing — the ground-truth source
```

One structural decision: new top-level `src/` + `evals/` (+ `pyproject.toml`). Already the Phase 2
production standard; starting it in Phase 1 is coherent because the eval requires the callable
core. Flag it as such in the Phase 0 note.

---

## 9. Definition of done (Phase 1)
- [ ] `map_specialty()` extracted; output contract = display name + derived code; demo behavior
      unchanged (regression-verified).
- [ ] `resolve_code(name)` + display-name↔code bijection proven (test_resolve).
- [ ] `classify_ambiguity()` (display-name-based) built + tested (gastro/cardio/neuro +
      sibling-vs-ancestor fixture).
- [ ] Single clean parser; 7-fallback removed; `parse_success_rate` measured; `candidates`
      (display names) + `name_unresolvable` fields.
- [ ] `mi_v1.jsonl` generated, self-verified (incl. bijection sanity + tier↔classifier
      agreement), committed, seed-pinned (~180 cases).
- [ ] First full run → **Number A tier profile** in a standalone report (T-unique / T-dominant /
      T-coequal / no-match), scored on the display name; `nucc_code_acc == specialty_name_acc`.
- [ ] Behavior-correct scoring live on the T-coequal tier (candidate set of display names);
      `coequal_overcommit` reported.
- [ ] Calibration (ECE + bands) + failure taxonomy (incl. `name_unresolvable_rate`) quantified.
- [ ] ≥1 before/after regression diff demonstrating the instrument.
- [ ] Report states the two-link answer key + display-name↔code bijection + synthetic-set
      limitation explicitly (Number A ≠ Number B).