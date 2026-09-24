#!/usr/bin/env bash
# agkr-nvf4 profile: 05_profile.py (bench_result + sync timers) on the dev tree /workspace/src at VUS (default 4096).
# Warm Triton cache (~/.triton), so it is not a timing record; the per-phase split is what it is for.
set -uo pipefail
source /workspace/env.sh
VUS=${1:-4096}; REPS=${2:-2}; TAG=${3:-p}
O=/workspace/agkr-nvf4/prof-$TAG; rm -rf $O; mkdir -p $O
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
$PY -m gpu.nvf4.circuit export --out $O/stmt > /dev/null
echo "== profile vus=$VUS reps=$REPS $(date -u +%H:%M:%S)"
ENTRY=/workspace/agkr-nvf4/pod-scripts/05_profile.py
[[ $TAG == t* ]] && ENTRY=bench_result.py          # timing only: no sync timers
RESEARCH_RUN_DIR=$O/run $PY $ENTRY $O/stmt --relation fp4-nvf4 --vus $VUS --reps $REPS \
    --warmup 1 --verifier /workspace/bin/verity-gkr-verify --threads 13 > $O/prof.log 2>&1
echo "rc=$?"
grep -E '^\{"rep"|profile_rep|t_total|Error|error' $O/prof.log | cut -c1-3000 | tail -12
echo "== done $(date -u +%H:%M:%S)"
