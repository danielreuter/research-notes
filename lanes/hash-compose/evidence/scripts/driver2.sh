#!/usr/bin/env bash
# driver 2: the committed bf16-ampere column in the other two modes at l=16384 (non-ZK interactive, Fiat-Shamir ZK), and the bare vu.py
# reference at l=8192 (so both l values have a same-pod bare number).
set -uo pipefail
S=~/.research/notes/lanes/hash-compose/evidence/scripts
$S/launch.sh amp-hash-nonzk-int-l16k -- --relation bf16-ampere bench-vu --mode interactive --batch 16384 --total-vus 4096 --reps 3 --auth included-hash --root /workspace/bench-instances/v1
$S/launch.sh amp-hash-fs-zk-l16k     -- --relation bf16-ampere bench-vu --zk --mode fiat-shamir --batch 16384 --total-vus 4096 --reps 3 --auth included-hash --root /workspace/bench-instances/v1
TOOL=bench_vu $S/launch.sh bare-vu-int-zk-l8k -- --relation bf16 bench-vu --zk --mode interactive --batch 8192 --total-vus 4096 --reps 3 --root /workspace/bench-instances/v1
echo DRIVER2_DONE
