#!/usr/bin/env bash
# Reproduce one sp1-op-bench number (edf1fb4) on the pod with the fp8 fork (3510b39a7) and its forked sp1-gpu-server:
# the batch2048 TC_DOT row of results/gpu-run/gpu_zerocopy.csv (n = 16384, k = 2048 dots: 2^25 fp8 MACs, core proof, cuda prover;
# RTX 4090 reference: 21033942 cycles, 66 shards, prove_s 40.59).
set -euo pipefail
W=/workspace/sp1-tcdot
export PATH="$HOME/.sp1/bin:$HOME/.cargo/bin:/usr/local/cuda/bin:/usr/local/go/bin:$PATH"
stamp() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }
mkdir -p "$W/sp1-op-bench"
cd "$W/sp1-op-bench"
[ -f Cargo.toml ] || tar -xzf "$W/sp1-op-bench-edf1fb4.tgz"
stamp "build op-bench host (cuda)"
cargo build --release -p op-bench-host --features cuda 2>&1 | grep -v -E "^\s+(Compiling|Downloaded|Downloading) " | tail -5
stamp "prove batch2048 on cuda"
./target/release/op-bench-host sweep --mode prove --cuda --ops batch-dot --dtypes fp8e4m3 --impls tc-pre \
  --ns 16384 --ks 2048 --out "$W/repro_batch2048.csv" 2>&1 | tail -15
cat "$W/repro_batch2048.csv"
stamp "done"
