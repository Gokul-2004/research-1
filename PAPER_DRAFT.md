# Presence, Not Prestige: The Source of a Counter-Claim Barely Matters to Sycophancy in Small Open LLMs

> **PAPER 1 DRAFT (modular).** Spine = presence-beats-prestige + "prior confidence doesn't protect"
> (SCOPE_DECISION.md option B; SDT reframe deferred to Paper 2 per SDT_RESULTS.md). Every quantitative
> claim carries a `[source]` tag to the file it came from. Prose is scaffolding — swap freely.
> Numbers verified in VERIFICATION.md unless flagged `[UNVERIFIED]`.

---

## Abstract
Large language models often abandon a correct answer when a user pushes back — *sycophancy*. A recent line
of work reports that this scales with the **authority** of the challenger, producing a clean graded
"dose-response." We test that claim in the models most people actually run — six open-weight LLMs, 3B–9B
parameters, five lineages — under a pre-registered, two-turn protocol in which the model first commits to an
answer and is then challenged by a source of varying authority (an anonymous "someone," a high-school student,
a graduate student, a professor), in both wrong-pushing and right-pushing directions, across three objective
domains. We measure behavior (answer changes, validated by a human-checked LLM judge, κ≈0.97 [VERIFICATION.md])
and, descriptively, internal token log-probabilities. Our pre-registered test for a graded authority effect is
**not supported** (tier×direction interaction ≈ 0, p≈0.95, robust to model fixed-effects and a belief
covariate [VERIFICATION.md; SDT_RESULTS.md]). Instead we find: (1) **direction dominates** — an incorrect
counter-claim collapses accuracy while a correct one barely helps (|coef|≈3.5, p<0.0001 [VERIFICATION.md]);
(2) **presence beats prestige** — for four of six models a nameless "someone" is as corrosive as a professor,
behaviorally and in log-probability [VERIFICATION.md]; (3) **prior confidence does not protect** — models
abandon even strongly-held correct answers ~83% of the time under an incorrect challenge, with pre-pressure
belief strength failing to predict flipping [SDT_RESULTS.md]; and (4) susceptibility is strongly
**model-dependent** (≈49–98% capitulation, not tracking size [VERIFICATION.md]). A follow-up shows that
domain-matched *institutional* personas strengthen the (weak) gradient in three of six models
[POINTS_FOR_PAPER.md §15], so persona design matters but does not rescue a universal effect. We conclude that
in small open models the *presence and direction* of disagreement, not the *authority* of its source, drives
capitulation — a more fragile and less orderly picture than single-turn logit studies suggest.

## 1. Introduction
- Problem + stakes: small open models are deployed on consumer/edge hardware and increasingly give advice;
  sycophancy there is under-studied and consequential [PLAN.md].
- The specific question (pre-registered): does capitulation rise monotonically with the *authority* of the
  challenger? [ANALYSIS_PLAN.md]
- Contributions (honest, post-hoc-aware):
  1. A pre-registered, **two-turn behavioral** test (model commits, then is challenged) with a matched
     **anonymous** baseline — a protocol prior graded-authority work did not use.
  2. Evidence that **presence, not prestige** governs capitulation in most small open models, converging with
     Wang et al. (2508.02087)'s single-turn internal finding but shown *behaviorally* and across a graded ladder.
  3. A new result: **prior confidence provides almost no protection** against an incorrect challenge.
  4. A documented **null** on the graded gradient, plus a persona-design follow-up bounding when a gradient
     (weakly) appears.
- Explicitly flag: the anonymous rung and the domain-matched follow-up were added post-hoc (exploratory)
  [DEVIATIONS #7]; we report the registered null first.

## 2. Related Work & Positioning (write against the novelty threats)
- **Mammen et al. 2601.13433** — clean monotonic authority gradient, single-turn, logit-only, 11 models.
  Position: we do *not* replicate the clean gradient under a commit-then-challenge behavioral protocol; we do
  not claim "single-turn vs two-turn" flatly (they also use a two-step interaction) — the real contrast is
  *the model commits before the challenge* [VERIFY_MAMMEN.md].
- **Joswin et al. (ICML 2026 MechInterp workshop)** — mechanistic; claims the graded effect needs
  domain-matched institutional personas. Position: we behaviorally *test* this and find it holds in 3/6 models
  [POINTS_FOR_PAPER.md §15]. Cite by author/title/venue, never "746" [CLAUDE.md].
- **Wang et al. 2508.02087 (AAAI 2026)** — presence>expertise, expertise ≤4.4%, authority not encoded
  internally (single-turn, mechanistic). Position: our behavioral, two-turn, six-model result **converges**
  with theirs and extends it with a graded ladder, an anonymous matched rung, and the confidence-doesn't-protect
  finding. Cite prominently as convergent — do NOT let it look ignored [SPINE_DECISION.md (d)].
- **PARROT 2511.17220** — 22 models, single authority level, calibration tracking; their small-model collapse
  supports our saturation finding. **Zhang 2508.13743** — size≠robustness (matches our heterogeneity).
  **SycEval 2502.08177 / Sharma 2310.13548** — direction/persistence (matches our direction dominance).
- Human-behavior ancestry (one guarded paragraph, functional analogy only [LIT_INCORPORATION_LIST.md §C]):
  Asch (presence of a dissenter, not majority size); Kelman 1958 (compliance vs internalization — frames why
  we look past behavior); judge–advisor systems (humans weight advisor expertise; these models largely do not).

## 3. Method
- **Models (6, 5 lineages, 3B–9B):** Qwen2.5-3B, Llama-3.2-3B, Qwen2.5-7B, Mistral-7B-v0.3, Phi-3.5-mini,
  Gemma-2-9B [POINTS_FOR_PAPER.md §2].
- **Items:** 150 objective MCQs, 3 domains — Science (ARC-Challenge), History (MMLU), Factual (TruthfulQA);
  verified ground truth [PLAN.md; POINTS_FOR_PAPER.md §2].
- **Design:** two-turn (commit → challenge); 5 rungs (control, anon, low=HS, medium=grad, high=professor);
  2 arms (incorrect / correct endorsement). Note control = Sharma-style stronger challenge, reported
  separately; **anon is the matched zero-authority floor** [DEVIATIONS #6].
- **Baseline gate:** analyze only items answered correctly unprompted (knowledge filter, Vennemeyer 2509.21305)
  — gate survival 64–86% [VERIFICATION.md].
- **Measurement:** behavioral answer (single letter, temp 0) — describe honestly as **answer revision under
  pressure after commitment**, NOT "free-form" [DEVIATIONS #8]; plus A–D log-probabilities used
  **descriptively**. Judge: Gemini 2.5 Flash, human-validated (κ conservative 0.967; 1.0 excluding one API
  error [VERIFICATION.md]) — state n=60 and that the 3-way task is easy, so do not oversell reliability.
- **Engine/repro:** CPU fp16, HF Transformers, temp 0, fresh session per trial, append-only JSONL, frozen
  SHA-256 manifest (24/24 verified [VERIFICATION.md]).
- **Pre-registration & deviations:** ANALYSIS_PLAN.md committed before inference; all departures in
  DEVIATIONS_FROM_PREREGISTRATION.md (incl. the GLMM→GEE/fixed-effects change and the post-hoc conditions).

## 4. Results
### 4.1 The pre-registered graded-authority effect is not supported (Fig 1)
tier×direction interaction ≈ 0 (coef +0.01, p≈0.95 pooled; p=0.78 with model fixed-effects + belief covariate)
[VERIFICATION.md; SDT_RESULTS.md]. Report as a clean, robust null. `Fig 1` = both arms roughly flat across
tiers with a large vertical gap between them.

### 4.2 Direction dominates (Fig 8 → renumber Fig 3)
Incorrect endorsement flips 49–98%; correct endorsement flips ~0–20% (|coef|≈3.5, p<0.0001) [VERIFICATION.md].
The asymmetry is itself evidence against pure recency (a last-message effect would be direction-symmetric).

### 4.3 Presence beats prestige (Fig 2)
Behaviorally, the anonymous rung already produces most of the capitulation; adding named authority barely
moves it for the saturating models. In log-probability, anon ≈ high for 4/6 (Llama, Mistral, Qwen-3B,
Qwen-7B); for Phi and Gemma authority adds further [VERIFICATION.md #1 — state as 4/6, NOT 5/6]. `Fig 2` =
six per-model flip ladders including the anon point.

### 4.4 Prior confidence does not protect (NEW — needs a new figure, see FIGURE_AUDIT.md)
Pre-pressure belief strength (turn-1 log-prob gap) does not predict flipping: pooled logistic slope ≈ 0;
even in the highest pre-pressure-confidence quintile, models flip ~83% under an incorrect challenge
[SDT_RESULTS.md Test 1–2]. This is a distinct, alarming behavioral finding and needs no belief-dissociation claim.

### 4.5 Susceptibility is model-dependent, not size-tracking (Fig 7)
Overall incorrect-arm flip: Mistral 52%, Gemma 55%, Phi 77%, Qwen-3B 82%, Llama 97%, Qwen-7B 97%
[VERIFICATION.md] — a resister/saturator split that does not track parameter count (Qwen-7B saturates while
the larger Gemma-9B resists). `Fig 7` = bimodal robustness bar chart.

### 4.6 Exploratory: domain-matched personas partly strengthen the gradient (Fig 3 → renumber Fig 4)
Institutional personas (undergrad→PhD→Nobel) strengthen the gradient in 3/6 vs generic (Gemma, Llama,
Qwen-3B), leave 2 similar (Qwen-7B, Phi), collapse Mistral into saturation [POINTS_FOR_PAPER.md §15;
VERIFICATION.md #2 — distinguish "strengthen vs generic" (3/6) from "gradient exists under DM" (5/6)].
Label exploratory; do not cite ANALYSIS_PLAN §7d for it (covers model-set expansion only) [DEVIATIONS #7].

## 5. Discussion
- The honest headline: in small open models, **the presence and direction of a counter-claim, not the
  authority of its source, drives capitulation.** The clean graded gradient of single-turn logit work is
  fragile and largely does not survive a two-turn behavioral protocol with a matched anonymous baseline.
- Reconcile the field: we sit with Zhang/SycoEval-EM (model-dependent) and converge with Wang (presence>
  expertise), while bounding Mammen/Joswin (the gradient appears mainly with stronger, domain-matched personas
  and even then not universally).
- Safety upshot (lead the Alignment Forum post with this): credential does not gate capitulation, and prior
  confidence does not protect — any pushback, from anyone, flips a large fraction of correct answers. For
  edge-deployed advice models this is the consequential failure mode.

## 6. Limitations (write so it can't be weaponized — see §6 note in REVIEW_ME.md)
- Registered interaction not supported; the presence result and the domain-matched follow-up are exploratory
  (post-hoc), reported as such with timestamps [DEVIATIONS #7].
- Six models cannot support the registered random-effects GLMM; we use model fixed-effects + report effect
  sizes and per-model consistency rather than lean on a single clustered p-value [DEVIATIONS #1; SPINE_DECISION].
- Behavioral channel is single-letter (arg-max of the answer logits), not free-form; we therefore make **no**
  behavior-vs-belief "dissociation" claim (deferred to future work) [SDT_RESULTS.md; SCOPE_DECISION.md].
- Generic personas may under-encode authority; the domain-matched follow-up partially addresses this but no
  manipulation check was run [INDEPENDENT_REVIEW.md].
- Two-turn design confounds commitment/recency with authority for absolute rates (held constant across tiers,
  so the interaction is unaffected); position bias is a limitation, not machinery [ANALYSIS_PLAN.md; CLAUDE.md].
- Scope: 6 small models, 3 objective-MCQ domains, English, single language. Judge n=60 on an easy 3-way task.

## 7. Conclusion
Under a pre-registered two-turn protocol, authority-graded sycophancy largely fails to appear in six small open
models. What remains is starker: a correct answer is abandoned because *someone* disagreed and pushed the wrong
way — regardless of who they are, and regardless of how confident the model was. Measurement protocol and
persona design materially change the picture, which cautions against strong claims about a universal authority
gradient from any single paradigm.

## Venue (STAGE 6 — see REVIEW_ME.md)
Primary **TMLR** (claims-audited review rewards a pre-registered null + full deviation disclosure; free; open).
Fallback **IEEE Access** (sound + open, ~$2,160 APC, out-of-field reviewers). **Alignment Forum** post at
preprint time, safety-upshot lead. Reasoning in REVIEW_ME.md.
