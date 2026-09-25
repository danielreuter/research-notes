#!/usr/bin/env bash
# flock-bench: ONE Flock union proof of BLAKE3 row leaves + the census transition units (verity_combined),
# on an existing 01-setup-cpu.sh checkout. env: THREADS=32  CSWEEP="ampere_bf16:96:16:64,1024,4096 ..."
set -uxo pipefail
W=/workspace/flock-bench; OUT=$W/out/comb-$(hostname)-$(date -u +%H%MZ); mkdir -p $OUT
IN="$RESEARCH_RUN_DIR/inputs"
source $HOME/.cargo/env
cd $W/flock
P=crates/flock-prover
cp $IN/verity_unit.rs $P/src/r1cs_hashes/verity_unit.rs
grep -q 'pub mod verity_unit;' $P/src/r1cs_hashes.rs || printf '\npub mod verity_unit;\n' >> $P/src/r1cs_hashes.rs
cp $IN/verity_combined.rs $P/benches/verity_combined.rs
grep -q 'name = "verity_combined"' $P/Cargo.toml || printf '\n[[bench]]\nname = "verity_combined"\nharness = false\n' >> $P/Cargo.toml
for pipe in ampere_bf16 ada_e4m3 hopper_bf16 hopper_e4m3; do
  (cd $IN && python3 export_unit.py $pipe $OUT/net-$pipe.txt 64) | tee -a $OUT/export.txt
done
cargo bench --no-run -p flock-prover --bench verity_combined -j $(nproc) > $OUT/build.txt 2>&1
rc=$?; tail -30 $OUT/build.txt; [ $rc = 0 ] || { cp -r $OUT "$RESEARCH_RUN_DIR/out"; exit 1; }
BIN=$(ls -t target/release/deps/verity_combined-* | grep -v '\.d$' | head -1)
TH=${THREADS:-$(nproc)}
CSWEEP=${CSWEEP:-"ampere_bf16:96:16:64,1024,4096 ada_e4m3:48:8:64,1024,4096 hopper_bf16:96:16:4096 hopper_e4m3:48:8:4096"}
for s in $CSWEEP; do
  IFS=: read pipe upv wb ns <<< "$s"
  for n in ${ns//,/ }; do
    runs=3; [ $n -ge 4096 ] && runs=2
    tag=comb-$pipe-n$n-t$TH
    RAYON_NUM_THREADS=$TH VU_NETLIST=$OUT/net-$pipe.txt VU_NAME=$pipe VU_UPV=$upv VU_WORD_BITS=$wb VU_NS=$n VU_RUNS=$runs \
      /usr/bin/time -v $BIN > $OUT/$tag.out 2> $OUT/$tag.err
    echo "rc=$? $tag"; grep RESULT $OUT/$tag.out; grep -E 'Maximum resident|Elapsed|panicked|dense_m' $OUT/$tag.err
  done
done
cat $OUT/*.out 2>/dev/null | grep RESULT > $OUT/results.tsv
cp -r $OUT "$RESEARCH_RUN_DIR/out" 2>/dev/null || true
