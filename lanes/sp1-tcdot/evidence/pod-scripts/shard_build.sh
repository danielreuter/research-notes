#!/usr/bin/env bash
# Fork patch 0006 (prover sharding): move the fork worktree /workspace/sp1-tcdot/sp1-bf16 to FORK_HEAD of the synced
# source (same path, so both builds are incremental), install its sp1-gpu-server under home-shard/.sp1/bin (the
# baseline server in home-bf16 stays), rebuild the tcdot host (target-tcdot), then info, one full guest execution,
# one --flip-y and the 52 negatives.  Run only while no bench is proving.
set -euo pipefail
export PATH=$HOME/.cargo/bin:$HOME/.sp1/bin:/usr/local/cuda/bin:$PATH
export CUDACXX=/usr/local/cuda/bin/nvcc CUDA_ARCHS=80
W=/workspace/sp1-tcdot
S=$W/src
F=$W/sp1-bf16
MAN=059103cf9bd55ee83cbd4bb14ae6db2f60db2cb4ddf85cdc22b1cecee6e4eeea
log() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }

HEAD=$(cat $S/backends/sp1/tcdot/FORK_HEAD)
git -C $F checkout -q --detach $HEAD
test "$(git -C $F rev-parse 'HEAD^{tree}')" = "$(cat $S/backends/sp1/tcdot/FORK_TREE)"
log "fork $HEAD tree $(git -C $F rev-parse 'HEAD^{tree}')"

log "sp1-gpu-server -> home-shard/.sp1/bin"
mkdir -p $W/home-shard/.sp1/bin
(cd $F && CARGO_TARGET_DIR=$W/target-server cargo install --locked --force --root $W/home-shard/.sp1 --path sp1-gpu/crates/server 2>&1 \
  | grep -v -E "^\s+(Compiling|Downloaded|Downloading) " | tail -5)
sha256sum $W/home-shard/.sp1/bin/sp1-gpu-server
echo $HEAD > $W/home-shard/server-fork-head

log "host (cuda)"
ln -sfn $F $S/backends/sp1/tcdot/sp1
export VERITY_TCDOT_FORK_HEAD=$HEAD CARGO_TARGET_DIR=$W/target-tcdot
cd $S/backends/sp1/tcdot
cargo build --release -p verity-tcdot-host --features cuda 2>&1 | grep -v "^warning: \|^note: " | tail -5
H=$CARGO_TARGET_DIR/release/verity-tcdot-host
sha256sum $H

log "info"
SP1_PROVER=cpu RUST_LOG=error $H info

log "bare-execute 0..4096"
$H bare-execute --instances $W/bi --manifest-sha256 $MAN --lo 0 --hi 4096 --vus-per-read 64 \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps({k: d[k] for k in ("verdict","matches_expected","total_cycles","execute_seconds","statement_sha256","public_values")}))'

log "bare-execute --flip-y 7 on 0..64"
$H bare-execute --instances $W/bi --manifest-sha256 $MAN --lo 0 --hi 64 --flip-y 7 \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps({k: d[k] for k in ("verdict","matches_expected","flipped")}))'

log "bare-negatives"
$H bare-negatives --instances $W/bi --manifest-sha256 $MAN | tail -1

log "done"
