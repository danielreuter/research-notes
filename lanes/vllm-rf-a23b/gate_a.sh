#!/bin/bash
# gate (a): VERITY_REGRESSION=1 VERITY_REGRESSION_TIERS=T0,T1 python -m pytest integrations/vllm/tests/regression -m regression, from the tree root, in venv312.
#   usage: gate_a.sh TREE TAG [pytest args...]      logs: /workspace/a23b/logs/TAG.{log,xml,env}
#   Runs from the local store only: every row's fixtures were prefetched and /root/r2ro.env deleted before this starts.
T=$1; TAG=$2; shift 2
L=/workspace/a23b/logs; mkdir -p $L /workspace/a23b/scratch/$TAG
cd "$T" || exit 3
[ -e /root/r2ro.env ] && { echo "refusing: /root/r2ro.env present"; exit 4; }
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src
export HF_HOME=/workspace/hf
export PYTHONDONTWRITEBYTECODE=1
export RESEARCH_STORE=/workspace/research/store
export RESEARCH_STORE_CONFIG=$T/tools/research/store.pod.toml
export VERITY_REGRESSION_SCRATCH=/workspace/a23b/scratch/$TAG
export VERITY_REGRESSION=1
export VERITY_REGRESSION_TIERS=T0,T1
unset VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITY_REGRESSION_ENGINE VERITY_REGRESSION_ORACLE VERITOR_REPO
env | sort | grep -E '^(PATH|PYTHON|HF_|OMP_|VERITY|VERITOR|RESEARCH|CUDA|TORCH|VLLM|TRITON)' > $L/$TAG.env
echo "start $(date -u +%FT%TZ) tree $T"
python -m pytest integrations/vllm/tests/regression -m regression -ra -o junit_family=xunit1 --junitxml=$L/$TAG.xml "$@" > $L/$TAG.log 2>&1
rc=$?
echo "exit $rc $(date -u +%FT%TZ)"
echo "exit $rc $(date -u +%FT%TZ)" >> $L/$TAG.log
