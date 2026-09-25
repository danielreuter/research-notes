#!/usr/bin/env bash
# agkr-bound: the link's dense GF(2^128) check and u_t commitment, costed (21_eq_cpu.c on the CPU, 21_dense_gpu.py on the A100).
# research run ... --send 21_dense.sh --send 21_eq_cpu.c --send 21_dense_gpu.py -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/21_dense.sh"'
set -uo pipefail
HERE=$(pwd)
ROOT=$(cd ../.. && pwd)
export PYTHONPATH="$ROOT/packages/verity/src:$ROOT/backends/numerical/python:$ROOT/tools/research/src:$ROOT:$HERE"
export PATH="/workspace/venv312/bin:/usr/local/cuda/bin:$PATH"
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
NT=$([ "$Q" = max ] && nproc || echo $(( Q / PER )))
export OMP_NUM_THREADS=$NT MKL_NUM_THREADS=$NT OPENBLAS_NUM_THREADS=$NT
IN=$RESEARCH_RUN_DIR/inputs
N=${N:-201326592}
echo "== CPU ($(lscpu | grep 'Model name' | sed 's/  */ /g'), $(date -u +%H:%M:%S))"
gcc -O3 -march=native -fopenmp $IN/21_eq_cpu.c -o $RESEARCH_RUN_DIR/eq_cpu || { echo "gcc failed"; exit 1; }
for T in $NT 1; do OMP_NUM_THREADS=$T $RESEARCH_RUN_DIR/eq_cpu $N; done
echo "== GPU ($(date -u +%H:%M:%S))"
/workspace/venv312/bin/python $IN/21_dense_gpu.py $N 3
echo "== done ($(date -u +%H:%M:%S))"
