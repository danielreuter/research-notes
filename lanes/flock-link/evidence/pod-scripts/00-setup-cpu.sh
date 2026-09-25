#!/usr/bin/env bash
# flock-live: rust + flock b684b12 clone + warm release build of flock-prover on a CPU pod.
set -uxo pipefail
W=/workspace/flock-link; mkdir -p $W
command -v cc >/dev/null || { apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq build-essential pkg-config >/dev/null; }
[ -x $HOME/.cargo/bin/cargo ] || curl -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain stable >/dev/null
source $HOME/.cargo/env; rustc --version
cd $W; [ -d flock ] || git clone -q https://github.com/succinctlabs/flock.git
cd flock && git checkout -q b684b12 && git log --oneline -1
lscpu | grep -E 'Model name|^CPU\(s\)|Flags' | sed 's/Flags:.*\(avx512f\).*/avx512f present/' | head -5
cat /sys/fs/cgroup/cpu.max 2>/dev/null
time cargo build --release -p flock-prover -j $(nproc) 2>&1 | tail -3
