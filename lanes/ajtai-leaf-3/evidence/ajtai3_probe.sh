#!/usr/bin/env bash
# lane ajtai-leaf-3: build the G1-fixed ligero-verify, then each Ajtai arm at --pipeline 4 with the chain-test encode chunk
# LIGERO_CHAIN_ENC_CHUNK in 16, 8 (first that fits wins; the result is bit-identical for every chunk), Rust batch per dump.
set -uo pipefail
IN="$RESEARCH_RUN_DIR/inputs"
BASE="$RESEARCH_RUN_DIR"
export PATH="$HOME/.cargo/bin:$PATH"
SRC=$(pwd)
( cd "$SRC/backends/ligero-verify" && CARGO_TARGET_DIR=/workspace/cargo-target cargo build --release 2>&1 | tail -1 \
  && cp /workspace/cargo-target/release/ligero-verify "$BASE/ligero-verify" )
sha256sum "$BASE/ligero-verify" | tee "$BASE/rv_sha256.txt"
ok=0
for arm in "$@"; do
  for ch in 16 8; do
    mkdir -p "$BASE/$arm-enc$ch"
    echo "=== $arm LIGERO_CHAIN_ENC_CHUNK=$ch"
    RESEARCH_RUN_DIR="$BASE/$arm-enc$ch" LIGERO_CHAIN_ENC_CHUNK=$ch RV_OVERRIDE="$BASE/ligero-verify" \
      bash "$IN/ajtai3_bench.sh" "$arm" 2>&1 | tail -30
    if grep -q '"batch_accepted": *true' "$BASE/$arm-enc$ch/bench/$arm/rust_batch.json" 2>/dev/null; then
      echo "=== $arm fits at enc chunk $ch"; break
    fi
    [ $ch -eq 8 ] && ok=1
  done
done
[ $ok -eq 0 ] && echo PROBE_OK || { echo PROBE_FAILED; exit 1; }
