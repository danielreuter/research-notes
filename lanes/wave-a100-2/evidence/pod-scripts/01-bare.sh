#!/usr/bin/env bash
# wave-a100 bare candidates, local coins (prover-only t.total), 4096 VUs, --zk interactive, 3 reps each, rep 1 dumped.
#   01-bare.sh ROUND     ROUND 1: v1 p8, v3 p8, v3x4 p4, v3x4 p8 + depth checks v1 p4, v3 p4; ROUND 2: reversed; ROUND 3: as 1.
# v1 = bf16-ampere (frozen vu-k1536 set), v3 = bf16-ampere-v3 (fused hints, default), v3x4 = bf16-ampere-v3x4 (fused, l=4096).
source /workspace/wave-a100/pod-scripts/lib.sh
r=$1
A=("v1p8:bf16-ampere:16384:8" "v3p8:bf16-ampere-v3:16384:8" "x4p4:bf16-ampere-v3x4:4096:4" "x4p8:bf16-ampere-v3x4:4096:8")
case $r in
  1) S=("${A[@]}" "v1p4:bf16-ampere:16384:4" "v3p4:bf16-ampere-v3:16384:4");;
  2) S=("${A[3]}" "${A[2]}" "${A[1]}" "${A[0]}");;
  *) S=("${A[@]}");;
esac
for spec in "${S[@]}"; do
  IFS=: read tag rel batch depth <<< "$spec"
  b bare-$tag-r$r $rel $batch $depth local
done
echo "$(date -u +%H:%M:%S) BARE_ROUND_${r}_DONE" | tee -a $SUM
