#!/bin/bash
# H100 pass 1b: lane rows at the validated commit (hp2-ship), bf16-hopper + fp8-hopper, int-ZK + non-ZK, --pipeline 3 and sequential
export POD=vy-hp2-host-h100 SSH=/tmp/hp2/ssh_h100.sh
L=$HOME/projects/verity-main-wt/hp2-ship
run() { echo "--- $(date -u +%H:%M:%S) $*"; /tmp/hp2/bench.sh "$@" 2>&1 | tail -2; }
run h1-lane-bf16h-zk-p3   $L bf16-hopper --zk --mode interactive --pipeline 3
run h1-lane-fp8h-zk-p3    $L fp8-hopper --zk --mode interactive --pipeline 3
run h1-lane-bf16h-nozk-p3 $L bf16-hopper --mode interactive --pipeline 3
run h1-lane-fp8h-nozk-p3  $L fp8-hopper --mode interactive --pipeline 3
run h1-lane-bf16h-zk-seq  $L bf16-hopper --zk --mode interactive --pipeline 0
run h1-lane-fp8h-zk-seq   $L fp8-hopper --zk --mode interactive --pipeline 0
run h1-lane-bf16h-zk-p2   $L bf16-hopper --zk --mode interactive --pipeline 2
echo "DRIVE2_DONE $(date -u +%H:%M:%S)"
