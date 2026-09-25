#!/usr/bin/env bash
# flock-link: apply backends/flock/flock-link-b684b12.patch to the flock b684b12 checkout from 00-setup-cpu.sh, drop
# backends/flock/live in as crates/flock-live, run the flock-link negatives (in-process verifier) and timed sessions
# against a verifier PROCESS (loopback, or VERIFIER=host:port for a verifier on another pod).
# F2 (the pinned census-unit + BLAKE3 union verifier and the GPU unit-table verifier): verity_unit.rs goes into
# flock-prover, the unit netlists are exported with export_unit.py, and `flock-live selftest-f2` runs when F2=1.
# LEGACY=1 also runs flock-live's own selftest (stub link, F3 cases) and its BLAKE3-union bench at LEGACY_N compressions
# (the same-host baseline: no circuit, no link claims).
# env: SELF_VUS="8 64"  BENCH_VUS="4096"  RUNS=2  VERIFIER=  SERVE_ONLY=  SKIP_BENCH=  F2=  LEGACY=  LEGACY_N=393216
set -uxo pipefail
W=/workspace/flock-link; F=$W/flock; O=$RESEARCH_RUN_DIR/out; mkdir -p $O
source $HOME/.cargo/env
[ -x /usr/bin/time ] || { apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq time >/dev/null; }
SRC=$(pwd)/backends/flock
cd $F
git checkout -q -- crates/flock-core crates/flock-prover && git apply $SRC/flock-link-b684b12.patch || exit 1
rm -rf crates/flock-live && cp -r $SRC/live crates/flock-live
grep -q '"crates/flock-live"' Cargo.toml || sed -i 's|    "crates/flock-transcript",|    "crates/flock-transcript",\n    "crates/flock-live",|' Cargo.toml
cp $SRC/verity_unit.rs crates/flock-prover/src/r1cs_hashes/verity_unit.rs
grep -q 'pub mod verity_unit;' crates/flock-prover/src/r1cs_hashes.rs || printf '\npub mod verity_unit;\n' >> crates/flock-prover/src/r1cs_hashes.rs
N=$W/net; mkdir -p $N
for pipe in hopper_bf16 hopper_e4m3; do (cd $SRC/pod && python3 export_unit.py $pipe $N/net-$pipe.txt 64) | tail -1 | tee -a $O/export.txt; done
sha256sum $N/net-*.txt | tee $O/netlists.sha256
QUOTA=$(awk '$1 != "max" {print int($1 / $2)}' /sys/fs/cgroup/cpu.max 2>/dev/null); TH=${QUOTA:-$(nproc)}
export RAYON_NUM_THREADS=$TH
cargo build --release -p flock-live --features verity-unit -j $TH 2>&1 | grep -E '^error|-->|Finished' | head -40
B=$F/target/release/flock-link; [ -x $B ] || exit 1
git -C $F diff --stat | tail -1 > $O/patch-stat.txt
if [ -n "${LEGACY:-}" ]; then
  $F/target/release/flock-live selftest --n 4096 2>&1 | tee $O/selftest-legacy.txt | grep -E '^(NEG|SELFTEST)' | cut -c1-300
  $F/target/release/flock-live bench --n ${LEGACY_N:-393216} --runs 3 2>&1 | tee $O/bench-legacy.txt | grep BENCH | cut -c1-600
fi
if [ -n "${F2:-}" ]; then
  $F/target/release/flock-live selftest-f2 --netlist $N/net-hopper_bf16.txt --netlist-other $N/net-hopper_e4m3.txt \
    --n ${F2_N:-4096} --units ${F2_UNITS:-4096} --nbl ${F2_NBL:-14} 2>&1 | tee $O/selftest-f2.txt | grep -E '^(NEG|SELFTEST)' | cut -c1-300
fi
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
grep -h '^NEG' $O/selftest-*.txt > $O/negatives.tsv 2>/dev/null; grep -h '^LIVE' $O/prove-*.txt > $O/sessions.tsv 2>/dev/null
true
