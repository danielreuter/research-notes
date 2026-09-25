#!/usr/bin/env bash
# ligero-steps-pin: live_test's shared-pair tests alone, at the lane tip (/workspace/src) and with main 25f0c1de's
# relchain.py / serialize.py (/workspace/base, made by before.sh): is the F in the regression run this lane's change?
set -uo pipefail
source /workspace/env.sh
for tree in src base; do
  cd /workspace/$tree
  export PYTHONPATH="/workspace/$tree/packages/verity/src:/workspace/$tree/backends/numerical/python:/workspace/$tree/tools/research/src:/workspace/$tree"
  echo "=== $tree"
  $PY -m pytest -p no:cacheprovider -q -rA --timeout 1800 backends/direct/ligero/live_test.py -k "shared_pair" 2>&1 | tee /workspace/lsp/live_shared_$tree.log | grep -E "^(PASSED|FAILED|ERROR)|^E  |passed|failed" | head -40
done
