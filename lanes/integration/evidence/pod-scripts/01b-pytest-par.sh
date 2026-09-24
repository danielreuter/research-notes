#!/usr/bin/env bash
# integration merge-val-3 (a): the rest of the full backends/direct/ligero pytest, split into parallel groups (the sequential
# run in 01-tests.sh reached test 83/449 in 26 min under the gates; it covered bench_result .. fp4/hints_device, with the one
# known fold_test[bf16-ampere-x4] failure). fold_test reruns here with the fixed bound.
source /workspace/env.sh
cd /workspace/src
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
# the container's CPU quota is 10.2 cores (cfs_quota_us 1020000) while torch sizes its pools for the 96 visible cores
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
O=/workspace/integration/tests; L=backends/direct/ligero
g() {  # tag, files...
  local tag=$1; shift
  $PY -m pytest "$@" -q -p no:cacheprovider -rfE > $O/pytest_$tag.log 2>&1
  echo "PYTEST_EXIT $?" >> $O/pytest_$tag.log
  echo "$tag $(tail -3 $O/pytest_$tag.log | grep -E 'passed|failed|error' | tail -1)" | tee -a $O/pytest_par_summary.txt
}
g g1 $L/fp4/relation_test.py $L/fp8/relation_test.py $L/hashchain_test.py $L/leaf/ajtai_key_test.py $L/leaf/ajtai_params_test.py \
     $L/leaf/ajtai_test.py $L/leaf/blake3_test.py $L/fold_test.py $L/privsel/relation_test.py $L/pubsel/relation_test.py &
g g2 $L/hints_fused_test.py $L/relations_test.py $L/v2/tests/test_toy.py $L/witness_device_test.py \
     $L/leaf/conformance_test.py $L/leaf_test.py $L/live_test.py $L/pipeline_race_test.py $L/reverify_test.py $L/steps_pin_test.py &
wait
echo PAR_DONE | tee -a $O/pytest_par_summary.txt
