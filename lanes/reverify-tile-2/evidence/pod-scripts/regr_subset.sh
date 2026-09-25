#!/usr/bin/env bash
# reverify-tile-2: the regression-list cases that failed on rvt-regression-3 (overloaded host), on the shipped tree.
set -uo pipefail
source /workspace/env.sh
echo "=== $(date -u +%H:%M:%SZ) source ${RESEARCH_SOURCE_SHA:-?}"
$PY -m pytest -p no:cacheprovider -q -rfEs --timeout 1500 "$@" 2>&1 | tee $RESEARCH_RUN_DIR/pytest_subset.log | tail -30
rc=${PIPESTATUS[0]}; echo "=== $(date -u +%H:%M:%SZ) done rc=$rc"; exit $rc
