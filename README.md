# Commitment Structure Outweighs Source Authority in the Sycophancy of Small Open Language Models

Code, data, pre-registration, and analysis for a **pre-registered** study of authority-graded
sycophancy in six small open-weight LLMs (3B–9B). We measure whether a model abandons a
correct answer under a user counter-claim, and how that depends on **who** disagrees
(source authority) versus **how/when** the disagreement arrives (conversational structure).

**Headline:** on identical, correctness-gated items, prior self-commitment (a two-turn
*commit-then-challenge* protocol) multiplies caving by **1.9–9.3×** relative to a single-turn
*question-then-hint* protocol (paired McNemar *p* < 10⁻¹⁵ in every model) — a larger effect, in
every model, than source authority.

## Pre-registration (committed before any inference)

- **`ANALYSIS_PLAN.md`** — the pre-specified analysis plan, committed in
  **`427d75a` (2026-06-29)**, *before* the first inference run (earliest output 2026-06-30).
  Verify the timestamp and the frozen text:
  ```bash
  git show -s --format=%ci 427d75a      # -> 2026-06-29
  git show 427d75a:ANALYSIS_PLAN.md     # the authoritative pre-registration
  ```
  > The tracked `ANALYSIS_PLAN.md` was later expanded; the **authoritative pre-registration is
  > the version at commit `427d75a`**, not the current file.
- **`DEVIATIONS_FROM_PREREGISTRATION.md`** — every departure from the plan, disclosed.

## Data integrity

- **`RESULTS_MANIFEST.sha256`** — SHA-256 hashes of the frozen raw outputs. Re-verify anytime:
  ```bash
  shasum -a 256 -c RESULTS_MANIFEST.sha256
  ```

## Repository layout

| Path | Contents |
|---|---|
| `data/` | the 150 verified MCQ items (ARC-Challenge, MMLU world history, TruthfulQA) |
| `src/` | inference + analysis code; `paper_numbers.py` regenerates every reported statistic |
| `results/inference/` | raw per-trial model outputs (JSONL) — the frozen raw data |
| `results/paper_numbers.json` | every statistic in the paper, regenerated from the raw data |
| `judge_bundle/` | LLM-judge code, judge outputs, and human-validation labels (κ = 0.967) |
| `paper/` | LaTeX source (`access.tex`), figures, and the IEEE Access template |

## Reproduce

Regenerating every statistic needs only Python (the analysis engine is pure-Python, no deps):

```bash
python3 src/paper_numbers.py     # -> results/paper_numbers.json + results/PAPER_NUMBERS.md
```

Regenerating the figures needs matplotlib:

```bash
python3 -m venv .venv-figs && .venv-figs/bin/pip install matplotlib
.venv-figs/bin/python src/make_figures_paper.py     # -> paper/figures/*.{png,pdf,svg}
```

Re-running inference from scratch (GPU-optional, CPU fp16 works) uses the scripts in `src/` and
the dependencies in `requirements.txt`.

## Models

Qwen2.5-3B-Instruct · Llama-3.2-3B-Instruct · Phi-3.5-mini-instruct ·
Mistral-7B-Instruct-v0.3 · Qwen2.5-7B-Instruct · Gemma-2-9B-it — run in fp16 at temperature 0,
a fresh session per trial.

## Data licenses

Items derive from **ARC-Challenge** (CC BY-SA), **MMLU** (MIT), and **TruthfulQA** (Apache 2.0),
used with attribution.

## Citation

Citation details (authors, venue, DOI) will be added on publication.
