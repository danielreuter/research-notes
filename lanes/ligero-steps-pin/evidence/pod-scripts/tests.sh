#!/usr/bin/env bash
# ligero-steps-pin: cargo build + cargo test --release (ligero-verify), then the ligero Python tests (steps_pin_test first,
# with $LIGERO_VERIFY so the +shared negatives run through Rust too), then red-team-leaf-2's +shared pair negatives
# through the new binary.  Run from /workspace/src (= lane/ligero-steps-pin tip).  Outputs under /workspace/lsp/.
set -uo pipefail
source /workspace/env.sh
cd /workspace/src
O=/workspace/lsp; mkdir -p $O
rc=0
echo "=== $(date -u +%H:%M:%SZ) cargo build/test (rustc $(rustc --version))"
( cd backends/ligero-verify && cargo build --release 2>&1 | tail -2 && cp $CARGO_TARGET_DIR/release/ligero-verify /workspace/bin/ \
  && cargo test --release 2>&1 | tee $O/cargo_test.log | grep -E "^test result|FAILED|panicked" ) || rc=1
grep -q "FAILED\|error\[" $O/cargo_test.log && rc=1
echo "=== $(date -u +%H:%M:%SZ) pytest steps_pin_test"
$PY -m pytest -p no:cacheprovider -q -rs --timeout 3600 backends/direct/ligero/steps_pin_test.py 2>&1 | tee $O/pytest_steps_pin.log | tail -15
[ ${PIPESTATUS[0]} -eq 0 ] || rc=1
echo "=== $(date -u +%H:%M:%SZ) pytest regression"
T="hashchain_test.py relations_test.py leaf_test.py chain_test.py reverify_test.py live_test.py leaf/ fp4/relation_test.py fp4/hashed_test.py fp8/relation_test.py"
$PY -m pytest -p no:cacheprovider -q -rs --timeout 3600 $(for t in $T; do echo backends/direct/ligero/$t; done) 2>&1 | tee $O/pytest_regression.log | tail -25
[ ${PIPESTATUS[0]} -eq 0 ] || rc=1
echo "=== $(date -u +%H:%M:%SZ) red-team-leaf-2 +shared pair negatives through the new Rust binary"
$PY backends/direct/ligero/redteam/leaf2_share_pair.py --out $O/share-pair --bin $LIGERO_VERIFY 2>&1 | tee $O/share_pair.log | tail -25
[ ${PIPESTATUS[0]} -eq 0 ] || rc=1
echo "=== $(date -u +%H:%M:%SZ) done rc=$rc"
exit $rc
