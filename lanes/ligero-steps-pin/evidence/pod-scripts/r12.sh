#!/usr/bin/env bash
# ligero-steps-pin, tip with R1 (auth layout) + R2 (reverify recomputes the trees): cargo build/test --release; pytest
# hashauth_test (R1 remap e2e through $LIGERO_VERIFY), steps_pin_test, reverify_test; the 9 regression dumps (Rust pinned
# batch + Python, reverify.py); R2 over the dumps (r2_dumps.py); then the ligero regression list again (conformance [blake3]
# deselected: too slow on CPU).  Scripts in /workspace/scripts; outputs /workspace/lsp/*_r12.*
set -uo pipefail
source /workspace/env.sh
cd /workspace/src
O=/workspace/lsp; S=/workspace/scripts; rc=0
echo "=== $(date -u +%H:%M:%SZ) cargo build/test (rustc $(rustc --version))"
( cd backends/ligero-verify && cargo build --release 2>&1 | tail -2 && cp $CARGO_TARGET_DIR/release/ligero-verify /workspace/bin/ \
  && cargo test --release 2>&1 | tee $O/cargo_test_r12.log | grep -E "^test result|FAILED|panicked" ) || rc=1
grep -q "FAILED\|error\[" $O/cargo_test_r12.log && rc=1
echo "=== $(date -u +%H:%M:%SZ) pytest hashauth_test steps_pin_test reverify_test test_frame_v3"
$PY -m pytest -p no:cacheprovider -q -rfEs --timeout 3600 backends/direct/ligero/hashauth_test.py backends/direct/ligero/steps_pin_test.py \
  backends/direct/ligero/reverify_test.py packages/verity/tests/commitments/test_frame_v3.py 2>&1 | tee $O/pytest_focus_r12.log | tail -20
[ ${PIPESTATUS[0]} -eq 0 ] || rc=1
echo "=== $(date -u +%H:%M:%SZ) regression dumps (Rust pinned batch + Python)"
OUT=$O/reverify_r12.json $PY $S/reverify.py 2>&1 | tee $O/reverify_r12.log | tail -12
[ ${PIPESTATUS[0]} -eq 0 ] || rc=1
echo "=== $(date -u +%H:%M:%SZ) R2 over the dumps"
$PY $S/r2_dumps.py 2>&1 | tee $O/r2_dumps.log | tail -12
echo "=== $(date -u +%H:%M:%SZ) ligero regression list"
T="hashchain_test.py relations_test.py leaf_test.py chain_test.py live_test.py leaf/ fp4/relation_test.py fp4/hashed_test.py fp8/relation_test.py"
$PY -m pytest -p no:cacheprovider -q -rfEs --timeout 1800 -k "not (conformance_test and blake3)" \
  $(for t in $T; do echo backends/direct/ligero/$t; done) 2>&1 | tee $O/pytest_regression_r12.log | tail -25
[ ${PIPESTATUS[0]} -eq 0 ] || rc=1
echo "=== $(date -u +%H:%M:%SZ) done rc=$rc"
exit $rc
