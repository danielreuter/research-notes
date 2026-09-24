#!/usr/bin/env bash
# Native oracle: unit tests of the new modules, then every VU of the four frozen sets through the Rust arithmetic.
set -euo pipefail
export PATH="$HOME/.sp1/bin:$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
export CARGO_TARGET_DIR=/workspace/sp1-target
cd /workspace/src/backends/sp1
cargo test --release -p veritor-zk-common --lib -- groupsum tc_fp8 tc_hopper_bf16 nvfp4 2>&1 | grep -E "^test |test result"
cargo run --release -q -p veritor-zk-common --features relation-bare --example format_oracle -- \
  /workspace/sp1-formats/inst/fp8-ada.bin /workspace/sp1-formats/inst/fp8-hopper.bin \
  /workspace/sp1-formats/inst/bf16-hopper.bin /workspace/sp1-formats/inst/fp4-nvf4.bin
