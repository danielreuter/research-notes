#!/usr/bin/env bash
# Fork patch 0008 (TC_DOT_BF16 takes each step's operands from the input stream): the edited files shipped to
# $W/stream-src on top of 0007 (cbf66ccd) in the fork worktree $W/sp1-bf16, executor unit tests, chip tests (the chip
# is 0007's, so the cost artifacts stay), a commit (lane identity, fixed dates) and its format-patch in $W/patch-0008.
# Then the sp1-gpu-server under home-stream/.sp1/bin (home-wit keeps 0007's), the tcdot host with --features
# cuda,stream-operands (target-tcdot), info, one full guest execution, one --flip-y and the 52 negatives.
set -euo pipefail
W=/workspace/sp1-tcdot
S=$W/src
F=$W/sp1-bf16
MAN=059103cf9bd55ee83cbd4bb14ae6db2f60db2cb4ddf85cdc22b1cecee6e4eeea
export PATH="$HOME/.sp1/bin:$HOME/.cargo/bin:/usr/local/cuda/bin:/usr/local/go/bin:$PATH"
export CUDACXX=/usr/local/cuda/bin/nvcc CUDA_ARCHS=80
stamp() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }
filter() { grep -E "^test |test result|^error|^warning: unused|panicked|FAILED|failures:" || true; }

stamp "fork cbf66ccd + the stream-src files"
cd $F
git checkout -q --detach cbf66ccd5c9b445afde336cefd209a25729f7242
cp -r $W/stream-src/crates/. crates/
git diff --stat

export CARGO_TARGET_DIR=$W/target-bf16
stamp "executor unit tests (tc_dot)"
cargo test --release -p sp1-core-executor --lib tc_dot 2>&1 | filter

stamp "chip tests (fp8 + bf16, incl. consistency)"
cargo test --release -p sp1-core-machine --lib -- tc_dot core_air_cost_consistency core_air_complexity_consistency \
   test_maximum_cycle test_maximum_padding 2>&1 | filter

stamp "commit patch 0008"
git add -A crates
GIT_AUTHOR_DATE="2026-09-24T08:10:00+0000" GIT_COMMITTER_DATE="2026-09-24T08:10:00+0000" \
  git -c user.name="verity sp1-tcdot lane" -c user.email="lane@verity.local" commit -q -F $W/stream-commit-msg
HEAD=$(git rev-parse HEAD)
echo "fork $HEAD tree $(git rev-parse 'HEAD^{tree}')"
rm -rf $W/patch-0008
git format-patch -q -1 HEAD --start-number 8 -o $W/patch-0008
ls $W/patch-0008

stamp "sp1-gpu-server -> home-stream/.sp1/bin"
mkdir -p $W/home-stream/.sp1/bin
(CARGO_TARGET_DIR=$W/target-server cargo install --locked --force --root $W/home-stream/.sp1 --path sp1-gpu/crates/server 2>&1 \
  | grep -v -E "^\\s+(Compiling|Downloaded|Downloading) " | tail -5)
sha256sum $W/home-stream/.sp1/bin/sp1-gpu-server
echo $HEAD > $W/home-stream/server-fork-head

stamp "host (cuda, stream-operands)"
ln -sfn $F $S/backends/sp1/tcdot/sp1
export VERITY_TCDOT_FORK_HEAD=$HEAD CARGO_TARGET_DIR=$W/target-tcdot
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
