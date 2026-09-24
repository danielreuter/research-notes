#!/usr/bin/env bash
# wave-5090-2: the live arm again after restarting the same-DC verifier with LIVE_JOBS=1 (it has 2 vCPU; with --jobs 2 the
# in-session RTT was 3.2 ms vs 0.8 ms idle). 3 rounds, alternating with the local depth-4 and depth-1 arms.
source /workspace/wave-5090-2/scripts/lib.sh
REPS=${REPS:-5}
ARMS=(
  "v1-live-j1-l16384 live 16384 1"
  "v1-p4-l16384 local 16384 4"
  "v1-p1-l16384 local 16384 1"
)
for r in ${ROUNDS:-4 5 6}; do
  idx=(0 1 2); [ $((r % 2)) -eq 1 ] && idx=(2 1 0)
  for i in "${idx[@]}"; do
    set -- ${ARMS[$i]}
    run bare-$1-r$r $2 fp4-nvf4 $3 $4 $REPS
  done
done
echo "LIVE_J1_DONE ${ROUNDS:-4 5 6}" | tee -a $LOG
