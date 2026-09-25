#!/usr/bin/env bash
# flock-128: Rust + flock b684b12 on a CPU pod, bench profile (thin LTO) build of the verity harnesses
# (flock-bench-80gb unit_shape.rs + verity_unit.rs, flock-bench verity_shape.rs; shipped unchanged as inputs).
set -uxo pipefail
W=/workspace/flock-128; mkdir -p $W/out $W/net; cd $W
FLOCK_REV=${FLOCK_REV:-b684b12}
lscpu | grep -E 'Model name|^CPU\(s\)|Thread'; nproc; cat /sys/fs/cgroup/cpu.max 2>/dev/null
grep -o -w -E 'avx512f|vpclmulqdq|pclmulqdq|gfni' /proc/cpuinfo | sort | uniq -c; free -g
[ -x /usr/bin/time ] || { apt-get update -qq && apt-get install -y -qq time; }
command -v git >/dev/null || { apt-get update -qq && apt-get install -y -qq git build-essential pkg-config; }
command -v cc >/dev/null || apt-get install -y -qq build-essential
if ! command -v cargo >/dev/null; then
  [ -x $HOME/.cargo/bin/cargo ] || curl -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain stable
fi
source $HOME/.cargo/env; rustc --version
[ -d flock ] || git clone -q https://github.com/succinctlabs/flock
cd flock && git fetch -q origin && git checkout -q $FLOCK_REV && git log --oneline -1
I=$RESEARCH_RUN_DIR/inputs
cp $I/verity_unit.rs crates/flock-prover/src/r1cs_hashes/verity_unit.rs
grep -q 'pub mod verity_unit;' crates/flock-prover/src/r1cs_hashes.rs || echo 'pub mod verity_unit;' >> crates/flock-prover/src/r1cs_hashes.rs
cp $I/unit_shape.rs crates/flock-prover/benches/unit_shape.rs
cp $I/verity_shape.rs crates/flock-prover/benches/verity_shape.rs
for b in unit_shape verity_shape; do
  grep -q "name = \"$b\"" crates/flock-prover/Cargo.toml || printf '\n[[bench]]\nname = "%s"\nharness = false\n' $b >> crates/flock-prover/Cargo.toml
done
git -C $W/flock rev-parse HEAD > $W/out/flock-rev.txt
time cargo bench --no-run -p flock-prover --bench unit_shape --bench verity_shape -j $(nproc) 2>&1 | grep -E '^error|-->|Finished|Executable' | head -40
