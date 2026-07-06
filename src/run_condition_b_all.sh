#!/usr/bin/env bash
# Condition B chain: run the 'anon' clean-baseline rung for all 4 models.
# Runs AFTER the main chain (run_all_models.sh) completes.
# Resume-safe per model. Writes to *__anonB.jsonl (separate from main files).
set -u
cd "$(dirname "$0")/.."
export $(grep -v '^#' .env | xargs)
export HF_HOME="$(pwd)/hf_cache"
export PYTHONPATH="$(pwd)/src"

MODELS=(
  "Qwen/Qwen2.5-3B-Instruct"
  "meta-llama/Llama-3.2-3B-Instruct"
  "Qwen/Qwen2.5-7B-Instruct"
  "mistralai/Mistral-7B-Instruct-v0.3"
)

for MODEL in "${MODELS[@]}"; do
  echo ""
  echo ">>> COND-B anon: $MODEL  $(date '+%H:%M:%S')"
  MODEL_ID="$MODEL" .venv/bin/python src/run_condition_b.py
  st=$?
  [ $st -ne 0 ] && { echo ">>> $MODEL cond-B failed ($st) — re-run to resume."; exit $st; }
  echo ">>> $MODEL cond-B COMPLETE $(date '+%H:%M:%S')"
done
echo ">>> ALL COND-B COMPLETE $(date '+%Y-%m-%d %H:%M:%S')"
