# STAGE 2.5 — Scope / Split Decision

## Decision: **OPTION (B) — Paper 1 airtight (empirical) + Paper 2 deferred (the method).**
Triggered by the decision rule: the SDT/thresholding reframe was **shaky, not robust** (SDT_RESULTS.md —
prior belief doesn't predict flipping; authority doesn't cleanly load on criterion). Under the pre-set rule,
a non-robust reframe means the behavior-vs-belief *method* does not belong in Paper 1.

## CRITICAL CHECK — does Paper 1 still clear novelty vs Mammen + Wang/PARROT after deferring the method?
**Yes, but only if we retain a MINIMUM of belief content.** A pure behavior-only Paper 1 (direction +
presence + heterogeneity + null) converges heavily with Wang (2508.02087) and risks reading as "Wang,
two-turn edition + a failed Mammen replication." To stay clearly *more than a replication*, Paper 1 keeps two
belief-touching results that need NO SDT formalization:
- **(i)** the belief signal *also* shows no clean authority gradient (anon ≈ high in logprob space, 4/6) —
  belief corroborates behavior, so the null is not a behavioral-measurement artifact;
- **(ii)** **prior confidence does not protect** — turn-1 belief strength fails to predict flipping
  (pooled slope ≈ 0; ~83% flip even at highest pre-pressure confidence). This is novel, behavioral-adjacent,
  and owned by nobody in the corpus.
These lift Paper 1 above both threats without asserting the (unsupported) "modality-is-decisive" thesis.

## What STAYS in Paper 1
1. Direction dominance (|coef|≈3.5, p<0.0001) — robust anchor result.
2. **Presence beats prestige** (behavioral 4/6; belief anon≈high 4/6) — empirical centerpiece.
3. Model-dependent susceptibility (49–98%, not size-tracking) — heterogeneity taxonomy.
4. **Pre-registered null on the graded gradient**, shown robust to model fixed-effects + belief covariate.
5. **Prior confidence does not protect** (Stage 2 Test 1) — the new behavioral finding.
6. Domain-matched persona A/B (institutional personas strengthen the gradient in 3/6) — persona-specificity test.
7. Belief used **descriptively only** (points i–ii above). Human-validated judge (κ conservative 0.967 / 1.0 excl. API error).

## What MOVES to Paper 2
- The "behavior-vs-belief measurement modality is decisive" **thesis**.
- The SDT / psychometric **formalization** (d′, criterion, threshold functions).
- Mechanistic localization (steering vectors, layer/probe — the Joswin-style white-box depth).
- The measurement-modality × persona-type **factorial**.
- Multi-turn persistence (Turn-of-Flip / Number-of-Flip).

## What NEW work Paper 2 needs to stand alone (it CANNOT be written from current data)
1. A behavioral channel **genuinely independent of the A–D arg-max** (free-form generation w/ reasoning, or
   temperature-sampled response distributions) — otherwise the dissociation is tautological.
2. **Full-distribution / per-token belief trajectories**, not just A–D logprobs at two turns.
3. **Mechanistic** localization of where authority acts (needs a GPU box — see GPU_OBJECTIVE.md).
4. The **single-turn vs two-turn ablation** to separate protocol from persona effects.
→ Detailed boundary in PAPER2_OUTLINE.md.

## Net
Ship **Paper 1** now (empirical, honest-null, presence>prestige, confidence-doesn't-protect). Treat **Paper 2**
as genuinely new work, named in Paper 1's Future Work, not committed to. This is NOT salami-slicing: Paper 2
requires new data and asks a new (mechanistic/measurement) question.
