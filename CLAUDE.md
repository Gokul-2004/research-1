# CLAUDE.md — project current-state card

> Index + current state, not the manual. Read in 30s, act correctly. Design details live in `PLAN.md` — do not duplicate them here.

## What this is
An empirical AI-safety study, **"Authority-Graded Sycophancy in Open-Source LLMs"** — does an open-weights LLM abandon a correct answer more readily as the *authority* of the user's counter-claim rises (graded dose-response), measured both behaviorally (free-form, judged) and via token log-probs? Deliverable: a paper targeting **arXiv preprint + IEEE Access** (open access), with an Alignment Forum write-up.

## Read first
**Full technical design is in `PLAN.md` — read it before starting work.** Per-paper literature analysis is in `Literature Survey/Analysis of Literature Survey.md`. Deep handoff/history is in `context.md`. **Completed work + all key numbers are in `PROGRESS.md` — read this before writing the paper.** (This file is the index + status card; those are the source of truth.)

## Locked decisions (don't re-litigate)
- **Contribution = methodological, NOT discovery.** Authority-graded sycophancy already exists in prior work (arXiv 2601.13433 + an ICML 2026 workshop paper). We measure it more rigorously/behaviorally and test a new question. Don't overclaim novelty.
- **Logprob arm = GO ✅** (feasibility spike passed) — logprobs ARE collected and used, but the **original "behavior-vs-belief divergence" headline is DEAD** (falsified: fig4 shows behavior & belief are CONCORDANT; the anon ladder shows no clean belief gradient either — POINTS §3g/§16/§20). **Current headline = "Presence, Not Prestige":** presence of a counter-claim, not source authority, drives capitulation; direction dominates; susceptibility is model-dependent. Do NOT reintroduce divergence/"logits recover a masked gradient" language.
- **Stats = ONE pooled GLMM, ONE confirmatory test:** the `authority_tier × endorsement_direction` interaction. Everything else is exploratory (BH-corrected as a family). Report two distinct numbers: (a) the interaction = the *test*; (b) `regressive_severity = flip(incorrect) − flip(zero-authority control)` = the *descriptive effect size*. Never present (b) as the test.
- **Recency/position = a Limitations sentence, not machinery** (two-turn puts pushback last in every condition → held constant across tiers).
- **Citations:** PDFs were downloaded from arXiv (IDs grounded). The workshop paper `746_A_Mechanistic_View_of_Auth.pdf` has **no arXiv ID — cite by authors/title/venue, never "746".**
- **Methodological framing, single `tier × direction` confirmatory GLMM test, two-arm design, length-matched zero-authority control, two-turn structure are all locked — ask before changing any of these.**

## Machine & engine (current — Linux workstation)
- **64 GB RAM, CPU fp16 — this is the binding constraint and the chosen engine.**
- GPU present (Quadro P1000/P2000, ~4–5 GB VRAM) but **too small to load these models — ignore GPU, ignore CUDA/bitsandbytes/quanto entirely.**
- The 8-bit/quanto spike is **obsolete — do not run it.**
- **Setup:** `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
- **Run a spike:** `HF_HOME="$(pwd)/hf_cache" .venv/bin/python src/<script>.py`
- **Layout:** `src/` code · `data/` questions · `results/` outputs (gitignored JSON) · `hf_cache/` model cache (gitignored).

## Spike results
| Spike | Model | Device | ms/scoring | s/trial | h/12,600 trials | Verdict |
|---|---|---|---|---|---|---|
| Phase 0.5 (Mac MPS) | Qwen2.5-3B-Instruct | MPS fp16 | 315 | 1.26 | 4.4 | GO ✅ |
| CPU 7B (Linux) | Mistral-7B-Instruct-v0.3 | CPU fp16 | 5,799 | 23.2 | 81.2 | GO ✅ |
| CPU 3B (Linux) | Qwen2.5-3B-Instruct | CPU fp16 | 5,931 | 23.7 | 83.0 | GO ✅ |

Result files: `results/spike/spike_result.json`, `results/spike/spike_cpu_7b.json`, `results/spike/spike_cpu_3b.json`.

## Wall-clock projection (at 50 Q/domain, CPU fp16)
**Key finding: 3B and 7B cost the same on CPU** — bottleneck is memory bandwidth, not compute.

| Model | ms/scoring | Hours (1,200 trials @ 50 Q) |
|---|---|---|
| Qwen2.5-3B | 5,931 ms | 7.9 h |
| Llama-3.2-3B (or substitute) | ~5,931 ms | ~7.9 h |
| Qwen2.5-7B | ~5,799 ms | ~7.7 h |
| Mistral-7B | 5,799 ms | 7.7 h |
| **Total** | | **~31 h** |

**Run plan:** 2 models per overnight session × 2 nights. No GPU rental needed.
**Do not start until power check is approved and question count locked.**

## Model lineup (provisional — pending power check)
**2× 3B + 2× 7B:**
- `Qwen/Qwen2.5-3B-Instruct` — ungated ✅
- `meta-llama/Llama-3.2-3B-Instruct` — **gated** (needs HF token + license); substitute another ungated 3B if friction
- `Qwen/Qwen2.5-7B-Instruct` — ungated ✅
- `mistralai/Mistral-7B-Instruct-v0.3` — ungated ✅ (already cached)

**Framing:** 3B–7B is the deliberate scope — "models realistically deployed on consumer/edge hardware, where sycophancy is least studied and most consequential." Frontier-scale (8–9B+) behavioral replication → Future Work explicitly.

## Question count (provisional — pending power check)
- **Target: 40 questions/domain** (down from 75), pending power check that cells survive the baseline gate and power the `tier × direction` interaction (not just the marginal trend).
- **Do not start the full run until power check is approved and question count is locked.**

## Status & next steps  (updated 2026-07-13)

### ✅ Completed — ALL INFERENCE + ANALYSIS DONE
- Phase 0: citation check, analysis plan, power pilot (all 3 domains)
- Phase 2: 150-question dataset (`data/questions.json`) — ARC-Challenge / MMLU / TruthfulQA
- Phase 2b: authority templates (`data/authority_templates.json`) — sourced from Mammen + Sharma PDFs
- Phase 3 inference: **all 6 models** (main 5-rung + Condition-B anon + domain-matched), both arms — DONE
- Phase 4 judge: **Gemini 2.5 Flash** (not 2.0 — see deviations), human validation **Cohen's κ=0.967, Gwet AC1=0.980** — DONE
- Phase 5 analysis: confirmatory GLMM (freq p=0.78 / GEE p=0.95 — NULL, triple-verified), Cochran-Armitage per model, ∆Entropy, Robustness Rate, direction asymmetry, 8 figures — DONE
- **Single-turn ablation** (exploratory, POINTS §22): 5/6 models done; Gemma finishing ~2026-07-14 AM
- Results frozen: `RESULTS_MANIFEST.sha256`. Everything pushed to github.com/Gokul-2004/research-1.

### 🔄 In progress
- Gemma-2-9b single-turn ablation (last model) — completes ~Tue 2026-07-14 morning.

### ⏳ Up next (in order)
1. Record final single-turn numbers in POINTS §22 (with Mistral p=0.088 / Phi p=0.107 counterpoint)
2. Paired stats for the commitment penalty (McNemar / GEE — same gate-passed items both structures)
3. Phase 6: Write-up — **IEEE Access** (framing = "Presence, Not Prestige"; cite 2509.16533 + 2508.02087 up front as findings we EXTEND, not discover). See POINTS §16 + lit-survey novelty reassessment.

> **⚠️ Two 2025-26 papers partially scoop our findings** (2509.16533 = turn-structure/"commitment penalty"; 2508.02087 = "presence not prestige"). Contribution is **extension/replication, not discovery** — already locked here. Frame accordingly.

## Conventions & gotchas
- **Log raw outputs to JSON; never overwrite** (append/timestamp — needed for re-analysis).
- **Every question needs verified ground truth** before it enters the set (hand-verify, esp. hand-authored history).
- **Precision-matching discipline:** CPU fp16 across all models/arms (do not mix dtypes).
- **Temp 0; fresh session per trial** (anti-caching).
- **Baseline gate:** only analyze items the model answers correctly unprompted (`ALREADY_WRONG` excluded).
- **Every dataset/algorithm/tool gets its source paper in brackets** (traceability).
- **No multi-day run without explicit go-ahead** — check wall-clock projection first.
