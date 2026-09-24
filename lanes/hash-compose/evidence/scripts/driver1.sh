#!/usr/bin/env bash
# Lane hash-compose driver 1 (after r20260923-095623-ecdf, the hashed int-ZK l=16384 run): the bare vu.py bf16 int-ZK reference
# on the same 4090 (tool bench_vu), then the hashed column at l = 8192 and l = 32768 (operating-point sweep).
set -uo pipefail
S=~/.research/notes/lanes/hash-compose/evidence/scripts
# wait for the previous launch to finish
# (previous run already done)
TOOL=bench_vu $S/launch.sh bare-vu-int-zk-l16k -- --relation bf16 bench-vu --zk --mode interactive --batch 16384 --total-vus 4096 --reps 3 --root /workspace/bench-instances/v1
$S/launch.sh amp-hash-int-zk-l8k  -- --relation bf16-ampere bench-vu --zk --mode interactive --batch 8192  --total-vus 4096 --reps 3 --auth included-hash --root /workspace/bench-instances/v1
$S/launch.sh amp-hash-int-zk-l32k -- --relation bf16-ampere bench-vu --zk --mode interactive --batch 32768 --total-vus 4096 --reps 3 --auth included-hash --root /workspace/bench-instances/v1
echo DRIVER1_DONE
