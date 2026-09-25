#!/usr/bin/env bash
# agkr-bound: 20_link_unit.py on the bf16-ampere R+sha256 statement export 09 left (cwd backends/gkr).
# research run ... --send 20_link_unit.sh --send 20_link_unit.py -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/20_link_unit.sh"'
set -uo pipefail
HERE=$(pwd)
ROOT=$(cd ../.. && pwd)
export PYTHONPATH="$ROOT/packages/verity/src:$ROOT/backends/numerical/python:$ROOT/tools/research/src:$ROOT:$HERE"
export PATH="/workspace/venv312/bin:$HOME/.cargo/bin:/usr/local/cuda/bin:$PATH"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
NT=$([ "$Q" = max ] && nproc || echo $(( Q / PER )))
export OMP_NUM_THREADS=$NT MKL_NUM_THREADS=$NT OPENBLAS_NUM_THREADS=$NT VY_CPU_THREADS=$NT
echo "commit ${RESEARCH_SOURCE_COMMIT:-?}; threads $NT ($(date -u +%H:%M:%S))"
O=/workspace/agkr-bound/link-unit; rm -rf $O
/workspace/venv312/bin/python "$RESEARCH_RUN_DIR/inputs/20_link_unit.py" /workspace/agkr-bound/commit/bf16-ampere-sha256/stmt $O \
    /workspace/bin/verity-gkr-verify-pinned 4096 $NT ${REPS:-3} 2>&1 | grep -v "^candidate"
echo "rc=${PIPESTATUS[0]} ($(date -u +%H:%M:%S))"
