# STAGE 2 — SDT / Threshold Reanalysis: RESULTS
> Code: `src/sdt_analysis.py`. Non-circularity fix used: latent signal = TURN-1 (pre-pressure)
> belief gap; flip = post-pressure behavior. Verdict up front: **the reframe does NOT hold up.
> Report honestly; do NOT rescue it.**

## Test 1 — Psychometric function: does P(flip) decline with pre-pressure belief? → NO
Flip rate (incorrect arm) by turn-1 belief-gap quintile:

| quintile (turn-1 belief) | n | flip% |
|---|---|---|
| Q1 lowest | 694 | 85.4 |
| Q2 | 689 | 62.4 |
| Q3 | 690 | 76.7 |
| Q4 | 690 | 73.2 |
| Q5 highest | 685 | 83.2 |

- **Non-monotonic. Pooled logistic slope = +0.0009 (z = +0.2) — indistinguishable from zero.**
- Per-model slopes are small and mixed-sign (Gemma −0.09, Mistral −0.04, Phi −0.02, Llama −0.05,
  Qwen-3B **+0.065**, Qwen-7B +0.01) — only Qwen-3B is significant, and in the WRONG direction.
- **Interpretation:** a model that believed the correct answer strongly *before* the challenge is
  ~as likely to flip as one that barely believed it. Even at the HIGHEST pre-pressure confidence,
  models still flip **83%** on the incorrect arm. Prior confidence provides almost no protection.
- **Consequence for the reframe:** the premise that flips are a threshold crossing of a graded latent
  belief is **not supported** — there is no clean belief→behavior transfer function to build on.

## Test 2 — Fixed-effects confirmatory (belief covariate + model dummies)
`flip ~ turn1_gap + tier + dir + tier:dir + C(model)`, n=5,510:
- `turn1_gap`: coef −0.008, **p = 0.40** — belief does not predict flipping (confirms Test 1).
- `tier:dir` interaction: coef +0.022, **p = 0.78** — the pre-registered null is **robust** to adding
  the belief covariate and model fixed effects (good — this is worth reporting).
- `dir`: coef +4.07, p<0.0001 — direction dominance survives every specification.

## Test 3 — SDT d′ / criterion per model × tier: does authority move criterion or sensitivity?
- Authority-tier variation is **criterion-dominant in only 2/6** (Llama, Mistral) and
  **sensitivity-dominant in 4/6** (Gemma, Phi, Qwen-3B, Qwen-7B).
- So the clean "authority is a criterion pathology" story is **NOT supported** — the decomposition is
  mixed, and if anything leans toward sensitivity (d′) changes.
- One genuine nugget worth keeping (descriptive): **Mistral** shows a real criterion shift
  (c: anon −1.11 → low +0.18) — the resister raises its bar to comply — but it is one model, not a law.

## Bottom line (feeds Stage 2.5)
The signal-detection / thresholding reframe is **cosmetic, not robust**: prior belief doesn't predict
flipping (Test 1–2) and authority doesn't cleanly load on criterion (Test 3). **Per the pre-set decision
rule, this triggers option (B): keep the SDT/behavior-vs-belief *method* out of Paper 1 and defer it to
Paper 2.** What DOES survive and is worth keeping in Paper 1:
1. **The pre-registered null is robust** to belief covariate + model fixed effects (Test 2).
2. **A new, clean, alarming behavioral finding:** *prior confidence does not protect* — models abandon
   even strongly-held correct answers at ~83% under an incorrect counter-claim (Test 1). This needs NO
   SDT machinery and sharpens the safety message.
3. Belief (logprob) can still be used **descriptively** to corroborate that neither behavior nor belief
   shows a clean authority gradient — but NOT as a "modality-decisive dissociation" thesis.
