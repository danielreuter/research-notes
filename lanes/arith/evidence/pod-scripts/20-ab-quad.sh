#!/usr/bin/env bash
# arith step 1 (4090): bit-exactness script, then base (main 22741456) vs tip (quad_v4 + reduce kernel), fp8-ada-v3x4 l=4096 p8,
# 3 alternating rounds, then a profile of the tip.
source /workspace/arith/scripts/lib.sh
(cd /workspace/src && PYTHONPATH="/workspace/src/packages/verity/src:/workspace/src/backends/numerical/python:/workspace/src/tools/research/src:/workspace/src" \
  $PY -m backends.direct.ligero.tests_fused_test --reps 3 > $A/tests_fused_test.out 2>&1; echo "tests_fused_test rc=$? $(tail -1 $A/tests_fused_test.out)" | tee -a $LOG)
for rr in 1 2 3; do
  if [ $rr = 2 ]; then order="tip base"; else order="base tip"; fi
  for arm in $order; do
    if [ $arm = base ]; then SRC=/workspace/src-base COMMIT=227414560b6588f8e99336686ff01af8144ee2e7 run s1-base-p8-r$rr fp8-ada-v3x4 4096 8 5
    else SRC=/workspace/src COMMIT=$TIP run s1-tip-p8-r$rr fp8-ada-v3x4 4096 8 5; fi
  done
done
prof s1-tip-p8 fp8-ada-v3x4 4096 8
echo DONE-20
