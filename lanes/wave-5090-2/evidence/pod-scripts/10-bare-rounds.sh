#!/usr/bin/env bash
# wave-5090-2: Table 2 bare fp4-nvf4 on the RTX 5090, 4096 VUs, --zk interactive, 3 rounds, arm order alternated
# (forward / reverse / forward). Local arms at pipeline depth 1/4/8 (l=16384) + depth 4 at l=8192; one live arm per round
# (under --verifier fp4/chain.py proves the sub-batches sequentially whatever --pipeline says, so live = depth 1).
# Usage: ROUNDS="1 2 3" bash 10-bare-rounds.sh
source /workspace/wave-5090-2/scripts/lib.sh
REPS=${REPS:-5}
ARMS=(
  "v1-p4-l16384 local 16384 4"
  "v1-p8-l16384 local 16384 8"
  "v1-p1-l16384 local 16384 1"
  "v1-p4-l8192 local 8192 4"
  "v1-live-l16384 live 16384 1"
)
for r in ${ROUNDS:-1 2 3}; do
  idx=(0 1 2 3 4); [ $((r % 2)) -eq 0 ] && idx=(4 3 2 1 0)
  for i in "${idx[@]}"; do
    set -- ${ARMS[$i]}
    run bare-$1-r$r $2 fp4-nvf4 $3 $4 $REPS
  done
done
echo "BARE_ROUNDS_DONE ${ROUNDS:-1 2 3}" | tee -a $LOG
