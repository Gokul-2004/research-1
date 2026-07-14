# Independent Re-Analysis + Problem Register (2026-07-08)

> Computed directly from raw JSONL (not from repo summaries) with self-contained scripts
> (pure-Python; no numpy/statsmodels available in the clone). Purpose: verify the claimed
> results and surface real problems before drafting.

## Verification verdict: results reproduce
Every headline number recomputed from raw data matches the repo's claims:

| Quantity | Repo claim | Independently recomputed | Match |
|---|---|---|---|
| Gate survival (6 models) | 77/64/83/71/77/86% | 77.3/64.0/83.3/70.7/77.3/86.0% | ✅ |
| Behavioral flip taxonomy (incorrect arm) | saturators 81–98%, resisters 49/59%, Phi graded | Qwen3B 81, Llama 97, Qwen7B 98, Mistral 49, Gemma 59, Phi 60→94 | ✅ |
| Direction effect | coef −3.50, p<0.0001 | \|coef\|=3.53, p<0.0001 | ✅ |
| tier×dir interaction (confirmatory) | coef −0.013, p=0.95 | coef +0.011 (≈0), n=5510 | ✅ NOT significant |
| Anon-ladder monotonicity | only Gemma monotonic | only Gemma monotonic (5/6 = NO) | ✅ |
| Domain-matched Spearman ρ | Gemma −0.25, Llama −0.24, Phi −0.32, Qwen3B −0.17, Mistral −0.09 ns, Qwen7B −0.11 | −0.254, −0.236, −0.318, −0.173, −0.089, −0.107 | ✅ |
| Judge vs regex agreement | ~99.9% | 99.7–99.8% | ✅ |

Conclusion: the data and the honest write-up are trustworthy. The problems below are about
interpretation, inference, and framing — not data integrity.

## Experiments performed (verified inventory)
1. **Timing spike** — CPU fp16 feasibility; ~5.8–5.9 s/scoring, 3B≈7B (bandwidth-bound). GO.
2. **Power pilot** — 10 Q/domain gate-survival check; GO at 50 Q/domain.
3. **Main run** — 6 models × 150 Q × 4 rungs (control/low/medium/high) × 2 arms, GENERIC personas, two-turn, dual measurement.
4. **Condition B (anon)** — added POST-HOC: the "someone thinks X" rung, 6 models × 2 arms.
5. **Domain-matched run** — 6 models × 3 rungs (low/med/high) × 2 arms, INSTITUTIONAL personas.
6. **Judge** — Gemini 2.5 Flash, 5,513 trials (2,090 REGRESSIVE / 3,199 HELD / 224 OTHER; 7 API errors).
7. **Human validation** — n=60, κ=0.967.

## PROBLEM REGISTER (ranked)

### Tier 1 — core scientific tensions
1. **The headline rests on a post-hoc condition.** The pre-registered confirmatory test failed
   (interaction ≈ 0). The compelling story — "presence, not authority" — comes entirely from the
   anon rung, which was Condition B, added after the fact (exploratory). Well-disclosed, but the
   paper's main claim is not the pre-registered one. Reviewers will press this hard.
2. **6 clusters can't support the pre-registered inference.** The random-effects GLMM
   (`(1|model)`) is unfittable with 6 models (VB gave a spurious z=10.4 → fell back to GEE). But
   GEE cluster-robust SEs with 6 clusters are themselves anti-conservative (small-cluster problem).
   The confirmatory p-value stands on shaky inferential ground *either way* — mitigated only because
   the interaction coefficient is so close to zero (I confirmed ≈0.01) that no reasonable SE makes
   it significant.
3. **The behavior-vs-belief "dissociation" may be a thresholding artifact, not a modality one.**
   Behavior = single forced letter = argmax over the same logprobs the belief arm reads continuously.
   "Behavior saturates while belief still grades" is arithmetically expected: once the belief margin
   crosses zero the letter flips, and further erosion moves the logprob but not the letter. So the
   claim "measurement *modality* is decisive" is arguably "the *binary readout* discards the graded
   signal." CONSTRUCTIVE FIX: reframe as a thresholded readout of a continuous belief (psychometric
   function: flip ~ logistic(belief margin)) + SDT criterion-vs-sensitivity — this is honest AND stronger.
4. **"No authority gradient" is slightly too strong.** Among NAMED personas (low→med→high) the
   belief gap IS monotonic for 4/6 models (Phi −3.0→−6.0→−9.8; Qwen3B −3.5→−4.4→−5.2; Qwen7B
   −9.2→−10.8→−11.5; Llama −2.9→−3.1→−3.6). The correct claim is subtler: *an anonymous assertion
   already produces most of the shift; authority level adds little beyond presence* — NOT "authority
   does nothing."

### Tier 2 — comparability / positioning
5. **Mammen differentiators are weaker than the docs assumed** (from VERIFY_MAMMEN): the
   "two-turn vs single-turn" contrast is real only as "commit-first vs Question-then-Hint"; and the
   "Mistral grades steepest" claim was FALSE (agent error, already flagged for deletion).
6. **Novelty threat — Wang et al. 2508.02087 (AAAI 2026)** reports essentially the same headline
   (presence not authority; expertise ≤4.4%). Must cite-and-differentiate before a reviewer does.
7. **Confident-error (ΔH<0) non-replication** is a scope boundary (their reasoning/medical/logit vs
   our non-reasoning/broad/two-turn), not a flat contradiction. Frame carefully.

### Tier 3 — data / pipeline hygiene
8. **Fragmentation invites a wrong-subset number.** The anon rung lives in separate `__anonB.jsonl`
   files, the main run in timestamped files, domain-matched in another dir. Any analysis MUST
   explicitly merge anon — I hit the nan trap on the first pass. Verify the committed `analyze*.py`
   merges anon everywhere it should.
9. **Domain-matched has only low/med/high** (no control/anon) → cannot run the anon-falsification
   *within* the domain-matched data; the generic-vs-DM comparison is limited to 3 rungs.
10. **Modest per-cell n after gating** (Llama 96, Mistral 106 questions; ~50–125 trials per tier×arm).
    Fine for descriptives, thin for a 3-way tier×dir×domain interaction.
11. **Minor non-monotonicity even in "clean" cases** (Phi domain-matched: med 94.8% > high 91.4% flip).
