#!/usr/bin/env bash
# verify-night: build the modified-SP1 (TC_DOT chip) verifier host, CPU only (sp1-tcdot handoff 20260924T0655Z).
#   [REV=<commit> SRC=<dir> TGT=<cargo target dir>] bash 12-tcdot-build.sh      (defaults: 572018a3, /workspace/tcdot-src, .../target)
# Source: `git archive $REV backends/sp1` (lane/sp1-tcdot) -> $SRC. build_fork.sh clones upstream sp1 v6.4.0 (f66b4bff5),
# applies sp1-patches/0001-0005 and refuses unless the tree is FORK_TREE (reuses the checkout when HEAD already matches);
# SKIP_SERVER=1 (no CUDA server). OPERANDS=witness: the witness-operands arm (patches witness-operands/0007-0009, handoff
# 20260924T0841Z); FEATURES: host cargo features (stream-operands for that arm's guest).
set -uo pipefail
export PATH=$HOME/.sp1/bin:$HOME/.cargo/bin:$PATH
REV=${REV:-572018a3}; SRC=${SRC:-/workspace/tcdot-src}; TGT=${TGT:-/workspace/tcdot-verify/target}; FROOT=${FROOT:-/workspace/tcdot-verify}
O=/workspace/verify-night; H=$TGT/release/verity-tcdot-host
{
echo "=== [$(date -u +%H:%M:%S)] build_fork ($REV, $SRC, OPERANDS=${OPERANDS:-memory})"
cd $SRC && OPERANDS=${OPERANDS:-} SKIP_SERVER=1 SP1_TCDOT_ROOT=$FROOT bash backends/sp1/tcdot/build_fork.sh 2>&1 | tail -25
echo "fork_rc=${PIPESTATUS[0]}"
cd $SRC/backends/sp1/tcdot
echo "=== [$(date -u +%H:%M:%S)] host (features: ${FEATURES:-none})"
VERITY_TCDOT_FORK_HEAD=$(git -C sp1 rev-parse HEAD) CARGO_TARGET_DIR=$TGT \
  cargo build --release --locked -p verity-tcdot-host ${FEATURES:+--features $FEATURES} 2>&1 | grep -v -E "^\s+(Compiling|Downloaded|Downloading) " | tail -15
echo "build_rc=${PIPESTATUS[0]}"
echo "=== [$(date -u +%H:%M:%S)] info"
SP1_PROVER=cpu RUST_LOG=error $H info 2>/dev/null | grep '^{'
sha256sum $H
echo "=== [$(date -u +%H:%M:%S)] done"
} > $O/tcdot-build-$REV.out 2>&1
