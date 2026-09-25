#!/usr/bin/env bash
# b-ligero-vllm-v1: instance-equiv/v1 of REL at VUS (the plateau size), then --check re-derives it.
IN=$(dirname "$0"); source "$IN/lib.sh"
RD=${RESEARCH_RUN_DIR:?}
PYTHONPATH=backends/numerical/python:$PYTHONPATH $PY -m verity_numerical.bench.instance_equiv --relation ${REL:?} --vus ${VUS:?} --procs 8 --out-dir $RD/equiv
echo "rc=$?"
PYTHONPATH=backends/numerical/python:$PYTHONPATH $PY -m verity_numerical.bench.instance_equiv --check $RD/equiv/*.json; echo "check rc=$?"
