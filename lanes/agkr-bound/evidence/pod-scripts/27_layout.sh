#!/usr/bin/env bash
# agkr-bound: 27_layout.py on bf16-ampere+sha256 and fp8-hopper+blake3 (the statements export 09 left; cwd backends/gkr).
# research run ... --send 27_layout.sh --send 27_layout.py -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/27_layout.sh"'
set -uo pipefail
HERE=$(pwd)
ROOT=$(cd ../.. && pwd)
export PYTHONPATH="$ROOT/packages/verity/src:$ROOT/backends/numerical/python:$ROOT/tools/research/src:$ROOT:$HERE"
export PATH="/workspace/venv312/bin:$HOME/.cargo/bin:/usr/local/cuda/bin:$PATH"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
NT=$([ "$Q" = max ] && nproc || echo $(( Q / PER )))
export OMP_NUM_THREADS=$NT MKL_NUM_THREADS=$NT OPENBLAS_NUM_THREADS=$NT VY_CPU_THREADS=$NT
echo "commit ${RESEARCH_SOURCE_COMMIT:-?}; threads $NT ($(date -u +%H:%M:%S))"
rc=0
for c in bf16-ampere:sha256 fp8-hopper:blake3; do
    export REL=${c%%:*} LEAF=${c##*:}
    /workspace/venv312/bin/python "$RESEARCH_RUN_DIR/inputs/27_layout.py" /workspace/agkr-bound/commit/$REL-$LEAF/stmt \
        /workspace/agkr-bound/layout/$REL-$LEAF 4096 $NT || rc=1
done
echo "rc=$rc ($(date -u +%H:%M:%S))"
exit $rc
