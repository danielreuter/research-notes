#!/usr/bin/env bash
# agkr-bound: 30_link_build.py on the R+leaf statement export 09 left (cwd backends/gkr); [REL=bf16-ampere LEAF=sha256].
# research run ... --send 30_link_build.sh --send 30_link_build.py -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/30_link_build.sh"'
set -uo pipefail
HERE=$(pwd)
ROOT=$(cd ../.. && pwd)
export PYTHONPATH="$ROOT/packages/verity/src:$ROOT/backends/numerical/python:$ROOT/tools/research/src:$ROOT:$HERE"
export PATH="/workspace/venv312/bin:$HOME/.cargo/bin:/usr/local/cuda/bin:$PATH"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
NT=$([ "$Q" = max ] && nproc || echo $(( Q / PER )))
export OMP_NUM_THREADS=$NT MKL_NUM_THREADS=$NT OPENBLAS_NUM_THREADS=$NT VY_CPU_THREADS=$NT
echo "commit ${RESEARCH_SOURCE_COMMIT:-?}; threads $NT; MALLOC_MMAP_MAX_=$MALLOC_MMAP_MAX_ ($(date -u +%H:%M:%S))"
export REL=${REL:-bf16-ampere} LEAF=${LEAF:-sha256}
O=/workspace/agkr-bound/link-build-$REL; rm -rf $O
/workspace/venv312/bin/python "$RESEARCH_RUN_DIR/inputs/30_link_build.py" /workspace/agkr-bound/commit/$REL-$LEAF/stmt $O 4096 $NT ${REPS:-3}
rc=$?
true
echo "rc=$rc ($(date -u +%H:%M:%S))"
exit $rc
