#!/usr/bin/env bash
# wave-5090-2: column 2 at depth 8 (fp4-nvf4+poseidon2 --auth included-hash, tree d30c32f6), local + live on ver8,
# alternating with the depth-4 committed local arm. 3 rounds.
source /workspace/wave-5090-2/scripts/lib.sh
V8=tcp://213.173.111.87:22539
REPS=${REPS:-5}
HASH="--auth included-hash --auth-cache /workspace/auth-cache-fp4h"
ARMS=(
  "c2-hash-p8-l16384 local - 8"
  "c2-hash-live-p8-v8-l16384 live $V8 8"
  "c2-hash-p4-l16384 local - 4"
)
for r in ${ROUNDS:-4 5 6}; do
  idx=(0 1 2); [ $((r % 2)) -eq 1 ] && idx=(2 1 0)
  for i in "${idx[@]}"; do
    set -- ${ARMS[$i]}
    VERIFIER=$3 run $1-r$r $2 fp4-nvf4+poseidon2 16384 $4 $REPS $HASH
  done
done
echo "COMMITTED_P8_DONE ${ROUNDS:-4 5 6}" | tee -a $LOG
