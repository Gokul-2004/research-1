# PAPER_SELECTION — which paper maximizes honest IEEE Access acceptance odds
> Decision doc (Fable pass, 2026-07-14). Scored against Wang 2508.02087 + Mammen 2601.13433 scoop-risk
> and IEEE Access's soundness/novelty/clarity bar. Inputs: fab_inference.md (adversarial recompute,
> post-single-turn), KEY_PAPERS_DEEP_DIVE.md, SCOPE_DECISION.md, VERIFICATION.md, raw JSONL.

## Candidates scored

Criteria (0–5): SOUND = supported by verified data; NOVEL = net of Wang/Mammen/Kim–Khashabi (2509.16533);
CLEAN = one-sentence claim + strong figure; RISK = inverse scoop/overclaim risk. IEEE Access gates on
soundness, but a reviewer still needs a reason to say yes.

| # | Spine | SOUND | NOVEL | CLEAN | RISK | Verdict |
|---|---|---|---|---|---|---|
| A | **Commitment structure dominates** (1.9–9.3× per-model amplification, McNemar p<10⁻¹⁵ ×6) + presence/prestige refinement | 5 | 4 | 5 | 4 | **CHOSEN** |
| B | Presence-not-prestige leads | 4 | 2 (Wang core claim) | 4 | 2 | support, not spine |
| C | Heterogeneity / measurement taxonomy | 4 | 2 (Zhang, SycoEval-EM) | 3 | 3 | one section |
| D | Pure negative result (gradient fails to replicate) | 5 | 2 (null-only, and NOT clean — see below) | 3 | 2 | reported inside A |

## Why A wins (from the numbers, not the prior)
1. **It is the largest effect in the entire dataset**: same items, same models, same tiers — adding only
   a prior self-commitment multiplies caving 1.9–9.3× (median ≈3×), significant at p<10⁻¹⁵ in ALL six
   models, saturators and resisters alike (fab_inference §survived; re-verified in src/paper_numbers.py).
   Effects this large, this uniform, and this cheaply stated are what soundness-gated venues accept.
2. **Scoop check**: Kim & Khashabi 2509.16533 have turn-structure on frontier models with other-LLM
   rebuttals of evaluator judgments; Wang has presence-over-expertise single-turn logits; Mammen has the
   authority gradient. NOBODY has the per-model commitment penalty on small open weights under a true
   self-commitment gate, factorially crossed with authority tiers, an anon floor, and a persona-design
   A/B on one item set — that crossing is the contribution. (fab_inference NOVELTY VERDICT concurs.)
3. **Candidate D is not clean**: the "null is robust" story died in adversarial review — pooled single-turn
   FE trend +0.094/rung p=0.024, and anon≠high with inconsistent sign in 3/6 (McNemar). A null-led paper
   would have to spend its abstract on caveats. Inside paper A these become *supporting texture*:
   the pre-registered interaction failed (reported plainly), and what remains is small, model-dependent,
   inconsistent-sign modulation — dominated by commitment structure.
4. **B is Wang's claim**; as spine it invites "confirmatory replication" rejection. As §2 of A it becomes
   independent behavioral confirmation + a sharper refinement Wang cannot see (±17–22pp inconsistent-sign
   prestige modulation in non-saturated models vs their ≤4.4% expertise effect).

## The chosen paper (one paragraph)
Pre-registered, human-validated (κ=0.967, main run) study of six open 3B–9B models × three domains ×
five authority rungs × two endorsement directions, in TWO turn structures on identical items. The
pre-registered authority×direction interaction FAILS (reported as failure). What actually governs
capitulation, in order of effect size: (1) prior self-commitment — removing it collapses caving 1.9–9.3×,
McNemar p<10⁻¹⁵ in all six models; (2) endorsement direction (|β|≈3.5, p<10⁻⁴); (3) presence of any
counter-claim (an anonymous "someone" achieves most of the effect); with source authority contributing
only a small, model-dependent, inconsistent-sign modulation (±17–22pp where models have headroom) that
institutional domain-matched personas partially strengthen (3/6). Prior confidence does not protect.
Title (fab_inference): **"Presence, Not Prestige: Commitment Structure Dominates Source Authority in the
Sycophancy of Small Open LLMs."**

## Locked no-say list (constraints honored)
- No rescue of the failed pre-registration; ANALYSIS_PLAN.md cited with commit timestamp (427d75a, 2026-06-29).
- No "flat in single-turn" blanket claim; no universal "anon ≈ professor"; no bounding/refuting Mammen via
  protocol (per-model single-turn gradients are ns on our items → difference unexplained; stated as limitation).
- Confirm-and-extend Wang; ΔH non-replication = scope boundary; Mistral–Mammen contrast = unresolved,
  domains/personas/measurement confounded.

## Acceptance estimate
~65–70% as fab_inference read the claims; target ~75% after its four reframes are folded in (done in this
manuscript) — the residual risk is process (authorship/APC/licensing) and the unjudged single-turn labels
(mitigated by scoping κ + three verified integrity checks; killable entirely by one API evening).
