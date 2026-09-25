#!/usr/bin/env bash
# flock-live: build backends/flock/live (shipped with --source) into the flock b684b12 checkout from 00-setup-cpu.sh,
# run the negatives (selftest, in-process verifier) and FS-vs-live timing against a verifier PROCESS over loopback TCP.
# env: NS="4096 16384"  BENCH_NS="..."  RUNS=5  SKIP_BENCH
set -uxo pipefail
W=/workspace/flock-live; F=$W/flock; O=$RESEARCH_RUN_DIR/out; mkdir -p $O
source $HOME/.cargo/env
SRC=$(pwd)/backends/flock/live
rm -rf $F/crates/flock-live && cp -r $SRC $F/crates/flock-live
cd $F
grep -q '"crates/flock-live"' Cargo.toml || sed -i 's|    "crates/flock-transcript",|    "crates/flock-transcript",\n    "crates/flock-live",|' Cargo.toml
QUOTA=$(awk '$1 != "max" {print int($1 / $2)}' /sys/fs/cgroup/cpu.max 2>/dev/null); TH=${QUOTA:-$(nproc)}
export RAYON_NUM_THREADS=$TH
cargo build --release -p flock-live -j $TH 2>&1 | grep -E '^(error|warning: unused)|-->|Finished' | head -40
B=$F/target/release/flock-live; [ -x $B ] || exit 1
lscpu | grep -E 'Model name' | tee $O/host.txt; echo "threads $TH" | tee -a $O/host.txt
for n in ${NS:-4096 16384}; do
  $B selftest --n $n 2>&1 | tee $O/selftest-$n.txt | grep -E '^(NEG|SELFTEST)' | cut -c1-400
done
[ -n "${SKIP_BENCH:-}" ] && exit 0
for n in ${BENCH_NS:-16384}; do
  $B serve --listen 127.0.0.1:7100 --out $O/sessions-$n --n $n > $O/serve-$n.log 2>&1 &
  SP=$!; sleep 2
  $B bench --verifier 127.0.0.1:7100 --n $n --runs ${RUNS:-5} 2>&1 | tee $O/bench-$n.txt | grep BENCH | cut -c1-500
  kill $SP; wait $SP 2>/dev/null
done
grep -h '^NEG' $O/selftest-*.txt > $O/negatives.tsv; grep -h '^BENCH' $O/bench-*.txt > $O/bench.tsv 2>/dev/null
true
