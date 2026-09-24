#!/bin/bash
# H100 pass 2 (new pod vy-hp2-host-h100b): main 6babe27 baseline rows + lane 8d743d6 rows (default --pipeline 3) + one sequential A/B
export POD=vy-hp2-host-h100b SSH=/tmp/hp2/ssh_h100b.sh
L=$HOME/projects/verity-main-wt/hp2-ship
B=$HOME/projects/verity-main-wt/hp2-base
run() { echo "--- $(date -u +%H:%M:%S) $*"; /tmp/hp2/bench.sh "$@" 2>&1 | tail -2; }
run h2-main-bf16h-zk      $B bf16-hopper --zk --mode interactive
run h2-lane-bf16h-zk-p3   $L bf16-hopper --zk --mode interactive
run h2-main-fp8h-zk       $B fp8-hopper --zk --mode interactive
run h2-lane-fp8h-zk-p3    $L fp8-hopper --zk --mode interactive
run h2-lane-bf16h-nozk-p3 $L bf16-hopper --mode interactive
run h2-lane-fp8h-nozk-p3  $L fp8-hopper --mode interactive
run h2-lane-bf16h-zk-seq  $L bf16-hopper --zk --mode interactive --pipeline 0
echo "DRIVE3_DONE $(date -u +%H:%M:%S)"
