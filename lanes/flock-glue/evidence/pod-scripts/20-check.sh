#!/usr/bin/env bash
# flock-glue: correctness gate per pipeline: device witness == host reference (bit for bit), device-witness proof
# verifies, proof tampers and a planted NaN operand are rejected.  env: PIPES, CHECK_NVU (default 64)
set -uxo pipefail
export MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000
W=/workspace/flock-glue; F=$W/flock
export LD_LIBRARY_PATH=/usr/local/cuda-13.3/lib64:${LD_LIBRARY_PATH:-}
Q=$(awk '{ if ($1 != "max") printf "%d", $1 / $2; else print 16 }' /sys/fs/cgroup/cpu.max 2>/dev/null || echo 16)
export RAYON_NUM_THREADS=${RAYON_NUM_THREADS:-$Q}
BIN=$(ls -t $F/target/release/deps/gpu_glue-* | grep -v '\.d$' | head -1)
OUT=${RESEARCH_RUN_DIR:-$W/out}/check; mkdir -p $OUT
cd $F/crates/flock-cuda-ffi
for pipe in ${PIPES:-ampere_bf16 hopper_bf16 hopper_e4m3}; do
  VU_NETLIST=$W/net/net-$pipe.txt VU_NAME=$pipe VU_NVU=${CHECK_NVU:-64} $BIN --ignored --nocapture --exact glue_check > $OUT/$pipe.txt 2>&1
  echo "rc=$? $pipe"; grep -E "VSETUP|VCHECK|VNAN|VPLANT|panicked|FFI: mode|error" $OUT/$pipe.txt | head -20
done
