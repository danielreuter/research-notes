#!/usr/bin/env bash
# route-a-live: the CPU verifier pod. flock b684b12 (00-setup-cpu.sh) + the flock-link patch + this tree's live crate,
# flock-link release build, the flock-link selftest at 8 VUs (every negative, the live-prime order and the G2 replay
# cases included), and verity-gkr-verify (for the gate re-run beside the records).
set -uxo pipefail
SRC=$(pwd); O=$RESEARCH_RUN_DIR/out; mkdir -p $O
bash backends/flock/pod/00-setup-cpu.sh 2>&1 | tail -5
source $HOME/.cargo/env
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
TH=$([ "$Q" = max ] && nproc || echo $(( Q / PER ))); export RAYON_NUM_THREADS=$TH
F=/workspace/flock-link/flock
cd $F && git checkout -q -- . && rm -rf crates/flock-live && git apply $SRC/backends/flock/flock-link-b684b12.patch || exit 1
cp -r $SRC/backends/flock/live crates/flock-live
grep -q '"crates/flock-live"' Cargo.toml || sed -i 's|    "crates/flock-transcript",|    "crates/flock-transcript",\n    "crates/flock-live",|' Cargo.toml
cargo build --release -p flock-live -j $TH 2>&1 | grep -E '^(error|warning)|-->|Finished' | head -30
B=$F/target/release/flock-link; [ -x $B ] || exit 1
mkdir -p /workspace/bin && cp $B /workspace/bin/flock-link-live
cd $SRC/backends/gkr/verifier && cargo build --release -j $TH 2>&1 | grep -E '^error|Finished' | head -3
cp target/release/verity-gkr-verify /workspace/bin/verity-gkr-verify-live 2>/dev/null || cp ${CARGO_TARGET_DIR:-target}/release/verity-gkr-verify /workspace/bin/verity-gkr-verify-live
sha256sum /workspace/bin/* | tee $O/binaries.sha256
lscpu | grep 'Model name'; echo "threads $TH"
$B selftest --vus 8 > $O/selftest-8.txt 2>&1
grep -E '^(NEG|SELFTEST)' $O/selftest-8.txt | cut -c1-300
echo "failed cases: $(grep -c '"pass":false' $O/selftest-8.txt)"
true
