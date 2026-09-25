#!/usr/bin/env bash
# x4-sha256-fill (from b-ligero-sha256 10-pins-gates.sh): $BASE+sha256 fixture (compose, one proved sub-batch, ligero-verify
# system-digest -> the leaf.rs PINS row), then the gate (honest sub-batches + the 86-negative battery), then the sha256
# conformance suite on $BASE (slow: ~15 min of committed-operand negatives).  Exits nonzero if the fixture or gate fails.
IN=$(dirname "$0"); source "$IN/lib.sh"
RD=${RESEARCH_RUN_DIR:?}; mkdir -p $RD
BASE=${BASE:?}; GATE_VUS=${GATE_VUS:-2048}
echo "=== $(date -u +%H:%M:%SZ) fixture $BASE+sha256"
$PY -u -m backends.direct.ligero.leaf.fixtures --relation $BASE --leaf sha256 --device cuda --out $RD/fixtures/$BASE-sha256 > $RD/fixture-$BASE.log 2>&1
r=$?; echo "fixture rc=$r"; tail -8 $RD/fixture-$BASE.log
[ $r -eq 0 ] || exit 5
gpu_idle
echo "=== $(date -u +%H:%M:%SZ) gate $BASE+sha256 --vus $GATE_VUS --batch ${GATE_BATCH:-4096}"
t0=$(date +%s)
$PY -u -m backends.direct.ligero.run --relation $BASE+sha256 gate-vu --vus $GATE_VUS --batch ${GATE_BATCH:-4096} --zk --mode interactive \
    --auth included-hash --target -128 --device cuda --instance-procs 16 --out $RD/gate-$BASE.json > $RD/gate-$BASE.log 2>&1
g=$?; echo "gate rc=$g wall=$(( $(date +%s) - t0 ))s"; tail -8 $RD/gate-$BASE.log
if [ "${CONF:-1}" = 1 ]; then
  echo "=== $(date -u +%H:%M:%SZ) conformance sha256 on $BASE"
  VERITY_LEAF_CONFORMANCE_REL=$BASE $PY -m pytest -q -x backends/direct/ligero/leaf/conformance_test.py -k sha256 > $RD/conf-$BASE.log 2>&1
  echo "conformance rc=$?"; tail -8 $RD/conf-$BASE.log
fi
exit $g
