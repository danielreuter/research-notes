#!/usr/bin/env bash
# verify-night: build a stock-SP1 verifier host (CPU, relation-bare) of one commit, as 14-sp1f-build.sh does for 2581406f:
#   REV=<commit> bash 18-sp1-build-rev.sh
# Source: `git archive $REV backends/sp1` (shipped from the laptop) at /workspace/sp1-src-$REV; FRESH target dir
# /workspace/sp1-target-$REV (sp1_build's rerun-if-changed paths are absolute: a reused target dir can embed a stale guest ELF).
# Then `info` (elf_sha256, vk_hash) and the host's sha256. Log: /workspace/verify-night/sp1-build-$REV.out
set -uo pipefail
export PATH="$HOME/.sp1/bin:$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
REV=${REV:?REV}; export CARGO_TARGET_DIR=/workspace/sp1-target-$REV
{
echo "=== [$(date -u +%H:%M:%S)] build $REV"
cd /workspace/sp1-src-$REV/backends/sp1 && cargo build --release --locked -p veritor-zk-host --features relation-bare 2>&1 \
  | grep -v -E "^\s+(Compiling|Downloaded|Downloading) " | tail -20
echo "build rc=${PIPESTATUS[0]}"
echo "=== [$(date -u +%H:%M:%S)] info"
SP1_PROVER=cpu $CARGO_TARGET_DIR/release/veritor-zk-host info 2>/dev/null | grep '^{'
sha256sum $CARGO_TARGET_DIR/release/veritor-zk-host
echo "=== [$(date -u +%H:%M:%S)] done"
} > /workspace/verify-night/sp1-build-$REV.out 2>&1
