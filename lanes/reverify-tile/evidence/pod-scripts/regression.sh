#!/usr/bin/env bash
# reverify-tile: the ligero regression list ligero-steps-pin ran (r12.sh), at the tip in /workspace/src; conformance
# [blake3] deselected (too slow on CPU, as there).  Output /workspace/reverify-tile/pytest_regression.log.
set -uo pipefail
source /workspace/env.sh
q=$(awk '{print $1}' /sys/fs/cgroup/cpu.max 2>/dev/null); p=$(awk '{print $2}' /sys/fs/cgroup/cpu.max 2>/dev/null)
[ -n "$q" ] && [ "$q" != max ] && export RAYON_NUM_THREADS=$((q / p)) OMP_NUM_THREADS=$((q / p))
cd /workspace/src
O=/workspace/reverify-tile; mkdir -p $O
echo "=== $(date -u +%H:%M:%SZ) ligero regression list at $(head -c 200 .research-source.json)"
T="hashchain_test.py relations_test.py leaf_test.py chain_test.py live_test.py leaf/ fp4/relation_test.py fp4/hashed_test.py fp8/relation_test.py"
$PY -m pytest -p no:cacheprovider -q -rfEs --timeout 1800 -k "not (conformance_test and blake3)" \
  $(for t in $T; do echo backends/direct/ligero/$t; done) 2>&1 | tee $O/pytest_regression.log | tail -25
rc=${PIPESTATUS[0]}
echo "=== $(date -u +%H:%M:%SZ) done rc=$rc"; exit $rc
