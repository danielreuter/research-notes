#!/usr/bin/env bash
# Build the scratch cycle/prove harness (evidence/cyc) against the synced common crate; cuda so it reuses the host's deps.
set -euo pipefail
export PATH="$HOME/.sp1/bin:$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
export CARGO_TARGET_DIR=/workspace/sp1-target
cd /workspace/sp1-formats/cyc
cargo build --release -p sp1f-cyc-script --features cuda 2>&1 | grep -v -E "^\s+(Compiling|Downloaded|Downloading) " | tail -20
ls -la $CARGO_TARGET_DIR/release/sp1f-cyc-script
