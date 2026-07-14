# STAGE 0 — Independent Verification
> Recomputed from canonical `results/inference/*.jsonl` (hash-frozen, 24/24 OK vs RESULTS_MANIFEST)
> + `judge_bundle/results/judged/*`. Pure-Python, no numpy/statsmodels. Script: `src/verify_stage0.py`.
> Reproduced independently by a skeptical co-author; discrepancies flagged, not smoothed.

## Manifest integrity
- `shasum -a 256 -c RESULTS_MANIFEST.sha256` → **24/24 data files OK.** (1 "improperly formatted" line = the
  human-readable `manifest frozen 2026-07-07` footer, benign.) Data is intact and matches the freeze.

## Headline numbers — REPRODUCED ✅
| Claim (POINTS_FOR_PAPER.md) | Reproduced value | Verdict |
|---|---|---|
| Gate survival 77/64/83/71/77/86% | 77.3/64.0/83.3/70.7/77.3/86.0 (Qwen3B/Llama/Qwen7B/Mistral/Phi/Gemma) | ✅ exact |
| Saturators 81–98% / resisters 49–59% / Phi graded 60→94 | Qwen3B 81.9, Llama 96.7, Qwen7B 97.4, Mistral 51.9, Gemma 54.9, Phi 60.3→94.0 | ✅ |
| Direction \|coef\|≈3.5, p<0.0001 | coef +3.532, p<1e-4 (n=5,510) | ✅ |
| tier×dir interaction ≈0, p=0.95 → **PRIMARY HYPOTHESIS FAILED** | coef +0.011, p=0.89 (naive; cluster-robust only widens) | ✅ failed, confirmed |
| Judge vs regex agreement ~99.9% | 99.82% (5,496/5,506) | ✅ |

**The pre-registered primary hypothesis is confirmed FAILED by independent recomputation.** The direction
effect is the single robust pooled result. Both stand.

## Discrepancies FOUND — flag before any draft ⚠️
1. **"presence ≈ prestige for 5/6" is OVERSTATED — it is 4/6 on the belief metric.**
   On belief-gap(anon) vs belief-gap(high), incorrect arm: anon ≥ high (presence wins) for **Llama, Mistral,
   Qwen-3B, Qwen-7B (4/6)**. For **Phi (−4.6→−9.8) and Gemma (+1.3→−1.0), authority DOES add beyond anon.**
   → Correct claim: "for a majority of models (4/6) a nameless source is as corrosive as a professor; for
   two (Phi, Gemma) authority adds further." Do NOT write "5/6" or "6/6". (POINTS §3g's "only Gemma monotonic
   across the full ladder" is a *different* metric and is separately true.)
2. **"institutional personas help 3/6" vs "5/6 show a gradient" — two different questions, don't conflate.**
   - Does a belief gradient EXIST under domain-matched personas (ρ<−0.10, low<med<high)? → **5/6** (all but Mistral).
   - Does domain-matched STRENGTHEN vs generic? → **3/6** (Gemma, Llama, Qwen-3B), per POINTS §15.
   Both are true. The paper must state which it means each time. The defensible headline is the *strengthening*
   comparison (3/6), because "gradient exists" alone doesn't isolate the persona-type manipulation.
3. **Human κ=0.967 reproduces ONLY if the 1 judge API ERROR is counted as a disagreement (conservative).**
   Excluding idx 23 (judge returned ERROR, not a label): 59/59 agree → raw 100%, **κ=1.000**. Counting the ERROR
   as a miss (POINTS' choice): 59/60 → 98.3%, κ=0.967. POINTS reports the CONSERVATIVE number — good practice,
   keep it, but state the handling explicitly. **Caveat for the paper:** n=60 on a near-deterministic
   single-letter 3-way task makes high κ unremarkable; do not oversell judge reliability as a headline strength.

## Minor
- Gemma overall incorrect-arm flip: I get 54.9% (5 tiers incl. control/anon); POINTS says 59%. Averaging
  convention differs (which rungs are pooled). Immaterial to any claim; pick one convention and state it.

## Numbers I could NOT independently source
- POINTS §3d Spearman ρ per model on the *generic* ladder (I verified the domain-matched ρ and the pooled
  logistic; the generic-ladder per-model ρ table was not re-run here — recompute before it enters the draft).
- The GEE cluster-robust p=0.95 exact value (I reproduced the ≈0 coefficient and naive p=0.89; the *cluster*-
  robust SE needs statsmodels — not installed. Conclusion is invariant: coefficient ≈0 cannot be significant.)
