#!/bin/bash
# H100 pass 1: main 6babe27 (hp2-base) vs lane 0d8e178 (hp2-ship), bf16-hopper + fp8-hopper, int-ZK + non-ZK
export POD=vy-hp2-host-h100 SSH=/tmp/hp2/ssh_h100.sh
B=$HOME/projects/verity-main-wt/hp2-base
L=$HOME/projects/verity-main-wt/hp2-ship
run() { echo "--- $(date -u +%H:%M:%S) $*"; /tmp/hp2/bench.sh "$@" 2>&1 | tail -2; }
# done: r20260923-071319-3390  run h1-main-bf16h-zk   $B bf16-hopper --zk --mode interactive
run h1-lane-bf16h-zk-p3 $L bf16-hopper --zk --mode interactive --pipeline 3
run h1-main-fp8h-zk    $B fp8-hopper --zk --mode interactive
run h1-lane-fp8h-zk-p3  $L fp8-hopper --zk --mode interactive --pipeline 3
run h1-main-bf16h-nozk $B bf16-hopper --mode interactive
run h1-lane-bf16h-nozk-p3 $L bf16-hopper --mode interactive --pipeline 3
run h1-main-fp8h-nozk  $B fp8-hopper --mode interactive
run h1-lane-fp8h-nozk-p3 $L fp8-hopper --mode interactive --pipeline 3
run h1-lane-bf16h-zk-seq $L bf16-hopper --zk --mode interactive --pipeline 0
run h1-lane-fp8h-zk-seq  $L fp8-hopper --zk --mode interactive --pipeline 0
echo "DRIVE1_DONE $(date -u +%H:%M:%S)"
