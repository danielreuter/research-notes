#!/usr/bin/env bash
# flock-link: apply backends/flock/flock-link-b684b12.patch to the flock b684b12 checkout from 00-setup-cpu.sh, drop
# backends/flock/live in as crates/flock-live, run the flock-link negatives (in-process verifier) and timed sessions
# against a verifier PROCESS (loopback, or VERIFIER=host:port for a verifier on another pod).
# env: SELF_VUS="8 64"  BENCH_VUS="4096"  RUNS=2  VERIFIER=  SERVE_ONLY=  SKIP_BENCH=
set -uxo pipefail
W=/workspace/flock-link; F=$W/flock; O=$RESEARCH_RUN_DIR/out; mkdir -p $O
source $HOME/.cargo/env
SRC=$(pwd)/backends/flock
cd $F
git checkout -q -- crates/flock-core crates/flock-prover && git apply $SRC/flock-link-b684b12.patch || exit 1
rm -rf crates/flock-live && cp -r $SRC/live crates/flock-live
grep -q '"crates/flock-live"' Cargo.toml || sed -i 's|    "crates/flock-transcript",|    "crates/flock-transcript",\n    "crates/flock-live",|' Cargo.toml
QUOTA=$(awk '$1 != "max" {print int($1 / $2)}' /sys/fs/cgroup/cpu.max 2>/dev/null); TH=${QUOTA:-$(nproc)}
export RAYON_NUM_THREADS=$TH
cargo build --release -p flock-live -j $TH 2>&1 | grep -E '^error|-->|Finished' | head -40
B=$F/target/release/flock-link; [ -x $B ] || exit 1
git -C $F diff --stat | tail -1 > $O/patch-stat.txt
lscpu | grep -E 'Model name' | tee $O/host.txt; echo "threads $TH" | tee -a $O/host.txt; free -g | tee -a $O/host.txt
if [ -n "${SERVE_ONLY:-}" ]; then
  for v in ${BENCH_VUS:-4096}; do
    /usr/bin/time -v $B serve --listen 0.0.0.0:7200 --out $O/sessions-$v --vus $v --seed 10 > $O/serve-$v.log 2> $O/serve-$v.time
  done
  exit 0
fi
for v in ${SELF_VUS:-8 64}; do
  $B selftest --vus $v 2>&1 | tee $O/selftest-$v.txt | grep -E '^(NEG|SELFTEST)' | cut -c1-300
done
[ -n "${SKIP_BENCH:-}" ] && { grep -h '^NEG' $O/selftest-*.txt > $O/negatives.tsv; exit 0; }
for v in ${BENCH_VUS:-4096}; do
  ADDR=${VERIFIER:-}
  if [ -z "$ADDR" ]; then
    $B serve --listen 127.0.0.1:7200 --out $O/sessions-$v --vus $v --seed 10 > $O/serve-$v.log 2>&1 &
    SP=$!; ADDR=127.0.0.1:7200
    for i in $(seq 180); do grep -q SERVING $O/serve-$v.log && break; sleep 1; done
  fi
  /usr/bin/time -v $B prove --verifier $ADDR --vus $v --seed 10 --runs ${RUNS:-2} 2> $O/prove-$v.time | tee $O/prove-$v.txt | cut -c1-900
  grep -E 'Maximum resident|Elapsed' $O/prove-$v.time
  [ -n "${SP:-}" ] && { sleep 2; kill $SP; wait $SP 2>/dev/null; unset SP; }
done
grep -h '^NEG' $O/selftest-*.txt > $O/negatives.tsv; grep -h '^LIVE' $O/prove-*.txt > $O/sessions.tsv
true
