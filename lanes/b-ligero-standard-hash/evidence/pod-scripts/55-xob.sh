#!/usr/bin/env bash
# b-ligero-standard-hash: the XOR-output-bits BLAKE3 compression prototype (leaf/blake3_xob.py, survey §3.2): its
# numpy-interpreter tests (== compress_np, tampered rows rejected), then the census at 8- and 16-bit words (CPU only).
# research run --on POD --project verity --cwd /workspace/src --send lib.sh --send 55-xob.sh -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/55-xob.sh"'
IN=$(dirname "$0"); source "$IN/lib.sh"
RD=${RESEARCH_RUN_DIR:?}
export PYTHONPATH="$(pwd)/packages/verity/src:$(pwd)/backends/numerical/python:$(pwd)/tools/research/src:$(pwd)"
$PY -m pytest -q backends/direct/ligero/leaf/blake3_xob_test.py -k "not census" 2>&1 | tail -n 15
echo "pytest rc=${PIPESTATUS[0]}"
for wb in 8 16; do
  $PY -m backends.direct.ligero.leaf.blake3_xob $wb > $RD/census_$wb.json 2> $RD/census_$wb.err
  echo "census $wb rc=$?"; cat $RD/census_$wb.json; tail -n 3 $RD/census_$wb.err
done
