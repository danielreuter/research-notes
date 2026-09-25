#!/usr/bin/env bash
# ligero-steps-pin: the focused tests at the final tip (hashauth_test R1/R2/R4, reverify_test, steps_pin_test H2 incl. the
# +shared fail-closed check) and R2 over the 9 dumps again.  Outputs /workspace/lsp/*_final.*
set -uo pipefail
source /workspace/env.sh
cd /workspace/src
O=/workspace/lsp; rc=0
echo "=== $(date -u +%H:%M:%SZ) pytest"
$PY -m pytest -p no:cacheprovider -q -rfEs --timeout 3600 backends/direct/ligero/hashauth_test.py backends/direct/ligero/reverify_test.py \
  backends/direct/ligero/steps_pin_test.py 2>&1 | tee $O/pytest_final.log | tail -12
[ ${PIPESTATUS[0]} -eq 0 ] || rc=1
echo "=== $(date -u +%H:%M:%SZ) R2 over the dumps"
$PY /workspace/scripts/r2_dumps.py 2>&1 | cut -c1-300 | tee $O/r2_dumps_final.log
echo "=== $(date -u +%H:%M:%SZ) done rc=$rc"; exit $rc
