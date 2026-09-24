#!/bin/bash
# gate (b): python -m pytest integrations/vllm/tests, from the tree root, in the bootstrap's venv312.
#   lane a1's baseline-gate_b.sh with the log directory moved to /workspace/out/gates.
#   usage: gate_b.sh TREE TAG [pytest args...]      logs: /workspace/out/gates/TAG.{log,xml,env,rss}
T=$1; TAG=$2; shift 2
L=/workspace/out/gates; mkdir -p $L
cd "$T" || exit 3
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src
export HF_HOME=/workspace/hf
export PYTHONDONTWRITEBYTECODE=1
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO
env | sort | grep -E '^(PATH|PYTHON|HF_|OMP_|MKL_|VERITY|VERITOR|RESEARCH|CUDA|TORCH|VLLM|TRITON)' > $L/$TAG.env
( while sleep 10; do echo "$(date -u +%FT%TZ) $(cat /sys/fs/cgroup/memory.current 2>/dev/null || cat /sys/fs/cgroup/memory/memory.usage_in_bytes 2>/dev/null) $(ps -eo rss= | awk '{s+=$1} END {print s*1024}')"; done ) > $L/$TAG.rss 2>&1 &
MON=$!
echo "start $(date -u +%FT%TZ) tree $T sha $(python -c 'import json,sys; print(json.load(open(sys.argv[1]))["commit"])' $T/.research-source.json 2>/dev/null)" > $L/$TAG.status
python -m pytest integrations/vllm/tests -ra -o junit_family=xunit1 --junitxml=$L/$TAG.xml "$@" > $L/$TAG.log 2>&1
rc=$?
kill $MON 2>/dev/null
echo "exit $rc $(date -u +%FT%TZ)" >> $L/$TAG.status
echo "exit $rc $(date -u +%FT%TZ)" >> $L/$TAG.log
