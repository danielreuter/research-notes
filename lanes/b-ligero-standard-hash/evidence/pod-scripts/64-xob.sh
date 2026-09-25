#!/usr/bin/env bash
# b-ligero-standard-hash: the blake3-xob scheme (leaf/blake3_xob.py): the xob / witness-generator / conformance tests on the
# pod (CUDA), then fixtures of fp8-ada / fp8-ada-x4 under blake3-xob (the PINS rows to add) and of fp8-ada under blake3
# (the refactored gadget must keep the 71f39e44 pin), each checked by the pod's ligero-verify system-digest.
# research run --on POD --project verity --cwd /workspace/src --send lib.sh --send 10-pins-gates.sh --send 64-xob.sh \
#     -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/64-xob.sh"'
IN=$(dirname "$0"); source "$IN/lib.sh"
RD=${RESEARCH_RUN_DIR:?}
export PYTHONPATH="$(pwd)/packages/verity/src:$(pwd)/backends/numerical/python:$(pwd)/tools/research/src:$(pwd)"
gpu_idle || exit 3
L=backends/direct/ligero
$PY -m pytest -q -p no:cacheprovider $L/leaf/blake3_xob_test.py $L/witness_device_test.py $L/leaf_test.py 2>&1 | tail -n 15
echo "pytest xob/witness rc=${PIPESTATUS[0]}"
$PY -m pytest -q -p no:cacheprovider $L/leaf/conformance_test.py -k "blake3" 2>&1 | tail -n 15
echo "pytest conformance rc=${PIPESTATUS[0]}"
RESEARCH_RUN_DIR=$RD LEAF=blake3 RELS="fp8-ada" GATES=0 bash "$IN/10-pins-gates.sh"
RESEARCH_RUN_DIR=$RD LEAF=blake3-xob RELS="${XRELS:-fp8-ada fp8-ada-x4}" GATES=0 bash "$IN/10-pins-gates.sh"
for d in $RD/fixtures/*; do
  echo "$(basename $d): $($V system-digest --system $d/system.bin 2>&1 | head -c 400)"
  $PY -c "import json,sys,glob; m=json.load(open(glob.glob(sys.argv[1]+'/*manifest*.json')[0])); print(' pins_row', m.get('pins_row'), 'sys', m['system'].get('sys_id'), 'rows', m['system'].get('m'))" $d 2>&1 | tail -n 2
done
