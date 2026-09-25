#!/usr/bin/env bash
# flock-bench: Flock CPU prove/verify of the binary-census transition unit (verity_unit table) at our
# batch shape, plus (BLAKE=1) the BLAKE3 row-leaf table on the same host (verity_shape).
# env: THREADS_LIST="32"  USWEEP="ampere_bf16:96:64,1024,4096 ada_e4m3:48:64,1024,4096"
#      BSWEEP="blake3:bf16:64,1024,4096 blake3:fp8:64,1024,4096"  BLAKE=1  BUILD_ONLY=0
set -uxo pipefail
W=/workspace/flock-bench; OUT=$W/out/unit-$(hostname)-$(date -u +%H%MZ); mkdir -p $OUT
IN="$RESEARCH_RUN_DIR/inputs"
source $HOME/.cargo/env
[ -x /usr/bin/time ] || { apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq time; }
command -v python3 >/dev/null || { apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq python3; }
cd $W/flock
P=crates/flock-prover
cp $IN/verity_unit.rs $P/src/r1cs_hashes/verity_unit.rs
grep -q 'pub mod verity_unit;' $P/src/r1cs_hashes.rs || printf '\npub mod verity_unit;\n' >> $P/src/r1cs_hashes.rs
cp $IN/verity_unit_bench.rs $P/benches/verity_unit_bench.rs
cp $IN/verity_shape.rs $P/benches/verity_shape.rs
for b in verity_unit_bench verity_shape; do
  grep -q "name = \"$b\"" $P/Cargo.toml || printf '\n[[bench]]\nname = "%s"\nharness = false\n' $b >> $P/Cargo.toml
done
for pipe in ampere_bf16 ada_e4m3 hopper_bf16 hopper_e4m3; do
  (cd $IN && python3 export_unit.py $pipe $OUT/net-$pipe.txt 64) | tee -a $OUT/export.txt
done
cargo bench --no-run -p flock-prover --bench verity_unit_bench --bench verity_shape -j $(nproc) > $OUT/build.txt 2>&1
rc=$?; tail -30 $OUT/build.txt; [ $rc = 0 ] || { cp -r $OUT "$RESEARCH_RUN_DIR/out"; exit 1; }
[ "${BUILD_ONLY:-0}" = 1 ] && { cp -r $OUT "$RESEARCH_RUN_DIR/out"; exit 0; }
UBIN=$(ls -t target/release/deps/verity_unit_bench-* | grep -v '\.d$' | head -1)
BBIN=$(ls -t target/release/deps/verity_shape-* | grep -v '\.d$' | head -1)
lscpu | grep -E 'Model name|^CPU\(s\)|Thread' | tee $OUT/host.txt; nproc | tee -a $OUT/host.txt
cat /sys/fs/cgroup/memory.max 2>/dev/null | tee -a $OUT/host.txt; free -g | tee -a $OUT/host.txt
THREADS_LIST=${THREADS_LIST:-"$(nproc)"}
USWEEP=${USWEEP:-"ampere_bf16:96:64,1024,4096 ada_e4m3:48:64,1024,4096"}
BSWEEP=${BSWEEP:-"blake3:bf16:64,1024,4096 blake3:fp8:64,1024,4096"}
for th in $THREADS_LIST; do
  for s in $USWEEP; do
    IFS=: read pipe upv ns <<< "$s"
    for n in ${ns//,/ }; do
      runs=3; [ $n -ge 4096 ] && runs=2
      tag=unit-$pipe-n$n-t$th
      RAYON_NUM_THREADS=$th VU_NETLIST=$OUT/net-$pipe.txt VU_NAME=$pipe VU_UPV=$upv VU_NS=$n VU_RUNS=$runs \
        /usr/bin/time -v $UBIN > $OUT/$tag.out 2> $OUT/$tag.err
      echo "rc=$? $tag"; grep RESULT $OUT/$tag.out; grep -E 'Maximum resident|Elapsed|panicked' $OUT/$tag.err
    done
  done
  if [ "${BLAKE:-1}" = 1 ]; then
    for s in $BSWEEP; do
      IFS=: read h p ns <<< "$s"
      for n in ${ns//,/ }; do
        runs=3; [ $n -ge 4096 ] && runs=2
        tag=$h-$p-n$n-t$th
        RAYON_NUM_THREADS=$th VS_HASH=$h VS_PREC=$p VS_NS=$n VS_RUNS=$runs \
          /usr/bin/time -v $BBIN > $OUT/$tag.out 2> $OUT/$tag.err
        echo "rc=$? $tag"; grep RESULT $OUT/$tag.out; grep -E 'Maximum resident|Elapsed' $OUT/$tag.err
      done
    done
  fi
done
for pipe in ampere_bf16 ada_e4m3; do
  upv=96; [ $pipe = ada_e4m3 ] && upv=48
  tag=tamper-$pipe-n64
  VU_TAMPER=1 VU_NETLIST=$OUT/net-$pipe.txt VU_NAME=$pipe VU_UPV=$upv VU_NS=64 VU_RUNS=1 $UBIN > $OUT/$tag.out 2> $OUT/$tag.err
  echo "rc=$? $tag"; grep RESULT $OUT/$tag.out; grep panicked $OUT/$tag.err
done
cat $OUT/*.out 2>/dev/null | grep RESULT > $OUT/results.tsv
cp -r $OUT "$RESEARCH_RUN_DIR/out" 2>/dev/null || true
