#!/usr/bin/env bash
# agkr-bound: the stub link (tools/link_stub.py, k = 1) through the CUDA prover (15_link_gpu.py) at B units.
# research run ... --send 16_link_gpu.sh --send 15_link_gpu.py -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/16_link_gpu.sh"'
set -uo pipefail
PY=/workspace/venv312/bin/python
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
NT=$([ "$Q" = max ] && nproc || echo $(( Q / PER )))
export OMP_NUM_THREADS=$NT MKL_NUM_THREADS=$NT OPENBLAS_NUM_THREADS=$NT VY_CPU_THREADS=$NT
O=/workspace/agkr-bound/link/gpu-k${K:-1}
mkdir -p $O
$PY tools/link_stub.py --out $O --units 64 --k ${K:-1} | cut -c1-160
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
for B in ${BS:-4096 65536 393216}; do
  echo "== GPU stub link k=${K:-1} B=$B ($(date -u +%H:%M:%S))"
  $PY "$RESEARCH_RUN_DIR/inputs/15_link_gpu.py" $O $B 2 2>&1 | tail -4 | cut -c1-600
done
echo "== done ($(date -u +%H:%M:%S))"
