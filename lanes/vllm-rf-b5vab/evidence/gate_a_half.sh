#!/bin/bash
# vyv-rf-c4ir-reg: gate (a) T0+T1 at the shipped tree ($PWD), one half selected by $K (pytest -k), on the fixtures already
# in /workspace/research/store (no key, no fetch). Env as c4ir's reg_gate_a.sh; tree copy and scratch are this half's own.
#   usage: research run --on vyv-rf-c4ir-reg --project verity --custody-r2 --source <tree> --cwd source --timeout 28800
#          --env HALF=rp|rest --env K=<expr> --send gate_a_half.sh -- bash -c 'bash "$RESEARCH_RUN_DIR/inputs/gate_a_half.sh"'
S=$PWD; L=$RESEARCH_RUN_DIR; H=/workspace/b5vab/tree-$HALF
echo "start $HALF $(date -u +%FT%TZ) src $S k=$K"
mkdir -p /workspace/b5vab && rm -rf $H && cp -a $S $H && find $H -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=$H/integrations/vllm:$H/packages/verity/src:$H/tools/research/src
export RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=$H/tools/research/store.pod.toml
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
cd $H
rm -rf /workspace/scratch/b5vab-$HALF && mkdir -p /workspace/scratch/b5vab-$HALF
export VERITY_REGRESSION_SCRATCH=/workspace/scratch/b5vab-$HALF VERITY_REGRESSION=1 VERITY_REGRESSION_TIERS=T0,T1
unset VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITY_REGRESSION_ENGINE VERITY_REGRESSION_ORACLE VERITOR_REPO
env | sort | grep -E '^(PATH|PYTHON|HF_|OMP_|VERITY|VERITOR|RESEARCH|CUDA|TORCH|VLLM|TRITON)' > $L/gate_a-$HALF.env
echo "gate_a start $(date -u +%FT%TZ)"
python -m pytest integrations/vllm/tests/regression -m regression -k "$K" -ra -o junit_family=xunit1 --junitxml=$L/gate_a-$HALF.xml > $L/gate_a-$HALF.log 2>&1
echo "gate_a rc=$? $(tail -1 $L/gate_a-$HALF.log) $(date -u +%FT%TZ)"
