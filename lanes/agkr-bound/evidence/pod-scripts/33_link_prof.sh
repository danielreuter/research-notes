#!/usr/bin/env bash
# agkr-bound: 33_link_prof.py (cwd backends/gkr).  research run ... --send 33_link_prof.sh --send 33_link_prof.py -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/33_link_prof.sh"'
set -uo pipefail
HERE=$(pwd); ROOT=$(cd ../.. && pwd)
export PYTHONPATH="$ROOT/packages/verity/src:$ROOT/backends/numerical/python:$ROOT:$HERE"
export PATH="/workspace/venv312/bin:/usr/local/cuda/bin:$PATH" MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
NT=$([ "$Q" = max ] && nproc || echo $(( Q / PER ))); export OMP_NUM_THREADS=$NT MKL_NUM_THREADS=$NT
echo "commit ${RESEARCH_SOURCE_COMMIT:-?}; threads $NT; MALLOC_MMAP_MAX_=$MALLOC_MMAP_MAX_ ($(date -u +%H:%M:%S))"
/workspace/venv312/bin/python "$RESEARCH_RUN_DIR/inputs/33_link_prof.py" ${REPS:-3}
echo "rc=$? ($(date -u +%H:%M:%S))"
