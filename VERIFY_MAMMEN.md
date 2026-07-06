# Mammen (2601.13433) PDF Verification — spot-checked against actual Table 1 + Figure 3

## CLAIM 1 (flagged): "Mammen's logit tables show Mistral grading steepest"
VERDICT: **FALSE / UNVERIFIABLE AS STATED — DO NOT USE.**
- Mammen's Table 1 reports per-model ΔAcc/Robustness/ΔH at 4 tiers for AQuA-RAT, LEXam,
  MedMCQA, MedQA. Mistral-7B IS in the table (non-reasoning models block).
- Reading the Mistral-7B row: its ΔAcc values under incorrect/misleading endorsement do
  NOT show it as "grading steepest" — several reasoning models (e.g. DeepSeek-R1) and the
  headline Figure-3 example show STEEPER degradation. The steepest illustrated case is
  DeepSeek-R1 on MedQA (−0.019 → −0.356), NOT Mistral.
- The agent claim that "Mistral grades steepest" is NOT supported by the tables. DELETE it.

## CLAIM 2: their headline gradient example
VERIFIED TRUE: DeepSeek-R1 on MedQA — correct endorsement +0.381 at Board-Certified
Physician; misleading −0.019 (First-Year) → −0.356 (Board-Certified Physician). Monotonic.
(Figure 3 + text p.4.) Safe to cite.

## CLAIM 3: "confident errors = negative ∆entropy at high authority"
VERIFIED TRUE: text states DeepSeek-R1-Qwen3-8B shows ΔH −0.261 on MedQA under a
board-certified physician incorrect endorsement = increased confidence in wrong answer.
So Mammen's confident-error claim is on REASONING models / medical / single-turn-logit.
Our non-replication (positive ∆H at 3B-9B, two-turn) is a legitimate bounded contrast —
BUT frame carefully: he shows it for reasoning models; we test different (non-reasoning,
smaller) models under a different protocol. Not a direct contradiction; a scope boundary.

## CLAIM 4: single-turn vs two-turn
VERIFIED TRUE: Mammen §Related Work explicitly contrasts RoSe's "single-prompt architecture"
and says THEY use "a two-step interaction to eliminate look-ahead bias." 
IMPORTANT NUANCE: Mammen ALSO uses a two-step/two-turn-ish interaction (to remove look-ahead
bias)! So our "two-turn vs their single-turn" differentiator is WEAKER than we thought for
Mammen specifically. RE-CHECK: their endorsement is appended after the question in ONE prompt
(Fig 2 earlier), but they mention a "two-step interaction." Their design = question+options,
then endorsement appended — the model sees both before answering (Question-then-Hint). This
is NOT the same as our commit-first-then-challenge two-turn. Our differentiator holds (they
don't have the model COMMIT to an answer first), but describe it precisely: "the model has
not publicly committed to an answer before the endorsement" — do NOT claim they are "single
turn" flatly.

## CLAIM 5: logits-only, no free-form generation
VERIFIED TRUE: "extract output logits over answer choices (A-D) ... deterministic, no
free-form generation" (Tools). Safe. Our behavioral-generation differentiator holds.

## CLAIM 6: steering vector recovers accuracy
VERIFIED TRUE: Fig 4 + §4.2 — subtracting v_auth recovers accuracy toward baseline. This is
their mechanistic depth we lack (already noted §14). Safe to cite.

## CLAIM 7: Mistral + Gemma are shared models
VERIFIED TRUE: Mistral-7B and Gemma-2-9B-IT both in their roster. Our direct-comparison
point holds. (But per CLAIM 1, do NOT claim their Mistral "grades steepest.")

---
## ACTIONS
- DELETE any "Mammen shows Mistral grades steepest" claim (unsupported — was agent error).
- Soften "single-turn" -> "the model does not commit to an answer before the endorsement
  (Question-then-Hint), vs our commit-then-challenge two-turn."
- Confident-error non-replication: frame as scope boundary (reasoning/medical/logit vs
  ours), not flat contradiction.
- Safe to cite: DeepSeek-R1 gradient example, steering-vector recovery, logits-only design,
  shared Mistral/Gemma models.
