#!/usr/bin/env bash
# Rebuild the stream host (cuda,stream-operands; target-tcdot) from the synced source after merging sp1-table's kernel
# k7, fork unchanged at FORK_HEAD_WIT (e3756374), then info, one full guest execution, one --flip-y and the 52 negatives.
set -euo pipefail
W=/workspace/sp1-tcdot; S=$W/src
export PATH=$HOME/.cargo/bin:/usr/local/cuda/bin:$PATH CUDACXX=/usr/local/cuda/bin/nvcc
stamp() { echo; echo "=== [$(date -u +%T)] $*"; }
test "$(git -C $W/sp1-bf16 rev-parse HEAD)" = "$(cat $S/backends/sp1/tcdot/FORK_HEAD_WIT)"
grep -q 'exclude = \["tcdot"\]' $S/backends/sp1/Cargo.toml || sed -i 's/^\[workspace\]$/[workspace]\nexclude = ["tcdot"]/' $S/backends/sp1/Cargo.toml
ln -sfn $W/sp1-bf16 $S/backends/sp1/tcdot/sp1
MAN=059103cf9bd55ee83cbd4bb14ae6db2f60db2cb4ddf85cdc22b1cecee6e4eeea

stamp "host (cuda, stream-operands)"
export VERITY_TCDOT_FORK_HEAD=$(cat $S/backends/sp1/tcdot/FORK_HEAD_WIT) CARGO_TARGET_DIR=$W/target-tcdot
cd $S/backends/sp1/tcdot
cargo build --release -p verity-tcdot-host --features cuda,stream-operands 2>&1 | grep -v "^warning: \\|^note: " | tail -5
H=$CARGO_TARGET_DIR/release/verity-tcdot-host
sha256sum $H

stamp "info"
SP1_PROVER=cpu RUST_LOG=error $H info

stamp "bare-execute 0..4096"
$H bare-execute --instances $W/bi --manifest-sha256 $MAN --lo 0 --hi 4096 --vus-per-read 64 \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps({k: d[k] for k in ("verdict","matches_expected","total_cycles","execute_seconds","statement_sha256","public_values")}))'

stamp "bare-execute --flip-y 7 on 0..64"
$H bare-execute --instances $W/bi --manifest-sha256 $MAN --lo 0 --hi 64 --flip-y 7 \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps({k: d[k] for k in ("verdict","matches_expected","flipped")}))'

stamp "bare-negatives"
$H bare-negatives --instances $W/bi --manifest-sha256 $MAN | tail -1

stamp "done"
