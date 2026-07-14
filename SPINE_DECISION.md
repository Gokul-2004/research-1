# STAGE 1 — Spine + Novelty (co-author, skeptical-reviewer hat)

## (a) The 3 strongest reasons a reviewer rejects this as-is
1. **Registered study failed; the compelling result is post-hoc.** The pre-registered `tier×direction`
   interaction is ≈0 (VERIFICATION.md). The finding that carries the paper — presence-beats-prestige —
   comes from the `anon` rung added *after* the fact (DEVIATIONS #7). Left unframed, this reads as
   HARKing: "the registered thing didn't work, so they found something else and led with it."
2. **The behavior-vs-belief "dissociation" is a measurement artifact as stated.** The behavioral DV is the
   arg-max over {A,B,C,D} of the *same* logits the belief DV reads continuously. "Behavior saturates while
   belief grades" is the expected signature of a thresholded readout of one signal, not two dissociable
   systems. As written, Reviewer 2 kills the novel claim in one sentence: *"your two measures are the same
   quantity at two resolutions."*
3. **Novelty overlap.** Mammen (2601.13433) owns the graded-authority phenomenon; Wang (2508.02087, AAAI'26)
   owns "presence, not expertise" *with internal mechanism*; PARROT (2511.17220) owns large-scale
   susceptibility+calibration. Unpositioned, this looks like "a failed replication of Mammen + an increment
   on Wang." (Secondary: 6 clusters can't fit the registered GLMM; generic personas may not encode as
   authority; single-letter output is not "free-form.")

## (b) With the primary FAILED, what is the paper actually about? — three candidate spines
- **Spine A — Direction dominance** (incorrect push devastates, correct barely helps; \|coef\|≈3.5). *Robust,
  huge, clean.* But it is the **least novel** thing in the corpus (SycEval, Sharma, everyone). A paper spined
  on direction is a replication. → keep as a *result*, not the spine.
- **Spine B — Presence beats prestige** (disagreement itself, not its authority, drives caving; 4/6 on belief,
  VERIFICATION #1). *Striking, ecologically sharp.* But (i) it is **partly scooped by Wang**; (ii) it rests on
  the **post-hoc anon rung**; (iii) it is **4/6, not universal**. Strong as the empirical centerpiece; risky as
  the *sole* spine.
- **Spine C — Behavior-vs-belief as a signal-detection / thresholding phenomenon.** Recast: behavioral flips
  are a *thresholded readout* of a graded latent belief; authority and model identity move the **decision
  criterion**, not (only) the latent sensitivity. *Most novel, nobody else's, and it ORGANIZES everything
  else* (direction, heterogeneity, presence>prestige, the failed gradient) under one lens. **Highest novelty,
  highest risk** — depends entirely on whether the reframe is non-circular and robust (Stage 2).

### DECISION (conditional, resolved in Stage 2.5)
**Primary spine = C (signal-detection/threshold reframe), with B as the empirical centerpiece that motivates
it, and A + the pre-registered null as robust supporting results.** Rationale: C is the only genuinely
un-scooped contribution, and it converts the paper's biggest weakness (artifact critique of #2) into its
thesis. **Fallback, per the Stage 2.5 rule:** if Stage 2 shows the SDT reframe is circular or fragile, demote
to **Spine B** as the spine and defer the SDT formalization to Paper 2.

## (c) Pressure-test: must behavior-vs-belief be recast as thresholding/SDT? — YES, and here is the crux
- **The hunch is correct and necessary.** Without the reframe, claim #2 is a fatal confound (behavior = argmax
  of the belief signal). With it, the contribution becomes: *where does each model's threshold sit, and what
  moves it?* — a real, defensible question.
- **The reframe's OWN risk (the thing Stage 2 must clear): circularity.** If the "signal" were the *turn-2*
  belief gap, then flip = (turn-2 argmax crossed) is mechanically the same event → circular, dead on arrival.
  **The escape:** use the **turn-1 (pre-pressure) belief gap** as the latent signal. Turn-1 belief is measured
  *before* the endorsement; the flip is *post*-pressure behavior. Relating a pre-pressure latent to a
  post-pressure behavior is a legitimate psychometric function, NOT circular. Stage 2 must confirm (i) P(flip)
  genuinely declines with turn-1 belief strength (there is real slack, not a step function), and (ii) the tier
  effect loads on criterion more than on sensitivity. If both hold → Spine C. If P(flip) is a near-deterministic
  step in turn-1 belief (no slack) or the d′/criterion split is under-identified → the reframe is cosmetic →
  fall back to Spine B, defer to Paper 2.

## (d) Novelty stress-test vs the threats — where I'm scooped, what's defensibly mine
| Prior work | What they own (we're scooped on) | What stays defensibly ours |
|---|---|---|
| **Mammen 2601.13433** (single-turn, logit-only, 11 models, clean gradient) | the graded-authority phenomenon itself; steering-vector mechanism | commit-then-challenge **two-turn behavioral** protocol; the **anon** matched baseline; behavioral **heterogeneity**; the **null** as a boundary condition. (Per VERIFY_MAMMEN: do NOT claim "single-turn vs two-turn" flatly — real diff = *model commits first*.) |
| **Joswin workshop** (mechanistic; claims graded effect needs domain-matched institutional personas) | white-box mechanism; the persona-specificity claim | we **behaviorally test** their persona claim across 6 models → holds in 3/6 (a test they invite). Claim no mechanism. |
| **Wang 2508.02087** (single-turn, internal; presence>expertise, expertise ≤4.4%, authority not encoded) | **presence-beats-prestige, with mechanism** — the dangerous overlap | two-turn **behavioral** (they're single-turn-internal); a **graded ladder + anon rung** (they contrast presence vs expertise, not a ladder); **dual** measure on same items; domain-matched A/B; pre-registration+human validation. Cite as **convergent, complementary** — never ignore. |
| **PARROT 2511.17220** (22 models, single authority level, calibration tracking) | large-scale susceptibility + calibration shift | graded ladder; two-turn; presence-vs-authority contrast. Their small-model collapse **supports** our saturation. |

**Net defensibly-mine, ranked:** (1) the SDT/threshold account of authority sycophancy (if Stage 2 clears it) —
least scooped; (2) presence>prestige demonstrated **behaviorally, two-turn, across 6 small models**, converging
with Wang's single-turn-internal result; (3) the model-heterogeneity taxonomy; (4) the pre-registered null on
the graded gradient as a cautionary methodological result; (5) human-validated behavioral judging. **Without
(1), the paper is "convergent-with-Wang + boundary-on-Mammen" — publishable but incremental. (1) is what makes
it stand alone.**
