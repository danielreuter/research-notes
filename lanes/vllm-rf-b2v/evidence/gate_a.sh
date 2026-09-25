#!/bin/bash
# gate (a): VERITY_REGRESSION=1 VERITY_REGRESSION_TIERS=T0,T1 python -m pytest integrations/vllm/tests/regression -m regression, from the
#   tree root, in venv312.  Lane a1's baseline-gate_a.sh with the key line removed (the fixtures are prefetched into the pod store and the
#   key deleted before this runs), tiers T0,T1, and the log/scratch directories moved to /workspace/out/gates.
#   usage: gate_a.sh TREE TAG [pytest args...]      logs: /workspace/out/gates/TAG.{log,xml,env,status}
T=$1; TAG=$2; shift 2
L=/workspace/out/gates; mkdir -p $L $L/scratch/$TAG
cd "$T" || exit 3
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
export PATH=/workspace/venv312/bin:$PATH
export CUDA_VISIBLE_DEVICES=""       # b2v: run on a GPU pod (no CPU pod available); GPUs hidden as on a CPU pod
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src
export HF_HOME=/workspace/hf
export PYTHONDONTWRITEBYTECODE=1
export RESEARCH_STORE=/workspace/research/store
export RESEARCH_STORE_CONFIG=$T/tools/research/store.pod.toml
export VERITY_REGRESSION_SCRATCH=$L/scratch/$TAG
export VERITY_REGRESSION=1 VERITY_REGRESSION_TIERS=T0,T1
unset VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITY_REGRESSION_ENGINE VERITY_REGRESSION_ORACLE VERITOR_REPO
env | sort | grep -E '^(PATH|PYTHON|HF_|OMP_|VERITY|VERITOR|RESEARCH|CUDA|TORCH|VLLM|TRITON|AWS)' > $L/$TAG.env
echo "start $(date -u +%FT%TZ) tree $T sha $(python -c 'import json,sys; print(json.load(open(sys.argv[1]))["commit"])' $T/.research-source.json 2>/dev/null || cat $T/.b2v-tree) key_file_present=$([ -e /root/r2ro.env ] && echo yes || echo no) args: $*" > $L/$TAG.status
python -m pytest integrations/vllm/tests/regression -m regression -ra -o junit_family=xunit1 --junitxml=$L/$TAG.xml "$@" > $L/$TAG.log 2>&1
rc=$?
echo "exit $rc $(date -u +%FT%TZ)" >> $L/$TAG.status
echo "exit $rc $(date -u +%FT%TZ)" >> $L/$TAG.log
