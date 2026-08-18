# The Pitch — "We already have a Claude license, why do we need this?"

A ready-to-use response to the most common objection, plus the value story it
rests on. Everything below is built and running, not proposed.

---

## The objection, in the customer's words

> "We have a Claude license. We could just drop our file of specialties into
> Claude chat and have it do the same thing. What does this actually do that
> the model can't?"

Concede the honest kernel up front so you don't get called out:

> "You're right that the core mapping is an LLM call — a capable model can
> produce a similar mapping in a chat. That's not the claim."

The license is for the **model**. The mapper's value is everything **around**
the model — and none of that ships in a license. (Note: this system doesn't
even use Claude; it's pointed at a local open-weights endpoint. So "we already
have Claude" is orthogonal to the value.)

---

## Why the license isn't the tool

### 1. Codes are never LLM-generated
The model only picks a NUCC **display name**. The **code is resolved by
deterministic lookup** against the master taxonomy (883 codes, exact match +
tight fuzzy fallback). If you ask a chat model for a NUCC code, it will
hallucinate one — and one bad code flowing into a claims pipeline is a
data-integrity incident. A chat model has no ground-truth table it's
constrained against; this tool does. Unresolvable names are flagged for review,
never guessed.

### 2. It's a service, not a task
"Dropping a file into Claude" is a one-off thing a human pastes in and copies
out. This is an **API with a stable JSON contract** your ETL calls unattended,
at scale, with no human in the loop. No license gets you that — you'd build it
either way.

### 3. A number to route on, and a "don't guess" gate
Every row returns a **confidence score**, and a consumer policy tiers
auto-accept / review / reject off it. There's also an explicit **null-gate**:
no medical connotation → null, never a best-effort guess. Raw chat models tend
to over-map everything to *something*; you lose the ability to route on
confidence or to reject junk.

### 4. Reproducible and measurable
Same input → same output, testable against an eval set (the taxonomy itself is
the truth — a clean bijection, so the benchmark is unambiguous). What "Claude
did in a chat" can't be reproduced, audited, or regression-tested. There's no
baseline.

### 5. Tracks the taxonomy, not the model's training cutoff
The reference is a **versioned** NUCC file (v25.1), bumped on formal taxonomy
releases. A chat model's knowledge of the *current* taxonomy is stale and
unversioned.

---

## The mapping store — the part that's not in any license

Every label your pipeline maps is **persisted to a store** (SQLite in this
build). Recurring inputs are served from the store, not re-sent to the model.
This is where the pitch moves from "it's a harness" to "it's an asset."

**Determinism.** The LLM is non-deterministic even at low temperature — the
same input can score 0.95 one run and 0.98 the next. The store freezes the
first result, so a data pipeline sees a **stable answer every time**. For
claims data, that's the real win.

**A compounding, auditable data asset.** Every real-world label that's been
mapped becomes a persistent, versioned entry. The store gets more complete and
more accurate with every deployment. That's proprietary. A chat model has zero
memory across sessions; every session starts from zero.

**Performance at scale.** Measured on this build, identical inputs go from a
**~5.9s** first map (LLM) to a **~4ms** cache hit — roughly a 1000x speedup on
repeats. At claim-pipeline scale with heavy label repetition, hit rates should
be 80–95% after the first pass.

**Clean invalidation on taxonomy upgrades.** Every entry is tagged with the
taxonomy version it was produced under. On a NUCC version bump, prior-version
entries are treated as stale (re-derived by the model) rather than silently
served — so a rename in a new taxonomy release can't leak a stale mapping into
production.

**A null is a valid, cached answer.** "Not a medical specialty" is deliberate
and reproducible, not an error to re-roll.

**Manual override.** Any entry can be deleted to force a fresh re-map — an
operator escape hatch, not a guess trap.

---

## The one-liner

> "The license is for the model. The mapper isn't an LLM — it's a harness:
> deterministic code resolution so no hallucinated codes, a confidence score we
> can route on, a service our pipeline calls, and an eval that tells us how
> good it is. And the mapping store means every label your pipeline sees becomes
> a permanent, versioned, owned entry — the system gets faster and more
> consistent with every run, and that data is yours. Claude in chat forgets
> everything the moment the session closes."

## The 30-second version

- **Concede:** yes, the core is an LLM call; a model can do a similar mapping in
  a chat.
- **Reframe:** the value is the harness around the model — deterministic
  code resolution (no hallucinated codes), a confidence score to route on, a
  "don't guess" null-gate, an API your pipeline calls, and an eval baseline.
- **Close:** and the mapping store turns every deployment into a compounding,
  versioned, auditable data asset that a stateless chat model can't match.
  Swap Claude in for the local model and the value is unchanged — the license
  doesn't get you any of that.

---

## Proof, not promises (what's actually built)

- Two-stage mapping: LLM → display name, deterministic dataset lookup → code.
  Code is never LLM-generated.
- SQLite mapping store with normalized keys, taxonomy-version tagging, null
  caching, and override.
- Measured: identical inputs **5.9s → 4ms** (~1000x) after the first map.
- Live endpoints: `POST /api/map`, `GET /api/cache/stats`, `GET /api/cache`,
  `DELETE /api/cache/{input}`.
