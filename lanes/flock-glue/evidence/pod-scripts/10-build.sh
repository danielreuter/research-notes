#!/usr/bin/env bash
# flock-glue: patch the flock tree from 00-setup.sh (patch_ffi.py, flock-bench verity_unit.rs + glue additions,
# gen_test.py -> tests/gpu_glue.rs), export the three unit netlists (with COUT), build the GPU test binary.
set -uxo pipefail
I=${INPUTS:-$RESEARCH_RUN_DIR/inputs}
W=/workspace/flock-glue; F=$W/flock
source $HOME/.cargo/env
export PATH=/usr/local/cuda-13.3/bin:$PATH NVCC=/usr/local/cuda-13.3/bin/nvcc
cd $F
# re-apply from pristine each time (the patchers are idempotent only on first application)
git checkout -q cuda-ghash/prove_ffi.cu cuda-ghash/challenger.hpp
python3 $I/patch_ffi.py $I || exit 1
P=crates/flock-prover
cat $I/verity_unit.rs $I/verity_unit_glue.rs > $P/src/r1cs_hashes/verity_unit.rs
grep -q 'pub mod verity_unit;' $P/src/r1cs_hashes.rs || printf '\npub mod verity_unit;\n' >> $P/src/r1cs_hashes.rs
python3 $I/gen_test.py $I || exit 1
mkdir -p $W/net
for pipe in ampere_bf16 hopper_bf16 hopper_e4m3; do
  (cd $I && python3 export_unit.py $pipe $W/net/net-$pipe.txt 64) || exit 1
done
cargo test -p flock-cuda-ffi --release --features gpu --test gpu_glue --test gpu_roundtrip --no-run 2>&1 | grep -vE '^\s+Compiling' | tail -40
ls -t target/release/deps/gpu_glue-* | grep -v '\.d$' | head -1
git diff --stat
