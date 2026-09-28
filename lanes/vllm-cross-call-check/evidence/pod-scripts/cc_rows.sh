#!/usr/bin/env bash
# circuit-check over served rows' request Programs (the Q_word partition over every Call, the Call outputs no commitment holds), on a
# bootstrapped pod, from the shipped tree's root (research run --on <pod> --source <tree> --cwd source --send cc_rows.sh):
#   bash cc_rows.sh BUILD_REQUEST_DIR:LABEL ...      -> $RESEARCH_RUN_DIR/cc-row-LABEL.json
set -uo pipefail
T=$(pwd -P)
export PYTHONPATH=$T/tools/research/src:$T/packages/verity/src:$T/backends/numerical/python:$T/integrations/vllm:$T/protocols/sampled_proofs:$T/protocols/one_stage:$T/backends/flock/python:$T/tools/circuit_check/src
PY=${PY:-/workspace/venv312/bin/python}
for s in "$@"; do
  "$PY" -m circuit_check "${s%%:*}" --out "${RESEARCH_RUN_DIR:?}/cc-row-${s##*:}.json"
  echo "[cc_rows] ${s##*:} rc=$?"
done
