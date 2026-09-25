#!/usr/bin/env bash
# b-ligero-standard-hash: +$LEAF (default blake3) on relations without a pin. Per relation: leaf.fixtures (compose, one proved sub-batch,
# ligero-verify system-digest -> the leaf.rs PINS row), then the gate (honest sub-batches + the negatives battery).
# research run --on POD --project verity --cwd /workspace/src --send lib.sh --send 10-pins-gates.sh \
#     --env RELS="bf16-ampere fp8-hopper" -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/10-pins-gates.sh"'
IN=$(dirname "$0"); source "$IN/lib.sh"
RD=${RESEARCH_RUN_DIR:-/workspace/b-ligero-standard-hash/pins}; mkdir -p $RD
GATE_VUS=${GATE_VUS:-2048}; LEAF=${LEAF:-blake3}
for rel in ${RELS:-bf16-ampere fp8-hopper}; do
  echo "=== $(date -u +%H:%M:%SZ) fixture $rel+$LEAF"
  $PY -m backends.direct.ligero.leaf.fixtures --relation $rel --leaf $LEAF --device cuda --out $RD/fixtures/$rel-$LEAF > $RD/fixture-$rel-$LEAF.log 2>&1
  echo "rc=$?"; tail -4 $RD/fixture-$rel-$LEAF.log
  [ "${GATES:-1}" = 1 ] || continue
  gpu_idle
  echo "=== $(date -u +%H:%M:%SZ) gate $rel+$LEAF --vus $GATE_VUS --batch 4096"
  t0=$(date +%s)
  $PY -m backends.direct.ligero.run --relation $rel+$LEAF gate-vu --vus $GATE_VUS --batch 4096 --zk --mode interactive \
      --auth included-hash --target -128 --device cuda > $RD/gate-$rel-$LEAF.log 2>&1
  echo "rc=$? wall=$(( $(date +%s) - t0 ))s"; tail -6 $RD/gate-$rel-$LEAF.log
done
