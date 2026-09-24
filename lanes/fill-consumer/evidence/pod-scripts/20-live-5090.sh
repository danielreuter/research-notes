#!/usr/bin/env bash
# fill-consumer, RTX 5090: LIVE rounds against the same-DC SECURE verifier vy-fill-consumer-vtest (1vchd2ej1iey9k, cpu3c
# 16 vCPU, EU-RO-1, live-verifier@1b3c7be67343, probe RTT 0.7 ms). The local winners (l=8192 p8, both columns) alternate
# with l=16384 p8 (fewer sub-batches = fewer coin round trips). 3 rounds, order reversed on odd rounds, --reps 5, rep 1 dumped.
source /workspace/fill-consumer/scripts/lib.sh
VERIFIER=${VERIFIER:-tcp://213.173.105.95:48843}
H="--auth included-hash --auth-cache /workspace/auth-cache-fp4h"
ARMS=(
  "L-b-l8192-p8 fp4-nvf4 8192 8"
  "L-h-l8192-p8 fp4-nvf4+poseidon2 8192 8 $H"
  "L-b-l16384-p8 fp4-nvf4 16384 8"
  "L-h-l16384-p8 fp4-nvf4+poseidon2 16384 8 $H"
)
for r in ${ROUNDS:-1 2 3}; do
  idx=(0 1 2 3); [ $((r % 2)) -eq 1 ] && idx=(3 2 1 0)
  for i in "${idx[@]}"; do
    set -- ${ARMS[$i]}; t=$1 rel=$2 l=$3 p=$4; shift 4
    run $t-r$r live $rel $l $p 5 "$@"
  done
done
echo "LIVE_DONE ${ROUNDS:-1 2 3}" | tee -a $LOG
