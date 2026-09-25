#!/usr/bin/env bash
# b-ligero-standard-hash: the BLAKE3 leaf + core-vector tests (leaf_bytes_many == leaf_bytes == blake3 package), then one short fp8-ada+blake3 commit-per-rep bench.
# research run --on POD --project verity --cwd /workspace/src --send lib.sh --send 13-check.sh -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/13-check.sh"'
IN=$(dirname "$0"); source "$IN/lib.sh"
RD=${RESEARCH_RUN_DIR:?}
export PYTHONPATH="$(pwd)/packages/verity/src:$(pwd)/backends/numerical/python:$(pwd)/tools/research/src:$(pwd)"
$PY -m pytest -q -x backends/direct/ligero/leaf/blake3_test.py backends/direct/ligero/leaf/core_schema_test.py 2>&1 | tail -n 5
trc=${PIPESTATUS[0]}; echo "pytest rc=$trc"
[ $trc -eq 0 ] || exit $trc
gpu_idle || exit 3
$PY -m backends.direct.ligero.run --relation fp8-ada+blake3 bench-vu --zk --mode interactive --auth included-hash --commit-per-rep \
    --batch 4096 --pipeline 2 --total-vus 4096 --target -128 --reps 1 --device cuda --out $RD/result.json > $RD/bench.log 2>&1
echo "bench rc=$?"; grep -E "^rep |committed" $RD/bench.log | cut -c1-400
