#!/usr/bin/env bash
# verify-night: build the modified-SP1 (TC_DOT chip) verifier host, CPU only (sp1-tcdot handoff 20260924T0655Z).
# Source: `git archive 572018a3 backends/sp1` (lane/sp1-tcdot) -> /workspace/tcdot-src. build_fork.sh clones upstream sp1 v6.4.0
# (f66b4bff5), applies sp1-patches/0001-0005 and refuses unless the tree is FORK_TREE; SKIP_SERVER=1 (no CUDA server).
set -uo pipefail
export PATH=$HOME/.sp1/bin:$HOME/.cargo/bin:$PATH
O=/workspace/verify-night; H=/workspace/tcdot-verify/target/release/verity-tcdot-host
{
echo "=== [$(date -u +%H:%M:%S)] build_fork"
cd /workspace/tcdot-src && SKIP_SERVER=1 SP1_TCDOT_ROOT=/workspace/tcdot-verify bash backends/sp1/tcdot/build_fork.sh 2>&1 | tail -25
echo "fork_rc=${PIPESTATUS[0]}"
cd /workspace/tcdot-src/backends/sp1/tcdot
echo "=== [$(date -u +%H:%M:%S)] host"
VERITY_TCDOT_FORK_HEAD=$(git -C sp1 rev-parse HEAD) CARGO_TARGET_DIR=/workspace/tcdot-verify/target \
  cargo build --release --locked -p verity-tcdot-host 2>&1 | grep -v -E "^\s+(Compiling|Downloaded|Downloading) " | tail -15
echo "build_rc=${PIPESTATUS[0]}"
echo "=== [$(date -u +%H:%M:%S)] info"
SP1_PROVER=cpu RUST_LOG=error $H info 2>/dev/null | grep '^{'
sha256sum $H
echo "=== [$(date -u +%H:%M:%S)] done"
} > $O/tcdot-build.out 2>&1
