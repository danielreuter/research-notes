#!/usr/bin/env bash
# Build the modified-SP1 (TC_DOT chip) Verity host against the BF16 fork worktree and run the cheap checks:
# native crosscheck of every step of the 4096 VUs, one guest execution, the 52 negatives.
set -euo pipefail
export PATH=$HOME/.cargo/bin:$HOME/.sp1/bin:/usr/local/cuda/bin:$PATH
export CUDACXX=/usr/local/cuda/bin/nvcc CUDA_ARCHS=80
W=/workspace/sp1-tcdot
V=$W/vt
MAN=059103cf9bd55ee83cbd4bb14ae6db2f60db2cb4ddf85cdc22b1cecee6e4eeea
log() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }

rm -rf $V && mkdir -p $V && tar -xzf $W/tcdot-src.tgz -C $V
ln -sfn $W/sp1-bf16 $V/backends/sp1/tcdot/sp1
# The stock workspace must exclude tcdot/ (else cargo resolves the fork crates' inherited fields from it).
grep -q '^exclude = \["tcdot"\]' $V/backends/sp1/Cargo.toml ||
  sed -i 's/^members = \(.*\)$/members = \1\nexclude = ["tcdot"]/' $V/backends/sp1/Cargo.toml
export VERITY_TCDOT_FORK_HEAD=$(git -C $W/sp1-bf16 rev-parse HEAD)
export CARGO_TARGET_DIR=$W/target-tcdot
cd $V/backends/sp1/tcdot
log "fork $VERITY_TCDOT_FORK_HEAD tree $(git -C $W/sp1-bf16 rev-parse HEAD^{tree})"

log "build host (cuda)"
cargo generate-lockfile 2>&1 | tail -3
cargo build --release -p verity-tcdot-host --features cuda 2>&1 | grep -v "^warning: \|^note: " | tail -40
H=$CARGO_TARGET_DIR/release/verity-tcdot-host
cp Cargo.lock $W/tcdot-Cargo.lock

log "crosscheck 0..4096"
$H crosscheck --instances $W/bi --manifest-sha256 $MAN --lo 0 --hi 4096

log "bare-execute 0..64"
$H bare-execute --instances $W/bi --manifest-sha256 $MAN --lo 0 --hi 64 --vus-per-read 64 \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); [d.pop(k) for k in ("public_values","expected_public_values")]; print(json.dumps(d))'

log "bare-negatives"
$H bare-negatives --instances $W/bi --manifest-sha256 $MAN > $W/negatives.jsonl
tail -1 $W/negatives.jsonl

log "done"
