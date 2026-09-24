#!/usr/bin/env bash
# fill-consumer, RTX 4090: LIVE rounds against vy-fill-consumer-vtest (1vchd2ej1iey9k, cpu3c 16 vCPU, EU-RO-1,
# live-verifier@1b3c7be67343; probe from this pod 0.6-0.7 ms, 5-7 Gbps). It is the 5090's verifier too: the 5090's live
# rounds were finished before these start and none run while these do (the two dedicated 4090 verifiers tried -- cpu3c on
# hosts at load 320-400: probe RTT 2.6 ms; L4 GPU pod: ~0.9 Gbps -- failed the same-DC checks). Waits for the local sweep.
# Chosen: bare fp8-ada-v3x4 l=4096 p8, column 2 fp8-ada --auth included-hash l=8192 p4. 3 rounds, order alternated, --reps 5.
source /workspace/fill-consumer/scripts/lib.sh
VERIFIER=${VERIFIER:-tcp://213.173.105.95:48843}
until grep -q SWEEP2_DONE $LOG; do sleep 5; done
H="--auth included-hash --auth-cache /workspace/auth-cache-fp8h"
ARMS=(
  "L-b-v3x4-p8 fp8-ada-v3x4 4096 8"
  "L-h-v1-l8192-p4 fp8-ada 8192 4 $H"
)
for r in ${ROUNDS:-1 2 3}; do
  idx=(0 1); [ $((r % 2)) -eq 0 ] && idx=(1 0)
  for i in "${idx[@]}"; do
    set -- ${ARMS[$i]}; t=$1 rel=$2 l=$3 p=$4; shift 4
    run $t-r$r live $rel $l $p 5 "$@"
  done
done
echo "LIVE_DONE ${ROUNDS:-1 2 3}" | tee -a $LOG
