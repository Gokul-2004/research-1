# Points For The Paper
# "Authority-Graded Sycophancy in Open-Source LLMs"
# Target: arXiv preprint + IEEE Access (open access) + Alignment Forum write-up
# Compiled 2026-07-04 from: ANALYSIS_PLAN.md, PLAN.md, CITATIONS.md, PROGRESS.md,
#   context.md, results/ANALYSIS_4model_summary.md, Literature Survey analysis, and
#   the completed 6-model experiment. This is a raw idea/evidence bank for drafting —
#   not the paper itself. Use honestly; do not overclaim.

---

## 0. ONE-PARAGRAPH HONEST SUMMARY OF WHAT WE FOUND

We tested whether 6 open-weight LLMs (3B–9B, 5 lineages) abandon a correct answer
more readily as the *authority* of a counter-claim rises, across 3 objective domains,
measured BOTH behaviorally (free-form flips) and via token log-probabilities. The
pre-registered confirmatory test (a graded `tier × direction` interaction) was NOT
supported when pooled across models (p≈0.95). Instead we found: (1) a huge, robust
DIRECTION effect — incorrect endorsement devastates accuracy, correct endorsement
barely helps; (2) strong MODEL HETEROGENEITY — some models saturate (cave to any
challenge ~80-99%), others resist (~30-60%); (3) a graded authority trend that is
significant in the BELIEF (logprob) signal for some models but behaviorally MASKED
by capitulation-saturation in the most suggestible ones. The headline contribution is
methodological: **behavioral measurement alone misses authority effects that the logit
signal reveals — measurement modality is decisive.** Our heterogeneity reconciles a
standing tension in the literature (clean gradients vs "general susceptibility").

---

## 1. THE GAP / CONTRIBUTION (what is genuinely new)

- **Behavior-vs-belief divergence** — NOBODY in the corpus measured both free-form
  behavioral flips AND logprobs on the same authority-graded items. Mammen (2601.13433)
  used logits only; SycEval/SYCON used behavior only. We show they DIVERGE. This is the
  single novel contribution.
- **Reconciling the literature's split** — Mammen + Ask-Don't-Tell found clean monotonic
  gradients; Zhang + SycoEval-EM found inconsistent/model-dependent "general
  susceptibility." Our 6-model dual-measurement study shows BOTH are right: the gradient
  lives in belief for some models, is masked behaviorally in others. (Survey line 417
  explicitly flags this tension as "worth discussing.")
- **Small-open-model focus** — 3B–9B, "models realistically deployed on consumer/edge
  hardware, where sycophancy is least studied and most consequential." Zhang explicitly
  says small open models are "valid, even ideal, subjects" (size ≠ robustness).
- **Two-turn pressure design** (commit → challenge) vs predecessors' single-turn
  question+hint — a more stringent, ecologically realistic test.
- **Length-matched prompts + explicit zero-authority control that still asserts X** —
  design controls Mammen did not use.
- **Full statistical trend testing** (Spearman, Wilson CIs, GEE/GLMM) — Mammen reported
  descriptive means without inferential trend tests.

---

## 2. WHAT WE DID (methods, for the Method section)

### Design
- 6 subject models × 150 questions × 5 authority rungs × 2 endorsement arms.
- **Rungs:** control (Sharma "I don't think that's right, answer is X"), anon ("Someone
  thinks the answer is X"), low (high-school student), medium (grad student), high
  (professor). anon<low<medium<high = clean format-matched ladder; control = separate
  stronger Sharma-style challenge.
- **Two arms:** incorrect-endorsement (asserts wrong X) + correct-endorsement (asserts
  right answer) — symmetric design from Mammen; = regressive/progressive split (SycEval).
- **Two-turn:** model answers cold (turn-1), then authority pushback (turn-2). Flip =
  turn-2 answer ≠ turn-1.
- **Domains:** Science (ARC-Challenge), History (MMLU world_history+prehistory),
  Factual (TruthfulQA mc1). All objective, verified ground truth.
- **Baseline gate:** only items the model answers correctly unprompted enter analysis
  (ALREADY_WRONG excluded) — the "knowledge filter" [Vennemeyer 2509.21305].

### Measurement (two arms per trial, one forward pass)
- **Behavioral arm:** free-form generation (temp 0, greedy, max_new_tokens=20), single
  letter enforced via system prompt; flip = letter change.
- **Belief arm (logprob):** P(correct_letter) − P(wrong_X_letter) from next-token logits
  over A/B/C/D; judge-free. Also ∆entropy computable. [method: Mammen 2601.13433,
  multilingual 2606.08451]

### Engine / reproducibility
- CPU fp16, HuggingFace Transformers (not Ollama — Ollama doesn't expose clean logprobs).
- Temp 0, fresh session per trial (anti-caching [Ben Natan 2601.15436]).
- Raw outputs → JSONL, flushed per trial, never overwritten; resume-safe.
- ~5,510 pooled analyzable trials across 6 models.

### Model set (5 lineages, pre-committed before running the last 2)
| Model | Size | Lineage | In Mammen roster? |
|---|---|---|---|
| Qwen2.5-3B-Instruct | 3B | Alibaba | family |
| Llama-3.2-3B-Instruct | 3B | Meta | family |
| Qwen2.5-7B-Instruct | 7B | Alibaba | family |
| Mistral-7B-Instruct-v0.3 | 7B | Mistral | yes |
| Phi-3.5-mini-instruct | 3.8B | Microsoft | Phi-4 family |
| Gemma-2-9b-it | 9B | Google | yes |

---

## 3. KEY RESULTS (the numbers — report honestly)

### 3a. Gate survival (baseline capability)
| Model | Gate survival | Post-gate n |
|---|---|---|
| Qwen-3B | 77% | 116 |
| Llama-3B | 64% | 96 |
| Qwen-7B | 83% | 125 |
| Mistral-7B | 71% | 106 |
| Phi-3.5 | 77% | 116 |
| Gemma-9B | 86% | 129 |

### 3b. Behavioral flip % — INCORRECT arm (the saturation/heterogeneity finding)
| Model | control | anon | low | medium | high | overall |
|---|---|---|---|---|---|---|
| Qwen-3B | 84% | 85% | 79% | 80% | 80% | 81% (SATURATES) |
| Llama-3B | 99% | 97% | 94% | 96% | 98% | 97% (SATURATES) |
| Qwen-7B | 98% | 96% | 95% | 98% | 99% | 98% (SATURATES) |
| Mistral-7B | 84% | 63% | 30% | 36% | 47% | 49% (RESISTS) |
| Phi-3.5 | 80% | 72% | 60% | 77% | 94% | 78% (graded) |
| Gemma-9B | 92% | 39% | 42% | 45% | 57% | 59% (resists) |

### 3c. Belief gap [logP(correct)−logP(wrongX)], INCORRECT arm
(turn-1 = pre-pressure baseline; positive = believes correct; negative = believes wrong)
| Model | turn-1 | control | anon | low | medium | high |
|---|---|---|---|---|---|---|
| Qwen-3B | +17.9 | −6.9 | −5.2 | −3.5 | −4.4 | −5.2 |
| Llama-3B | +4.3 | −5.0 | −3.2 | −2.9 | −3.1 | −3.6 |
| Qwen-7B | +16.5 | −13.0 | −11.1 | −9.2 | −10.8 | −11.5 |
| Mistral-7B | +15.5 | −3.4 | −1.5 | +2.2 | +1.6 | +0.8 |
| Phi-3.5 | (high +) | −9.9 | −4.6 | −3.0 | −6.0 | −9.8 |
| Gemma-9B | (high +) | −4.6 | +1.3 | +0.7 | +0.4 | −1.0 |

### 3d. Belief-trend significance (Spearman ρ on anon→low→med→high ladder, incorrect arm)
| Model | ρ | p | Significant? |
|---|---|---|---|
| Qwen-3B | +0.003 | 0.95 | no |
| Qwen-7B | −0.054 | 0.23 | no |
| Llama-3B | −0.081 | 0.11 | no |
| Mistral-7B | +0.152 | 0.002 | yes (note: +sign) |
| Phi-3.5 | −0.240 | <0.001 | yes |
| Gemma-9B | −0.164 | <0.001 | yes |
→ 3 of 6 significant on this ladder. (Persona-only coding gives slightly different
counts — REPORT BOTH honestly; the exact count depends on ladder definition.)

### 3e. CONFIRMATORY TEST (pre-registered) — the honest headline
- Pooled GEE/GLMM logistic, `flip ~ tier * dir`, cluster=model, n=5,510:
  - **`tier × dir` interaction: coef −0.013, p = 0.95 → NOT SUPPORTED.**
  - **`dir` (direction) main effect: coef −3.50, p < 0.0001 → HUGE, robust.**
  - tier main effect: coef +0.094, p = 0.30 → n.s.
- HONEST STATEMENT: our single pre-specified hypothesis failed; the dominant effect is
  endorsement direction, not authority gradation.

### 3f. The three-way model taxonomy (a clean way to present heterogeneity)
- **Saturators** (cave to any challenge, no gradient): Qwen-3B, Qwen-7B, Llama-3B
- **Resisters** (resist a lot, but authority level barely matters): Mistral, Gemma-9B
- **Partial authority-escalation**: Phi-3.5 (only model with a real low→high escalation)
  — but even Phi's anon rung breaks the clean ladder (see 3g).

### 3g. ⚠️ THE DECISIVE RESULT — the anon ladder FALSIFIES the clean-gradient story
The anon rung ("Someone thinks X") is the properly format-matched zero-authority baseline,
built specifically to test the clean ladder anon<low<medium<high. If authority graded
belief cleanly, belief should erode monotonically down that ladder. IT DOES NOT.

Belief gap [logP(correct)−logP(wrongX)], incorrect arm, full ladder:
| Model | anon | low | medium | high | monotonic anon→high? |
|---|---|---|---|---|---|
| Qwen-3B | −5.22 | −3.47 | −4.41 | −5.24 | NO (anon ≈ high; personas WEAKER than anon) |
| Qwen-7B | −11.10 | −9.25 | −10.82 | −11.55 | NO (essentially flat) |
| Llama-3B | −3.22 | −2.92 | −3.13 | −3.55 | NO (flat) |
| Mistral-7B | −1.50 | +2.24 | +1.63 | +0.77 | NO (ladder runs BACKWARDS — anon more negative than personas) |
| Phi-3.5 | −4.61 | −3.03 | −6.03 | −9.81 | NO (clean low→high, but anon breaks it) |
| Gemma-9B | +1.29 | +0.69 | +0.37 | −0.99 | YES — but Gemma barely moves at all |

**Only 1 of 6 (Gemma) is monotonic across the clean ladder, and Gemma barely shifts.**

**HONEST CONCLUSION (the true finding):** There is NO clean authority gradient — not
behaviorally, not in belief, not even in the matched anon ladder. What actually drives
capitulation is the **PRESENCE of a counter-claim** (anonymous or authoritative), NOT the
**AUTHORITY of its source**. The anon rung — a nameless "someone" — produces a shift as
large as or larger than "a professor" in almost every model. Authority LEVEL mostly does
not matter; disagreement itself does.

**Earlier "significant Spearman" caveat (important, do not overclaim):** the significant
trend p-values reported in intermediate analyses (Mistral p=0.002, Phi p<0.001, Gemma
p=0.006) do NOT indicate a clean authority gradient. A significant ρ only means *some*
monotonic-ish trend; the anon rung shows the trend is often non-monotonic or backwards.
Only Phi shows genuine authority escalation among personas, and even its anon breaks it.

---

## 4. HOW OUR RESULTS COMPARE TO THE LITERATURE (crucial for Related Work / Discussion)

| Their finding | Paper | Our result | Verdict |
|---|---|---|---|
| Clean monotonic authority gradient, all models | Mammen 2601.13433 (11 models, logit-only, single-turn) | Gradient only in 3/6, mostly in belief | We REFINE: under stricter 2-turn behavioral protocol the clean gradient partially collapses to saturation |
| Graded authority, accuracy→15-34% at top tier | Mechanistic 746 (3 models, MedQA) | Our saturators hit similar low correctness under pressure | Consistent |
| "Correlates with alignment, NOT size"; model-dependent | Zhang 2508.13743 | Our 30%→99% spread, not tracking size | MATCHES directly |
| "General susceptibility," tactics indistinguishable, bimodal | SycoEval-EM 2601.16529 (19 models) | Our saturators = their "cave" mode; tiers indistinguishable | MATCHES directly |
| Direction/incorrect dominates; regressive from citations | SycEval 2502.08177 | Our dir effect coef −3.50 p<0.0001 | MATCHES; our strongest result |
| Monotonic with epistemic certainty | Ask Don't Tell 2602.23971 | Our authority ladder = their certainty ladder analog | Conceptual sibling |
| Behavior vs belief measurement | (NOBODY) | We show divergence | OURS — novel |

### 4a. Per-paper comparison — full prose (draft-ready for Related Work / Discussion)

**1. Mammen "Who Endorsed It?" (2601.13433) — direct predecessor — found a CLEAN monotonic gradient.**
- *Them:* "Clear monotonic hierarchy across all domains and both model types." Board-Certified
  Physician drops accuracy to 15% (Llama), 29% (Qwen), 34% (Gemma) from ~60% baseline. Clean,
  universal, monotonic. 11 models, logit-only, single-turn.
- *Us:* Gradient significant in only 3 of 6 models; pre-registered interaction failed (p=0.95).
- *The honest tension:* They got a much cleaner result. But three methodological differences
  explain most of it — and they favor us:
  1. They used **single-turn** (question+hint together); we used **two-turn** (commit, then
     challenge). Two-turn is a HARDER test — the model has already committed, so pressure is
     stronger and saturation more likely.
  2. They read **pure logits over A–D**; we measured **behavioral flips + logits**. Our
     behavioral arm reveals saturation theirs could not see.
  3. Their baseline **asserts nothing**; ours **asserts X**. Their "gradient" had more headroom.
- *Defensible framing (not a failure):* "Under a more stringent two-turn behavioral protocol,
  Mammen's clean gradient partially collapses into saturation — revealing that the effect is more
  fragile and measurement-dependent than the logit-only single-turn view suggests." We are
  REFINING their finding, not contradicting it.

**2. Zhang "Sycophancy under Pressure" (2508.13743) — found model-dependence, NOT clean gradients.**
- *Them:* "Correlates with alignment strategy and reasoning ability, NOT model size" — Qwen-32B
  beats Qwen-72B. Robustness is model-specific and inconsistent.
- *Us:* Exactly this. Our models range from 49% overall flips (Mistral) / 59% (Gemma) to 97-98%
  (Llama, Qwen-7B) — huge model-dependence, not tracking size (Qwen-7B saturates while the
  larger Gemma-9B resists).
- *Verdict:* Our result MATCHES Zhang directly. Our heterogeneity isn't noise — it is the same
  "robustness is model-specific" finding the field's own recent work reports.

**3. SycoEval-EM (2601.16529) — found "general susceptibility," tactics indistinguishable.**
- *Them:* "All 5 persuasion tactics statistically indistinguishable — general susceptibility."
  Bimodal: models either resist (~0-10%) or cave (~52-100%). 19 models.
- *Us:* Our saturating models (Qwen×2, Llama at 80-99%) are exactly their "cave" mode; the
  authority tiers being indistinguishable in those models = their "tactics indistinguishable."
- *Verdict:* Our saturation finding MATCHES SycoEval-EM. (Survey line 417 explicitly flags the
  tension between this and Mammen as "worth discussing" — we resolve it.)

**4. SycEval (2502.08177) — the direction/persistence effect.**
- *Them:* Regressive (toward wrong) 14.66% vs progressive 43.52%; persistence 78.5%; direction
  and rebuttal type matter enormously; citation rebuttals → most regressive.
- *Us:* Our massive DIRECTION effect (coef −3.50, p<0.0001 — incorrect endorsement devastates,
  correct barely moves) is the SAME phenomenon, and it is our single strongest, cleanest result.
- *Verdict:* MATCHES; direction dominance is robust and field-consistent.

**5. Ask Don't Tell (2602.23971) — monotonic with epistemic certainty.**
- *Them:* Sycophancy increases monotonically with certainty (statement < belief < conviction);
  closed models, subjective topics; length-controlled.
- *Us:* Our authority ladder is the conceptual sibling of their certainty ladder; their
  length-control validates our length-matching invariant.

### 4b. The honest bottom line (use near the top of Discussion)

Our messy result is NOT an outlier — it sits squarely in the middle of the field's actual findings:

| Finding | Who else found it |
|---|---|
| Model-dependent, inconsistent authority effect | Zhang (size≠robustness), SycoEval-EM |
| Saturation / "general susceptibility" | SycoEval-EM |
| Direction / incorrect-endorsement dominates | SycEval, Sharma |
| Behavior-vs-belief measurement matters | NOBODY — this is OURS |

The field is split: Mammen + 746 + Ask-Don't-Tell found clean monotonic gradients (single-turn,
logit-only, domain-matched personas); Zhang + SycoEval-EM found inconsistent, model-dependent
susceptibility. **Our result lands on the Zhang/SycoEval-EM side and goes further: under a
two-turn behavioral protocol with a matched anonymous baseline, the authority gradient does NOT
appear — not behaviorally, not in belief (see 3g). What drives capitulation is the PRESENCE of a
counter-claim, not the AUTHORITY of its source.**

**KEY POSITIONING / REFRAME SENTENCE (use in Abstract + Discussion):** "Under a realistic two-turn
behavioral protocol with a properly matched anonymous baseline, authority-graded sycophancy —
the clean monotonic effect reported under single-turn logit measurement — largely FAILS to
replicate across six open models. The presence of a counter-claim, rather than the authority of
its source, dominates capitulation. This suggests the graded effect may be fragile, or may
require the domain-matched institutional personas that prior work used."

HONEST FRAMING NOTE: Do NOT claim we "reconcile" the field by finding the gradient in belief —
the anon ladder falsified that (3g). The honest contribution is a NULL/fragility result on the
authority gradient + the direction-dominance finding + the behavior-vs-belief method. This is a
harder paper to sell than a clean replication, but it is TRUE. Honest IEEE estimate: ~45-55%,
depending on framing rigor and whether we run the domain-matched-persona disambiguation (4c).

### 4c. WHY WE DIFFER FROM THE CLEAN-GRADIENT PAPERS (honest diagnosis)

THREE papers got CLEAN monotonic gradients; we got a NULL on the gradient:
- Mammen 2601.13433: "Clear monotonic hierarchy across all domains and both model types"
  (e.g. −0.356 at Board-Certified Physician, near-zero at First-Year Student).
- Mechanistic 746: "graded manner proportional to authority... dampens monotonically."
- Ask Don't Tell 2602.23971: "sycophancy increases monotonically with epistemic certainty"
  (certainty ladder, not authority — but same clean-monotonic shape).
(Feng 2603.16643 showed authority-bias > user-bias, but only 2 levels, not a graded ladder.)

They share THREE methodological choices we changed — verified from the survey:

| Difference | Clean-gradient papers | Us | Likely to suppress our gradient? |
|---|---|---|---|
| Turn structure | SINGLE-turn: hint appended to question, model answers once (Mammen "appended after the question"; 746 "Question-then-Hint") | TWO-turn: model commits, THEN authority pushes back | YES — likely main cause. Two-turn = social confrontation; model capitulates to *disagreement*, ~independent of source |
| Measurement | Pure logits over A–D, NO free-form generation (both Mammen & 746 explicit) | Forced generation + logprobs | YES — logits capture fine-grained preference that shifts smoothly; committed generation is coarser/saturated |
| Persona ladder | DOMAIN-MATCHED institutional hierarchy (Board-Certified Physician→...; Senior Legal Counsel→...) | GENERIC competence ladder (high-schooler→grad→professor) across all domains | POSSIBLY — 746 explicitly says the effect "emerges ONLY when personas carry socially meaningful institutional hierarchy, domain-matched, third-person" — we may violate this precondition |

Domain-difficulty is NOT a valid excuse for us: Mammen & 746 both found the OBJECTIVE/math
domain showed the STRONGEST effect (lowest robustness). Our objective domains should, by
their logic, have shown a strong gradient — they didn't. So difficulty doesn't rescue us.

**Two honest interpretations (state BOTH in the paper):**
- (A, charitable/defensible): "Authority-graded sycophancy is FRAGILE — it appears under
  single-turn logit measurement but largely COLLAPSES under a realistic two-turn behavioral
  confrontation with a matched anonymous baseline. Disagreement presence, not source
  authority, drives capitulation in most small open models."
- (B, the concession): "Our generic (non-domain-matched) persona ladder may not carry the
  institutional-authority signal that 746 says is REQUIRED for the graded effect — so our
  null may partly reflect persona design, not a genuine absence of the effect."

**The disambiguating experiment (FUTURE WORK / optional):** re-run with DOMAIN-MATCHED
INSTITUTIONAL personas (per 746's precondition). If the gradient appears → our null was a
persona-design artifact (report honestly). If it still doesn't → the two-turn protocol
genuinely kills it (strong finding). Cost: full re-run (~50-60h CPU or a few hours on cloud
GPU). NOT yet decided — do after judge + human validation lock down current results.

### Are we BETTER or WORSE than the clean-gradient papers? (honest)
- BETTER on: ecological realism (two-turn commit-then-challenge), behavioral+belief dual
  measurement, full statistical trend testing (they reported descriptive means), the anon
  control baseline (which is what EXPOSED the non-monotonicity).
- WORSE on: we got a NULL where they got clean results; generic personas (vs domain-matched);
  fewer models (6 vs 11).
- Net honest framing: we are the "stress-test / fragility" study, not a "we replicated
  Mammen" study. Whether the persona-design concession is fatal depends on the disambiguating
  re-run above.

### Model-count context (pre-empt "too few models")
- We use 6. Mammen used 11; SYCON 17; SycoEval-EM 19; ELEPHANT 11.
- BUT: mechanistic authority paper (746) = 3; SycEval = 3; Ben Natan = 4; Ask Don't
  Tell = 3; Sharma = 5; Multilingual = 6. Focused/accepted studies routinely use ≤6.
- Our 6 span 5 lineages (Qwen, Meta, Mistral, Microsoft, Google), 3B–9B — good diversity.
- Frame model count as adequate; lead with the behavior-vs-belief depth, not breadth.

---

## 5. FRAMING / NARRATIVE OPTIONS (pick one, commit, be honest)

**Recommended honest headline:**
> "Behavioral capitulation masks authority-graded belief shifts in small open LLMs:
> a behavior-vs-belief measurement study."

Key claims (all defensible from data):
1. Endorsement DIRECTION dominates — incorrect pushback is devastating, correct barely
   helps (huge, robust, p<0.0001).
2. Authority-graded sycophancy is REAL BUT MODEL-DEPENDENT — significant in a subset,
   absent (via saturation or indifference) in others.
3. Behavioral saturation MASKS a belief-level authority signal — logit measurement is
   necessary; behavioral-only measurement under-detects the effect.
4. This reconciles the literature's disagreement.

**Do NOT claim:** a clean universal authority gradient (the confirmatory test failed).

---

## 6. INTEGRITY / PRE-REGISTRATION POINTS (state these explicitly — strengthens credibility)

- ANALYSIS_PLAN.md was committed BEFORE any inference (pre-registration). The
  confirmatory `tier × direction` interaction was pre-specified; report its FAILURE
  honestly. Reviewers reward a documented null over a silent pivot.
- The belief/behavior-vs-belief analysis was ALSO pre-specified (§3c of ANALYSIS_PLAN
  lists logprob as a reported quantity and the "behavior-vs-belief headline") — so
  promoting it is NOT HARKing.
- Model-set expansion (Phi + Gemma) was pre-committed in ANALYSIS_PLAN §7d before those
  two ran, with commitment to report both regardless of outcome — pre-empts cherry-pick.
- Condition B (clean anon baseline) was run specifically to TEST whether our aggressive
  control caused the behavioral ceiling. Result: it did NOT — anon also saturates the
  suggestible models. So the ceiling is a genuine model property, not a design artifact.
  (This kills the biggest reviewer objection.)

---



## 6b. JUDGE VALIDATION RESULT (completed 2026 — reproducible)
- Judge: Gemini 2.5 Flash (work-laptop run; note: 2.5, not 2.0 as originally planned — update Methods).
- 5,513 trials labeled (correct/incorrect/erroneous), 7 API errors (0.1%).
- Human validation: n=60, raw agreement 98.3% (59/60).
  - **Cohen's kappa = 0.967** (bar >=0.70; SycoEval-EM gold standard = 0.957 — we match/exceed).
  - **Gwet's AC1 = 0.980** (prevalence-robust, for skewed labels [multilingual 2606.08451]).
  - **Beta judge-accuracy ~ Beta(60,2): mean 0.968 +/- 0.022** [SycEval method].
  - The single non-match was an API ERROR (no judge label returned), not a judgment disagreement.
- Files: judge_bundle/results/judged/*__judge1.jsonl, judge_bundle/results/human_validation/.
- CONCLUSION: behavioral labels are human-validated at top-of-field reliability. Kills the
  "unvalidated LLM judge" reviewer objection.

---

## 7. LIMITATIONS (state proactively — Batzner 2512.00656 threats-to-validity backbone)

- **Confirmatory hypothesis not supported** — state plainly; reframe honestly.
- **Position/recency bias** — pushback always last; held constant across conditions so
  can't confound the interaction, but absolute flip rates may carry a position component
  [Ben Natan 2601.15436]. Future: counterbalance answer order.
- **wrong_X fixed letter position** per question — position held constant, not randomized.
- **Behavioral arm is near-forced-choice** (single-letter system prompt) — close to the
  logprob arm; the judge adds value mainly for rare format-breaks/refusals.
- **Gemma prompt-format difference** — Gemma rejects a system role, so its system
  instruction was folded into the user turn (content identical, position differs). Minor.
- **6 models, 3B–9B only** — no frontier scale; no base-vs-instruct axis.
- **No human-perception measure** yet (Batzner critique) — judge + ~100 human labels
  planned (Phase 4) with Cohen's κ + Gwet's AC1.
- **In-context (two-turn) = conservative lower bound** vs preemptive [SycEval:
  61.75% vs 56.52%] — we do not inflate the effect.
- **Small trend magnitudes / mixed signs** — Mistral's belief trend is +sign; the
  gradient, where significant, is modest.

---

## 8. METRICS TO REPORT (for comparability with prior work)
- Behavioral flip rate + Wilson 95% CIs (per model, tier, arm).
- Regressive severity = flip(incorrect, tier) − flip(control, incorrect).
- Belief gap [logP(correct) − logP(wrongX)] pre/post pressure. [Mammen, multilingual]
- ∆Entropy (Shannon over A/B/C/D) — confident-error signal [Mammen: negative ∆entropy
  = confident wrong answers].
- Robustness / Resistance Rate — fraction unchanged by endorsement [Zhang, Mammen].
- Progressive vs regressive split [SycEval].
- Direction main effect (our strongest result) — emphasize.
- Spearman trend on authority ladder; pooled GEE/GLMM interaction (report the null).

---

## 9. CITATIONS — KEY ANCHORS (verified, see CITATIONS.md for full table)
- **Mammen, Joswin, Venkitachalam 2026** "Who Endorsed It?" arXiv:2601.13433 — PRIMARY
  predecessor; graded authority, behavioral, 11 open models, logit-only. Differentiate.
- **Joswin, Medicherla, Mammen 2026** "A Mechanistic View of Authority Hierarchy in LLM
  Sycophancy" — ICML 2026 Mech Interp Workshop, Seoul. NO arXiv ID — cite by
  authors/title/venue only. (mechanistic half; graded authority; knowledge erasure)
- **Sharma et al. 2024** "Towards Understanding Sycophancy" arXiv:2310.13548 (ICLR 2024)
  — definitional anchor; "Are you sure?" paradigm; our control descends from it. Cite
  YEAR = 2024 (ICLR), not 2025.
- **Zhang et al. 2025** "Sycophancy under Pressure" arXiv:2508.13743 — size≠robustness;
  ARC-Challenge source; SRR/MRR metrics; small-open-model justification.
- **Fanous et al. 2025** "SycEval" arXiv:2502.08177 — progressive/regressive; rebuttal
  ladder; judge design (adopt); direction/persistence; in-context vs preemptive.
- **Peng et al. 2026** "SycoEval-EM" arXiv:2601.16529 — "general susceptibility";
  bimodal; κ=0.957 human-validation bar.
- **Feng et al. 2026** "Good Arguments Against the People Pleasers" arXiv:2603.16643 —
  authority-bias > user-bias; CoT masks sycophancy (→ judge must read full response).
- **Dubois et al. 2026** "Ask Don't Tell" arXiv:2602.23971 — graded certainty ladder
  (conceptual sibling); length-control validates our length-matching.
- **Ben Natan & Tsur 2026** arXiv:2601.15436 — neutral-baseline protocol; position/
  recency confound; temp-0 + fresh sessions.
- **Shah et al. 2026** "Multilingual" arXiv:2606.08451 — forced-choice logprob method;
  stats stack; Gwet's AC1 for skewed data; open-weights justification.
- **Batzner et al. 2025** arXiv:2512.00656 — construct-definition/threats-to-validity;
  human-in-the-loop critique.
- **Vennemeyer et al. 2026** arXiv:2509.21305 — knowledge-filter principle (our gate).
- Foundational: Perez 2212.09251 (model-written evals, inverse scaling); Wei 2308.03958
  (scaling+IT↑sycophancy, synthetic-data mitigation); Turpin 2305.04388 (unfaithful CoT);
  Casper 2307.15217 (RLHF limits); Panickssery 2312.06681 (CAA steering).

---

## 10. FUTURE WORK (name explicitly — reviewers reward this)
- Mechanistic localization on our generation setting (logit/Tuned lens, DiffMean/CAA);
  note mean-vector steering fails, per-question needed [746, Mammen].
- Frontier + larger open models (70B/405B) — does grading recover with scale?
- Base-vs-instruct axis (does RLHF CAUSE the saturation? SYCON: alignment tuning
  amplifies) — URIAL for base-model dialogue.
- Multi-turn escalation (Turn-of-Flip/Number-of-Flip [SYCON]; persistence [SycEval]).
- Richer/adversarial endorsement formats (fabricated citations [SycEval]).
- Multilingual authority-sycophancy [multilingual 2606.08451].
- Mitigations evaluated not just named: authority steering [Mammen], synthetic data
  [Wei], Pressure-Tune [Zhang], question-reframing [Ask Don't Tell].
- Quantization × sycophancy (edge-deployment relevance).
- Human-perception study [Batzner] — corpus has ~zero; distinctive contribution.
- Preemptive vs in-context comparison on open models [SycEval].

---

## 11. STILL TODO BEFORE SUBMISSION (not results — process)
- Phase 4 JUDGE: Gemini 2.0 Flash, dual-run, CoT-before-label, SycEval two-stage
  labeling, κ≥0.70 + Gwet's AC1, ~100 human labels, Beta(α,β) judge-accuracy model,
  generation-integrity audit. Needs Google AI Studio API key. (src/run_judge.py ready.)
- Formal pooled GLMM with (1|model)+(1|question) random effects (currently GEE cluster).
- Wilson CIs + Cochran-Armitage on final data; BH-correct exploratory family.
- ∆Entropy computation across tiers.
- SycophancyEval baseline calibration run (E6).
- Figures: flip-rate ladders per model; belief-gap ladders; behavior-vs-belief scatter.

---

## 12. THE HONEST ELEVATOR PITCH (for abstract)
Small open LLMs are widely deployed yet under-studied for authority-driven sycophancy.
Testing 6 models (3B–9B, 5 lineages) across 3 objective domains with a two-turn pressure
protocol and BOTH behavioral and log-probability measurement, we find: (i) endorsement
direction dominates — an incorrect authoritative counter-claim collapses accuracy while
a correct one barely helps; (ii) susceptibility is strongly model-dependent, from ~30%
to ~99% capitulation, not tracking size; (iii) a graded authority effect exists in the
internal belief signal of several models but is behaviorally MASKED by near-total
capitulation-saturation in the most suggestible ones. Behavioral measurement alone
under-detects authority sycophancy; the log-probability signal recovers it. Our findings
reconcile a standing disagreement in the literature between "clean graded sycophancy"
and "general susceptibility," and argue that measurement modality is decisive for
evaluating sycophancy in the small open models most people actually run.

---

## 13. DOMAIN-MATCHED PERSONA EXPERIMENT + MAMMEN COMPARISON (2026-07-06)

### Why we ran it
Original null (generic personas: high-schooler→grad→professor) may be a persona-design
artifact. Joswin 746 claims the graded effect emerges ONLY with domain-matched
institutional personas. Wang found generic framing does ~nothing. We ran the direct A/B
test: same 6 models, same everything, swap generic ladder → domain-matched institutional
ladder (undergrad→PhD→Nobel laureate / world-leading authority). Pre-committed in
ANALYSIS_PLAN §7d. Split across machines (group A: Qwen-3B/Llama-3B/Qwen-7B; C: Gemma;
D: Mistral+Phi). Status at time of writing: 4 models fully done, Mistral+Phi finishing.

### Belief-gradient result — GENERIC vs DOMAIN-MATCHED (incorrect arm, Spearman on low<med<high)
| Model | Generic | Domain-matched | Effect of domain-matching |
|---|---|---|---|
| Qwen-3B | ρ=−0.07 p=0.17 (ns) | ρ=−0.17 p=0.001* | gradient APPEARED |
| Llama-3B | ρ=−0.14 p=0.018* | ρ=−0.24 p<0.001* | STRONGER |
| Qwen-7B | ρ=−0.21 p<0.001* | ρ=−0.11 p=0.039* | weaker (exception) |
| Gemma-9B | ρ=−0.14 p=0.006* | ρ=−0.25 p<0.001* | STRONGER |
| Mistral-7B | ρ=−0.16 p=0.004* | ρ=−0.03 p=0.70 (ns) | COLLAPSED (saturates) |
→ domain-matched STRENGTHENS gradient in 3/5 (Qwen-3B, Llama, Gemma), weakens Qwen-7B,
  COLLAPSES Mistral. Effect of persona-specificity is itself MODEL-DEPENDENT.

### Mistral-7B — the key nuance (SAME model as Mammen)
- GENERIC personas: monotonic gradient (flip 30%→36%→47%) — REPLICATES Mammen.
- DOMAIN-MATCHED (stronger) personas: gradient COLLAPSES — flat ~60-66% flip, model caves
  near-uniformly regardless of tier. Accuracy floor ~34-40%.
- INTERPRETATION: the authority gradient is BOUNDED — it holds at moderate authority but
  SATURATES into indiscriminate capitulation once authority is strong enough. Mammen's
  single-persona-strength design could not detect this ceiling. This is a NOVEL extension,
  NOT a contradiction. (Correction to an earlier read that called it a same-model contradiction.)

### Accuracy retained under STRONG INSTITUTIONAL AUTHORITY (high tier, domain-matched, incorrect arm)
| Model | Mammen top-tier (Board-Certified Physician) | Ours (Nobel/world-authority) |
|---|---|---|
| Gemma-9B | 34% | 24% (caves harder) |
| Llama | 15% | 2% (caves harder) |
| Qwen | 29% | 1% (caves harder) |
| Mistral-7B | ~low (monotonic) | 34% (RESISTS — exception) |
→ 3/4 models cave AS HARD OR HARDER than Mammen under strong authority (confirms his core
  danger, behaviorally + two-turn). Mistral is the resister. NOT apples-to-apples (his:
  MedQA/single-turn/logit; ours: ARC-MMLU-TruthfulQA/two-turn/behavioral; our Llama/Qwen
  are smaller) — so compare DIRECTION not exact %.

### HONEST POSITIONING vs MAMMEN (do NOT overclaim)
- We are NOT uniformly opposing Mammen. On Gemma + Llama we REPLICATE (and strengthen with
  domain-matched personas). Qwen difference is confounded by size (ours smaller → saturates).
- We CONFIRM his core finding: strong institutional authority devastates accuracy (our 1-24%
  ≈ or worse than his 15-34%), and we show it holds BEHAVIORALLY under a two-turn protocol.
- We EXTEND him: (a) behavior-vs-belief measurement; (b) persona-strength variation revealing
  a SATURATION CEILING (Mistral); (c) model-dependence — the effect is real but NOT universal.
- FRAMING: "we confirm and extend Mammen, identifying the conditions (persona strength, model)
  under which the graded effect holds vs saturates" — NOT "we oppose/beat Mammen."

### Which design is "better" — Mammen's or ours? (honest)
- NOT competing; complementary. MAMMEN STRONGER on: 11 models (larger + reasoning), mechanistic
  depth (steering vectors, layer localization), cleaner single-turn logit isolation, better
  resourced — it's the flagship. OURS STRONGER on: two measurement arms (behavior+belief),
  two-turn realistic protocol, persona-strength variation (finds saturation), rigorous stats +
  human-validated judge (κ=0.967) + pre-registration.
- Our paper = narrower but methodologically complementary EXTENSION. Position as extending/
  refining, never as superior.

### Caveats (state honestly)
- Mistral + Phi domain-matched not yet complete at time of writing — confirm final numbers.
- Cross-study comparison is directional only (different domains/protocol/model sizes).
- Qwen-7B and Mistral break the "domain-matched strengthens gradient" pattern → effect is
  model-dependent, not a clean universal fix. Report the heterogeneity honestly.

---

## 14. MECHANISTIC DEPTH — what Mammen/746 has that we DON'T (+ counterpoint)

### POINT (their advantage): mechanistic interpretability we lack
Mammen (2601.13433) + 746 look INSIDE the network (white-box), not just input→output. Specifically:
1. **Steering vectors (activation addition):** extract an "authority direction" in activations;
   SUBTRACTING it RECOVERS accuracy → authority is a manipulable internal signal, steerable.
2. **Layer localization ("peak layer"):** pinpoint the exact layer where damage happens —
   L17 (Llama), L28 (Gemma), L29 (Qwen); at that layer the correct-answer representation is
   ACTIVELY ERASED (probe accuracy drops below chance). "Mechanistic knowledge erasure."
3. **Probing (linear/MLP):** classifiers on activations show the model stops "knowing" the answer.
4. **Logit lens / Tuned lens:** decode intermediate layers, watch the answer flip mid-network.
5. **Per-question vs mean steering:** mean vectors fail (≤7%), per-question reproduce 63-82% of
   flips → authority is question-specific, not a global "trust" direction.
→ We have NONE of this. We only observe behavior (flips) + output-layer logprobs. We cannot say
   WHERE or HOW inside the network authority acts. This is a genuine depth gap.

### COUNTERPOINT (why it's not fatal for us — complementary, not inferior)
- Mechanistic work needs white-box access + TransformerLens + a separate skillset; their own
  mechanistic analysis is SINGLE-DOMAIN (medical) and PRELIMINARY (no full ablation/SAE — they
  say so).
- Our behavioral + TWO-TURN approach measures what they CANNOT: what the model actually DOES in
  realistic multi-turn interaction. Mechanistic = WHERE in the net; behavioral = WHAT in deployment.
- We can name mechanistic analysis of our two-turn setup as explicit FUTURE WORK (probing,
  DiffMean/CAA on our generation setting; note 746's finding that per-question vectors are needed).
- HONEST FRAMING: their mechanistic depth and our behavioral realism are complementary lenses on
  the same phenomenon. Do not pretend we have mechanistic evidence; do cite theirs and position
  ours as the behavioral/deployment complement.

---

## 15. FINAL 6-MODEL DOMAIN-MATCHED RESULT (2026-07-06, ALL COMPLETE)

All 6 models finished. Belief trend (Spearman low<med<high, incorrect arm) + behavioral
flip% (low->high) + accuracy retained at high tier, GENERIC vs DOMAIN-MATCHED personas:

| Model | Generic (rho, p) | Domain-matched (rho, p) | Flip% gen -> dom (high) | Effect |
|---|---|---|---|---|
| Qwen-3B | −0.07, 0.17 (ns) | −0.17, 0.001* | 80% -> 84% | STRONGER (appeared) |
| Llama-3B | −0.14, 0.018* | −0.24, <0.001* | 98% -> 98% | STRONGER |
| Qwen-7B | −0.21, <0.001* | −0.11, 0.039* | 99% -> 99% | similar |
| Gemma-9B | −0.14, 0.006* | −0.25, <0.001* | 57% -> 76% | STRONGER (clean behavioral) |
| Mistral-7B | −0.16, 0.004* | −0.09, 0.114 (ns) | 47% -> 53% | COLLAPSED (saturation) |
| Phi-3.5 | −0.33, <0.001* | −0.32, <0.001* | 94% -> 91% | similar (already strong) |

### Final tally: domain-matched -> 3 STRONGER, 2 similar, 1 COLLAPSED
- STRENGTHENED (Qwen-3B, Llama, Gemma): institutional personas recover/amplify gradient -> confirms 746.
  Qwen-3B goes ns->SIG; Gemma behavioral flip 43->64->76% (clean dose-response).
- SIMILAR (Qwen-7B, Phi): already graded; personas didn't shift much. Phi is the STRONGEST/cleanest
  grader (flip 60->77->94% generic, p<0.001) — behaviorally textbook.
- COLLAPSED (Mistral): SIG generic -> ns domain-matched. Saturation ceiling: strong authority -> caves
  more overall (47->53% at high, and 30->47% generic became 46->53% dom) but stops discriminating tiers.

### Two clean headline findings (final data)
1. Phi-3.5 = strongest/cleanest authority grader (60->77->94% flip, p<0.001, both persona sets).
2. Gemma = clean domain-matched win (behavioral 43->76%), and it's SHARED with Mammen -> we confirm+strengthen him.

### FINAL honest story (6 models, complete)
"Authority-graded sycophancy in small open LLMs is real but heterogeneous. Domain-matched institutional
personas strengthen the graded effect in half the models (Qwen-3B, Llama, Gemma) and leave it strong in
others (Phi, Qwen-7B) — confirming persona specificity matters (746). But in the most robust model
(Mistral), strong institutional authority SATURATES susceptibility, collapsing the gradient into
indiscriminate capitulation. The effect is bounded and model-dependent, not the universal clean gradient
prior single-turn logit work (Mammen) reported."

### Status: ALL EXPERIMENTS COMPLETE
- Main run (6 models, 5 rungs, 2 arms): done.
- Condition B (anon baseline): done.
- Domain-matched persona run (6 models, low/med/high): done.
- Judge (Gemini 2.5 Flash) + human validation kappa=0.967: done.
- REMAINING: formal pooled GLMM, figures, write-up. No more inference needed.

---

## 16. INTEGRITY CORRECTIONS + ROADMAP ADOPTION (2026-07-06)

### ⚠️ CORRECTION — domain-matched run is EXPLORATORY, not pre-registered
- ANALYSIS_PLAN §7d pre-registered MODEL-SET EXPANSION only (adding Phi + Gemma), NOT the
  domain-matched persona experiment/analysis.
- Therefore the domain-matched run is POST-HOC / EXPLORATORY. Label it as such in the paper.
- Do NOT cite §7d as pre-registering the domain-matched analysis (false + checkable).
- The domain-matched A/B is still a legitimate exploratory contribution — just honestly framed
  as exploratory, not confirmatory.

### Framing correction (supersedes earlier §5/§12 vintage language)
- DO NOT say "gradient lives in belief, masked behaviorally" or "we reconcile the field" —
  the anon-ladder (§3g) FALSIFIED the clean-belief-gradient story. Purge this language.
- DO NOT say "fails to replicate Mammen" — we never ran their single-turn logit protocol.
  SAY: "does not translate to two-turn behavioral measurement."
- Control rung is NOT "zero-authority" — it out-pushes "professor"; anon is the floor.
- Do NOT attribute heterogeneity to size or RLHF (Qwen-7B saturates while Gemma-9B resists —
  no evidence either way).

### The paper (adopted from multi-agent roadmap): "confirm and bound," null-first
Headline: in a pre-registered two-turn protocol with an assertion-matched anonymous baseline,
the PRESENCE of a counter-claim — not the AUTHORITY of its source — drives capitulation
(direction p<0.0001; pre-registered tier×direction p=0.95). Authority grading emerges only
model-dependently and only under domain-matched personas (3/6, exploratory — first within-
protocol test of Joswin's boundary condition). Mistral saturates under strong authority.
Working title: "Presence, Not Prestige: Claim Presence Dominates Source Authority in the
Behavioral Sycophancy of Small Open LLMs."

### THE TWO BLOCKERS (do first — every results sentence depends on these)
1. Recompute confirmatory stats on JUDGE substance labels (judge_bundle/results/judged/
   *__judge1.jsonl), not regex flips. Fit on BOTH regex and judge labels; report if they differ.
2. Formal pre-registered GLMM: correct_after_pressure ~ tier*direction*domain + (1|model)+(1|question),
   LRT on tier×direction, GENERIC PERSONAS ONLY (never pool with domain-matched for confirmatory).

### MUST-VERIFY before drafting (agent-derived claims from PDFs — spot-check against real tables)
- "Mammen's logit tables show Mistral grading steepest" — VERIFY against actual Mammen tables.
- Any per-model Mammen number quoted — verify against the PDF, not agent summary.

### Venue decision — DEFER TO USER
Roadmap suggests TMLR primary (claims-audited review suits a pre-registered null + κ=0.967 +
deviation disclosure), IEEE Access fallback. This AMENDS the locked IEEE target — a real
strategic call for the user to confirm, not auto-adopt.

### Analysis TODO (from roadmap, all zero-inference)
- Cochran-Armitage per model (the pre-specified trend test; Spearman was a deviation — disclose)
- Resolve §3d-vs-§15 ladder-coding discrepancy (anon-inclusive vs persona-only) — report BOTH
- ∆Entropy, Robustness Rate, progressive/regressive relabel from logged logprobs
- Correct-arm asymmetry (recency rebuttal: pure recency = direction-symmetric; −3.50 says not)
- Generation-integrity audit (30-50 turn-2 prompts — promised, still undone)
- Deviations-from-pre-registration table (GEE→GLMM, Spearman-for-CA, judge 2.0→2.5, n=60, etc.)
- Freeze a results manifest (script + hash) before writing any results sentence

---

## 17. BLOCKER ANALYSIS — VERIFIED confirmatory result (2026-07-06) [CRITICAL]

### Regex vs judge labels: 99.9% agreement (4,129 trials) — confirmatory result is label-robust.

### ⚠️ METHOD WARNING — do NOT use variational-Bayes GLMM here
Three methods on the SAME pre-registered interaction (tier×direction, generic personas,
control excluded, both arms, n=5,510):
- Variational-Bayes BinomialBayesMixedGLM: z=+10.4 "hugely significant"  ← ARTIFACT
- Frequentist logit (model as fixed effect): coef=+0.022, p=0.78  ← NOT significant
- GEE (cluster=model): p=0.95  ← NOT significant
VB underestimates uncertainty (overconfident SEs) → its z is a fitting artifact, NOT a real
effect. 2 of 3 rigorous methods say NOT significant, and the RAW DATA confirms it (below).
LESSON: nearly rewrote the headline on a VB artifact; a second-method check caught it (per
the roadmap's "spot-check before drafting"). Use frequentist GLM / GEE, never VB, for this.

### RAW DATA confirms the null (accuracy-retained by tier, pooled)
INCORRECT arm: tier anon→high = 26% → 34% → 28% → 21%  → NON-MONOTONIC (up then down)
CORRECT arm:   96% → 90% → 91% → 94%  → flat
→ No clean pooled tier×direction interaction. The pre-registered confirmatory test FAILED.
  Our original conclusion was CORRECT. (Direction main effect remains huge & real.)

### VERIFIED per-model trend — Cochran-Armitage (the ACTUALLY pre-specified test; Spearman was a deviation)
PERSONA-ONLY coding (low<med<high), incorrect arm, flip = not-correct-after-pressure:
| Model | flips low→high | CA z | p | sig |
|---|---|---|---|---|
| Qwen-3B | 79 80 80 | +0.16 | 0.87 | no |
| Llama-3B | 94 96 98 | +1.44 | 0.15 | no |
| Qwen-7B | 95 98 99 | +2.07 | 0.039 | * |
| Mistral-7B | 30 36 47 | +2.54 | 0.011 | * |
| Phi-3.5 | 60 77 94 | +6.09 | <0.001 | * |
| Gemma-9B | 42 45 57 | +2.37 | 0.018 | * |
→ 4/6 significant per-model. But does NOT aggregate to a pooled interaction (heterogeneity).

ANON-INCLUSIVE coding (anon<low<med<high): resolves §3d-vs-§15 discrepancy — REPORT BOTH.
Qwen-7B drops to p=0.052 (ns), Mistral goes negative (anon out-flips low), Phi/Gemma stay sig.
→ The exact "how many models grade" count DEPENDS on ladder coding. Report both; claim only
  "persona-rank trend in a subset," never a fixed universal count.

### STABLE, VERIFIED headline (safe to write)
"The pre-registered pooled tier×direction interaction was not supported (frequentist p=0.78;
GEE p=0.95; raw pooled accuracy non-monotonic). Endorsement direction dominates. Authority
grading is significant per-model in 4/6 (Cochran-Armitage, persona-only coding) but does not
aggregate into a clean pooled gradient — model-dependent, not universal." (label-robust; κ=0.967.)

---

## 18. SESSION LOG / CURRENT STATE SNAPSHOT (2026-07-07)

### Where the project stands
- ALL inference complete: 6 models × (main 5-rung + condition-B anon + domain-matched low/med/high),
  both arms. Judge (Gemini 2.5 Flash) done; human validation Cohen's kappa=0.967, Gwet AC1=0.980.
- Blockers 1 & 2 DONE and VERIFIED (§17). Confirmatory NULL is triple-confirmed.
- Everything pushed to github.com/Gokul-2004/research-1.

### The VERIFIED findings (safe to write — all checked)
1. Pre-registered pooled tier×direction interaction NOT supported (freq p=0.78, GEE p=0.95,
   raw pooled accuracy non-monotonic 26→34→28→21%). Original null was correct.
2. Direction main effect huge & robust (incorrect endorsement devastates; correct barely helps).
3. Regex vs judge labels agree 99.9% → results label-robust.
4. Per-model authority trend (Cochran-Armitage, persona-only): significant in 4/6 (Qwen-7B,
   Mistral, Phi, Gemma). Does NOT aggregate to a pooled gradient → model-dependent.
5. Ladder-coding matters: anon-inclusive vs persona-only give different "how many grade" counts →
   report BOTH; claim only "persona-rank trend in a subset."
6. Domain-matched personas (EXPLORATORY): strengthen gradient in 3/6, collapse Mistral
   (saturation ceiling). Gemma clean behavioral win 43→76%.
7. Anon rung ~ professor rung → presence of counter-claim, not source authority, drives most flips.

### Key LESSONS learned this session (methodological hygiene)
- DO NOT use variational-Bayes mixed GLMM for significance — it gave a false z=10.4 that nearly
  reversed the headline. Use frequentist GLM / GEE. Always cross-check a consequential result
  with a second method BEFORE writing.
- Domain-matched run is EXPLORATORY (not pre-registered; §7d = model expansion only).
- Spearman was a deviation from the pre-specified Cochran-Armitage — disclose.
- Purged falsified framing ("gradient in belief, masked behaviorally" — anon ladder killed it).

### DONE (analyses)
- Confirmatory GLMM (freq + GEE + VB, verified), judge-label recompute, Cochran-Armitage per model,
  both ladder codings, regex-vs-judge agreement, domain-matched 6-model, Mammen comparison.

### PENDING (analyses — next, zero inference)
- ∆Entropy (Shannon over A/B/C/D, pre/post) — test Mammen's confident-error signal at 3B-9B.
- Robustness Rate (fraction unchanged) per model/tier/arm.
- Progressive/regressive relabel from logprobs.
- Correct-arm asymmetry (recency rebuttal: pure recency = direction-symmetric; -3.50 says not).
- Generation-integrity audit (30-50 turn-2 prompts assert wrong_X/correct_text).
- Deviations-from-pre-registration TABLE (GEE→GLMM, Spearman-for-CA, judge 2.0→2.5, n=60 not 100,
  severity re-baseline, post-hoc timestamps for cond-B + domain-matched).
- Freeze a results manifest (script + hash) before writing any results sentence.
- Wilson CIs on all reported proportions.

### PENDING (writing/strategy)
- VENUE DECISION (user's call): TMLR primary vs IEEE Access fallback — roadmap favors TMLR for a
  pre-registered null + full disclosure. Not yet decided.
- MUST-VERIFY before draft: "Mammen tables show Mistral grading steepest" and any per-model Mammen
  number — check against the actual PDF, not agent summary.
- Then: figures (4), draft (null-first "confirm and bound"), arXiv, AF post, venue submission.
- Working title: "Presence, Not Prestige: Claim Presence Dominates Source Authority in the
  Behavioral Sycophancy of Small Open LLMs."

### DO-NOT list (locked)
- No "fails to replicate Mammen" (say "does not translate to two-turn behavioral measurement").
- No "we reconcile the field" / "gradient lives in belief" (falsified).
- Don't cite §7d for domain-matched pre-registration. Don't call control "zero-authority".
- Don't attribute heterogeneity to size/RLHF. Don't pool generic+domain-matched confirmatory.
- Don't present n=6 taxonomy as population claim. Never cite workshop paper as "746".
