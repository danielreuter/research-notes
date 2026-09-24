#!/usr/bin/env bash
# pod_bootstrap.sh's build / guest identity / install stages for the cuda,relation-bare host, without its install stages
# (its `cargo prove --version | grep 6.4.0` check never matches this cargo-prove, whose version line is
# "cargo-prove sp1 (f66b4bf ...)", so it reinstalls SP1 on every run, which stalls on a slow link).  The host's build-script
# fingerprints are removed first: sp1_build's rerun-if-changed paths are absolute, so a new source dir would otherwise
# keep the previous tree's guest.            build_bare.sh SRC_DIR
set -euo pipefail
SRC=$1
export PATH="$HOME/.sp1/bin:$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
export CARGO_TARGET_DIR=/workspace/sp1-target-cuda-relation-bare
BIN=/workspace/bin
mkdir -p "$BIN" "$CARGO_TARGET_DIR"
rm -rf "$CARGO_TARGET_DIR"/release/.fingerprint/veritor-zk-host-* "$CARGO_TARGET_DIR"/release/build/veritor-zk-host-*
echo "=== [$(date -u +%H:%M:%S)] build (source: $SRC)"
cd "$SRC/backends/sp1"
cargo prove --version
cargo build --release -p veritor-zk-host --features cuda,relation-bare 2>&1 | grep -v -E "^\s+(Compiling|Downloaded|Downloading) "
BUILT="$CARGO_TARGET_DIR/release/veritor-zk-host"
grep -h "built at" "$CARGO_TARGET_DIR"/release/build/veritor-zk-host-*/output || true
echo "=== [$(date -u +%H:%M:%S)] guest identity"
"$BUILT" info | grep '^{' | tail -1
install -m 0755 "$BUILT" "$BIN/veritor-zk-host-cuda-relation-bare"
sha256sum "$BIN/veritor-zk-host-cuda-relation-bare"
echo "=== [$(date -u +%H:%M:%S)] done"
