#!/usr/bin/env bash
# fill-consumer, RTX 5090: second local sweep around the round-1 winners (bare l=8192 p4 0.0365, hashed l=8192 p8 0.1416):
# smaller l and the other depth. Warm-up for the new l, then 3 rounds, order reversed on odd rounds, --reps 5.
source /workspace/fill-consumer/scripts/lib.sh
H="--auth included-hash --auth-cache /workspace/auth-cache-fp4h"
ARMS=(
  "b-l8192-p4 fp4-nvf4 8192 4"
  "b-l8192-p8 fp4-nvf4 8192 8"
  "b-l4096-p4 fp4-nvf4 4096 4"
  "h-l8192-p8 fp4-nvf4+poseidon2 8192 8 $H"
  "h-l8192-p4 fp4-nvf4+poseidon2 8192 4 $H"
  "h-l4096-p8 fp4-nvf4+poseidon2 4096 8 $H"
)
run warm-b-l4096-p4 local fp4-nvf4 4096 4 1
run warm-h-l4096-p8 local fp4-nvf4+poseidon2 4096 8 1 $H
for r in ${ROUNDS:-4 5 6}; do
  idx=(0 1 2 3 4 5); [ $((r % 2)) -eq 1 ] && idx=(5 4 3 2 1 0)
  for i in "${idx[@]}"; do
    set -- ${ARMS[$i]}; t=$1 rel=$2 l=$3 p=$4; shift 4
    run $t-r$r local $rel $l $p 5 "$@"
  done
done
echo "SWEEP2_DONE ${ROUNDS:-4 5 6}" | tee -a $LOG
