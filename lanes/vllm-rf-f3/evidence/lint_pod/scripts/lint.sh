#!/bin/bash
# the coordinator's lint run: python -m pytest integrations/vllm/tests/lint -q, from the tree root, gate (b)'s environment.
#   usage: lint.sh TREE TAG [pytest args...]      logs: /workspace/rff3/logs/TAG.{log,xml,env}
T=$1; TAG=$2; shift 2
L=/workspace/rff3/logs; mkdir -p $L
cd "$T" || exit 3
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src
export HF_HOME=/workspace/hf
export PYTHONDONTWRITEBYTECODE=1
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO
env | sort | grep -E '^(PATH|PYTHON|HF_|OMP_|VERITY|VERITOR|RESEARCH)' > $L/$TAG.env
echo "start $(date -u +%FT%TZ) tree $T sha $(python -c 'import json,sys; print(json.load(open(sys.argv[1]))["commit"])' $T/.research-source.json 2>/dev/null)"
python -m pytest integrations/vllm/tests/lint -q -ra -o junit_family=xunit1 --junitxml=$L/$TAG.xml "$@" > $L/$TAG.log 2>&1
rc=$?
echo "exit $rc $(date -u +%FT%TZ)"
echo "exit $rc $(date -u +%FT%TZ)" >> $L/$TAG.log
