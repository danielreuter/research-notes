#!/usr/bin/env bash
# flock-128: CPU union proofs (census unit + BLAKE3 row leaves, one Flock union proof) under today's profile and the
# 2^-128 profile, timed alternately on the same pod (unit_shape128.rs). Build from 00-setup-cpu.sh's tree.
# env: NETS="hopper_bf16 hopper_e4m3"  NS="1024 4096"  RUNS=5  PROFILES="fastx1 fast100x2 fastx2"  NEG=1  BUILD_ONLY
set -uxo pipefail
W=/workspace/flock-128; OUT=$W/out/cpu128-$(date -u +%H%MZ); mkdir -p $OUT $W/net
source $HOME/.cargo/env
cp $RESEARCH_RUN_DIR/inputs/unit-*.netlist $W/net/ 2>/dev/null || true
cd $W/flock
cp $RESEARCH_RUN_DIR/inputs/unit_shape128.rs crates/flock-prover/benches/unit_shape128.rs
grep -q 'name = "unit_shape128"' crates/flock-prover/Cargo.toml || printf '\n[[bench]]\nname = "unit_shape128"\nharness = false\n' >> crates/flock-prover/Cargo.toml
cargo bench --no-run -p flock-prover --bench unit_shape128 -j $(nproc) 2>&1 | grep -E '^error|-->|Finished|Executable' | head -40
BIN=$(ls -t target/release/deps/unit_shape128-* | grep -v '\.d$' | head -1); [ -x "$BIN" ] || exit 1
[ -n "${BUILD_ONLY:-}" ] && exit 0
lscpu | grep -E 'Model name|^CPU\(s\)' | tee $OUT/host.txt; cat /sys/fs/cgroup/cpu.max 2>/dev/null | tee -a $OUT/host.txt; uptime | tee -a $OUT/host.txt
QUOTA=$(awk '$1 != "max" {print int($1 / $2)}' /sys/fs/cgroup/cpu.max 2>/dev/null)
TH=${THREADS:-${QUOTA:-$(nproc)}}; [ "$TH" -gt "$(nproc)" ] && TH=$(nproc)
echo "threads $TH" | tee -a $OUT/host.txt
for net in ${NETS:-hopper_bf16 hopper_e4m3}; do
  tag=u128-$net-${MODE:-mixed}-t$TH
  RAYON_NUM_THREADS=$TH US_NET=$W/net/unit-$net.netlist US_MODE=${MODE:-mixed} US_NS="${NS:-1024 4096}" US_RUNS=${RUNS:-5} \
    US_PROFILES="${PROFILES:-fastx1 fast100x2 fastx2}" US_NEG=${NEG:-1} /usr/bin/time -v $BIN > $OUT/$tag.out 2> $OUT/$tag.err
  echo "rc=$? $tag"; grep -E 'RESULT|NEG' $OUT/$tag.out | cut -c1-400; grep -E 'Maximum resident|panicked' $OUT/$tag.err
done
cat $OUT/*.out | grep -E 'RESULT|NEG' > $OUT/results.tsv
cp -r $OUT "$RESEARCH_RUN_DIR/out"
