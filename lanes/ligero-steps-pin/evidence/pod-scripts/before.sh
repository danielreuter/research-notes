#!/usr/bin/env bash
# ligero-steps-pin "before": the lane's steps_pin_test +shared cases against main 25f0c1de's relchain.py / serialize.py
# (the inputs/ copies), in a copy of the tree.  Expected: the Python asserts FAIL where main accepts; Rust asserts hold.
set -uo pipefail
source /workspace/env.sh
rm -rf /workspace/base && cp -a /workspace/src /workspace/base
cp $RESEARCH_RUN_DIR/inputs/ligero-steps-pin-base-relchain.py /workspace/base/backends/direct/ligero/relchain.py
cp $RESEARCH_RUN_DIR/inputs/ligero-steps-pin-base-serialize.py /workspace/base/backends/direct/ligero/serialize.py
cd /workspace/base
export PYTHONPATH="/workspace/base/packages/verity/src:/workspace/base/backends/numerical/python:/workspace/base/tools/research/src:/workspace/base"
$PY -m pytest -p no:cacheprovider -q -rA --timeout 3600 backends/direct/ligero/steps_pin_test.py -k shared 2>&1 | tee /workspace/lsp/before_shared.log | grep -E "^(PASSED|FAILED|E  +AssertionError|E  +assert)|passed|failed" | head -30
exit 0
