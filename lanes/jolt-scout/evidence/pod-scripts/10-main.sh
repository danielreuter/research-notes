#!/usr/bin/env bash
# jolt-scout: current a16z/jolt main (CPU prover, Dory/BN254 default). Build + run sha2-chain; build jolt-prover harness.
set -uo pipefail
W=/workspace/jolt-scout; cd $W/jolt; source $HOME/.cargo/env
L=$W/10-main.log; exec > >(tee -a $L) 2>&1
echo "REV $(git rev-parse HEAD)"; export CARGO_TARGET_DIR=$W/target-main
t0=$(date +%s); /usr/bin/time -v cargo build --release -p sha2-chain 2>&1 | tail -25; echo "BUILD_SHA2CHAIN $(( $(date +%s)-t0 ))s"
for i in 1 2; do
  echo "== sha2-chain run $i"; RUST_LOG=info /usr/bin/time -v $CARGO_TARGET_DIR/release/sha2-chain 2>&1 | grep -v '^\s*$' | tail -40
done
t0=$(date +%s); cargo build --release -p jolt-prover --features profiling 2>&1 | tail -3; echo "BUILD_PROVER $(( $(date +%s)-t0 ))s"
$CARGO_TARGET_DIR/release/jolt-prover benchmark --help; $CARGO_TARGET_DIR/release/jolt-prover profile --help
echo MAIN_DONE
