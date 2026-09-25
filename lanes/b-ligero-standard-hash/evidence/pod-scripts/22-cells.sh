#!/usr/bin/env bash
# b-ligero-standard-hash: 20-cell.sh once per REL in RELS, each into its own $RESEARCH_RUN_DIR/<rel> (result.json, bench.log,
# proofs/ + the pod's Rust verdicts), one after the other.
# research run --on POD --project verity --cwd /workspace/src --custody-r2 --custody-ttl 8h --send lib.sh --send 20-cell.sh \
#     --send 22-cells.sh --env RELS="fp8-ada+blake3 fp8-ada-x4+blake3" -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/22-cells.sh"'
IN=$(dirname "$0"); RD=${RESEARCH_RUN_DIR:?}; rc=0
for rel in ${RELS:?}; do
  mkdir -p "$RD/$rel"
  echo "=== $(date -u +%H:%M:%SZ) $rel"
  RESEARCH_RUN_DIR="$RD/$rel" REL=$rel bash "$IN/20-cell.sh" || rc=$?
done
exit $rc
