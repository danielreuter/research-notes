#!/usr/bin/env bash
# fill-consumer, RTX 4090: column-2 follow-up (fp8-ada --auth included-hash, the only fp8-ada relation with a pinned hashed
# system): l=16384 p8 OOMs on 24 GB (1.53 GiB short) and l=8192 p4 (0.348-0.390) beat l=16384 p4 (0.408-0.527), so smaller l
# and deeper pipelines. Warm-up for the new l, then 3 rounds, order reversed on odd rounds, --reps 5.
source /workspace/fill-consumer/scripts/lib.sh
H="--auth included-hash --auth-cache /workspace/auth-cache-fp8h"
ARMS=(
  "h-v1-l8192-p4 fp8-ada 8192 4 $H"
  "h-v1-l8192-p8 fp8-ada 8192 8 $H"
  "h-v1-l4096-p4 fp8-ada 4096 4 $H"
  "h-v1-l4096-p8 fp8-ada 4096 8 $H"
)
[ "${WARM:-1}" = 1 ] && { run warm-h-v1-l8192-p8 local fp8-ada 8192 8 1 $H; run warm-h-v1-l4096-p4 local fp8-ada 4096 4 1 $H; run warm-h-v1-l4096-p8 local fp8-ada 4096 8 1 $H; }
for r in ${ROUNDS:-4 5 6}; do
  idx=(0 1 2 3); [ $((r % 2)) -eq 1 ] && idx=(3 2 1 0)
  for i in "${idx[@]}"; do
    set -- ${ARMS[$i]}; t=$1 rel=$2 l=$3 p=$4; shift 4
    run $t-r$r local $rel $l $p 5 "$@"
  done
done
echo "SWEEP2_DONE ${ROUNDS:-4 5 6}" | tee -a $LOG
