#!/usr/bin/env bash
# jolt-scout: a16z/jolt 4c259be477 (2025-07-02), the last main commit whose MSM dispatch calls ICICLE.
# PCS there is HyperKZG over BN254 (the SDK switched to Dory on 2025-07-30, after ICICLE dispatch was deleted in #779;
# the one side-branch commit with both, 16763aac48, hard-codes use_icicle=false in Dory's MSMs).
# Builds sha2-chain CPU-only and with --features icicle (ICICLE CUDA backend, from ingonyama-zk/icicle-jolt 2441eba),
# runs both, samples the GPU during the icicle run.
set -uo pipefail
W=/workspace/jolt-scout; cd $W/jolt-icicle; source $HOME/.cargo/env
export PATH=/usr/local/cuda/bin:$PATH CUDACXX=/usr/local/cuda/bin/nvcc CUDA_HOME=/usr/local/cuda
L=$W/20-icicle.log; exec > >(tee -a $L) 2>&1
echo "REV $(git rev-parse HEAD) toolchain $(rustup show active-toolchain)"
export CARGO_TARGET_DIR=$W/target-icicle-cpu
t0=$(date +%s); cargo build --release -p sha2-chain 2>&1 | tail -5; echo "BUILD_CPU rc=${PIPESTATUS[0]} $(( $(date +%s)-t0 ))s"
export CARGO_TARGET_DIR=$W/target-icicle-gpu
t0=$(date +%s); cargo build --release -p sha2-chain --features jolt-sdk/icicle 2>&1 | tail -40; echo "BUILD_GPU rc=${PIPESTATUS[0]} $(( $(date +%s)-t0 ))s"
BK=$(find $W/target-icicle-gpu -type d -path '*lib/backend' 2>/dev/null | head -1); echo "ICICLE_BACKEND_DIR=$BK"; ls -R "$BK" 2>/dev/null | head -20
for i in 1 2; do
  echo "== CPU run $i"; RUST_LOG=info $W/target-icicle-cpu/release/sha2-chain 2>&1 | tail -8
done
for i in 1 2; do
  echo "== ICICLE run $i"
  nvidia-smi --query-gpu=timestamp,utilization.gpu,memory.used --format=csv,noheader -lms 200 > $W/20-icicle-gpu-sample-$i.csv &
  S=$!
  ICICLE_BACKEND_INSTALL_DIR=$BK RUST_LOG=info $W/target-icicle-gpu/release/sha2-chain 2>&1 | tail -8
  kill $S; echo "GPU max util: $(cut -d, -f2 $W/20-icicle-gpu-sample-$i.csv | tr -dc '0-9\n' | sort -n | tail -1)%  max mem: $(cut -d, -f3 $W/20-icicle-gpu-sample-$i.csv | tr -dc '0-9\n' | sort -n | tail -1) MiB"
done
echo ICICLE_DONE
