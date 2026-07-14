# 4-Model Analysis Summary (2026-07-02, main run complete)

> ⚠️ **SUPERSEDED — HISTORICAL SNAPSHOT (kept for the integrity trail; do NOT cite as current).**
> This was written at the 4-model stage. Its **"KEY FINDINGS" #1/#3 and the "Paper story" are FALSIFIED**
> by later evidence and must NOT be used:
> - The **"behavior-vs-belief divergence" headline is DEAD.** fig4 (POINTS §20) shows behavior and belief
>   are **CONCORDANT** (tight diagonal), not divergent. Behavioral flips faithfully track the belief shift.
> - **"Belief gradient is UNIVERSAL" is FALSE.** The **anon ladder** (POINTS §3g) shows the belief gap is
>   NOT monotonic across the format-matched anon<low<med<high ladder for 5/6 models; a nameless "someone"
>   moves belief as much as "a professor." There is **no clean authority gradient in belief either.**
> - The monotonic "persona-only" trend below is real *as a persona-only sub-trend* but does NOT survive the
>   anon rung and does NOT aggregate into a pooled tier×direction interaction (pre-registered test failed,
>   p=0.95; triple-verified in POINTS §17).
>
> **Current headline (see POINTS §16/§17/§20):** *presence of a counter-claim — not source authority —
> drives capitulation; direction dominates; susceptibility is model-dependent.* The tables in this file
> (flip %, belief gaps, Condition B) remain numerically correct; only the interpretation was wrong.

## Behavioral flip % (incorrect-endorsement arm)
| model | n | control | low | medium | high |
|---|---|---|---|---|---|
| Qwen-3B | 116 | 84% | 79% | 80% | 80% | (ceiling)
| Llama-3B | 96 | 99% | 94% | 96% | 98% | (ceiling)
| Qwen-7B | 125 | 98% | 95% | 98% | 99% | (ceiling)
| Mistral-7B | 106 | 84% | 30% | 36% | 47% | **GRADIENT + robust**

## Belief gap [logP(correct)-logP(wrong)], incorrect arm
| model | control | low | medium | high | persona trend |
|---|---|---|---|---|---|
| Qwen-3B | -6.92 | -3.47 | -4.41 | -5.24 | MONOTONIC down |
| Llama-3B | -4.99 | -2.92 | -3.13 | -3.55 | MONOTONIC down |
| Qwen-7B | -12.99 | -9.25 | -10.82 | -11.55 | MONOTONIC down |
| Mistral-7B | -3.40 | +2.24 | +1.63 | +0.77 | MONOTONIC down |

## KEY FINDINGS (⚠️ #1 and #3 FALSIFIED — see banner; struck-through interpretation kept for the trail)
1. ~~**Belief gradient is UNIVERSAL** — all 4 models show monotonic authority effect.~~
   **[FALSIFIED]** Monotonic only on the *persona-only* (low<med<high) sub-ladder; the format-matched
   **anon** rung breaks it in 5/6 models (POINTS §3g). No universal belief gradient. It's a *persona-rank
   sub-trend in a subset*, not a clean authority gradient.
2. **Mistral-7B breaks the behavioral ceiling** — shows a clear behavioral gradient (30%->47%) AND high
   robustness. Still TRUE that the flat behavior in Qwen/Llama/Qwen-7B is a real saturation property, NOT
   a method artifact (Condition B confirmed this — see below). ✓ (retained)
3. ~~**Behavior-vs-belief divergence** — behavior saturates while belief stays graded; logits recover it.~~
   **[FALSIFIED]** fig4 (POINTS §20) shows behavior and belief are **CONCORDANT**, not divergent — behavioral
   flips faithfully track the belief shift. There is no hidden gradient for logits to "recover." Do NOT use.
4. Mistral belief gaps POSITIVE at persona tiers (+2.24 to +0.77) = often keeps believing correct answer
   even under pressure = most robust model. ✓ (retained — numerically correct)

## Paper story  ⚠️ [SUPERSEDED — do not use; kept for the trail]
~~Authority-graded sycophancy manifests universally in the belief signal but is masked behaviorally by
capitulation-saturation. Logit measurement is necessary to detect authority sycophancy.~~
**CURRENT story (POINTS §16):** In a pre-registered two-turn protocol with an assertion-matched anonymous
baseline, the **PRESENCE of a counter-claim — not the AUTHORITY of its source — drives capitulation**
(direction p<0.0001; pre-registered tier×direction p=0.95). Authority grading is a per-model sub-trend
(4/6, Cochran-Armitage, persona-only) that does not aggregate; behavior and belief are concordant.

## CONDITION B RESULT (anon clean baseline, 2026-07-02)
| model | control | anon | low | medium | high |
|---|---|---|---|---|---|
| Qwen-3B | 84% | 85% | 79% | 80% | 80% |
| Llama-3B | 99% | 97% | 94% | 96% | 98% |
| Qwen-7B | 98% | 96% | 95% | 98% | 99% |
| Mistral-7B | 84% | 63% | 30% | 36% | 47% |

### What condition B settles:
- **Ceiling is NOT a control-strength artifact.** Even a clean minimal anon baseline
  ("Someone thinks the answer is X") saturates Qwen/Llama/Qwen-7B (~85-97%), same as
  personas. So the flat behavior is a REAL property of these models, not caused by our
  aggressive control. This kills the main reviewer objection.
- These 3 models cave near-totally to ANY assertion (anon or authoritative).
- Mistral: anon 63% > personas (30/36/47) — anonymous source flips it MORE than a named
  low-authority persona (vague "someone" less dismissible than "a high school student"?).
  Persona tiers still monotonic (30->36->47).
- ~~Belief gradient (all 4 monotonic) remains the universal finding~~ **[FALSIFIED — see banner;
  the anon rung breaks the belief monotonicity too, POINTS §3g].** What Condition B DID settle and
  remains TRUE: behavior saturates in 3/4 models regardless of baseline cleanliness → the ceiling is
  a genuine model property, not a control-strength artifact. ✓
