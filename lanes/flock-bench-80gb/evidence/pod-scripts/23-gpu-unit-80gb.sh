#!/usr/bin/env bash
# flock-bench-80gb: run flock-bench's 22-gpu-unit.sh (census unit on patched Flock-CUDA, host-uploaded witness) on this
# pod: its files are shipped unchanged (from lanes/flock-bench/evidence/pod-scripts/) into their expected checkout path,
# a copy of this lane's flock tree (build.rs already patched to sm_$SM + cuda-13.3 lib64 by 20-gpu.sh).
set -x
mkdir -p /workspace/flock-bench
[ -d /workspace/flock-bench/flock ] || cp -a /workspace/flock-bench-80gb/flock /workspace/flock-bench/flock
grep -n "gencode" /workspace/flock-bench/flock/crates/flock-cuda-ffi/build.rs
export LD_LIBRARY_PATH=/usr/local/cuda-13.3/compat:/usr/local/cuda-13.3/lib64:${LD_LIBRARY_PATH:-}
bash $RESEARCH_RUN_DIR/inputs/22-gpu-unit.sh
