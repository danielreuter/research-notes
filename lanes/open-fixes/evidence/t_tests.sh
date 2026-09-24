#!/bin/bash
# t_tests.sh -- lane open-fixes pod tests on the 4090 (lane tree /workspace/src):
#   pytest backends/direct/ligero (torch + CUDA, default RELMIN_DIFF_N), the v1-v2 differential at 1e5 units per relation
#   (RELMIN_DIFF_N=100000, pubsel), cargo test --release in backends/ligero-verify
PY=/workspace/venv312/bin/python
export PATH=/root/.cargo/bin:/root/.local/bin:/usr/local/cuda/bin:$PATH
export CARGO_TARGET_DIR=/workspace/cargo-target
L=/workspace/logs
log() { echo "$(date -u +%H:%M:%S) $*" >> $L/tests.log; }
export LIGERO_INSTANCES_CACHE=/workspace/instances-cache
/workspace/run.sh /workspace/src tests_pytest $PY -m pytest -q -p no:cacheprovider backends/direct/ligero --deselect backends/direct/ligero/v2
log "pytest backends/direct/ligero: $(grep -E '[0-9]+ (passed|failed)' $L/tests_pytest.log | tail -1)"
RELMIN_DIFF_N=100000 /workspace/run.sh /workspace/src tests_diff1e5 $PY -m pytest -q -p no:cacheprovider backends/direct/ligero/pubsel/relation_test.py -k differential -v
log "pubsel differential 1e5: $(grep -E '[0-9]+ (passed|failed)' $L/tests_diff1e5.log | tail -1)"
(cd /workspace/src/backends/ligero-verify && cargo test --release 2>&1 | grep -E "^test result|FAILED|panicked" > $L/tests_cargo.log; echo "rc=${PIPESTATUS[0]}" >> $L/tests_cargo.log)
log "cargo test --release: $(tr '\n' ' ' < $L/tests_cargo.log)"
log TESTS_DONE
