#!/usr/bin/env bash
# wave-5090-2: the live arm against a second same-DC verifier with 8 vCPU (vy-wave-5090-2-ver8 7reoox6szli7e6, cpu5m x8, EU-RO-1,
# live_serve.sh from main 24f252b1, jobs 8) -- the 2-vCPU verifier's in-session RTT was ~3 ms vs 0.8 ms idle.
# 3 rounds, alternating with the local depth-1 and depth-4 arms.
VERIFIER=tcp://213.173.111.87:22539
source /workspace/wave-5090-2/scripts/lib.sh
REPS=${REPS:-5}
ARMS=(
  "v1-live-v8-l16384 live 16384 1"
  "v1-p4-l16384 local 16384 4"
  "v1-p1-l16384 local 16384 1"
)
for r in ${ROUNDS:-7 8 9}; do
  idx=(0 1 2); [ $((r % 2)) -eq 0 ] && idx=(2 1 0)
  for i in "${idx[@]}"; do
    set -- ${ARMS[$i]}
    run bare-$1-r$r $2 fp4-nvf4 $3 $4 $REPS
  done
done
echo "LIVE_V8_DONE ${ROUNDS:-7 8 9}" | tee -a $LOG
