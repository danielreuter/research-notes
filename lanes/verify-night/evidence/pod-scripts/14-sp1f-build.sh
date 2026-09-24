#!/usr/bin/env bash
# verify-night: build the stock-SP1 verifier host (CPU, relation-bare) of lane/sp1-formats @ 2581406f (handoff 20260924T0712Z):
# `git archive 2581406f backends/sp1` -> /workspace/sp1f-src, FRESH target dir (sp1_build's rerun-if-changed paths are absolute),
# then `info` (expect elf_sha256 504423b7..., vk_hash 0x00a8ed87...). Toolchain as 07-sp1-build.sh (already installed).
set -uo pipefail
export PATH="$HOME/.sp1/bin:$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
export CARGO_TARGET_DIR=/workspace/sp1f-target
{
echo "=== [$(date -u +%H:%M:%S)] build 2581406f"
cd /workspace/sp1f-src/backends/sp1 && cargo build --release --locked -p veritor-zk-host --features relation-bare 2>&1 \
  | grep -v -E "^\s+(Compiling|Downloaded|Downloading) " | tail -20
echo "build rc=${PIPESTATUS[0]}"
echo "=== [$(date -u +%H:%M:%S)] info"
SP1_PROVER=cpu $CARGO_TARGET_DIR/release/veritor-zk-host info 2>/dev/null | grep '^{'
sha256sum $CARGO_TARGET_DIR/release/veritor-zk-host
echo "=== [$(date -u +%H:%M:%S)] done"
} > /workspace/verify-night/sp1f-build.out 2>&1
