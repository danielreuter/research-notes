#!/usr/bin/env bash
# wave-5090-2: live arms PIPELINED (tree b278f508: fp4/chain.py bench-vu --pipeline N --verifier = HELLO window N +
# non-blocking coin exchanges, as relchain) against both same-DC verifiers -- v8 = vy-wave-5090-2-ver8 (8 vCPU, jobs 8),
# v2 = vy-wave-5090-verifier (2 vCPU, restarted with LIVE_JOBS=1) -- alternating with the local depth-4 arm. 3 rounds.
source /workspace/wave-5090-2/scripts/lib.sh
V8=tcp://213.173.111.87:22539; V2=tcp://213.173.111.88:49715
REPS=${REPS:-5}
ARMS=(
  "v1-livepipe-p4-v8-l16384 live 16384 4 $V8"
  "v1-livepipe-p8-v8-l16384 live 16384 8 $V8"
  "v1-livepipe-p4-v2-l16384 live 16384 4 $V2"
  "v1-p4-l16384 local 16384 4 -"
)
for r in ${ROUNDS:-10 11 12}; do
  idx=(0 1 2 3); [ $((r % 2)) -eq 1 ] && idx=(3 2 1 0)
  for i in "${idx[@]}"; do
    set -- ${ARMS[$i]}
    VERIFIER=$5 run bare-$1-r$r $2 fp4-nvf4 $3 $4 $REPS
  done
done
echo "LIVE_PIPE_DONE ${ROUNDS:-10 11 12}" | tee -a $LOG
