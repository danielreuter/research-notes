#!/bin/bash
# lints + gate (b) on the shipped tree ($PWD), in a fresh copy; run head and base on the same pod and jdiff them.
#   usage: research run --on <pod> --project verity --custody-r2 --source <tree> --cwd source --timeout 7200
#          --env TAG=head|base --env VENV=<venv dir> --send gate_b.sh -- bash -c 'bash "$RESEARCH_RUN_DIR/inputs/gate_b.sh"'
S=$PWD; L=$RESEARCH_RUN_DIR; H=/workspace/b5vab-$TAG
echo "start $TAG $(date -u +%FT%TZ) src $S $(git -C $S rev-parse HEAD 2>/dev/null)"
rm -rf $H && cp -a $S $H && find $H -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null
export PATH=$VENV/bin:$PATH HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=$H/integrations/vllm:$H/packages/verity/src:$H/tools/research/src
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN VERITY_REGRESSION
cd $H
python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py integrations/vllm/tests/test_imports_resolve.py \
  -q -o junit_family=xunit1 --junitxml=$L/lints-$TAG.xml > $L/lints-$TAG.log 2>&1
echo "lints rc=$? $(tail -1 $L/lints-$TAG.log) $(date -u +%FT%TZ)"
OMP_NUM_THREADS=3 python -m pytest integrations/vllm/tests -ra -n 12 --dist loadfile -o junit_family=xunit1 --junitxml=$L/b-$TAG.xml > $L/b-$TAG.log 2>&1
echo "gate_b rc=$? $(tail -1 $L/b-$TAG.log) $(date -u +%FT%TZ)"
