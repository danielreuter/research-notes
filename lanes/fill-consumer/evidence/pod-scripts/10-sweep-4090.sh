#!/usr/bin/env bash
# fill-consumer, RTX 4090 fp8-ada-mma-draft: warm-up (round 0, reps 1, not a candidate) then 3 local rounds, arm order
# reversed on odd rounds, --reps 5, one job at a time. Bare: fp8-ada-v3x4 l=4096 p8 / p4 (equivalence art:d40f5065),
# fp8-ada v1 l=16384 p4 (frozen ref). Column 2: fp8-ada --auth included-hash (Poseidon2 per row, unshared; the only fp8-ada
# relation with a pinned hashed system in ligero-verify) l=16384 p4 / p8, l=8192 p4.
source /workspace/fill-consumer/scripts/lib.sh
H="--auth included-hash --auth-cache /workspace/auth-cache-fp8h"
ARMS=(
  "b-v3x4-p8 fp8-ada-v3x4 4096 8"
  "b-v3x4-p4 fp8-ada-v3x4 4096 4"
  "b-v1-p4 fp8-ada 16384 4"
  "h-v1-p4 fp8-ada 16384 4 $H"
  "h-v1-p8 fp8-ada 16384 8 $H"
  "h-v1-l8192-p4 fp8-ada 8192 4 $H"
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
