# CLAUDE.md — project current-state card

> Index + current state, not the manual. Read in 30s, act correctly. Design details live in `PLAN.md` — do not duplicate them here.

## What this is
An empirical AI-safety study, **"Authority-Graded Sycophancy in Open-Source LLMs"** — does an open-weights LLM abandon a correct answer more readily as the *authority* of the user's counter-claim rises (graded dose-response), measured both behaviorally (free-form, judged) and via token log-probs? Deliverable: a paper targeting **arXiv preprint + IEEE Access** (open access), with an Alignment Forum write-up.

## Read first
**Full technical design is in `PLAN.md` — read it before starting work.** Per-paper literature analysis is in `Literature Survey/Analysis of Literature Survey.md`. Deep handoff/history is in `context.md`. (This file is the index + status card; those are the source of truth.)

## Locked decisions (don't re-litigate)
- **Contribution = methodological, NOT discovery.** Authority-graded sycophancy already exists in prior work (arXiv 2601.13433 + an ICML 2026 workshop paper). We measure it more rigorously/behaviorally and test a new question. Don't overclaim novelty.
- **Logprob arm = GO ✅** (feasibility spike passed). **Behavior-vs-belief is the headline.** "Forbidden middle": never lead the abstract with behavior-vs-belief while deferring the logprob evidence.
- **Stats = ONE pooled GLMM, ONE confirmatory test:** the `authority_tier × endorsement_direction` interaction. Everything else is exploratory (BH-corrected as a family). Report two distinct numbers: (a) the interaction = the *test*; (b) `regressive_severity = flip(incorrect) − flip(zero-authority control)` = the *descriptive effect size*. Never present (b) as the test.
- **Recency/position = a Limitations sentence, not machinery** (two-turn puts pushback last in every condition → held constant across tiers).
- **16 GB RAM is the binding constraint** on this Mac. Forces: **precision matched across arms/models** (don't mix fp16 here, 8-bit there); **3B in fp16 is the clean anchor** (proven). 8-bit on Mac = **optimum-quanto**, NOT bitsandbytes (CUDA-only). An fp16 8B (~16 GB) does NOT fit here.
- **Citations:** PDFs were downloaded from arXiv (IDs grounded). The workshop paper `746_A_Mechanistic_View_of_Auth.pdf` has **no arXiv ID — cite by authors/title/venue, never "746".**

## Spike results (Phase 0.5, on Qwen2.5-3B-Instruct, MPS)
- MPS vs CPU logprob: max per-token diff **0.031** (≤0.05 threshold) → MPS correct.
- Multi-token answer scoring works ("the Nile" 2 tok, correct answer preferred).
- Throughput: **315 ms/scoring ≈ 1.26 s/trial (4 scorings) ≈ 4.4 h for ~12,600 trials**.
- Verdict file: `results/spike/spike_result.json`.

## Status & next steps
1. **NEXT: 8B-at-8-bit spike (PENDING)** — re-run the 3 checks + peak-memory on a *true 8B* (ungated, e.g. Ministral-8B or a NousResearch Llama-3.1-8B mirror) quantized 8-bit via quanto on MPS. Decides whether the final lineup can include an 8B or must **cap at ≤7B**. (On a 32 GB+ machine this becomes a quick fp16 confirmation instead.)
2. Lock the 4-model lineup (currently provisional: `llama3.2:3b`, `llama3.1:8b`, `mistral:7b`, `gemma2:9b` — 8B inclusion gated on step 1).
3. Build the 225-item dataset (sources in `PLAN.md` §9b).
4. Then Phases 0→8 in `PLAN.md` §9.

## How to run
- **Env:** Python **3.13** venv at `.venv/` (NOT system 3.14). torch 2.12 + transformers + optimum-quanto; MPS confirmed.
- **Setup on a fresh machine:** `python3.13 -m venv .venv && .venv/bin/pip install -r requirements.txt`
- **Check MPS:** `.venv/bin/python -c "import torch; print(torch.backends.mps.is_available())"`
- **Run the spike:** `HF_HOME="$(pwd)/hf_cache" .venv/bin/python src/spike_logprob.py`
- **Layout:** `src/` code · `data/` questions · `results/` outputs (gitignored JSON) · `hf_cache/` model cache (gitignored).
- **HF token:** none needed — use ungated models. Llama-3.1-8B is gated (token + license) only if specifically required.

## Conventions & gotchas
- **Log raw outputs to JSON; never overwrite** (append/timestamp — needed for re-analysis).
- **Every question needs verified ground truth** before it enters the set (hand-verify, esp. hand-authored history).
- **Precision-matching discipline:** same dtype across models/arms in a comparison; note it if you deviate.
- **Temp 0; fresh session per trial** (anti-caching).
- **Baseline gate:** only analyze items the model answers correctly unprompted (`ALREADY_WRONG` excluded).
- **Every dataset/algorithm/tool gets its source paper in brackets** (traceability).
- **bitsandbytes does NOT work on Mac** — use quanto for any quantization here.
