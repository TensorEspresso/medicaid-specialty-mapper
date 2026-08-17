# Specialty Mapper — FDE Engagement Plan

> Status: Draft v1 (2026-08-17)
> Scope: **NUCC-only.** The client problem is "map free-text provider specialty
> labels to the NUCC code universe." No state/Medicaid mapping in the current build —
> the state crosswalks are a **parked extension** (see §7), not part of this engagement.
> Companion to `EVAL_HARNESS_SPEC.md` (the eval spec) and `PROMOTION_PLAN.md` (leverage framing).
> This doc is the **executable plan**: it turns the FDE arc into a build sequence and
> maps each stage to the skill it proves.

---

## 0. The client problem (NUCC-only framing)

A client receives provider specialty labels in free text — abbreviations
(`Ortho`, `ENT`, `Peds Card`), colloquial terms (`Allergies`, `Infectious`), typos,
case/separator noise — and must resolve each to a **NUCC taxonomy code**. Today this is
manual, slow, and inconsistent.

**The deliverable:** a service that maps free-text label → NUCC display name → NUCC code,
with a measured confidence, a clean failure surface, and a **measured accuracy number**
you can defend in front of the client.

Two stages; only the first touches the LLM:

1. **Label → NUCC Display Name (LLM).** The model sees the 883 display names (codes
   withheld) and returns the best-matching display name + confidence + (when genuinely
   ambiguous) a candidate set.
2. **Display Name → Code (deterministic lookup).** The code is **never LLM-generated** —
   it is resolved by lookup in `data/nucc/nucc_taxonomy_251.csv`. Display name ↔ code is a
   verified bijection (883/883, zero collisions), so picking the right name ⟺ producing
   the right code.

---

## 1. Why this is an FDE-shaped engagement

The FDE arc is: **Discover → Scope → Build → Evaluate → Productionize → Prove business
value → Hand off & iterate.** This project runs the whole arc on a single, real problem
— which is exactly what an FDE does inside one account. Each arc stage is where an FDE
earns a specific skill; each stage here has a concrete artifact that proves it.

The point of the portfolio is the **arc**, not the demo. A working `demo/main.py` is the
entry ticket; the differentiators are the *measured number*, the *failure taxonomy*, the
*regression instrument*, and the *business value line* — none of which exist yet.

---

## 2. Current status (honest)

| FDE stage | Status | What exists |
|---|---|---|
| 1. Discover | ✅ Done | Real problem framed; NUCC v25.1 spine (883 codes) |
| 2. Scope / frame | ✅ Done | Two-link answer key, display-name↔code bijection, behavior-correct scoring rule |
| 3. Build | 🟡 Demo only | `demo/main.py` runs, but is a script fused to FastAPI — no package, no `pyproject`, no tests |
| 4. Evaluate | 🔴 Spec only | `EVAL_HARNESS_SPEC.md` exists (but is MI-seeded — needs de-MI, §5). No `src/`, no dataset, no run, **no Number A** |
| 5. Productionize | 🔴 Not started | No packaging, CI, observability, cost/latency measurement |
| 6. Business value | 🔴 Not started | No business metric (Number B) |
| 7. Handoff | 🔴 Not started | No runbook, no regression tracking live |

**The gap to "speakable" is stages 3–7.** Those map almost 1:1 onto the skills the
curriculum (`personal/swe-fde-curriculum.md`) flags as weak. Building the project to the
end *is* learning the progression — on a real engagement, not toy problems.

---

## 3. The arc → skill → artifact map (the core deliverable)

| FDE stage | Project milestone (this repo) | FDE skill proven | Curriculum phase | What you can show at the end |
|---|---|---|---|---|
| **3. Build** | Extract `src/specialty_mapper/`; kill the 7-fallback parser; thin `demo/main.py` to a wrapper; `pyproject.toml` + tests | **Production code, not demo.** Correctness > performance; one clean failure mode | Ph 1 (Python depth) + Ph 2 | `pip install -e .`; `pytest` green; demo output regression-identical |
| **4. Evaluate** | NUCC-native eval: `classify_ambiguity()`, `perturb.py`, `nucc_v1.jsonl`, `run.py`, `score.py`, `report.py` → **Number A** | **Evals — the #1 differentiator.** Converting a self-reported "confidence" claim into a *measured* number + failure taxonomy + calibration (ECE) | Ph 2 (Evals & Monitoring) — critical gap | Standalone `report.md`: "99% clean / 92% noisy / 61% behavior-correct on ambiguous," overconfident-error rate, failure table |
| **5. Productionize** | CI (evals on PR), Docker, structured logging, cost/latency (tokens, p50/p95) | **MLOps, serving, deployment, cost discipline** | Ph 2 + 3 + 4 | Green CI pipeline; a latency/cost row in the report; a reproducible container |
| **6. Business value** | A business metric on a client-like feed: error rate, manual-review load, $ value | **Tying tech to a $ metric** — what gets you hired over a generic AI eng | Ph 5 + 6 (FDE layer) | One line in the memo: "cuts review load X% / saves ~$Y/yr" |
| **7. Handoff** | Runbook, regression-diff instrument (run N vs N+1), architecture one-pager leading with the number | **Customer communication + regression discipline** — "here's what changed and it didn't regress the hard tier" | Ph 6 (Customer-facing) | Two pinned runs with a diff: "prompt change moved T-dominant 88→92%, no T-coequal overcommit regression" |

**Read of the shape:** the *thinking* (discovery, framing, the bijection, behavior-correct
scoring) is already FDE-grade — that's the 30% of the role that's consulting and most
engineers can't do. What's missing is the 70% that's engineering: the package, the
measured number, the CI, the $ metric. The curriculum's "Critical / High" skills
(Model Serving, MLOps, Evals, CI/CD, Customer Communication) *are* stages 3–7. The
curriculum stops being abstract the moment each row above has a real artifact attached.

---

## 4. What "speakable" means (the end-state checklist)

When all of these exist, an interviewer or stakeholder can **see** the FDE arc instead of
being told about it:

1. `pip install -e .` works; `pytest` green; demo behavior regression-verified → *you build real, not demo*
2. A committed `nucc_v1.jsonl` (~180 seeded cases, NUCC-native ground truth) + a standalone `report.md` leading with the **tier profile** and overconfident-error rate → *you measure, you don't assert*
3. **Number A** stated at a level that cites only the public NUCC taxonomy → *portable, citable proof*
4. CI runs the evals before merge → *you guard regressions*
5. A cost/latency row + Docker → *you think in production cost*
6. A one-pager with a business metric (or an honest "client data not granted; Number A stands") → *you tie it to money*
7. Two pinned runs with a before/after diff → *you iterate, you don't screenshot*

Items 1–3 are the **keystone** (they are "Number A"). They're the single highest-leverage
build and are sequenced in §5.

---

## 5. Build sequence (NUCC-only, with gates)

Sequenced so each step has a verifiable gate before the next. Step 0 corrects the
inherited spec's scope; Steps 1–7 build the keystone.

### Step 0 — De-MI the eval spec (scope correction) — ✅ DONE
`EVAL_HARNESS_SPEC.md` v4 is **NUCC-native**. Ground truth is the NUCC taxonomy itself
(883 display names → their own codes, a verified bijection). *Rationale: the MI crosswalk
rows are all `match_confidence: best-effort` — an LLM-derived mapping, i.e. the same error
class we measure. Using it as the answer key contaminates the eval. The canonical taxonomy
is the only clean answer key.*
- **Kept (already NUCC-native):** two-link answer key, display-name↔code bijection,
  `classify_ambiguity()` (pure NUCC hierarchy), the perturbation taxonomy,
  behavior-correct scoring on T-coequal, ECE/calibration, regression tracking.
- **Dropped:** `state_code`, `state_category`, `state_cat_acc`, `load_state_catalog()`,
  `load_state_crosswalk()`, `mi_v1.jsonl` → replaced by `nucc_v1.jsonl`.
- Dataset composition stays two-axis: **ambiguity tier** (from the NUCC hierarchy) ×
  **noise class** (from the label). Templated bulk = 883 display names × deterministic
  perturbation; curated tail = hand-authored abbreviations/synonyms/co-equal forks,
  expected name assigned by judgment against the NUCC taxonomy.
- **Gate:** spec is internally consistent NUCC-only; no reference to a state repo remains
  in the *eval* (the data repo may still be cited as a parked extension in prose).

### Step 1 — Extract the callable core → `src/specialty_mapper/`
- `nucc.py` — `load_nucc()`, `resolve_code(name)` (link-B lookup), bijection helper.
- `client.py` — single clean LLM call, structured output requested.
- `mapper.py` — `map_specialty(labels) -> list[MappingResult]` (the core; demo + eval call this).
- `parse.py` — one clean parser (replaces the 7-fallback).
- `demo/main.py` becomes a thin wrapper importing from `src/`. Add `pyproject.toml` + `tests/`.
- **Gate:** `pip install -e .`; `pytest` green; demo returns semantically-identical results
  on the same smoke inputs (regression-verified) before the eval touches anything.

### Step 2 — `classify_ambiguity()` (NUCC hierarchy)
- Tier is a measured property of the taxonomy, not opinion: **T-unique / T-dominant /
  T-coequal**, from the display-name candidate set and ancestor/sibling structure.
- **Gate:** `gastro`→T-unique, `cardio`→T-dominant, `neuro`→T-coequal, plus a small audit
  table of other roots prints correctly.

### Step 3 — Single clean parser + structured output
- Kill the 7-fallback in `parse.py`; request structured output in `client.py`.
- Add `candidates` (display names) + `name_unresolvable` to `MappingResult`.
- **Gate:** `parse_success_rate` is a real number; the 7-fallback code is deleted.

### Step 4 — `perturb.py` + `dataset.py` → `nucc_v1.jsonl`
- Seed from the 883 display names + curated set; deterministic, seed-pinned.
- Self-verify every row: expected name exists in the reference;
  `resolve_code(expected_name) == expected_code` (bijection sanity); tier matches
  `classify_ambiguity()` (a disagreement is a dataset bug, caught at build time).
- **Gate:** `nucc_v1.jsonl` (~180 cases) committed, self-verified, hand-checked sample.

### Step 5 — `run.py` + `score.py` → **Number A**
- Tier-conditional scoring on the display name: exact-match (T-unique/T-dominant) vs
  behavior-correct (T-coequal, with a recorded `commit_threshold`).
- **Gate:** first full run → **Number A tier profile** exists; `nucc_code_acc ==
  specialty_name_acc` asserted (impossible to diverge by the bijection — a divergence is a bug).

### Step 6 — `report.py` → standalone report
- `report.md` + `summary.json` + `results.jsonl` under `evals/runs/<ts>_<model>/`.
- Leads with the profile: tier table + overconfident-error rate, then noise breakdown,
  calibration/ECE, the failures, cost/latency, and an explicit methodology + limitation
  section (synthetic-robustness result, not a production-coverage measurement).
- **Gate:** report reads as "here's the number, here's the failure, here's why."

### Step 7 — Regression instrument
- Pin every run to (model, prompt hash, dataset hash); produce **≥1 before/after diff**.
- **Gate:** a diff exists showing a change moved one tier and did not regress another.

**After the keystone (arc stages 5–7):** CI (run evals on PR), Docker, structured logging
+ cost/latency (tokens, p50/p95), the business-metric one-pager, and the runbook.

---

## 6. Tests (from the spec, NUCC-native)
`tests/test_parse.py` (valid / truncated / non-JSON / schema-mismatch → one clean failure),
`test_classify.py` (gastro/cardio/neuro + sibling-vs-ancestor fixture),
`test_resolve.py` (display-name↔code bijection: every name resolves, code unique, round-trips),
`test_perturb.py` (determinism + taxonomy coverage),
`test_score.py` (band math, no_match_recall, ECE, behavior-correct rule on a T-coequal
fixture, code==name equivalence assertion).

---

## 7. Explicitly out of scope for now (parked, not deleted)
- **State / Medicaid mapping** — the `medicaid-state-specialty-ref` data repo (11 verified
  states) is the substrate for a *later* feature that maps a label to a target state's
  Medicaid categories alongside NUCC. It is **not** in this engagement. The eval does not
  read it. (Revisit only when the NUCC-only system is measured and stable.)
- **Number B (business metric on client data)** — requires client data access. Until
  granted, Number A is the standing result.
- **Agent mode** — the mapper is a single direct LLM call; no tool-using agent loop.

---

## 8. Definition of done (the keystone)
- [ ] Step 0: eval spec is NUCC-only (no state-repo dependency in the eval).
- [ ] Steps 1–3: `src/` extracted, demo regression-verified, single parser, `classify_ambiguity()` tested.
- [ ] Step 4: `nucc_v1.jsonl` committed, self-verified, seed-pinned.
- [ ] Steps 5–6: **Number A tier profile** in a standalone `report.md`; `nucc_code_acc == specialty_name_acc`.
- [ ] Step 7: ≥1 regression diff demonstrating the instrument.
- [ ] Report states the two-link answer key + bijection + synthetic-set limitation explicitly.
