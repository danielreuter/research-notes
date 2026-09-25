#!/usr/bin/env bash
# reverify-tile-2: cargo test --release (ligero-verify) + pytest hashauth_test reverify_test steps_pin_test, on the shipped
# --source tree (--cwd source).  Adapted from reverify-tile's tests.sh; logs into the run dir.
set -uo pipefail
source /workspace/env.sh
q=$(awk '{print $1}' /sys/fs/cgroup/cpu.max 2>/dev/null); p=$(awk '{print $2}' /sys/fs/cgroup/cpu.max 2>/dev/null)
[ -n "$q" ] && [ "$q" != max ] && export RAYON_NUM_THREADS=$((q / p)) OMP_NUM_THREADS=$((q / p))
O=$RESEARCH_RUN_DIR; rc=0
echo "=== $(date -u +%H:%M:%SZ) cargo build/test (rustc $(rustc --version)) source ${RESEARCH_SOURCE_SHA:-?}"
mkdir -p /workspace/bin
( cd backends/ligero-verify && cargo build --release 2>&1 | tail -2 && cp $CARGO_TARGET_DIR/release/ligero-verify /workspace/bin/ \
  && cargo test --release 2>&1 | tee $O/cargo_test.log | grep -E "^test result|FAILED|panicked" ) || rc=1
grep -q "FAILED\|error\[" $O/cargo_test.log && rc=1
echo "=== $(date -u +%H:%M:%SZ) pytest hashauth_test reverify_test steps_pin_test"
$PY -m pytest -p no:cacheprovider -q -rfEs --timeout 3600 backends/direct/ligero/hashauth_test.py backends/direct/ligero/reverify_test.py \
  backends/direct/ligero/steps_pin_test.py 2>&1 | tee $O/pytest_focus.log | tail -40
[ ${PIPESTATUS[0]} -eq 0 ] || rc=1
echo "=== $(date -u +%H:%M:%SZ) done rc=$rc"; exit $rc
