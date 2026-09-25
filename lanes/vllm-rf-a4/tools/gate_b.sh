#!/bin/bash
# gate (b): python -m pytest integrations/vllm/tests, from the tree root, in the bootstrap's venv312.
#   usage: gate_b.sh TREE TAG [pytest args...]      logs: /workspace/a4/logs/TAG.{log,xml,env}
T=$1; TAG=$2; shift 2
L=/workspace/a4/logs; mkdir -p $L
cd "$T" || exit 3
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src
export HF_HOME=/workspace/hf
export PYTHONDONTWRITEBYTECODE=1
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO
env | sort | grep -E '^(PATH|PYTHON|HF_|OMP_|MKL_|VERITY|VERITOR|RESEARCH|CUDA|TORCH|VLLM|TRITON)' > $L/$TAG.env
echo "start $(date -u +%FT%TZ) tree $T"
python -m pytest integrations/vllm/tests -ra -o junit_family=xunit1 --junitxml=$L/$TAG.xml "$@" > $L/$TAG.log 2>&1
rc=$?
echo "exit $rc $(date -u +%FT%TZ)" | tee -a $L/$TAG.log
