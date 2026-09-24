#!/usr/bin/env bash
# fill-dc A100 local sweep (local coins, no dumps): 3 candidates per column, rounds 1-3 (even rounds reversed), --reps 5.
# Every bf16-ampere* relation reads the frozen vu-k1536 set at 9989797f+ (bootstrap BENCH_INSTANCES=1).
#   ROUNDS="1 2 3" bash 20-a100-sweep.sh      -> /workspace/fill-dc/runs/<tag>-r<n>/, one line each in summary.txt
source /workspace/fill-dc/scripts/lib.sh
S=(
  ab-v3p8:bf16-ampere-v3:16384:8
  ab-x4p8:bf16-ampere-v3x4:4096:8
  ab-x4p4:bf16-ampere-v3x4:4096:4
  ah-v3p8:bf16-ampere-v3:16384:8:--auth,included-hash
  ah-x4p4:bf16-ampere-v3x4:4096:4:--auth,included-hash
  ah-v1p8:bf16-ampere:16384:8:--auth,included-hash
)
[ -n "${ONLY:-}" ] && { T=(); for s in "${S[@]}"; do [[ " $ONLY " == *" ${s%%:*} "* ]] && T+=("$s"); done; S=("${T[@]}"); }
if [ "${WARM:-1}" = 1 ]; then
  REPS=1 run warm-a-x4 bf16-ampere-v3x4 4096 4
  REPS=1 run warm-a-v3 bf16-ampere-v3 16384 8
fi
for r in ${ROUNDS:-1 2 3}; do PREFIX=a100 round $r "${S[@]}"; done
echo "$(date -u +%H:%M:%S) SWEEP_DONE" | tee -a $SUM
