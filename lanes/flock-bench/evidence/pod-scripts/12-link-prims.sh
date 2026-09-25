#!/usr/bin/env bash
# flock-bench: time the §3.8 link's O(N) primitives (link_prims.rs) and flock's F128 field bench on the CPU pod.
set -uxo pipefail
W=/workspace/flock-bench; OUT=$W/out/link-$(date -u +%H%MZ); mkdir -p $OUT
source $HOME/.cargo/env
cd $W/flock
cp "$RESEARCH_RUN_DIR/inputs/link_prims.rs" crates/flock-prover/benches/link_prims.rs
grep -q 'name = "link_prims"' crates/flock-prover/Cargo.toml || printf '\n[[bench]]\nname = "link_prims"\nharness = false\n' >> crates/flock-prover/Cargo.toml
cargo bench --no-run -p flock-prover --bench link_prims --bench field 2>&1 | tail -3 || exit 1
BIN=$(ls -t target/release/deps/link_prims-* | grep -v '\.d$' | head -1)
RAYON_NUM_THREADS=$(nproc) LP_LOGS="${LP_LOGS:-22 24 26 27 28}" /usr/bin/time -v $BIN > $OUT/link-t$(nproc).out 2> $OUT/link-t$(nproc).err; echo rc=$?
RAYON_NUM_THREADS=1 LP_LOGS="22 24" LP_RUNS=2 $BIN > $OUT/link-t1.out 2> $OUT/link-t1.err; echo rc=$?
cat $OUT/link-*.out
RAYON_NUM_THREADS=$(nproc) timeout 600 cargo bench -p flock-prover --bench field > $OUT/field.txt 2>&1; echo rc=$?
grep -i -E "mul|GMul|ns" $OUT/field.txt | head -40
cp -r $OUT "$RESEARCH_RUN_DIR/out" 2>/dev/null || true
