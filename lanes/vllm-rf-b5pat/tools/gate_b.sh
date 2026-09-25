#!/bin/bash
# gate (b): OMP_NUM_THREADS=3 python -m pytest integrations/vllm/tests -ra -n 12 --dist loadfile, from the tree root, in venv312
# (a23b's gate_b.sh, logs moved).  Runs on a copy of TREE (/workspace/trees/TAG) so the shipped tree stays as shipped.
#   usage: gate_b.sh TREE TAG [pytest args...]      logs: /workspace/b5pat/logs/TAG.{log,xml,env,rss}
SRC=$1; TAG=$2; shift 2
L=/workspace/b5pat/logs; mkdir -p $L /workspace/trees
T=/workspace/trees/$TAG
rm -rf "$T" && cp -a "$SRC" "$T" || exit 3
cd "$T" || exit 3
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src
export HF_HOME=/workspace/hf
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=3
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO
env | sort | grep -E '^(PATH|PYTHON|HF_|OMP_|MKL_|VERITY|VERITOR|RESEARCH|CUDA|TORCH|VLLM|TRITON)' > $L/$TAG.env
( while sleep 10; do echo "$(date -u +%FT%TZ) $(cat /sys/fs/cgroup/memory.current 2>/dev/null || cat /sys/fs/cgroup/memory/memory.usage_in_bytes 2>/dev/null) $(ps -eo rss= | awk '{s+=$1} END {print s*1024}')"; done ) > $L/$TAG.rss 2>&1 &
MON=$!
echo "start $(date -u +%FT%TZ) tree $SRC -> $T sha $(python -c 'import json,sys; print(json.load(open(sys.argv[1]))["commit"])' $SRC/.research-source.json 2>/dev/null)"
python -m pytest integrations/vllm/tests -ra -n 12 --dist loadfile -p no:cacheprovider -o junit_family=xunit1 --junitxml=$L/$TAG.xml "$@" > $L/$TAG.log 2>&1
rc=$?
kill $MON 2>/dev/null
echo "exit $rc $(date -u +%FT%TZ)"
echo "exit $rc $(date -u +%FT%TZ)" >> $L/$TAG.log
exit $rc
