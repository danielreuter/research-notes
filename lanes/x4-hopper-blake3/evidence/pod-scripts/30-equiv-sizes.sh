#!/usr/bin/env bash
# x4-hopper-blake3: the instance-equiv/v1 document of every other sweep size (coordinator 1836Z: one per size), each
# --check re-derived, published by 50-outputs.py as instance-equiv/v1 outputs (never labelled verified here).
#   EQ="fp8-hopper-x4:1024,2048 bf16-hopper-x4:1024"
# research run --on vy-x4-hopper-blake3-h100 --project verity --cwd /workspace/src --custody-r2 --custody-ttl 8h \
#     --send lib.sh --send 50-outputs.py --send 30-equiv-sizes.sh --env EQ="..." -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/30-equiv-sizes.sh"'
IN=$(dirname "$0"); RD=${RESEARCH_RUN_DIR:?}
cd /workspace/src
source "$IN/lib.sh"
export PYTHONPATH="$(pwd)/packages/verity/src:$(pwd)/backends/numerical/python:$(pwd)/tools/research/src:$(pwd)"
mkdir -p $RD/outputs
rc=0
for e in ${EQ:?}; do
  rel=${e%%:*}
  for n in $(echo ${e#*:} | tr ',' ' '); do
    E=$RD/outputs/instance-equiv-$rel-$n.json
    echo "##### $(date -u +%H:%M:%SZ) instance-equiv $rel n=$n"
    $PY -m verity_numerical.bench.instance_equiv --relation $rel --vus $n --procs $NT --out $E 2>&1 | tail -n 1 | cut -c1-200
    $PY -m verity_numerical.bench.instance_equiv --check $E --vus $n --procs $NT 2>&1 | tail -n 1 | cut -c1-200
    r=${PIPESTATUS[0]}; echo "check rc=$r"; [ $r -ne 0 ] && rc=$r
  done
done
$PY "$IN/50-outputs.py" $RD x4-hopper-blake3
exit $rc
