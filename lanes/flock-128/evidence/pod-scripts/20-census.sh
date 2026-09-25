#!/usr/bin/env bash
# flock-128: challenge-site census (site_census.rs) of one union proof per (net, N, profile); builds the bench first.
set -uxo pipefail
W=/workspace/flock-128; OUT=$W/out/census-$(date -u +%H%MZ); mkdir -p $OUT $W/net
source $HOME/.cargo/env
cp $RESEARCH_RUN_DIR/inputs/unit-*.netlist $W/net/ 2>/dev/null || true
cd $W/flock
cp $RESEARCH_RUN_DIR/inputs/site_census.rs crates/flock-prover/benches/site_census.rs
grep -q 'name = "site_census"' crates/flock-prover/Cargo.toml || printf '\n[[bench]]\nname = "site_census"\nharness = false\n' >> crates/flock-prover/Cargo.toml
cargo bench --no-run -p flock-prover --bench site_census -j $(nproc) 2>&1 | grep -E '^error|^warning: unused|-->|Finished|Executable' | head -40
SBIN=$(ls -t target/release/deps/site_census-* | grep -v '\.d$' | head -1); [ -x "$SBIN" ] || exit 1
for prof in ${PROFILES:-fast fast100}; do
  for net in ${NETS:-hopper_bf16}; do
    for n in ${NS:-4096}; do
      tag=census-$net-n$n-$prof
      RUST_BACKTRACE=1 PROFILE=$prof US_NET=$W/net/unit-$net.netlist US_NS=$n $SBIN > $OUT/$tag.out 2> $OUT/$tag.err
      echo "rc=$? $tag"; grep RESULT $OUT/$tag.out; grep -E 'panicked|error' $OUT/$tag.err | head -3
    done
  done
done
cp -r $OUT "$RESEARCH_RUN_DIR/out"
