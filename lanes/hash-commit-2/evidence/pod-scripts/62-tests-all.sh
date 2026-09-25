#!/usr/bin/env bash
# hash-commit-2: byte-identity + neighbour suites in one pytest, no -x (every failure listed), on /workspace/src;
# log $HC/tests-all-<commit>.log, one line to runs.txt.
source /workspace/hash-commit-2/scripts/lib.sh
c=$(python3 -c "import json;print(json.load(open('/workspace/src/.research-source.json'))['commit'][:8])")
gpu_idle || exit 1
( cd /workspace/src && PATH=/workspace/bin:$PATH PYTHONPATH="$PWD/packages/verity/src:$PWD/backends/numerical/python:$PWD/tools/research/src:$PWD" \
  $PY -m pytest -q backends/shared/hash_gpu/tests backends/direct/ligero/frame_gpu_test.py tests/test_commit_cost_benchmark.py \
    backends/direct/ligero/hashchain_test.py backends/direct/ligero/leaf_test.py backends/direct/ligero/leaf/core_schema_test.py \
    packages/verity/tests/commitments > $HC/tests-all-$c.log 2>&1 )
echo "$(date -u +%H:%M:%SZ) tests-all $c rc=$? $(tail -1 $HC/tests-all-$c.log)" | tee -a $LOG
