#!/usr/bin/env bash
# arith step 2 (4090): bit-exactness script, then the lincomb2 (w and v in one pass) sweep against two lincomb calls on the
# fp8-ada-v3x4 l=4096 system.
source /workspace/arith/scripts/lib.sh
export PYTHONPATH="/workspace/src/packages/verity/src:/workspace/src/backends/numerical/python:/workspace/src/tools/research/src:/workspace/src"
cd /workspace/src
$PY -m backends.direct.ligero.tests_fused_test --reps 3 > $A/tests_fused_test-s2.out 2>&1
echo "tests_fused_test s2 rc=$? $(tail -1 $A/tests_fused_test-s2.out)" | tee -a $LOG
$PY /workspace/arith/scripts/kbench.py --relation fp8-ada-v3x4 --l 4096 --reps 20 --wv > $A/kbench-wv.out 2>&1
echo "kbench wv rc=$?" | tee -a $LOG
echo DONE-40
