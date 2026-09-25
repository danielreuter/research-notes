#!/usr/bin/env bash
# x4-hopper-blake3: bootstrap the H100 pod (pod_bootstrap.sh on the synced tree), then 10-pins-gates.sh: fixtures + the
# leaf.rs PINS row + the gate (2048 VUs + the 86 negatives) of fp8-hopper-x4 / bf16-hopper-x4 under $LEAF (default blake3).
# research run --on vy-x4-hopper-blake3-h100 --project verity --cwd /workspace/src --custody-r2 --custody-ttl 8h \
#     --send lib.sh --send 10-pins-gates.sh --send 01-boot-pins.sh -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/01-boot-pins.sh"'
IN=$(dirname "$0"); RD=${RESEARCH_RUN_DIR:?}
if [ "${BOOT:-1}" = 1 ]; then
  echo "=== $(date -u +%H:%M:%SZ) bootstrap"
  RELS= TILE64= bash /workspace/src/backends/direct/ligero/pod_bootstrap.sh > $RD/bootstrap.log 2>&1
  echo "bootstrap rc=$?"; tail -n 15 $RD/bootstrap.log
fi
cd /workspace/src
RESEARCH_RUN_DIR=$RD LEAF=${LEAF:-blake3} RELS="${XRELS:-fp8-hopper-x4 bf16-hopper-x4}" bash "$IN/10-pins-gates.sh"
for d in $RD/fixtures/*; do
  python3 -c "import json,sys; m=json.load(open(sys.argv[1]+'/manifest.json')); print(sys.argv[1].split('/')[-1], 'pins_row', m.get('pins_row'), 'rows', m['system']['rows'])" $d 2>&1 | tail -n 2
done
