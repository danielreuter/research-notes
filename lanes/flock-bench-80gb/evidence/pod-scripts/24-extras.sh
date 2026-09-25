#!/usr/bin/env bash
# flock-bench-80gb: (1) clmad_peak x2 + bench_f128 in a recorded run (forward-compat driver when < 580);
# (2) cross-check: flock-bench's own CPU unit harness (13-unit-bench.sh, shipped unchanged) at 4096 VUs on this host,
#     in its checkout path /workspace/flock-bench/flock (a copy of this lane's tree made by 23-gpu-unit-80gb.sh).
set -x
TAG=${TAG:-sm90}
C13=/usr/local/cuda-13.3
DRV=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1 | cut -d. -f1)
[ "$DRV" -lt 580 ] && export LD_LIBRARY_PATH=$C13/compat:${LD_LIBRARY_PATH:-}
cd /workspace/flock-bench-80gb/flock/cuda-ghash
{ nvidia-smi --query-gpu=name,driver_version,clocks.max.sm,power.limit --format=csv; echo "LD_LIBRARY_PATH=${LD_LIBRARY_PATH:-}";
  $C13/bin/cuobjdump -sass clmad_peak.$TAG | grep -c CLMAD; ./clmad_peak.$TAG; ./clmad_peak.$TAG; ./bench_f128.$TAG; } 2>&1 | tee $RESEARCH_RUN_DIR/clmad-f128-$TAG.txt
[ "${XCHECK:-1}" = 1 ] || exit 0
mkdir -p /workspace/flock-bench
[ -d /workspace/flock-bench/flock ] || cp -a /workspace/flock-bench-80gb/flock /workspace/flock-bench/flock
bash $RESEARCH_RUN_DIR/inputs/13-unit-bench.sh
