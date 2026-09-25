#!/usr/bin/env bash
# flock-bench: toolchain + flock build on a CPU pod. Output under /workspace/flock-bench.
set -euxo pipefail
W=/workspace/flock-bench; mkdir -p $W; cd $W
FLOCK_REV=${FLOCK_REV:-b684b12}
if ! command -v cargo >/dev/null; then
  [ -x $HOME/.cargo/bin/cargo ] || curl -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain stable
fi
source $HOME/.cargo/env
rustc --version
[ -d flock ] || git clone -q https://github.com/succinctlabs/flock
cd flock && git fetch -q origin && git checkout -q $FLOCK_REV && git log --oneline -1
# harness (verity_shape) is shipped next to this script; register it as a no-harness bench
if [ -f "${RESEARCH_RUN_DIR:-/nonexistent}/inputs/verity_shape.rs" ]; then
  cp "$RESEARCH_RUN_DIR/inputs/verity_shape.rs" crates/flock-prover/benches/verity_shape.rs
fi
if [ -f crates/flock-prover/benches/verity_shape.rs ] && ! grep -q 'name = "verity_shape"' crates/flock-prover/Cargo.toml; then
  printf '\n[[bench]]\nname = "verity_shape"\nharness = false\n' >> crates/flock-prover/Cargo.toml
fi
NJ=$(nproc)
time cargo build --release -p flock-prover --benches -j $NJ
ls -la target/release/deps | grep -E 'verity_shape|blake3_proof|sha2_proof' | grep -v '\.d$' || true
