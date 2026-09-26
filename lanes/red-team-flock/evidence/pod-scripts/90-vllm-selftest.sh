#!/usr/bin/env bash
# red-team-flock: flock-vllm-block/v1 at ff1c1e3f, CPU only: build flock-vllm-v1, run vllm_block's Rust tests against the core
# vectors, and the CPU selftest at 8/64 VUs on instances I generated (verity_flock.instances --scheme vllm-v1, fp8-hopper).
set -uxo pipefail
REPO=$(pwd); I=$RESEARCH_RUN_DIR/inputs; O=$RESEARCH_RUN_DIR/out; mkdir -p $O
MODE=build GPU=0 bash backends/flock/pod/20-gpu-link.sh > $O/build.log 2>&1 || { tail -30 $O/build.log; exit 1; }
source $HOME/.cargo/env
F=/workspace/flock-gpu-link/flock; TH=$(nproc)
(cd $F && cargo build --release -p flock-live --bin flock-vllm-v1 -j $TH) >> $O/build.log 2>&1 || { tail -40 $O/build.log; exit 1; }
B=$F/target/release/flock-vllm-v1; sha256sum $B | tee $O/binary.sha256
(cd $F && VLLM_V1_VECTORS=$REPO/packages/verity/src/verity/commitments/vllm_v1/vectors.json cargo test --release -p flock-live --lib vllm_block -j $TH 2>&1 | tail -15) | tee $O/rust-tests.txt
for n in 8 64; do
  $B selftest --instances $I/self-$n.bin --netlist $I/net-fp8-hopper.txt > $O/selftest-cpu-$n.txt 2>&1; grep -h 'SELFTEST\|"pass":false\|panicked' $O/selftest-cpu-$n.txt | cut -c1-300
done
true
