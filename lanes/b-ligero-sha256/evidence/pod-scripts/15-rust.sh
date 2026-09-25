#!/usr/bin/env bash
# b-ligero-sha256: rebuild /workspace/bin/ligero-verify from the synced tree (/workspace/src), cargo test, then the
# pinned batch verify (no --allow-any-system) of the +sha256 fixtures FIX_RUN wrote (10-pins-gates.sh).
IN=$(dirname "$0"); source "$IN/lib.sh"
export PATH="$HOME/.cargo/bin:$PATH" CARGO_TARGET_DIR=/workspace/cargo-target
cd /workspace/src/backends/ligero-verify
cargo build --release 2>&1 | tail -2 && cp $CARGO_TARGET_DIR/release/ligero-verify /workspace/bin/ && sha256sum /workspace/bin/ligero-verify
cargo test --release 2>&1 | grep -E "^test result|FAILED|panicked" | head -20
for d in /workspace/research/runs/${FIX_RUN:?}/fixtures/*; do
  /workspace/bin/ligero-verify system-digest --system $d/system.bin | head -c 300; echo
  /workspace/bin/ligero-verify batch --system $d/system.bin --dir $d --jobs 2 --threads 1 --target-bits 128 --json $d/rust_batch.json > $d/rust_batch.out 2>&1
  echo "$(basename $d) pinned batch rc=$? $(tail -n 1 $d/rust_batch.out | cut -c1-300)"
done
