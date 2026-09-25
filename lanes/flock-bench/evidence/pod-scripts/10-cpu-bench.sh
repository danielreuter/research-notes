#!/usr/bin/env bash
# flock-bench: Flock CPU prove/verify on verity's row-leaf shape (verity_shape harness), plus flock's own benches as a cross-check.
# env: THREADS_LIST="8 1"  SWEEP="blake3:bf16:64,1024,4096 ..."  XCHECK=1
set -uxo pipefail
W=/workspace/flock-bench; OUT=$W/out/cpu-$(hostname)-$(date -u +%H%MZ); mkdir -p $OUT
source $HOME/.cargo/env
[ -x /usr/bin/time ] || { apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq time; }
cd $W/flock
cp "$RESEARCH_RUN_DIR/inputs/verity_shape.rs" crates/flock-prover/benches/verity_shape.rs
grep -q 'name = "verity_shape"' crates/flock-prover/Cargo.toml || printf '\n[[bench]]\nname = "verity_shape"\nharness = false\n' >> crates/flock-prover/Cargo.toml
# bench profile (thin LTO), as flock's own `cargo bench` numbers
cargo bench --no-run -p flock-prover --bench verity_shape --bench blake3_proof --bench sha2_proof -j $(nproc) 2>&1 | tail -3 || exit 1
BIN=$(ls -t target/release/deps/verity_shape-* | grep -v '\.d$' | head -1)
lscpu | grep -E 'Model name|^CPU\(s\)|Thread' | tee $OUT/host.txt; nproc | tee -a $OUT/host.txt; cat /sys/fs/cgroup/memory.max | tee -a $OUT/host.txt
THREADS_LIST=${THREADS_LIST:-"8 1"}
SWEEP=${SWEEP:-"blake3:bf16:64,1024,4096 sha2:bf16:64,1024,4096 blake3:fp8:64,1024,4096 sha2:fp8:64,1024,4096"}
for th in $THREADS_LIST; do
  for s in $SWEEP; do
    IFS=: read h p ns <<< "$s"
    for n in ${ns//,/ }; do
      runs=3; [ $n -ge 4096 ] && runs=2
      tag=$h-$p-n$n-t$th
      RAYON_NUM_THREADS=$th VS_HASH=$h VS_PREC=$p VS_NS=$n VS_RUNS=$runs \
        /usr/bin/time -v $BIN > $OUT/$tag.out 2> $OUT/$tag.err
      echo "rc=$? $tag"; grep RESULT $OUT/$tag.out; grep -E 'Maximum resident|Elapsed' $OUT/$tag.err
    done
  done
done
if [ "${XCHECK:-1}" = 1 ]; then
  RAYON_NUM_THREADS=8 BLAKE3_LOG2S="13 17" BLAKE3_RUNS=3 cargo bench -p flock-prover --bench blake3_proof > $OUT/xcheck-blake3_proof-t8.txt 2>&1
  RAYON_NUM_THREADS=8 SHA2_LOG2S="13 17" cargo bench -p flock-prover --bench sha2_proof > $OUT/xcheck-sha2_proof-t8.txt 2>&1
  grep -E '===|best|verify|proof size|peak' $OUT/xcheck-*.txt
fi
cat $OUT/*.out | grep RESULT > $OUT/results.tsv
cp -r $OUT "$RESEARCH_RUN_DIR/out" 2>/dev/null || true
