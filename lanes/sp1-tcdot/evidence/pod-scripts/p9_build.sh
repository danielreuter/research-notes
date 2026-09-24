#!/usr/bin/env bash
# Fork patch 0009 (prover only): a TC_DOT_BF16 precompile shard merges its calls' local memory accesses into runs
# (crates/prover/src/worker/prover/core.rs = $W/p9/core.rs).  On the fork worktree at e3756374 (patch 0008): copy the
# file, build sp1-gpu-server into home-merge (the stream server in home-stream stays), commit 0009 with a fixed
# identity and date, format-patch it, rebuild the stream host at the new pin, then info, one full guest execution,
# one --flip-y and the 52 negatives.  No chip or executor change, so no cost regeneration and no chip tests.
set -euo pipefail
W=/workspace/sp1-tcdot; S=$W/src; F=$W/sp1-bf16
export PATH="$HOME/.cargo/bin:/usr/local/cuda/bin:/usr/local/go/bin:$PATH"
export CUDACXX=/usr/local/cuda/bin/nvcc CUDA_ARCHS=80
stamp() { echo; echo "=== [$(date -u +%T)] $*"; }
MAN=059103cf9bd55ee83cbd4bb14ae6db2f60db2cb4ddf85cdc22b1cecee6e4eeea

stamp "fork e3756374 + p9/core.rs"
test "$(git -C $F rev-parse HEAD)" = e37563743b23c612a7ec447a57c214a845380b54
test -z "$(git -C $F status --porcelain --untracked-files=no)"
cp $W/p9/core.rs $F/crates/prover/src/worker/prover/core.rs
git -C $F diff --stat

stamp "sp1-gpu-server -> home-merge/.sp1/bin"
cd $F
(CARGO_TARGET_DIR=$W/target-server cargo install --locked --force --root $W/home-merge/.sp1 --path sp1-gpu/crates/server 2>&1 \
  | grep -E "^error|^warning: unused|Installed|Finished" -A 6) || { echo "server build failed"; exit 1; }
test -x $W/home-merge/.sp1/bin/sp1-gpu-server
sha256sum $W/home-merge/.sp1/bin/sp1-gpu-server

stamp "commit patch 0009"
GIT_AUTHOR_DATE="2026-09-24T08:40:00+0000" GIT_COMMITTER_DATE="2026-09-24T08:40:00+0000" \
  git -c user.name="verity sp1-tcdot lane" -c user.email="lane@verity.local" commit -q -a -F $W/p9/COMMIT_MSG
HEAD=$(git rev-parse HEAD); echo "head $HEAD tree $(git rev-parse 'HEAD^{tree}')"
rm -rf $W/patch-0009 && git format-patch -q -1 HEAD --start-number 9 -o $W/patch-0009 && ls $W/patch-0009
echo $HEAD > $W/home-merge/server-fork-head

stamp "host (cuda, stream-operands) at $HEAD"
export VERITY_TCDOT_FORK_HEAD=$HEAD CARGO_TARGET_DIR=$W/target-tcdot
cd $S/backends/sp1/tcdot
cargo build --release -p verity-tcdot-host --features cuda,stream-operands 2>&1 | grep -v "^warning: \\|^note: " | tail -3
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
