#!/usr/bin/env bash
# wave-5090-2: Table 2 column 2 on the RTX 5090 -- fp4-nvf4+poseidon2 --auth included-hash (fp4-port 1aa1f00e merged at
# d30c32f6; --auth included-hash-shared is refused for fp4-nvf4 on that tree), with the bare settings: 4096 VUs, --zk
# interactive, l=16384, depth 4, reps 5; local + live on the same-DC 8-vCPU verifier (ver8, rebuilt from the merged tree).
# 3 rounds, arm order alternated bare/committed.
source /workspace/wave-5090-2/scripts/lib.sh
V8=tcp://213.173.111.87:22539
REPS=${REPS:-5}
HASH="--auth included-hash --auth-cache /workspace/auth-cache-fp4h"
ARMS=(
  "c2-hash-p4-l16384 local fp4-nvf4+poseidon2 -"
  "c2-bare-p4-l16384 local fp4-nvf4 -"
  "c2-hash-live-p4-v8-l16384 live fp4-nvf4+poseidon2 $V8"
  "c2-bare-live-p4-v8-l16384 live fp4-nvf4 $V8"
)
for r in ${ROUNDS:-1 2 3}; do
  idx=(0 1 2 3); [ $((r % 2)) -eq 0 ] && idx=(3 2 1 0)
  for i in "${idx[@]}"; do
    set -- ${ARMS[$i]}
    extra=""; [ "$3" != fp4-nvf4 ] && extra=$HASH
    VERIFIER=$4 run $1-r$r $2 $3 16384 4 $REPS $extra
  done
done
echo "COMMITTED_DONE ${ROUNDS:-1 2 3}" | tee -a $LOG
