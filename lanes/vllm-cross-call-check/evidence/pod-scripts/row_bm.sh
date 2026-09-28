#!/usr/bin/env bash
# One sweep row's Build and Match from the shipped tree (research run --on <pod> --source <tree> --cwd source/integrations/vllm),
# on a bootstrapped pod (ops/pod_bootstrap.sh --gpu), into its own sweep directory:
#   bash row_bm.sh ROW ROLE REPO REV SWEEP_DIR
set -uo pipefail
ROW=$1 ROLE=$2 REPO=$3 REV=$4 SWEEP=$5
PY=${PY:-/workspace/venv312/bin/python}
export PYTHONPATH=.:$(cd ../../packages/verity/src && pwd -P):$(cd ../../tools/research/src && pwd -P):$(cd ../../protocols/sampled_proofs && pwd -P)
mkdir -p "$SWEEP"
"$PY" -m verity_vllm.pipeline.cli row run "$ROW" "$ROLE" "$REPO" "$REV" --stages build,match --sweep-dir "$SWEEP"
rc=$?
echo "[row_bm] rc=$rc"
cat "$SWEEP/$ROW/stages.txt" 2>/dev/null
exit $rc
