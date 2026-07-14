# STAGE 5 — Red Team: the rejection I would file, and what survives it

## Reviewer 2 report (harshest honest version; has read Mammen, Joswin, Wang, PARROT)

**Recommendation: Reject (resubmit possible).**

**Summary.** The authors test whether small open LLMs capitulate more to higher-authority challengers, using a
two-turn protocol and both behavioral and log-probability read-outs. Their pre-registered interaction test
fails; they instead argue that the *presence* of a counter-claim, not its authority, drives capitulation.

**Major concerns.**
1. **The headline is a post-hoc pivot from a failed registration.** The registered `tier×direction` interaction
   is null. The "presence beats prestige" claim rests on an `anon` condition the authors admit was added
   afterward. A pre-registered paper whose registered hypothesis fails and whose lead finding is unregistered
   is, at best, exploratory — it should not be sold with the authority of pre-registration it does not have for
   this claim.
2. **Substantially scooped by Wang et al. (2508.02087).** Wang already show sycophancy is driven by opinion
   *presence*, that expertise framing moves behavior ≤4.4%, and — via logit-lens/patching — that authority is
   not internally encoded. The present paper's central claim is the same, with weaker evidence (no mechanism,
   behavior = arg-max of the answer logits). What is left beyond "Wang, but two-turn and behavioral"?
3. **Does not actually engage Mammen on Mammen's terms.** The authors did not run Mammen's single-turn
   logit protocol, so "the gradient does not replicate" is not a like-for-like comparison — it may simply be
   that a two-turn commit-then-challenge design measures a different thing. Without the single-turn arm on the
   same items, the null is uninterpretable as a challenge to Mammen.
4. **Under-powered inference.** Six models cannot support the registered random-effects model; the fallback
   cluster-robust/fixed-effects inference on six clusters is fragile. Per-model "trends" rest on ~50–125 gated
   trials per cell.
5. **Construct validity of the manipulation.** With generic personas and no manipulation check, a null on the
   gradient is indistinguishable from a failed manipulation (the models may not read "professor" as authority
   at all — consistent with Wang). The domain-matched follow-up hints exactly at this, undercutting the
   headline.
6. **Cross-model comparisons use different item sets** (per-model baseline gate), so the resister/saturator
   taxonomy partly reflects which items each model happened to know.

**Minor.** "Free-form" overstates a single-letter output. Judge validation n=60 on a near-deterministic 3-way
task is not strong evidence. Figure titles assert more than panels show (ΔEntropy). Domain relabeled mid-study.

---

## Minimum defensible contribution that SURVIVES this review
Strip everything the red team can kill; what remains is still publishable:

1. **A pre-registered, human-validated, reproducible behavioral stress-test of authority sycophancy in small
   open models** — the artifact and protocol have standalone value regardless of the null.
2. **The null itself, reported honestly**, is a legitimate boundary-condition result: *the clean single-turn
   logit gradient does not translate into a two-turn behavioral commit-then-challenge setting.* Framed as
   "does not translate," NOT "fails to replicate," this is defensible and useful to the field.
3. **Direction dominance** (|coef|≈3.5) and **model-dependent susceptibility** (49–98%, not size-tracking) —
   robust, and corroborate Zhang/SycEval; not novel alone but solid supporting evidence.
4. **"Prior confidence does not protect"** (SDT_RESULTS.md Test 1) — this is the one finding NOT owned by Wang,
   Mammen, or PARROT, needs no mechanism, and is directly safety-relevant. **Make this co-headline with
   presence-beats-prestige**, because it is the most defensible novel claim.
5. **Convergent (not competing) evidence with Wang**, behaviorally and across a graded ladder — reframed as
   *triangulation* (behavioral two-turn + their single-turn internal → same conclusion by independent methods),
   which is a genuine contribution, not a scoop victim.

## What the authors MUST do to lift it from Reject to Accept
- Reframe presence-beats-prestige as **convergent with Wang**, cited up front (kills concern 2).
- Add the **single-turn ablation** on ≥2 models (kills concern 3; ~overnight CPU — SCOPE_DECISION/PAPER2 pilot).
- Lead Limitations with the post-hoc disclosure + fixed-effects justification (blunts 1 and 4).
- Add the **common-item-subset** robustness check for the taxonomy (kills concern 6).
- Promote **"confidence doesn't protect"** to co-headline (adds the non-scooped contribution).
- Drop every behavior-vs-belief dissociation claim and Figure 4 (removes the weakest target).

**Verdict:** with those, this is a legitimate TMLR-caliber empirical + boundary-condition paper. Without the
single-turn ablation and the Wang reframe, it is a borderline reject.
