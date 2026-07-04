#!/usr/bin/env bash
# Domain-matched persona run for ALL 6 models on GPU. Resume-safe.
# Usage: bash src/run_domainmatched_all.sh
set -u
cd "$(dirname "$0")/.."
export $(grep -v '^#' .env | xargs)
export HF_HOME="$(pwd)/hf_cache"
export PYTHONPATH="$(pwd)/src"
export DEVICE="${DEVICE:-cuda}"

MODELS=(
  "Qwen/Qwen2.5-3B-Instruct"
  "meta-llama/Llama-3.2-3B-Instruct"
  "Qwen/Qwen2.5-7B-Instruct"
  "mistralai/Mistral-7B-Instruct-v0.3"
  "microsoft/Phi-3.5-mini-instruct"
  "google/gemma-2-9b-it"
)
for M in "${MODELS[@]}"; do
  echo ">>> DOMAIN-MATCHED: $M  $(date '+%H:%M:%S')"
  MODEL_ID="$M" .venv/bin/python src/run_domainmatched.py 2>/dev/null || MODEL_ID="$M" python src/run_domainmatched.py
  st=$?
  [ $st -ne 0 ] && { echo ">>> $M failed ($st) — re-run to resume."; exit $st; }
  echo ">>> $M DONE $(date '+%H:%M:%S')"
done
echo ">>> ALL DOMAIN-MATCHED DONE $(date)"
