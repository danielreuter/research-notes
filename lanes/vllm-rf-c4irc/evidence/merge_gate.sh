#!/bin/bash
# reg pod: lints + core + integration tests/query and tests/program on the shipped tree ($PWD), for the merge of
# origin/main into lane/vllm-rf-c4ir (head) and for origin/main itself (base); run both on the same pod and jdiff them.
#   usage: research run --on vyv-rf-c4ir-reg --project verity --custody-r2 --source <tree> --cwd source --timeout 7200
#          --env TAG=head|base --send merge_gate.sh -- bash -c 'bash "$RESEARCH_RUN_DIR/inputs/merge_gate.sh"'
S=$PWD; L=$RESEARCH_RUN_DIR; H=/workspace/c4irc-$TAG
echo "start $TAG $(date -u +%FT%TZ) src $S"
rm -rf $H && cp -a $S $H && find $H -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2
export PYTHONPATH=$H/integrations/vllm:$H/packages/verity/src:$H/tools/research/src
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN VERITY_REGRESSION
cd $H/integrations/vllm
python -m pytest tests/lint tests/test_no_by_name_rules.py tests/test_imports_resolve.py tests/test_no_dead_modules.py -q -o junit_family=xunit1 --junitxml=$L/lints-$TAG.xml > $L/lints-$TAG.log 2>&1
echo "lints rc=$? $(tail -1 $L/lints-$TAG.log) $(date -u +%FT%TZ)"
(cd $H/packages/verity && python -m pytest tests -q -n 4 -o junit_family=xunit1 --junitxml=$L/core-$TAG.xml > $L/core-$TAG.log 2>&1)
echo "core rc=$? $(tail -1 $L/core-$TAG.log) $(date -u +%FT%TZ)"
python -m pytest tests/query tests/program -q -n 6 --dist loadfile -o junit_family=xunit1 --junitxml=$L/qp-$TAG.xml > $L/qp-$TAG.log 2>&1
echo "query+program rc=$? $(tail -1 $L/qp-$TAG.log) $(date -u +%FT%TZ)"
