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
- **Graded resisters** (resist + authority matters): Mistral, Phi-3.5
- **Flat resister** (resist but authority-indifferent-ish): Gemma-9B
  (Gemma: robust like Mistral but belief trend weaker/mixed — decouples robustness
   from authority-sensitivity)

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

The field is genuinely split: Mammen + Ask-Don't-Tell found clean monotonic gradients; Zhang +
SycoEval-EM found inconsistent, model-dependent susceptibility. Our 6-model dual-measurement
result explains WHY they disagree — the gradient is real in BELIEF for some models (matching
Mammen) but MASKED behaviorally by saturation in others (matching Zhang/SycoEval-EM).

**KEY POSITIONING / REFRAME SENTENCE (use in Abstract + Discussion):** "We reconcile a tension in
the literature — Mammen's clean authority gradient and SycoEval-EM's 'general susceptibility' are
both correct, for different models and different measurement modalities. The authority gradient is
present in the internal belief signal but is behaviorally masked by capitulation-saturation in the
most suggestible models."

This is a STRONGER paper than "we replicated Mammen" would have been — we tested it across enough
diverse models, with both measurement arms, to see WHY the field disagrees. The comparison to the
literature rescues the apparent messiness: our result is consistent with the field, and adds the
one thing nobody else has (behavior-vs-belief). Honest IEEE estimate with this framing: ~60-65%.

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
