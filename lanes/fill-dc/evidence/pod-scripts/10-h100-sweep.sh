#!/usr/bin/env bash
# fill-dc H100 local sweep (local coins, no dumps): 3 candidates per column, rounds 1-3 (even rounds reversed), --reps 5.
# Warm-up first (--reps 1, untimed): the first v3x4 process per relation compiles the fused witness kernel (wave-h100-2).
#   ROUNDS="1 2 3" bash 10-h100-sweep.sh      -> /workspace/fill-dc/runs/<tag>-r<n>/, one line each in summary.txt
source /workspace/fill-dc/scripts/lib.sh
S=(
  f8b-x4p8:fp8-hopper-v3x4:4096:8
  f8b-x4p4:fp8-hopper-v3x4:4096:4
  f8b-v1p4:fp8-hopper:16384:4
  f8h-x4p4:fp8-hopper-v3x4:4096:4:--auth,included-hash
  f8h-v3p4:fp8-hopper-v3:16384:4:--auth,included-hash
  f8h-v1p4:fp8-hopper:16384:4:--auth,included-hash
  b16b-x4p4:bf16-hopper-v3x4:4096:4
  b16b-x4p8:bf16-hopper-v3x4:4096:8
  b16b-v1p8:bf16-hopper:16384:8
  b16h-x4p4:bf16-hopper-v3x4:4096:4:--auth,included-hash
  b16h-v3p8:bf16-hopper-v3:16384:8:--auth,included-hash
  b16h-v1p8:bf16-hopper:16384:8:--auth,included-hash
)
[ -n "${ONLY:-}" ] && { T=(); for s in "${S[@]}"; do [[ " $ONLY " == *" ${s%%:*} "* ]] && T+=("$s"); done; S=("${T[@]}"); }
if [ "${WARM:-1}" = 1 ]; then
  REPS=1 run warm-f8-x4 fp8-hopper-v3x4 4096 4
  REPS=1 run warm-b16-x4 bf16-hopper-v3x4 4096 4
fi
for r in ${ROUNDS:-1 2 3}; do PREFIX=h100 round $r "${S[@]}"; done
echo "$(date -u +%H:%M:%S) SWEEP_DONE" | tee -a $SUM
