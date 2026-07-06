#!/usr/bin/env bash
# Auto-chain: run inference for all remaining models, one after another.
# Resume logic in run_inference.py means each model skips already-done questions,
# so re-running this script after any interruption continues where it stopped.
#
# Usage:
#   bash src/run_all_models.sh
#
# Model 1 (Qwen2.5-3B) is already done — it will be skipped instantly (150/150).

set -u
cd "$(dirname "$0")/.."

export $(grep -v '^#' .env | xargs)
export HF_HOME="$(pwd)/hf_cache"

MODELS=(
  "Qwen/Qwen2.5-3B-Instruct"
  "meta-llama/Llama-3.2-3B-Instruct"
  "Qwen/Qwen2.5-7B-Instruct"
  "mistralai/Mistral-7B-Instruct-v0.3"
)

for MODEL in "${MODELS[@]}"; do
  echo ""
  echo "============================================================"
  echo ">>> MODEL: $MODEL"
  echo ">>> $(date '+%Y-%m-%d %H:%M:%S')"
  echo "============================================================"
  MODEL_ID="$MODEL" .venv/bin/python src/run_inference.py
  status=$?
  if [ $status -ne 0 ]; then
    echo ">>> $MODEL exited with status $status — stopping chain."
    echo ">>> Re-run 'bash src/run_all_models.sh' to resume from here."
    exit $status
  fi
  echo ">>> $MODEL COMPLETE at $(date '+%H:%M:%S')"
done

echo ""
echo "============================================================"
echo ">>> ALL MODELS COMPLETE — $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"
