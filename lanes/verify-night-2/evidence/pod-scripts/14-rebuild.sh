#!/usr/bin/env bash
# verify-night-2: rebuild ligero-verify from /workspace/src (research pods sync of lane/verify-night-2) and run the core
# commitments conformance tests (the reference 06-core-roots.py uses) plus the B-Ligero leaf/core-schema tests.
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
O=/workspace/verify-night-2; mkdir -p $O
{
echo "=== [$(date -u +%H:%M:%S)] src $(cat /workspace/src/.research-source.json 2>/dev/null | head -c 300)"
(cd backends/ligero-verify && cargo build --release 2>&1 | tail -2)
cp -f $CARGO_TARGET_DIR/release/ligero-verify /workspace/bin/ligero-verify && sha256sum /workspace/bin/ligero-verify
echo "=== [$(date -u +%H:%M:%S)] cargo test (ligero-verify)"
(cd backends/ligero-verify && cargo test --release 2>&1 | grep -E "^test result|FAILED|panicked" | head -20)
echo "=== [$(date -u +%H:%M:%S)] pytest core commitments + leaf schemas (PYTEST=${PYTEST:-1})"
[ "${PYTEST:-1}" = 1 ] && $PY -m pytest -q -x packages/verity/tests/commitments backends/direct/ligero/leaf/core_schema_test.py backends/direct/ligero/leaf/conformance_test.py 2>&1 | tail -4
echo "=== [$(date -u +%H:%M:%S)] done"
} 2>&1 | tee $O/rebuild-$(date -u +%H%M).out
