#!/usr/bin/env bash
# verify-night: build the SP1 verifier host (CPU, relation-bare) from lane/sp1-table @ b5e1ed5f (git archive -> /workspace/sp1src),
# as the sp1-table handoff 20260924T0632Z says: sp1up v6.4.0, cargo build --release --locked -p veritor-zk-host --features relation-bare,
# then `info` (expect elf_sha256 cffc5eff..., vk_hash 0x000503d6...). Log: /workspace/verify-night/sp1-build.out
set -uo pipefail
export DEBIAN_FRONTEND=noninteractive
export PATH="$HOME/.sp1/bin:$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
export CARGO_TARGET_DIR=/workspace/sp1-target-relation-bare
S=/workspace/sp1src/backends/sp1
{
echo "=== [$(date -u +%H:%M:%S)] apt"
apt-get update -qq && apt-get install -y -qq --no-install-recommends build-essential pkg-config libssl-dev clang libclang-dev cmake \
  protobuf-compiler libprotobuf-dev git curl ca-certificates jq >/dev/null
echo "=== [$(date -u +%H:%M:%S)] rustup + sp1up v6.4.0"
command -v rustup >/dev/null || curl -fsSL https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain stable >/dev/null
rustup toolchain install stable --profile minimal >/dev/null
if ! cargo prove --version 2>/dev/null | grep -q "6.4.0"; then
  curl -fsSL https://sp1up.succinct.xyz | bash >/dev/null
  "$HOME/.sp1/bin/sp1up" --version v6.4.0
fi
cargo prove --version; rustup toolchain list | grep succinct
echo "=== [$(date -u +%H:%M:%S)] build"
cd $S && cargo build --release --locked -p veritor-zk-host --features relation-bare 2>&1 | grep -v -E "^\s+(Compiling|Downloaded|Downloading) " | tail -20
echo "build rc=${PIPESTATUS[0]}"
echo "=== [$(date -u +%H:%M:%S)] info"
SP1_PROVER=cpu $CARGO_TARGET_DIR/release/veritor-zk-host info 2>/dev/null | tail -3
sha256sum $CARGO_TARGET_DIR/release/veritor-zk-host
echo "=== [$(date -u +%H:%M:%S)] done"
} > /workspace/verify-night/sp1-build.out 2>&1
