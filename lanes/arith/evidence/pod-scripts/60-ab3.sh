#!/usr/bin/env bash
# arith steps 2+3 (4090): bit-exactness script, then step 1 (9d1a7f15, /workspace/src-s1) vs step 2 (0baefa9d,
# /workspace/src-s2) vs tip (step 3: + intt_rows), fp8-ada-v3x4 l=4096 p8, 4 rounds in rotating order, then a tip profile.
# Nothing else may run on the pod meanwhile.
source /workspace/arith/scripts/lib.sh
(cd /workspace/src && PYTHONPATH="/workspace/src/packages/verity/src:/workspace/src/backends/numerical/python:/workspace/src/tools/research/src:/workspace/src" \
  $PY -m backends.direct.ligero.tests_fused_test --reps 3 > $A/tests_fused_test-s3.out 2>&1; echo "tests_fused_test s3 rc=$? $(tail -1 $A/tests_fused_test-s3.out)" | tee -a $LOG)
arm() {
  case $1 in
    s1) SRC=/workspace/src-s1 COMMIT=9d1a7f15bb3d50d3d53adadd9dff801f08b252f3 run s3-s1-p8-r$2 fp8-ada-v3x4 4096 8 5 ;;
    s2) SRC=/workspace/src-s2 COMMIT=0baefa9d7a7ff5a8d2af99f0617be0ae5f5764c8 run s3-s2-p8-r$2 fp8-ada-v3x4 4096 8 5 ;;
    tip) SRC=/workspace/src COMMIT=$TIP run s3-tip-p8-r$2 fp8-ada-v3x4 4096 8 5 ;;
  esac
}
for rr in 1 2 3 4; do
  case $rr in 1) order="s1 s2 tip";; 2) order="tip s1 s2";; 3) order="s2 tip s1";; 4) order="tip s2 s1";; esac
  for a in $order; do arm $a $rr; done
done
prof s3-tip-p8 fp8-ada-v3x4 4096 8
echo DONE-60
