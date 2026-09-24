#!/usr/bin/env bash
# Build the relation-bare/v2 tcdot host from the synced worktree (/workspace/sp1-tcdot/src, `research pods sync`)
# against the BF16 fork worktree, then the cheap checks: crosscheck of every step of the 4096 VUs, one full guest
# execution, the 52 negatives, one --flip-y.
set -euo pipefail
export PATH=$HOME/.cargo/bin:$HOME/.sp1/bin:/usr/local/cuda/bin:$PATH
export CUDACXX=/usr/local/cuda/bin/nvcc CUDA_ARCHS=80
W=/workspace/sp1-tcdot
S=$W/src
MAN=059103cf9bd55ee83cbd4bb14ae6db2f60db2cb4ddf85cdc22b1cecee6e4eeea
log() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }

ln -sfn $W/sp1-bf16 $S/backends/sp1/tcdot/sp1
test "$(git -C $W/sp1-bf16 rev-parse HEAD)" = "$(cat $S/backends/sp1/tcdot/FORK_HEAD)"
export VERITY_TCDOT_FORK_HEAD=$(git -C $W/sp1-bf16 rev-parse HEAD)
export CARGO_TARGET_DIR=$W/target-tcdot
cd $S/backends/sp1/tcdot
log "fork $VERITY_TCDOT_FORK_HEAD tree $(git -C $W/sp1-bf16 rev-parse HEAD^{tree}); source $(python3 -c 'import json;d=json.load(open("'$S'/.research-source.json"));print(d["commit"],d["dirty"])')"

log "build host (cuda)"
[ -f Cargo.lock ] || cp $W/tcdot-Cargo.lock Cargo.lock
cargo build --release -p verity-tcdot-host --features cuda 2>&1 | grep -v "^warning: \|^note: " | tail -40
H=$CARGO_TARGET_DIR/release/verity-tcdot-host
cp Cargo.lock $W/tcdot-Cargo.lock
sha256sum $H

log "info"
SP1_PROVER=cpu RUST_LOG=error $H info

log "crosscheck 0..4096"
$H crosscheck --instances $W/bi --manifest-sha256 $MAN --lo 0 --hi 4096

log "bare-execute 0..4096"
$H bare-execute --instances $W/bi --manifest-sha256 $MAN --lo 0 --hi 4096 --vus-per-read 64 \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps({k: d[k] for k in ("verdict","matches_expected","total_cycles","cycle_tracker","execute_seconds","input_bytes","statement_sha256","public_values")}))'

log "bare-execute --flip-y 7 on 0..64"
$H bare-execute --instances $W/bi --manifest-sha256 $MAN --lo 0 --hi 64 --flip-y 7 \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps({k: d[k] for k in ("verdict","matches_expected","flipped")}))'

log "bare-negatives"
$H bare-negatives --instances $W/bi --manifest-sha256 $MAN > $W/negatives-v2.jsonl
tail -1 $W/negatives-v2.jsonl

log "done"
