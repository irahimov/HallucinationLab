#!/usr/bin/env bash
# Sürətli demo: testlər, retrieval, robustness. --with-judge flag-ı ilə hakim ölçüləri də işləyir (yavaşdır, ~30+ dəq).
set -euo pipefail
cd "$(dirname "$0")/.."
source ~/.hal-lab-env/bin/activate

python -m pytest tests -q
python src/retrieval_eval.py | tee results/retrieval_console.log
python src/robustness_eval.py | tee results/robustness_console.log
python src/unanswerable_eval.py | tee results/unanswerable_console.log

if [[ "${1:-}" == "--with-judge" ]]; then
  python src/judge_eval.py | tee results/judge_eval_console.log
fi
echo "demo tamamlandı"
