# Specialty Mapper — Leverage & Growth Initiative Plan

> Status: **Draft v2** (created 2026-08-14, updated 2026-08-14 — leverage framing, not an immediate comp ask)
> Owner: Andy
> Sponsor: CDO (verbal endorsement — "had some teeth to it")
> Type: **60–90 day internal initiative** — NOT side work

---

## 1. Strategic Decision

The Specialty Mapper is squarely inside Quest Analytics' subject matter (provider data /
specialty / network for health plans). That means:

- **Do NOT** build it out on personal time/hardware as a side project. That re-opens IP
  exposure.
- **DO** make it an **official company initiative**: company scope, company time, company data,
  named ownership.
- **Do NOT make an immediate promotion/comp ask.** Andy is ~1 year into the DS role and the
  company has missed budget several quarters running — a formal comp/title event will likely
  bounce, and a bounced ask carries social cost. Instead: **bank the leverage and deploy it
  later** (next review window, when budget reopens, or externally).
- The *capability* (LLM pipeline + evals + deployment) is portable and stays with Andy no matter
  what. The *application* (healthcare provider specialty) is Quest's. Good trade: Andy gets the
  credit, the reference, the skills, and a durable asset; Quest gets the tool.

**The one line that frames everything:** the initiative produces a **durable leverage asset**, not
a one-shot comp event. Concretely, two numbers that do different jobs:

- **Number A — portable (the arsenal number).** Measured accuracy on a ground-truth set built from
  the *public* state Medicaid catalogs (already in the personal repo, on personal hardware).
  Stated at a level that reproduces **no proprietary mapping or company code**, this is the citable,
  resume-traveling proof: "built and shipped a provider-specialty classification pipeline with a
  ground-truth eval harness, X% measured accuracy, documented failure taxonomy."
- **Number B — Quest-locked (the commercial number).** The *business metric* (error rate,
  manual-review hours saved, $ value) computed on Quest's proprietary data. Justifies company
  investment. Stays at Quest.

**A travels with Andy. B stays at Quest.** The pipeline-as-code and the proprietary data are the
company's; the *capability* (eval-pipeline design, failure taxonomy, cost/latency discipline) is
Andy's and is not assignable. That split is why "make it official company work" is the right IP
move — it converts gray to clean: the company owns the deliverable, Andy owns the credit and the
portable capability.

**What "leverage" actually is when budget is frozen** — not cash, but the three things a frozen
budget *can't* block:
1. **Ownership** — named lead on a real initiative (cheap for the company to grant).
2. **The dated record** — a memo with Number A + Number B, owned by Andy, visible to the CDO.
3. **Advocacy** — the CDO (a decision-maker, a reference) has Andy's name on the number.

That is what makes "later" real — at the next review window, when budget reopens, or externally on
the FDE/remote path, where Number A + the capability is the proof.

---

## 2. Mapping Model (product definition)

The mapper works in two stages, and only the first stage touches the LLM:

1. **Input → NUCC Display Name (LLM).** The LLM sees the full NUCC display-name list
   (codes withheld) and returns the best-matching *display name string* for each input
   label, with a confidence score and notes.
2. **Display Name → Code (deterministic lookup).** The code is **never LLM-generated**.
   It is resolved by direct lookup in the NUCC dataset (normalized exact match, tight
   fuzzy fallback for minor drift). An unresolvable name is flagged for review, not
   guessed.

Why: codes are identifiers, not concepts — the LLM should do the semantic work (fuzzy
label → canonical name) and the dataset should do the exact work (name → code). This
removes a whole failure class (invented/malformed codes) and makes the output
deterministically checkable against the taxonomy file.

---

## 3. Diagnosis (what's real vs. what's thin)

### Has teeth (keep, protect)
- **11 states of verified Medicaid specialty reference data** (AZ, CA, FL, GA, IL, MI, NC, NY, OH,
  PA, TX) — each with source documentation + provenance. Rare, hard-to-get asset.
- **NUCC v25.1 spine** (883 codes).
- Sound concept: free-text label → **NUCC display name (LLM)** → **NUCC code
  (direct lookup in the NUCC dataset, never LLM-generated)** → state crosswalk,
  semantic fallback, confidence + review-flag.
- Working demo (FastAPI, single direct LLM call ~8s, Qwen3.6-27B local on 5090).
- Real, specific problem: provider specialty data is messy, manual, expensive.

### Thin (the gap to close)
- **No evals / ground-truth / accuracy number.** The output "confidence" is the LLM's
  *self-reported* claim, not a measurement. This is the #1 issue.
- **Fragile parser.** `parse_response` has 7 JSON-extraction fallbacks — a symptom of prompt
  fragility, not robustness.
- **Demo + scripts, not a package.** (Contrast: `qhp-specialty-framework` already has proper
  `src/` layout, `pyproject.toml`, 33 passing tests.)
- **NY and TX crosswalks `Missing`** in the manifest.

---

## 4. North Star / Success Criteria

The initiative is a success when all four are true:

1. **Number A (portable) exists** — measured accuracy on public-catalog ground truth, overall and
   by confidence band (e.g. "94% correct where confidence ≥ 0.8"), in a standalone report that
   cites no proprietary data.
2. **Number B (Quest) exists** — a defensible business metric on Quest's data (error rate,
   manual-review hours saved, $ value).
3. **It's scoped and named** — a 60–90 day initiative with a stated deliverable, Andy as named
   lead, ownership in writing.
4. **The deployment path is defined** — near-term (ownership/credit now) and later (comp event
   when a window opens, or externally) — not an immediate comp ask.

---

## 5. Open Questions (BLOCKING — resolve in Phase 0)

- [ ] **Eval-set source (load-bearing):** build Number A's ground truth from the *public* state
      catalogs (portable, citable, already in the personal repo). **Recommendation: yes — this is
      the core**, and it hedges IP. Number B is then computed on Quest data only *if* access is
      granted.
- [ ] **Access to Quest's real provider specialty data?** Needed only for Number B (the business
      metric). If denied, Number A still stands and the asset is still portable — flag the weaker
      business metric early in Phase 0, don't discover it in Phase 2.
- [ ] **Which state(s) first for evals?** Pick one with a *complete* crosswalk — CA, FL, OH, or
      MI are the strongest candidates.
- [ ] **What can a frozen budget actually grant right now?** (Named-lead / ownership on the
      initiative, defined scope, a documented record — all non-comp. The comp/title *event* is
      deferred, not dropped.)

---

## 6. Phases

### Phase 0 — Formalize (Week 1)
Goal: convert a CDO compliment into a named, scoped, owned initiative — and get ownership, not a
comp event.
- [ ] Short explicit conversation with the CDO:
      - "I want to make this real — scope it as a 60–90 day initiative."
      - "I'd like to own it."
      - "I'd like to understand the path for this to carry weight in my growth — timing can follow
        the ship."
- [ ] Get ownership **in writing** (email recap minimum; project charter better).
- [ ] Agree the success metric (Number B, see North Star #2) *before* building.
- [ ] Confirm the IP posture: this is company work, company time, company data.
- [ ] Resolve the open questions above.

### Phase 1 — Keystone: Eval Harness (Weeks 2–5)  ← *highest leverage*
Goal: turn the demo from "vibes" into a measured system. This is also the showcase for the
agentic-eval skill, and it produces **Number A** (the portable arsenal number).
- [ ] Build a **ground-truth eval set** from the **public state catalogs** (~100–200 real messy
      labels with known-correct NUCC/state mappings). This is Number A's substrate — portable and
      citable.
- [ ] Run the mapper against it. Report **accuracy overall and by confidence band**.
- [ ] Build a **failure taxonomy** (e.g. dual-mapping subspecialties, subspecialty→parent collapse,
      no-match, abbreviation ambiguity).
- [ ] Track **cost/latency** (LLM calls per batch, p50/p95 latency, tokens).
- [ ] Replace the 7-fallback parser with **constrained/structured output** + one clean failure mode.
- [ ] Output: a standalone eval report that leads with the number ("Here's the number, here's the
      6% failure, here's why").
- [ ] *(If Quest data access is granted)* compute **Number B** against Quest's data as a parallel
      track.

### Phase 2 — Business Metric + Productionization (Weeks 6–9)
Goal: tie Number B to a Quest dollar problem and make the code production-grade.
- [ ] Compute the **business metric (Number B)** against Quest's data (error rate,
      manual-review hours saved, $ value).
- [ ] **Package it** — proper `src/` layout, `pyproject.toml`, test suite (match the
      `qhp-specialty-framework` standard, not the demo standard).
- [ ] Complete **NY and TX crosswalks** (currently Missing).
- [ ] A short **README/one-pager** that leads with the measured accuracy (Number A), not the
      architecture.

### Phase 3 — Bank the Leverage + Deployment Playbook (Weeks 10–13)
Goal: convert the finished asset into durable leverage. Do **not** make the immediate comp ask.
- [ ] **The record** — one-page memo: problem, what was built, Number A (portable), Number B
      (Quest), cost/latency. Dated, owned, and persisted (repo + CDO).
- [ ] **Near-term ask (what a frozen budget grants):** named lead / ownership on the initiative and
      a defined follow-on scope — credit that sticks, no comp event.
- [ ] **Presentation to the CDO** — sell the *capability and its value*; keep the growth talk as a
      "let's talk when a window opens," not a demand.
- [ ] **The "later" optionality** — Number A + the capability are the resume/external line for the
      FDE/remote path. Keep Number B and company code proprietary; cite Number A at a level that
      leaks nothing.

---

## 7. The 5 Agentic Differentiators (what the work must demonstrate)

These are the resume/promotion lines almost nobody has. The initiative should visibly include them:

1. **Evals** — quantified success rate + failure-mode analysis + regression tracking. (Phase 1.)
2. **Tool design, not tool usage** — idempotent tools, clean error surface, LLM-readable docs,
   input validation.
3. **State management / context strategy** — how the pipeline tracks done/tried/failed and decides
   the next step; context-window strategy.
4. **Cost & latency awareness** — calls per task, p95 latency, small-model-vs-large-model routing.
5. **A specific, real workflow** — "maps provider specialty codes to state Medicaid + NUCC," not
   "an AI assistant." Specificity *is* the credibility.

---

## 8. Risks & IP

- **IP / non-compete:** Michigan (Andy's state) has a generally non-compete-hostile climate (EO
  2024-1, subsequently litigated — confirm current status with employment counsel if needed).
  Building this as *company work* neutralizes the main exposure. Keep side projects in
  non-Quest domains.
- **Portability boundary:** Number A must be citable without reproducing proprietary mappings or
  company code. The accuracy *value* on public data is Andy's to cite; the pipeline-as-code is
  the company's. Keep the external framing at the capability + result level, not the code level.
- **CDO engagement fading:** a compliment without ownership gets buried or reattributed. Phase 0
  exists to prevent this.
- **Scope creep:** one artifact at a time. The eval harness is the keystone; everything else
  supports the numbers.
- **Data access:** if Quest's real data isn't available, Number B (the business metric) gets
  weaker — but Number A (portable accuracy on public catalogs) still stands. Flag early in Phase 0.

---

## 9. Definition of Done

- [ ] **Number A** (portable accuracy on public-catalog ground truth), overall + by confidence
      band, in a standalone report citing no proprietary data.
- [ ] **Number B** (business metric on Quest's data), in the one-pager — or a documented note that
      data access wasn't granted and Number A is the standing result.
- [ ] Production-grade package (src layout, pyproject, tests passing) — not a demo.
- [ ] NY + TX crosswalks complete.
- [ ] Named lead in writing; the leverage asset banked (record + ownership) and the later
      deployment path defined — no immediate comp ask.
