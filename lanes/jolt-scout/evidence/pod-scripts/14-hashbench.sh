#!/usr/bin/env bash
# jolt-scout: main's examples/hash-bench (cycle markers for SHA-256 / BLAKE3 / Keccak / Blake2b inlines and reference
# crates at several input sizes), to price a keyed-BLAKE3 frame-v3 row leaf against the SHA-256 one in a Jolt guest.
set -uo pipefail
W=/workspace/jolt-scout; cd $W/jolt; source $HOME/.cargo/env
export CARGO_TARGET_DIR=$W/target-main
L=$W/14-hashbench.log; exec > >(tee -a $L) 2>&1
exec 9>$W/timing.lock; flock 9; echo "LOCK $(date -u +%H:%M:%SZ)"
t0=$(date +%s); cargo build --release -p hash-bench 2>&1 | grep -E '^error|Finished'; echo "BUILD rc=${PIPESTATUS[0]} $(( $(date +%s)-t0 ))s"
RUST_LOG=info $CARGO_TARGET_DIR/release/hash-bench 2>&1 | grep -E '"(sha|blake|keccak)[^"]*"|Prover runtime|valid|panick' | sed 's/.*tracer::emulator::cpu[^:]*: //' | cut -c1-200
echo HASHBENCH_DONE
