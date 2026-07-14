# STAGE 4 — Figure Audit
> All 8 PNGs in results/figures/ viewed directly. Verdict per figure against the chosen spine
> (presence-beats-prestige + confidence-doesn't-protect; behavior-vs-belief deferred to Paper 2).

| Fig | What it shows | Supports its claim? | Verdict for Paper 1 |
|---|---|---|---|
| **fig1** interaction null | both arms ~flat across anon→high, large gap between them | YES — clean visual of the null + direction gap | **KEEP → Figure 1.** Fix axis label to "accuracy retained (%)"; state error bars = Wilson 95%. |
| **fig2** per-model flip ladders (incl. anon) | 6 panels; saturators flat-high, resisters low, Phi rising; anon is leftmost point | YES — heterogeneity + presence (anon already high for saturators) | **KEEP → Figure 2.** The workhorse. Ensure anon is visually labeled as the matched floor. |
| **fig3** generic vs domain-matched | 6 panels, generic vs institutional personas | YES (exploratory) — DM strengthens Gemma/Llama/Qwen-3B; Phi med>high non-monotonic | **KEEP → Figure 4**, label "exploratory". Note the Phi non-monotonicity in caption, don't hide it. |
| **fig4** behavior vs belief (POST-pressure) | scatter: flip% vs post-pressure belief gap; strong negative correlation | **NO — misleading for Paper 1.** Uses *post*-pressure belief, so behavior (arg-max) and belief are the near-same quantity → shows correlation, not dissociation; and the title invites the deferred claim | **CUT from Paper 1** (move to Paper 2). This is exactly the circular framing SDT_RESULTS.md rejected. |
| **fig5** ΔAccuracy (Mammen-style) | per-model accuracy drop by tier; non-monotonic, lines cross | Partly — supports "not clean monotonic" but overlaps fig1/fig2 | **APPENDIX** (Mammen comparison). Redundant as a main figure. |
| **fig6** ΔEntropy | positive ΔH (less certain) vs Mammen's negative | Belief-signal figure; the confident-error non-replication is a *scope boundary*, not a contradiction | **APPENDIX**, and **soften title** — current "DOES NOT replicate" overclaims; frame as reasoning/medical/logit (theirs) vs non-reasoning/broad/two-turn (ours) [VERIFY_MAMMEN.md]. |
| **fig7** robustness split (bimodal) | resisters (Mistral/Gemma) vs saturators, 30% split line | YES — clean heterogeneity visual | **KEEP → Figure 5** (or merge into fig2's story to save a float). |
| **fig8** direction asymmetry | regressive ≫ progressive bars per model | YES — the recency rebuttal made visual | **KEEP → Figure 3.** One of the strongest reviewer-defense figures. |

## Figures MISSING that the chosen spine needs
- **NEW Figure (confidence-doesn't-protect):** flip rate vs turn-1 belief-gap quintile (from SDT_RESULTS.md
  Test 1) — currently no figure exists for §4.4, the paper's new finding. **Create it.** A flat/near-flat line
  at ~75–85% is the whole point; annotate "even highest pre-pressure confidence → ~83% flip."

## Net figure plan for Paper 1
Figure 1 = fig1 (null). Figure 2 = fig2 (per-model ladders + presence). Figure 3 = fig8 (direction/recency).
Figure 4 = fig3 (generic vs domain-matched, exploratory). Figure 5 = fig7 (bimodal robustness) OR fold into F2.
NEW Figure = confidence-doesn't-protect. Appendix = fig5, fig6 (reframed). **CUT = fig4** (circular; Paper 2).

## Caption discipline (applies to all)
State n, error-bar definition (Wilson 95%), gated-subset note, and "exploratory" where applicable. Do not use
"free-form" anywhere. Do not title any figure with a claim stronger than the panel supports (fig6 offender).
