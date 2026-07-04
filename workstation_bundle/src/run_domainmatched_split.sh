#!/usr/bin/env bash
# Domain-matched run for a SUBSET of models (for splitting across 2 machines).
# Usage:
#   Machine A (this laptop):   bash src/run_domainmatched_split.sh A
#   Machine B (other wkstn):   bash src/run_domainmatched_split.sh B
# Both CPU. Resume-safe. Writes separate *_domainmatched.jsonl per model.
set -u
cd "$(dirname "$0")/.."
export $(grep -v '^#' .env | xargs)
export HF_HOME="$(pwd)/hf_cache"
export PYTHONPATH="$(pwd)/src"
export DEVICE="${DEVICE:-cpu}"

GROUP="${1:-A}"
if [ "$GROUP" = "A" ]; then
  MODELS=("Qwen/Qwen2.5-3B-Instruct" "meta-llama/Llama-3.2-3B-Instruct" "Qwen/Qwen2.5-7B-Instruct")
elif [ "$GROUP" = "B" ]; then
  MODELS=("mistralai/Mistral-7B-Instruct-v0.3" "microsoft/Phi-3.5-mini-instruct" "google/gemma-2-9b-it")
else
  echo "Usage: $0 [A|B]"; exit 1
fi

echo ">>> DOMAIN-MATCHED SPLIT group $GROUP: ${MODELS[*]}"
for M in "${MODELS[@]}"; do
  echo ">>> $M  $(date '+%H:%M:%S')"
  MODEL_ID="$M" .venv/bin/python src/run_domainmatched.py 2>/dev/null || MODEL_ID="$M" python src/run_domainmatched.py
  st=$?
  [ $st -ne 0 ] && { echo ">>> $M failed ($st) — re-run to resume."; exit $st; }
  echo ">>> $M DONE $(date '+%H:%M:%S')"
done
echo ">>> GROUP $GROUP ALL DONE $(date)"
