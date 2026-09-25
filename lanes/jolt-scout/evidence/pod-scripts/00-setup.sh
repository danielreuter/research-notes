#!/usr/bin/env bash
# jolt-scout pod setup: toolchain + a16z/jolt clone with worktrees for the three revisions scouted.
#   main      : current a16z/jolt main (Dory/BN254 or Akita; CPU prover)
#   icicle    : 4c259be477 (2025-07-02), the last main commit whose MSM dispatch still calls ICICLE (HyperKZG PCS)
#   pr1618    : head of a16z/jolt PR #1618 "Draft: CUDA kernels" (jolt-kernels CUDA backend)
set -uo pipefail
W=/workspace/jolt-scout; mkdir -p $W; cd $W
exec > >(tee -a $W/00-setup.log) 2>&1
t0=$(date +%s)
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq && apt-get install -y -qq build-essential clang libclang-dev pkg-config libssl-dev python3-pip git curl time >/dev/null
pip3 install -q 'cmake>=3.28' || true
cmake --version | head -1
if ! command -v rustup >/dev/null; then
  curl -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain stable >/dev/null
fi
source $HOME/.cargo/env
rustc --version
[ -d jolt ] || git clone -q --filter=blob:none https://github.com/a16z/jolt.git jolt
cd jolt
git fetch -q origin main 'pull/1618/head:pr1618'
git checkout -q origin/main
[ -d ../jolt-icicle ] || git worktree add -q ../jolt-icicle 4c259be477
[ -d ../jolt-pr1618 ] || git worktree add -q ../jolt-pr1618 pr1618
for d in $W/jolt $W/jolt-icicle $W/jolt-pr1618; do echo "REV $d $(git -C $d rev-parse HEAD) $(git -C $d log -1 --format=%cI)"; done
# install the pinned toolchains (each tree has its own rust-toolchain.toml)
for d in $W/jolt $W/jolt-icicle $W/jolt-pr1618; do (cd $d && rustup show active-toolchain || rustup toolchain install) ; done
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
lscpu | grep -E 'Model name|^CPU\(s\)'
echo "SETUP_DONE $(( $(date +%s) - t0 ))s"
