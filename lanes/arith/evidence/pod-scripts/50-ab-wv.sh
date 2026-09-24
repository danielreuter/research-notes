#!/usr/bin/env bash
# arith step 2 (4090): step 1 (9d1a7f15, /workspace/src-s1) vs tip (lincomb2 + no beta), fp8-ada-v3x4 l=4096 p8,
# 3 alternating rounds, then a profile of the tip.  Nothing else may run on the pod meanwhile (6.8-core quota).
source /workspace/arith/scripts/lib.sh
for rr in 1 2 3; do
  if [ $rr = 2 ]; then order="tip s1"; else order="s1 tip"; fi
  for arm in $order; do
    if [ $arm = s1 ]; then SRC=/workspace/src-s1 COMMIT=9d1a7f15bb3d50d3d53adadd9dff801f08b252f3 run s2-s1-p8-r$rr fp8-ada-v3x4 4096 8 5
    else SRC=/workspace/src COMMIT=$TIP run s2-tip-p8-r$rr fp8-ada-v3x4 4096 8 5; fi
  done
done
prof s2-tip-p8 fp8-ada-v3x4 4096 8
echo DONE-50
