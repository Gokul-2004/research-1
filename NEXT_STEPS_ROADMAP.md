# Next-Steps Roadmap — synthesized 2026-07-06
# From multi-agent analysis: lit survey + POINTS_FOR_PAPER + ANALYSIS_PLAN + stashed FINDINGS_HONEST_REVIEW/Publication_Venues + Mammen & Joswin PDFs,
# adjudicated across adversarial-reviewer / novelty-maximizer / venue-strategist perspectives.

## 1. The paper you should write

Write the null-first, confirm-and-bound paper. Headline: **in a pre-registered two-turn protocol with an assertion-matched anonymous baseline, the mere presence of a counter-claim — not the authority of its source — overwhelmingly drives small open LLMs to abandon committed correct answers** (direction p<0.0001; pre-registered tier×direction interaction p=0.95); authority grading emerges only model-dependently and only under domain-matched institutional personas (3/6 strengthen, first within-protocol test of Joswin et al.'s boundary condition), and in the most resistant model (Mistral) strong authority *saturates* susceptibility — while Mammen's own logit tables show Mistral grading steepest, giving you a clean behavior-vs-belief dissociation. All three strategists converge here: the adversarial reviewer's "most defensible claim," the novelty ranking's top three items (presence-not-authority, saturation ceiling, domain-match manipulation), and the venue strategist's abstract skeleton are the same paper. Frame as methodological (locked): first behavioral, pre-registered, inferentially tested study in the Mammen/Joswin line — "confirm and bound," never "refute."

## 2. Immediate next steps (ordered, ~1–2 weeks, no new inference)

1. **Judge-label re-run (blocker).** Execute judge_bundle OBJECTIVE Step 4: recompute the confirmatory stats on the substance labels in `judge_bundle/results/judged/*__judge1.jsonl` instead of regex flips. Provenance of the current GEE is unverified — a post-arXiv number shift here destroys the pre-registration brand.
2. **Formal pre-specified GLMM (blocker).** `correct_after_pressure ~ tier*direction*domain + (1|model)+(1|question)`, tier ordered, LRT on tier×direction, on the ~5,510 gated main-run trials (`judge_bundle/results/inference/*.jsonl`), generic personas only — never pooled with domain-matched. Fit on both regex and judge labels; extract random tier-slope variance to formalize the saturator/resister/graded taxonomy.
3. **E-family + BH.** E1 Cochran–Armitage per model (incorrect arm; the pre-specified trend test — Spearman was a deviation), E2 domain term, E4 McNemar, E5 Kruskal–Wallis; BH-correct as one family. Recompute every ladder statistic — including §15 domain-matched — under **both codings** (anon-inclusive and persona-only) and make dual-coding canonical; this resolves the §3d-vs-§15 discrepancy.
4. **Control-rung repair, disclosed.** Report the control rung separately (it out-pushes the professor — a stronger-pressure condition, not a floor); redefine regressive_severity against the anon rung with Wilson CIs, stating the original definition and the deviation. Do not quietly swap.
5. **∆Entropy, Robustness Rate, SycEval progressive/regressive relabeling** from logged logprobs; test whether Mammen's ΔH<0 confident-errors replicates at 3B–9B.
6. **Correct-arm asymmetry analysis** (recency rebuttal): if capitulation were pure last-message recency it would be direction-symmetric; quantify the asymmetry behind the −3.50 coefficient.
7. **Generation-integrity audit** (30–50 turn-2 prompts; promised, undone) and the **deviations-from-pre-registration table**: GEE→GLMM, judge 2.0→2.5 Flash, single judge (cite OBJECTIVE.md rationale), n=60 not ~100, Spearman-for-C-A, severity baseline, and explicit post-hoc timestamps for Condition B (07-01) and the domain-matched run (07-04 pledge). This table converts five gotchas into a credibility asset.
8. **Freeze a results manifest** (script + hash) before writing any results sentence; purge §12/§5 vintage language from all drafts; fix Methods to Gemini 2.5 Flash; verify Mammen's publication status; delete the duplicate PDF.
9. **Figures** (see §4).

## 3. Analyses to ADD (all zero-inference; all survived novelty × HARKing scrutiny; label every one exploratory)

- **Behavior-on-belief psychometric function**: per-model logistic `flip ~ belief_gap(t2)` with (1|question). Quantifies the flip threshold and whether saturators sit lower than resisters — turns the dissociation claim into a curve nobody has published. *Exploratory.*
- **Step-vs-gradient coding contrast**: refit tier as linear-ordered vs high-vs-rest on generic and domain-matched data. Tests the "threshold, not gradient" reading that Joswin's own vector geometry predicts — reframes your null as agreeing with their mechanism. *Exploratory, BH family.*
- **Correct-endorsement-arm belief dose-response** (never cross-analyzed): does correct endorsement grade where incorrect doesn't? Doubles as the recency rebuttal. *Exploratory.*
- **Per-question susceptibility correlation across models**: item-level flip-rate matrix — the behavioral analogue of Joswin's per-question (not mean) steering vectors; a genuinely novel cross-paper link. *Exploratory/descriptive.*
- **Turn-1 belief margin as flip moderator** ("do models defend strongly-held beliefs?"). *Exploratory, minor.*

## 4. Framing & writing decisions

**Venue (adjudicated):** TMLR primary, IEEE Access fallback — I'm amending the locked IEEE target, with cause: TMLR's claims-audited review is the one venue where a pre-registered null + κ=0.967 validation + full deviation disclosure is an asset (est. 55–65% vs IEEE's ~50–60% with $2,160 APC and out-of-field reviewers). The locked deliverable ("arXiv + open access") is satisfied either way. Path: blockers → draft → arXiv → AF post within a week (safety-upshot lead: "credentials barely matter; any pushback flips 49–98%") → TMLR, with a concurrent non-archival NeurIPS/ICLR-workshop submission of the domain-matched A/B (same MechInterp community as Joswin). IEEE on TMLR reject.

**Title:** "Presence, Not Prestige: Claim Presence Dominates Source Authority in the Behavioral Sycophancy of Small Open LLMs." Keep the venue strategist's #2 (question-form, "pre-registered") as backup if TMLR reviewers read #1 as overclaiming.

**Figures:** Fig 1 pooled tier×direction interaction with Wilson CIs (the null made visible); Fig 2 six-panel per-model flip ladders **including the anon rung**; Fig 3 generic-vs-domain-matched paired ladders (Gemma 43→76% and Mistral collapse carry it); Fig 4 behavior-vs-belief scatter, Mistral quadrant highlighted. Appendix: deviation table, both codings, judge validation, integrity audit.

**Five sharpest attacks + neutralizations:**
1. *"Confirmatory failed; the paper is the pivot"* → Null-first structure; domain-matched run explicitly post-hoc with the OBJECTIVE.md report-either-outcome pledge and timestamps; never cite §7d for it.
2. *"Your 'recovered gradient' excludes the anon rung"* → Both codings in main text for every ladder; claim only "persona-rank trend among institutional personas," never "gradient from zero to high."
3. *"Your control isn't a control"* → Reported separately with the anomaly named; severity re-baselined to anon, deviation disclosed.
4. *"Direction effect is recency"* → Tier contrasts are position-controlled (pushback last in all conditions), so the null is clean; the direction asymmetry analysis is itself evidence against pure recency; Ben Natan cited in Limitations (locked sentence).
5. *"Single-letter answers aren't free-form behavior"* → Rebrand as "behavioral answer revision under conversational pressure after explicit commitment" — the two-turn commitment is the real novelty; drop "free-form" everywhere.

## 5. Small optional experiments

- **Turn-structure ablation** (Mammen's single-prompt hint format on your items, Mistral + Qwen-7B, ~5–10h CPU, OBJECTIVE-pledged before running): **GO** — the one experiment that separates measurement-modality from persona design as the gradient suppressor, your biggest open question; runs overnight in parallel with drafting. (Adjudication: novelty maximizer's top pick beats the reviewer's mismatched-domain arm, which answers a smaller question for similar cost.)
- **E6 SycophancyEval "Are you sure?" calibration**: **SKIP** — optional in the plan, anon rung already serves as the assertion floor; run only if a reviewer asks. (Adjudicating novelty-max "do" vs venue "defer": defer wins; it adds comparability, not validity.)
- **Dual-judge run 2**: **SKIP** — deprecated with documented rationale; human κ=0.967/AC1=0.980 is stronger evidence than a temp-0 self-rerun; disclose in the deviations table. (2-of-3 strategists against.)
- **Mismatched-domain high-authority arm**: **SKIP** — strength-vs-matching confound becomes a limitation sentence and Paper 2 factorial cell.
- **Position-counterbalance mini-run**: **SKIP** — contradicts the locked "Limitations sentence, not machinery" decision; the asymmetry analysis covers it.
- **First-vs-third-person A/B, repeated-sampling stability, base-vs-instruct**: **SKIP** — all Paper 2 material; scope creep now.

## 6. Future work / Paper 2

1. **Measurement-modality × persona-type factorial** (single-prompt-logit vs two-turn-behavioral × anon/generic/domain-matched, same items/models): directly adjudicates the field's clean-gradient-vs-general-susceptibility tension; runs on your existing fleet in 2–4 overnights; the turn-structure ablation is its pilot.
2. **Mechanistic probe of the saturation ceiling**: per-question steering vectors (Joswin) applied in the two-turn setting — does the ceiling live downstream of graded belief? Needs the already-scoped ~24GB GPU rental; highest novelty per dollar.
3. **Multi-turn persistence (ToF/NoF)**: authority may grade *resistance duration* rather than first-flip probability — a new DV the corpus hands you, cheap on CPU.

Not these: frontier-scale (infeasible locally — cite), human-perception (needs subjects/IRB — cite Batzner gap), mitigations (steering-vector literature is internally unresolved — cite the 2601.13433-vs-Joswin tension instead).

## 7. Do NOT do

- **Do not use any §12/§5 vintage language** ("gradient lives in belief, masked behaviorally"; "we reconcile the field") — falsified by your own anon ladder (1/6 monotonic; Mistral's ρ positive).
- **Do not say "fails to replicate" Mammen** — you never ran their protocol; say "does not translate to two-turn behavioral measurement."
- **Do not cite ANALYSIS_PLAN §7d for the domain-matched run** — it covers model expansion only; that citation is false and checkable.
- **Do not call the control rung "zero-authority" or compute severity against it** — anon is the floor.
- **Do not brand the DV "free-form"** — single-letter outputs; and do not run E3 hedging or CoT-failure quantification (degenerate on max_new_tokens=20; document as such).
- **Do not attribute heterogeneity to parameter count or RLHF** — no evidence, corpus unresolved (Qwen-7B saturates while Gemma-9B resists).
- **Do not pool generic and domain-matched runs in one confirmatory family**, present the taxonomy as a population claim (n=6, descriptive only), cite the workshop paper as "746," or lead the abstract with behavior-vs-belief while deferring the logprob evidence (locked).
- **Do not claim any universal gradient, in behavior or belief** — the honest story is presence-dominance, bounded and model-dependent grading, and the Mistral dissociation. That story is publishable; the inflated one is not.