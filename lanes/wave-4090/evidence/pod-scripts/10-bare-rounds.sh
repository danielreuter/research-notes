#!/usr/bin/env bash
# wave-4090: Table 2 bare candidates on the 4090 (fp8-ada family), 4096 VUs, --zk interactive, 3 rounds, arm order alternated
# (forward / reverse / forward). Each arm per round: local coins (rep1 dumped) then live against the same-DC verifier.
# Usage: ROUNDS="1 2 3" MODES="local live" bash 10-bare-rounds.sh
source /workspace/wave-4090/scripts/lib.sh
REPS=${REPS:-5}
ARMS=(
  "v1-p4 fp8-ada 16384 4"
  "v1-p8 fp8-ada 16384 8"
  "v3-p4 fp8-ada-v3 16384 4"
  "v3x4-p4 fp8-ada-v3x4 4096 4"
  "v3x4-p8 fp8-ada-v3x4 4096 8"
)
for r in ${ROUNDS:-1 2 3}; do
  idx=(0 1 2 3 4); [ $((r % 2)) -eq 0 ] && idx=(4 3 2 1 0)
  for i in "${idx[@]}"; do
    set -- ${ARMS[$i]}
    for m in ${MODES:-local live}; do
      run bare-$1-r$r-$m $m $2 $3 $4 $REPS
    done
  done
done
echo "BARE_ROUNDS_DONE ${ROUNDS:-1 2 3}" | tee -a $LOG
