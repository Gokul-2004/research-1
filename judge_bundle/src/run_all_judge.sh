#!/usr/bin/env bash
# Run the judge on ALL 6 model files. ONE pass by default (judge-vs-human is the
# primary validation; dual-judge is not used by the field at temp 0).
# Resume-safe: re-running continues where it stopped.
#
# Usage:
#   bash src/run_all_judge.sh            # paid tier, judge run 1
#   bash src/run_all_judge.sh 14         # free-tier rate cap (14 req/min), run 1
#   bash src/run_all_judge.sh 14 2       # optional 2nd run for self-consistency
set -u
cd "$(dirname "$0")/.."
RPM="${1:-0}"     # 0 = unlimited (paid); 14 = safe free-tier
RUN="${2:-1}"     # judge run number (default 1; pass 2 only for optional self-consistency)

FILES=$(ls results/inference/*.jsonl | grep -v anonB)

for F in $FILES; do
  echo ">>> judge run $RUN: $F  (rpm=$RPM)  $(date '+%H:%M:%S')"
  python src/run_judge.py --input "$F" --judge-run "$RUN" --rpm "$RPM"
done
echo ">>> JUDGING DONE (run $RUN) $(date '+%Y-%m-%d %H:%M:%S')"
