#!/usr/bin/env bash
# wave-4090-2: the ligero pytest files integration never reached, each in its own process with 2 threads, all concurrent
# (7 x 2 threads ~ the pod's 13.6-core quota). Only after the timing runs. Outputs /workspace/wave-4090/pytest/<name>.{out,xml}.
source /workspace/env.sh
cd /workspace/src
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
O=/workspace/wave-4090/pytest; mkdir -p $O
B=backends/direct/ligero
for f in steps_pin_test reverify_test live_test pipeline_race_test leaf_test leaf/conformance_test pubsel/relation_test; do
  n=${f//\//_}
  ( t0=$(date +%s); $PY -m pytest -q -p no:cacheprovider --timeout 3000 --junitxml $O/$n.xml $B/$f.py > $O/$n.out 2>&1
    echo "$(date -u +%H:%M:%SZ) $n rc=$? wall=$(( $(date +%s) - t0 ))s $(tail -n 1 $O/$n.out)" >> $O/summary.txt ) &
done
wait
echo PYTEST_DONE >> $O/summary.txt
