#!/usr/bin/env bash
# jolt-scout: (re)install the vu-k1536 example into main, build, and run the VU sweep under the timing lock.
# Args: $1 = vu-k1536.tgz. Env: VU_NS, MODES, REPS (see vu-k1536/src/main.rs).
set -uo pipefail
TGZ=$(readlink -f "$1")
W=/workspace/jolt-scout; cd $W/jolt; source $HOME/.cargo/env
L=$W/12-vu.log; exec > >(tee -a $L) 2>&1
export CARGO_TARGET_DIR=$W/target-main
rm -rf examples/vu-k1536; mkdir -p examples/vu-k1536; tar xzf "$TGZ" -C examples/vu-k1536 2>/dev/null
grep -q '"examples/vu-k1536"' Cargo.toml || sed -i 's|  "examples/sha2-chain",|  "examples/vu-k1536",\n  "examples/vu-k1536/guest",\n  "examples/sha2-chain",|' Cargo.toml
t0=$(date +%s); cargo build --release -p vu-k1536 2>&1 | grep -E '^error|-->|Finished' | head -30; echo "BUILD_VU rc=${PIPESTATUS[0]} $(( $(date +%s)-t0 ))s"
exec 9>$W/timing.lock; flock 9; echo "LOCK $(date -u +%H:%M:%SZ) load $(cut -d' ' -f1-3 /proc/loadavg)"
echo "VU_NS=${VU_NS:-1,4,16} MODES=${MODES:-0,1} REPS=${REPS:-1}"
VU_NS=${VU_NS:-1,4,16} MODES=${MODES:-0,1} REPS=${REPS:-1} RUST_LOG=info /usr/bin/time -v $CARGO_TARGET_DIR/release/vu-k1536 2>&1 \
  | grep -v -E '^\s*$' | grep -E 'COMPILE|PREPROCESS|TRACE|RESULT|panicked|error|Maximum resident|Elapsed|ycle|rowhash|kernel|max_log_n' | cut -c1-300
flock -u 9
echo "VU_DONE $(date -u +%H:%M:%SZ)"
