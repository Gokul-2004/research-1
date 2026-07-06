#!/usr/bin/env bash
# Run the 2 pre-committed additional models: main inference + condition B.
# Self-contained: does NOT touch the original 4 models.
# Resume-safe per model (run_inference.py skips done questions; condition B too).
set -u
cd "$(dirname "$0")/.."
export $(grep -v '^#' .env | xargs)
export HF_HOME="$(pwd)/hf_cache"
export PYTHONPATH="$(pwd)/src"

MODELS=(
  "microsoft/Phi-3.5-mini-instruct"
  "google/gemma-2-9b-it"
)

echo ">>> NEW MODELS RUN START $(date '+%Y-%m-%d %H:%M:%S')"

# Phase 1: main inference for both new models
for MODEL in "${MODELS[@]}"; do
  echo ""
  echo ">>> MAIN: $MODEL  $(date '+%H:%M:%S')"
  MODEL_ID="$MODEL" .venv/bin/python src/run_inference.py
  st=$?
  [ $st -ne 0 ] && { echo ">>> $MODEL main failed ($st) — re-run to resume."; exit $st; }
  echo ">>> $MODEL MAIN COMPLETE $(date '+%H:%M:%S')"
done

# Phase 2: condition B (anon rung) for both new models
for MODEL in "${MODELS[@]}"; do
  echo ""
  echo ">>> COND-B: $MODEL  $(date '+%H:%M:%S')"
  MODEL_ID="$MODEL" .venv/bin/python src/run_condition_b.py
  st=$?
  [ $st -ne 0 ] && { echo ">>> $MODEL cond-B failed ($st) — re-run to resume."; exit $st; }
  echo ">>> $MODEL COND-B COMPLETE $(date '+%H:%M:%S')"
done

echo ""
echo ">>> ALL NEW MODELS + COND-B COMPLETE $(date '+%Y-%m-%d %H:%M:%S')"
