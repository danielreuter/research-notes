#!/usr/bin/env bash
# jolt-scout: main, after 10-main.sh. Install the jolt CLI (guest builds), add the vu-k1536 example, run sha2-chain
# once and the VU sweep. Args: $1 = vu-k1536.tgz (the example, from evidence/pod-scripts/vu-k1536).
set -uo pipefail
TGZ=$(readlink -f "$1")
W=/workspace/jolt-scout; cd $W/jolt; source $HOME/.cargo/env
L=$W/11-main-run.log; exec > >(tee -a $L) 2>&1
export CARGO_TARGET_DIR=$W/target-main
t0=$(date +%s); cargo install --locked --path . 2>&1 | tail -2; echo "INSTALL_JOLT_CLI rc=${PIPESTATUS[0]} $(( $(date +%s)-t0 ))s"; which jolt
rm -rf examples/vu-k1536; mkdir -p examples/vu-k1536; tar xzf "$TGZ" -C examples/vu-k1536
grep -q '"examples/vu-k1536"' Cargo.toml || sed -i 's|  "examples/sha2-chain",|  "examples/vu-k1536",\n  "examples/vu-k1536/guest",\n  "examples/sha2-chain",|' Cargo.toml
git diff --stat
t0=$(date +%s); cargo build --release -p vu-k1536 2>&1 | grep -E '^(error|warning: unused)|-->|Finished' | head -30; echo "BUILD_VU rc=${PIPESTATUS[0]} $(( $(date +%s)-t0 ))s"
# timed work holds the pod-wide timing lock (other scripts' builds may still run; see the report for contention)
exec 9>$W/timing.lock; flock 9; echo "LOCK $(date -u +%H:%M:%SZ) load $(cut -d' ' -f1-3 /proc/loadavg)"
echo "== sha2-chain (1000 x SHA-256 of 32 B)"; RUST_LOG=info $CARGO_TARGET_DIR/release/sha2-chain 2>&1 | grep -v '^\s*$' | cut -c1-300 | tail -15
VU_NS=${VU_NS:-1,4,16} MODES=${MODES:-0,1} REPS=${REPS:-1} RUST_LOG=${RUST_LOG_VU:-info} /usr/bin/time -v $CARGO_TARGET_DIR/release/vu-k1536 2>&1 | grep -v -E '^\s*$' | grep -E 'COMPILE|PREPROCESS|TRACE|RESULT|panicked|error|Maximum resident|Elapsed|ycle|marker|rowhash|kernel' | cut -c1-300
flock -u 9
echo MAIN_RUN_DONE
