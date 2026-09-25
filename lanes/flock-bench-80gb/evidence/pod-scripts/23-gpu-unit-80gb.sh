#!/usr/bin/env bash
# flock-bench-80gb: run flock-bench's 22-gpu-unit.sh (census unit on patched Flock-CUDA, host-uploaded witness) on this
# pod: its files are shipped unchanged (from lanes/flock-bench/evidence/pod-scripts/) into their expected checkout path,
# a copy of this lane's flock tree (build.rs already patched to sm_$SM + cuda-13.3 lib64 by 20-gpu.sh).
# Files shipped with an fb_ prefix (combined runs, where this lane's own verity_unit.rs shares inputs/) are unpacked
# into $RESEARCH_RUN_DIR/fb/inputs and 22 runs with RESEARCH_RUN_DIR=$RESEARCH_RUN_DIR/fb.
set -x
mkdir -p /workspace/flock-bench
[ -d /workspace/flock-bench/flock ] || cp -a /workspace/flock-bench-80gb/flock /workspace/flock-bench/flock
# the copied target caches flock-cuda-ffi's build script against the OLD tree's rerun-if-changed paths
rm -rf /workspace/flock-bench/flock/target/release/build/flock-cuda-ffi-*
grep -n "gencode" /workspace/flock-bench/flock/crates/flock-cuda-ffi/build.rs
export LD_LIBRARY_PATH=/usr/local/cuda-13.3/compat:/usr/local/cuda-13.3/lib64:${LD_LIBRARY_PATH:-}
if ls $RESEARCH_RUN_DIR/inputs/fb_* >/dev/null 2>&1; then
  mkdir -p $RESEARCH_RUN_DIR/fb/inputs
  for f in $RESEARCH_RUN_DIR/inputs/fb_*; do cp $f $RESEARCH_RUN_DIR/fb/inputs/$(basename $f | sed 's/^fb_//'); done
  RESEARCH_RUN_DIR=$RESEARCH_RUN_DIR/fb bash $RESEARCH_RUN_DIR/fb/inputs/22-gpu-unit.sh
else
  bash $RESEARCH_RUN_DIR/inputs/22-gpu-unit.sh
fi
