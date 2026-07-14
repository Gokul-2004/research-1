# Deep Dive: Mammen (2601.13433) + Wang (2508.02087)
> The two papers our contribution is positioned against. Read from the actual sources
> (Mammen: local PDF, full text; Wang: arXiv HTML, full text) on 2026-07-08. Every number
> here is transcribed from the paper's own tables/figures. Facts flagged [VERIFY] were not
> fully confirmable from the source read and must be checked before entering the manuscript.
> Companion to VERIFY_MAMMEN.md (which caught earlier false claims — heed it).

---

# PART A — MAMMEN et al. (the direct predecessor)

## A1. Citation
- **Priyanka Mary Mammen (UMass Amherst), Emil Joswin, Shankar Venkitachalam (Independent Research).**
  "Who Endorsed It? Measuring Authority Bias Across Expertise Levels in Language Models."
  arXiv:2601.13433v4 [cs.CL], 29 May 2026. Funded by Bluedot AI Safety Rapid Grants.
- Note the author overlap with the Joswin ICML-2026 mechanistic workshop paper (Emil Joswin) —
  the two are a linked behavioral+mechanistic pair. Cite Mammen for the behavioral/steering
  results here.

## A2. What they did (setup)
- **11 models**, split to test whether reasoning ability changes susceptibility:
  - *Reasoning (4):* Qwen3-4B-Thinking, DeepSeek-R1-Qwen3-8B, Phi-4-Reasoning, Olmo-3.1-32B-Think.
  - *Non-reasoning (7):* Qwen-2.5-14B, LLaMA-3.1-8B, Phi-4, **Gemma-2-9B-IT**, Gemma-3-12B-IT,
    **Mistral-7B**, Olmo-3.1-32B.
  - **★ SHARED WITH US: Gemma-2-9B-IT and Mistral-7B.** (They use Qwen-2.5-**14B**, not our 7B.)
- **4 datasets, 3 domains:** AQuA-RAT (math/"science reasoning"), LEXam (legal, English subset),
  MedMCQA + MedQA (medical). **No overlap with our ARC/MMLU/TruthfulQA.**
- **4-tier DOMAIN-MATCHED institutional personas** (this is precisely what our domain-matched
  condition emulates):
  - Science: High Schooler → Undergrad → Grad Student → Professor
  - Medicine: First-Year Med Student → Third-Year Med Student → Chief Resident → Board-Certified Physician
  - Law: Undergraduate Law Student → Third-Year Law Student → Law Clerk → Senior Legal Counsel
- **Format:** endorsement appended to the MCQ as one line — *"A [persona] thinks the answer is [X]"* —
  no justification, minimal, uniform. 9 prompt variants per question (1 baseline + 4 correct + 4 incorrect),
  **each an independent model invocation.**
- **★ TURN STRUCTURE (the key differentiator — handle precisely):** The model sees question+hint
  *together* and answers once. Their Related Work calls this a "two-step interaction to eliminate
  look-ahead bias" — but that means baseline and endorsed are *separate invocations*; it is NOT a
  conversation where the model commits to an answer and is then challenged. **Correct framing:
  "the model has not publicly committed to an answer before the endorsement (Question-then-Hint),
  vs. our commit-then-challenge two-turn." Do NOT call Mammen flatly "single-turn."**
- **Measurement:** output **logits over A–D only**, greedy, **no free-form generation**. Confidence
  and entropy read from the output distribution. (Our behavioral free-generation arm is a genuine
  differentiator.)
- **Metrics:** ΔAccuracy (endorsed − baseline), ΔEntropy (ΔH; negative = more confident), Robustness
  Rate RR (fraction of answers unchanged by the endorsement).

## A3. Headline result
- **Clean monotonic authority hierarchy across all domains and both model types.** Correct
  endorsements → accuracy gains that grow with expertise; incorrect → degradation that grows with
  expertise. Their flagship (DeepSeek-R1, MedQA): correct **+0.381** at Board-Certified Physician;
  incorrect **−0.019** (First-Year) → **−0.356** (Board-Certified Physician). Monotonic both ways.
- They explicitly argue this is NOT baseline instability: *"A model that was merely unstable would
  be pushed around indiscriminately; the graded response we observe instead reflects an internalized
  authority hierarchy."* (This sentence is essentially the null hypothesis our pre-registration tested.)
- **"High-Expertise Incorrect Endorsement Induces Confident Errors":** DeepSeek-R1-Qwen3-8B ΔH
  **−0.261** on MedQA under a board-certified-physician incorrect endorsement (more confident in the
  wrong answer). NB: this is a **reasoning model, medical, single-invocation-logit** — the scope for
  our ΔH non-replication contrast.
- Math (AQuA-RAT) had the **lowest** robustness (highest susceptibility) despite being most
  "objective"; medical had higher resistance. → domain difficulty does not protect; do not use it as
  our excuse.
- Reasoning models were **not** immune.

## A4. ★ The two SHARED models — exact incorrect-endorsement ΔAccuracy (their Table 1)
These are the only apples-to-apples-ish comparison points we have. (Their values; single-invocation
logit; different domains from ours — directional comparison only.)

**Mistral-7B** (baseline acc in parens): tiers = [lowest → highest authority]
| Dataset | t1 | t2 | t3 | t4 (top) | shape |
|---|---|---|---|---|---|
| AQuA-RAT (0.264) | −0.15 | −0.106 | −0.197 | −0.236 | ↘ graded |
| MedMCQA (0.492) | −0.155 | −0.227 | −0.339 | −0.40 | clean monotonic ↘ |
| MedQA (0.529) | −0.095 | −0.188 | −0.295 | −0.447 | clean monotonic ↘ |
| LEXam (0.297) | −0.195 | −0.21 | −0.207 | −0.229 | ~flat |
→ **In Mammen, Mistral GRADES (clean monotonic degradation with authority) in 3/4 datasets.**
  In OUR two-turn behavioral setup Mistral is the RESISTER with a weak/collapsing gradient.
  **This is the single sharpest same-model contrast we can draw** — same model, opposite gradient
  behavior, attributable to protocol (single-invocation-logit vs two-turn-behavioral). The
  single-turn ablation is what will let us claim this cleanly.

**Gemma-2-9B** (baseline in parens):
| Dataset | t1 | t2 | t3 | t4 (top) | shape |
|---|---|---|---|---|---|
| AQuA-RAT (0.303) | +0.02 | +0.008 | −0.091 | −0.157 | flat then drop at top |
| MedMCQA (0.557) | −0.017 | −0.051 | −0.10 | −0.207 | monotonic ↘ |
| MedQA (0.623) | +0.024 | −0.006 | −0.038 | −0.225 | flat then drop at top |
| LEXam (0.488) | +0.003 | −0.081 | −0.191 | −0.368 | monotonic ↘ |
→ Gemma's authority effect is **concentrated at the top tier** (Professor/Physician/Senior Counsel).
  Matches OUR finding: Gemma resists low tiers, responds to strong authority, and domain-matched
  personas strengthen its gradient. **A convergence point, not a contradiction — usable.**

## A5. Mechanistic half (what we DON'T have)
- Steering vector `v_auth` = mean residual-stream difference between top- and bottom-authority
  *linguistic styles* (a SEPARATE ~90–120-prompt set, factually-correct answers, **no persona labels**
  — style only). Subtracting it recovers accuracy under misleading high-authority endorsements;
  adding it amplifies low-credibility persuasion. → authority bias is "mechanistically encoded in the
  residual stream," steerable at inference with no weight change.
- **Their own admission (use this):** the layer analysis is **preliminary** — intervention "most
  effective in the middle layers ([L/3, 2L/3])," but **no systematic layer ablation, no SAEs.** This is
  the explicit gap our Paper 2 (mechanistic probe of the two-turn saturation ceiling) would fill.

## A6. Their stated limitations (each is an opening for us)
1. Only ≤32B open models; no frontier scale.
2. Only 4 domains (math/legal/medical) — **all reasoning-heavy; none of our ARC/TruthfulQA-style
   general factual knowledge.**
3. **Endorsement is a single explicit statement, no variation in phrasing/confidence/justification** —
   they note real misinformation is more sophisticated. Our two-turn conversational pressure is a step
   toward that.
4. Mechanistic analysis preliminary (see A5).

## A7. How to position vs Mammen (LOCKED — from earlier analysis + VERIFY_MAMMEN)
- **BOUND, do not refute.** We did not run their protocol; we cannot overturn an 11-model study.
  Claim: *"Mammen's clean monotonic gradient holds under Question-then-Hint logit measurement; under
  a two-turn behavioral commit-then-challenge protocol it collapses into presence-driven capitulation
  in most small open models."* We are the stress-test / boundary-finder.
- **CONFIRM where we agree:** strong institutional authority devastates accuracy (their −0.36; our
  domain-matched high-tier accuracy floors); Gemma's top-tier sensitivity; reasoning/objective domains
  not protected.
- **DELETE the false claim:** "Mammen shows Mistral grades steepest" — FALSE. Steepest is DeepSeek-R1
  (−0.356 MedQA) / Phi-4-Reasoning (−0.81 LEXam). Mistral grades *monotonically* but not most steeply.
- **ΔH non-replication = scope boundary**, not contradiction (their confident-error is reasoning/
  medical/logit; ours is non-reasoning/broad/two-turn behavioral).

---

# PART B — WANG et al. (the novelty threat / convergent result)

## B1. Citation
- **Jin Li, Keyu Wang, Shu Yang, Zhuoran Zhang, Di Wang** (equal-contrib among leads).
  "When Truth Is Overridden: Uncovering the Internal Origins of Sycophancy in Large Language Models."
  arXiv:2508.02087v1, August 2025. [VERIFY affiliations + any AAAI-2026 acceptance before citing a venue;
  arXiv cite is safe.]

## B2. What they did (setup)
- **7 models, ~comparable size** (to isolate non-scale effects): Llama3.1-8B-Instruct,
  **Qwen2.5-7B-Instruct**, OPT-6.7B, **Mistral-7B-Instruct-v0.3**, Falcon-7B, OLMoE-1B-7B-Instruct,
  Pythia-6.9B.
  - **★ SHARED WITH US: Qwen2.5-7B-Instruct AND Mistral-7B-Instruct-v0.3.**
- **1 dataset:** MMLU (57 subjects, MCQ A–D). We use ARC + MMLU + TruthfulQA (broader).
- **★ SINGLE-TURN (confirmed):** opinion prepended to the question, model answers once with a single
  letter. **No commitment-then-challenge. Our two-turn design is a clean differentiator from Wang too.**
- **4 conditions:** (1) Plain baseline; (2) Opinion-only "I believe the right answer is [X]" (X = a random
  incorrect choice); (3) First-person expertise (Beginner/Intermediate/Advanced, GPT-4o-generated role
  descriptions, e.g. "As an Expert in Abstract Algebra…"); (4) Third-person expertise ("A professor of…
  they believe…").
- **★ They DO have a graded expertise ladder** (3 levels) — but generated competence descriptions, NOT
  our anon rung and NOT domain-matched *institutional* titles the way Mammen/we frame them.

## B3. ★ Headline numbers (their figures/tables)
- **Opinion-only sycophancy: 63.7% average across 7 models, range 46.6%–95.1%.** (Presence of a bare
  opinion already flips most models most of the time.)
- **Expertise framing effect is NEGLIGIBLE: within 4.4% for any given model.** Per-model first-person
  Beginner/Intermediate/Advanced, e.g. Qwen2.5-7B 42.99/38.46/39.51; Llama3.1 48.68/47.53/45.76;
  Mistral-7B 62.64/58.67/61.91; Falcon 91.16/89.20/88.14. → **This is "presence, not prestige,"
  quantified — and it is CONVERGENT with our null on the authority gradient.**
- **★ First-person > third-person by 13.6 pp on average** (e.g. Mistral 61.91%→45.45%, −16.5pp;
  OPT −21.6pp; Falcon −17.5pp). **THIS EXPLAINS OUR CONTROL-RUNG ANOMALY:** our `control` rung is
  first-person ("I don't think that's right… I believe X") and out-pushes our third-person personas —
  exactly Wang's first>third effect, independent of authority. **We can cite Wang to explain our own
  control behavior instead of treating it as a nuisance.**

## B4. Mechanistic findings (their internal-origins half)
- **Two-stage emergence:** (1) late-layer output-preference shift (Llama3.1 ~layer 19) — opinion
  prevents the correct-answer preference that forms in Plain; (2) deeper representational divergence
  (KL between Plain and Opinion hidden states) peaking ~layer 23 (Llama) / ~layer 27 (Qwen), negligible
  in early/mid layers.
- **Activation patching** at the critical layer (Llama L32, Qwen L27): suppression cuts Llama sycophancy
  by **36 pp**; induction raises it to **47%** → causal, bidirectional.
- **Expertise not encoded:** at Llama L32, expertise levels collapse into one cluster (cosine sim
  0.90–0.997) while opinion-only is separated (−0.95 to −0.998). → the model represents "there is an
  opinion" but not "how expert the opinion-holder is."
- **First/third person are near-orthogonal directions** (cosine ≈ −0.04).

## B5. Their limitations (our openings)
- Single dataset (MMLU); MCQ only; **single-turn only** (no multi-turn/open-ended — explicitly a gap);
  expertise via GPT-4o templates (not real credentials); cross-domain generalization not tested;
  analysis centered on Llama3.1 + Qwen2.5.

## B6. How to position vs Wang (LOCKED)
- **CONFIRM-AND-EXTEND, do not deny.** The overlap is real and only on the *one* claim (presence >
  expertise). Cite Wang **prominently in Intro + Related Work**: *"Wang et al. (2025) show
  mechanistically that opinion presence, not expertise, drives sycophancy; we provide independent,
  pre-registered BEHAVIORAL confirmation under a two-turn protocol and extend it in four ways they
  cannot."*
- **Our four extensions beyond Wang (the actual novelty):**
  1. **Two-turn commit-then-challenge** (Wang single-turn) — realistic conversational pressure.
  2. **Anon rung + domain-matched institutional personas** (Wang: GPT-4o competence blurbs) — and we
     resolve the Wang-vs-Joswin tension (competence framing does ~nothing / institutional framing
     matters) via our generic-vs-domain-matched A/B.
  3. **"Confidence doesn't protect"** — a finding Wang does not report.
  4. **Broader domains** (ARC/MMLU/TruthfulQA vs MMLU only) + **pre-registration + human-validated judge.**
- **Make the headline the thing Wang LACKS** (confidence-independence + the behavioral two-turn result +
  the persona-type A/B), and let presence-not-prestige read as "we independently confirm Wang."
- **Use Wang's first>third-person result** to explain our control rung (B3). Strong, verified, and it
  turns a messy design detail into a literature-grounded point.

---

# PART C — SYNTHESIS: the combined positioning

## C1. The one-paragraph story (draft-ready)
> Two independent studies with orthogonal methods bracket our result. Wang et al. (2025), using
> single-turn prompting and mechanistic analysis, find that the *presence* of a user opinion — not its
> stated *expertise* — drives sycophancy (expertise effect ≤4.4%). Mammen et al. (2026), using
> Question-then-Hint logit measurement over 11 models and domain-matched institutional personas, find
> the opposite-seeming result: a *clean monotonic authority gradient*. We reconcile them behaviorally.
> Under a pre-registered two-turn commit-then-challenge protocol across six small open models, the mere
> presence of a counter-claim dominates (a nameless "someone" ≈ "a professor" for 4/6 models;
> direction |coef|≈3.5, p<0.0001), the pre-registered authority×direction gradient is not supported
> (p≈0.95) — **converging with Wang** — yet domain-matched *institutional* personas partially restore a
> graded belief effect in 3/6 models — **bounding Mammen**. Authority grading is thus real but fragile:
> it survives single-turn logit measurement and institutional framing, and collapses under two-turn
> behavioral pressure and generic framing.

## C2. Shared-model comparison table (assemble once single-turn ablation lands)
Both predecessors share models with us → a rare direct bridge. Fill our two-turn + single-turn columns
after the ablation:
| Model | Wang (single-turn, MMLU) | Mammen (Q-then-Hint logit) | Us two-turn (done) | Us single-turn (ablation) |
|---|---|---|---|---|
| Mistral-7B-v0.3 | opinion-only syc high; expertise ≤4.4% | GRADES monotonically (3/4 datasets) | RESISTER, weak/collapsing gradient | [pending] |
| Qwen2.5-7B | in their 7 | (they use 14B, n/a) | SATURATOR | [pending] |
| Gemma-2-9B | n/a | top-tier authority effect | resister, domain-matched strengthens | [pending] |
→ The Mistral row is the headline: same model, GRADES in Mammen's protocol, RESISTS in ours. If the
  single-turn ablation shows Mistral grading under Question-then-Hint on OUR items, we have localized
  the entire difference to protocol — the cleanest possible "we bound Mammen" claim.

## C3. Citations to add to CITATIONS.md
- Wang et al. 2025, arXiv:2508.02087 — "When Truth Is Overridden" — convergent presence>expertise;
  mechanistic; first>third person. [VERIFY venue]
- (Mammen 2601.13433 already in corpus — ensure the shared-model + steering-preliminary points are captured.)

## C4. Facts to VERIFY before manuscript
- Wang: affiliations; any AAAI-2026 acceptance; exact author order (leads listed equal-contrib).
- Wang: whether they gate on baseline correctness (affects whether their 63.7% is comparable to our gated flip rates).
- Mammen: confirm the "two-step interaction" wording in their Related Work vs the append-to-question
  methodology — our differentiator is "no prior commitment," not "single vs two prompt." (VERIFY_MAMMEN.)
