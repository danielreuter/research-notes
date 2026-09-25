#!/usr/bin/env bash
# b-ligero-sha256: +sha256 per relation: the conformance suite (whole-block and half-block columns), leaf.fixtures (compose, one
# proved sub-batch, ligero-verify system-digest -> the leaf.rs PINS row), then the gate (honest sub-batches + negatives battery).
# research run --on vy-b-ligero-sha256 --project verity --cwd /workspace/src --send lib.sh --send 10-pins-gates.sh \
#     --env RELS="fp8-ada-x4 fp8-ada" -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/10-pins-gates.sh"'
IN=$(dirname "$0"); source "$IN/lib.sh"
RD=${RESEARCH_RUN_DIR:-/workspace/b-ligero-sha256/pins}; mkdir -p $RD
GATE_VUS=${GATE_VUS:-2048}
if [ "${CONF:-1}" = 1 ]; then
  $PY -m pytest -q backends/direct/ligero/leaf/core_schema_test.py > $RD/core-schema.log 2>&1; echo "core_schema rc=$?"; tail -2 $RD/core-schema.log
  for rel in ${CONF_RELS:-fp8-ada-x4 fp8-ada}; do
    echo "=== $(date -u +%H:%M:%SZ) conformance sha256 on $rel"
    VERITY_LEAF_CONFORMANCE_REL=$rel $PY -m pytest -q -x backends/direct/ligero/leaf/conformance_test.py -k sha256 > $RD/conf-$rel.log 2>&1
    echo "rc=$?"; tail -8 $RD/conf-$rel.log
  done
fi
for rel in ${RELS:-fp8-ada-x4}; do
  echo "=== $(date -u +%H:%M:%SZ) fixture $rel+sha256"
  $PY -u -m backends.direct.ligero.leaf.fixtures --relation $rel --leaf sha256 --device cuda --out $RD/fixtures/$rel-sha256 > $RD/fixture-$rel.log 2>&1
  echo "rc=$?"; tail -6 $RD/fixture-$rel.log
  [ "${GATES:-1}" = 1 ] || continue
  gpu_idle
  echo "=== $(date -u +%H:%M:%SZ) gate $rel+sha256 --vus $GATE_VUS --batch ${GATE_BATCH:-4096}"
  t0=$(date +%s)
  $PY -u -m backends.direct.ligero.run --relation $rel+sha256 gate-vu --vus $GATE_VUS --batch ${GATE_BATCH:-4096} --zk --mode interactive \
      --auth included-hash --target -128 --device cuda > $RD/gate-$rel.log 2>&1
  echo "rc=$? wall=$(( $(date +%s) - t0 ))s"; tail -8 $RD/gate-$rel.log
done
