#!/usr/bin/env bash
# reverify-tile: the ligero regression list (regression.sh) on the second pod vy-reverify-tile-2, in the shipped source root
# (`research run --source . --cwd source --custody-r2`): cpu_setup.sh, the ligero-verify release build, then the list.
# Output $RESEARCH_RUN_DIR/pytest_regression.log (custody on R2).
set -uo pipefail
S=$PWD; O=$RESEARCH_RUN_DIR
SRC=$S bash $O/inputs/cpu_setup.sh 2>&1 | tail -5
source /workspace/env.sh
export PYTHONPATH="$S/packages/verity/src:$S/backends/numerical/python:$S/tools/research/src:$S"
( cd backends/ligero-verify && cargo build --release 2>&1 | tail -2 ) && cp $CARGO_TARGET_DIR/release/ligero-verify /workspace/bin/ || exit 1
echo "=== $(date -u +%H:%M:%SZ) ligero regression list at $(git -C $S rev-parse HEAD 2>/dev/null || head -c 200 .research-source.json)"
T="hashchain_test.py relations_test.py leaf_test.py chain_test.py live_test.py leaf/ fp4/relation_test.py fp4/hashed_test.py fp8/relation_test.py"
$PY -m pytest -p no:cacheprovider -q -rfEs --timeout 1800 -k "not (conformance_test and blake3)" \
  $(for t in $T; do echo backends/direct/ligero/$t; done) 2>&1 | tee $O/pytest_regression.log | tail -25
rc=${PIPESTATUS[0]}
echo "=== $(date -u +%H:%M:%SZ) done rc=$rc"; exit $rc
