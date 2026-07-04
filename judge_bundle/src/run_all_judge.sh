#!/usr/bin/env bash
# Run the judge on ALL model files, BOTH judge runs (dual-judge).
# Resume-safe: re-running continues where it stopped.
# Free-tier: pass an RPM cap as first arg, e.g.  bash src/run_all_judge.sh 14
set -u
cd "$(dirname "$0")/.."
RPM="${1:-0}"   # 0 = unlimited (paid tier); 14 = safe free-tier cap

# Judge only the MAIN files (not __anonB) for the core validation.
# (anonB can be judged too if desired — add them to the glob.)
FILES=$(ls results/inference/*.jsonl | grep -v anonB)

for RUN in 1 2; do
  for F in $FILES; do
    echo ">>> judge run $RUN: $F  (rpm=$RPM)  $(date '+%H:%M:%S')"
    python src/run_judge.py --input "$F" --judge-run $RUN --rpm "$RPM"
  done
done
echo ">>> ALL JUDGING DONE $(date '+%Y-%m-%d %H:%M:%S')"
