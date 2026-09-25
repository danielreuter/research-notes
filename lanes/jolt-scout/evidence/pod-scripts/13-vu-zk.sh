#!/usr/bin/env bash
# jolt-scout: the vu-k1536 example (already installed into main by 12-vu.sh) built with jolt-sdk/zk (BlindFold, Dory),
# own target dir; VU sweep under the timing lock. Env: VU_NS, MODES, REPS.
set -uo pipefail
W=/workspace/jolt-scout; cd $W/jolt; source $HOME/.cargo/env
L=$W/13-vu-zk.log; exec > >(tee -a $L) 2>&1
export CARGO_TARGET_DIR=$W/target-main-zk
t0=$(date +%s); cargo build --release -p vu-k1536 --features jolt-sdk/zk 2>&1 | grep -E '^error|-->|Finished' | head -30; echo "BUILD_VU_ZK rc=${PIPESTATUS[0]} $(( $(date +%s)-t0 ))s"
exec 9>$W/timing.lock; flock 9; echo "LOCK $(date -u +%H:%M:%SZ) load $(cut -d' ' -f1-3 /proc/loadavg)"
echo "ZK VU_NS=${VU_NS:-16} MODES=${MODES:-0,1} REPS=${REPS:-2}"
VU_NS=${VU_NS:-16} MODES=${MODES:-0,1} REPS=${REPS:-2} RUST_LOG=info /usr/bin/time -v $CARGO_TARGET_DIR/release/vu-k1536 2>&1 \
  | grep -v -E '^\s*$' | grep --line-buffered -E 'COMPILE|PREPROCESS|TRACE|RESULT|panicked|error|Maximum resident|Elapsed|ycle|max_log_n' | cut -c1-300
flock -u 9
echo "VU_ZK_DONE $(date -u +%H:%M:%SZ)"
