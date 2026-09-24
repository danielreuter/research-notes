#!/usr/bin/env bash
# Rebuild the tcdot host from $W/tcdot-src.tgz (incremental), then: crosscheck, execute sweeps, negatives.
#   iter.sh [thresholds for the execute sweep ...]
set -euo pipefail
export PATH=$HOME/.cargo/bin:$HOME/.sp1/bin:/usr/local/cuda/bin:$PATH
export CUDACXX=/usr/local/cuda/bin/nvcc CUDA_ARCHS=80
W=/workspace/sp1-tcdot
V=$W/vt
MAN=059103cf9bd55ee83cbd4bb14ae6db2f60db2cb4ddf85cdc22b1cecee6e4eeea
log() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }
THRESHOLDS=${*:-97 16 8 4 2 1}

rm -rf $V/backends/sp1/tcdot/host $V/backends/sp1/tcdot/guest
tar -xzf $W/tcdot-src.tgz -C $V backends/sp1/tcdot/host backends/sp1/tcdot/guest backends/sp1/tcdot/Cargo.toml
grep -q '^exclude = \["tcdot"\]' $V/backends/sp1/Cargo.toml ||
  sed -i 's/^members = \(.*\)$/members = \1\nexclude = ["tcdot"]/' $V/backends/sp1/Cargo.toml
export VERITY_TCDOT_FORK_HEAD=$(git -C $W/sp1-bf16 rev-parse HEAD)
export CARGO_TARGET_DIR=$W/target-tcdot
cd $V/backends/sp1/tcdot
log "build host (cuda)"
cargo build --release -p verity-tcdot-host --features cuda 2>&1 | grep -E "^(error|warning: unused)|Finished|-->" | tail -20
H=$CARGO_TARGET_DIR/release/verity-tcdot-host
sha256sum $H

log "crosscheck 0..4096"
$H crosscheck --instances $W/bi --manifest-sha256 $MAN --lo 0 --hi 4096

for T in $THRESHOLDS; do
  log "bare-execute 0..4096 threshold $T"
  $H bare-execute --instances $W/bi --manifest-sha256 $MAN --lo 0 --hi 4096 --vus-per-read 64 --vu-software-threshold $T \
    | python3 -c 'import json,sys; d=json.load(sys.stdin); print({k: d[k] for k in ("verdict","matches_expected","total_cycles","gas","syscalls","execute_seconds")}); r=d["routing"]; print({k: r[k] for k in ("chip_steps","software_steps","software_vus","rejected_vus","kernel_mismatches")})'
done

for T in 0 8 97; do
  log "bare-negatives threshold $T"
  $H bare-negatives --instances $W/bi --manifest-sha256 $MAN --vu-software-threshold $T > $W/negatives-t$T.jsonl
  tail -1 $W/negatives-t$T.jsonl
done
log "done"
