#!/usr/bin/env bash
# fused-phases: the tests the lane touched or depends on, on the pod (frozen vu-k1536 built: the bf16-ampere family reads it).
source /workspace/fused-phases/scripts/lib.sh
cd /workspace/src
P=$FP/pytest; mkdir -p $P
OMP_NUM_THREADS=4 timeout 1500 $PY -m pytest -q -p no:cacheprovider --timeout 900 \
    backends/direct/ligero/phases_test.py backends/numerical/tests/bench/test_instance_equiv.py \
    backends/direct/ligero/fold_test.py backends/direct/ligero/hints_fused_test.py \
    --junitxml=$P/junit.xml > $P/pytest.log 2>&1
echo "PYTEST_DONE rc=$? $(tail -1 $P/pytest.log)" | tee -a $P/summary.txt
