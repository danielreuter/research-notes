#!/usr/bin/env bash
# fill-consumer, RTX 5090 nvfp4-sm120-mma-draft: warm-up (round 0, reps 1, not a candidate; absorbs the compute_89 PTX JIT)
# then 3 local rounds, arm order reversed on odd rounds, --reps 5, one job at a time. Bare: fp4-nvf4 (fp4/chain.py, frozen
# NVFP4 ref at exactly 4096 VUs) l=16384 p4 / p8, l=8192 p4. Column 2: fp4-nvf4+poseidon2 --auth included-hash (unshared)
# l=16384 p8 / p4, l=8192 p8.
source /workspace/fill-consumer/scripts/lib.sh
H="--auth included-hash --auth-cache /workspace/auth-cache-fp4h"
ARMS=(
  "b-p4 fp4-nvf4 16384 4"
  "b-p8 fp4-nvf4 16384 8"
  "b-l8192-p4 fp4-nvf4 8192 4"
  "h-p8 fp4-nvf4+poseidon2 16384 8 $H"
  "h-p4 fp4-nvf4+poseidon2 16384 4 $H"
  "h-l8192-p8 fp4-nvf4+poseidon2 8192 8 $H"
)
if [ "${WARM:-1}" = 1 ]; then
  for a in "${ARMS[@]}"; do set -- $a; t=$1 rel=$2 l=$3 p=$4; shift 4; run warm-$t local $rel $l $p 1 "$@"; done
fi
for r in ${ROUNDS:-1 2 3}; do
  idx=(0 1 2 3 4 5); [ $((r % 2)) -eq 1 ] && idx=(5 4 3 2 1 0)
  for i in "${idx[@]}"; do
    set -- ${ARMS[$i]}; t=$1 rel=$2 l=$3 p=$4; shift 4
    run $t-r$r local $rel $l $p 5 "$@"
  done
done
echo "SWEEP_DONE ${ROUNDS:-1 2 3}" | tee -a $LOG
