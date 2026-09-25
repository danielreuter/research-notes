#!/usr/bin/env bash
# flock-bench-80gb: Flock CPU prover (all host threads) on the pod:
#  A. unit_shape: census unit table alone (US_MODE=unit) and unit + BLAKE3 leaves in one union proof (mixed)
#  B. verity_shape (flock-bench's harness): BLAKE3 row-leaf table at the same batch shape
# env: NETS="ampere_bf16 hopper_bf16 hopper_e4m3"  NS="64 1024 4096"  MODES="unit mixed"  PARTS="A B"  THREADS=$(nproc)
set -uxo pipefail
W=/workspace/flock-bench-80gb; OUT=$W/out/cpu-${TAG:-x}-$(date -u +%H%MZ); mkdir -p $OUT
source $HOME/.cargo/env
I=$RESEARCH_RUN_DIR/inputs
cd $W/flock
cp $I/verity_unit.rs crates/flock-prover/src/r1cs_hashes/verity_unit.rs
grep -q 'pub mod verity_unit;' crates/flock-prover/src/r1cs_hashes.rs || echo 'pub mod verity_unit;' >> crates/flock-prover/src/r1cs_hashes.rs
cp $I/unit_shape.rs crates/flock-prover/benches/unit_shape.rs
cp $I/verity_shape.rs crates/flock-prover/benches/verity_shape.rs
for b in unit_shape verity_shape; do
  grep -q "name = \"$b\"" crates/flock-prover/Cargo.toml || printf '\n[[bench]]\nname = "%s"\nharness = false\n' $b >> crates/flock-prover/Cargo.toml
done
mkdir -p $W/net; cp $I/unit-*.netlist $W/net/
cargo bench --no-run -p flock-prover --bench unit_shape --bench verity_shape -j $(nproc) 2>&1 | grep -E '^(error|warning: unused)|-->|Finished|Executable' | head -40
UBIN=$(ls -t target/release/deps/unit_shape-* | grep -v '\.d$' | head -1)
VBIN=$(ls -t target/release/deps/verity_shape-* | grep -v '\.d$' | head -1)
[ -x "$UBIN" ] || exit 1
lscpu | grep -E 'Model name|^CPU\(s\)|Thread' | tee $OUT/host.txt; nproc | tee -a $OUT/host.txt; cat /sys/fs/cgroup/cpu.max /sys/fs/cgroup/memory.max 2>/dev/null | tee -a $OUT/host.txt
QUOTA=$(awk '$1 != "max" {print int($1 / $2)}' /sys/fs/cgroup/cpu.max 2>/dev/null)
TH=${THREADS:-${QUOTA:-$(nproc)}}
[ "$TH" -gt "$(nproc)" ] && TH=$(nproc)
echo "threads $TH (cgroup quota ${QUOTA:-none}, nproc $(nproc))" | tee -a $OUT/host.txt
NS=${NS:-"64 1024 4096"}
if [[ ${PARTS:-A B} == *A* ]]; then
  for net in ${NETS:-ampere_bf16 hopper_bf16 hopper_e4m3}; do
    for mode in ${MODES:-unit mixed}; do
      for n in $NS; do
        runs=3; [ $n -ge 4096 ] && runs=2
        tag=unit-$net-$mode-n$n-t$TH
        RAYON_NUM_THREADS=$TH US_NET=$W/net/unit-$net.netlist US_MODE=$mode US_NS=$n US_RUNS=$runs \
          /usr/bin/time -v $UBIN > $OUT/$tag.out 2> $OUT/$tag.err
        echo "rc=$? $tag"; grep RESULT $OUT/$tag.out; grep -E 'netlist|Maximum resident|panicked|error' $OUT/$tag.err | head -4
      done
    done
  done
fi
if [[ ${PARTS:-A B} == *B* ]]; then
  for s in ${SWEEP:-blake3:bf16 blake3:fp8}; do
    IFS=: read h p <<< "$s"
    for n in $NS; do
      runs=3; [ $n -ge 4096 ] && runs=2
      tag=vs-$h-$p-n$n-t$TH
      RAYON_NUM_THREADS=$TH VS_HASH=$h VS_PREC=$p VS_NS=$n VS_RUNS=$runs /usr/bin/time -v $VBIN > $OUT/$tag.out 2> $OUT/$tag.err
      echo "rc=$? $tag"; grep RESULT $OUT/$tag.out; grep -E 'Maximum resident|panicked' $OUT/$tag.err
    done
  done
fi
cat $OUT/*.out | grep RESULT > $OUT/results.tsv
cp -r $OUT "$RESEARCH_RUN_DIR/out" 2>/dev/null || true
