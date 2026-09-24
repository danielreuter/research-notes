#!/usr/bin/env bash
# Fork patch 0011 (prover only): TC_DOT_BF16 trace generation in parallel, byte lookups counted in a parallel
# generate_dependencies (the ShaExtend pattern) instead of the default, which built the whole trace sequentially just
# for its lookups.  $W/p11/bf16.rs on the fork worktree at 0e00bd15 (patch 0010); chip tests (trace values and lookup
# multiplicities: the CPU prove test verifies), commit 0011 (lane identity, fixed dates), format-patch in $W/patch-0011,
# the server under home-par/.sp1/bin, the host at the new pin, info, one full execution, --flip-y, the 52 negatives.
# No AIR change, so no cost regeneration.
set -euo pipefail
W=/workspace/sp1-tcdot
S=$W/src
F=$W/sp1-bf16
MAN=059103cf9bd55ee83cbd4bb14ae6db2f60db2cb4ddf85cdc22b1cecee6e4eeea
export PATH="$HOME/.sp1/bin:$HOME/.cargo/bin:/usr/local/cuda/bin:/usr/local/go/bin:$PATH"
export CUDACXX=/usr/local/cuda/bin/nvcc CUDA_ARCHS=80
stamp() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }
filter() { grep -E "^test |test result|^error|^warning: unused|panicked|FAILED|failures:" || true; }

stamp "fork 0e00bd15 + p11/bf16.rs"
cd $F
test "$(git rev-parse HEAD)" = 0e00bd154761e14f11df511c1d27947f0b170fc0
test -z "$(git status --porcelain --untracked-files=no)"
cp $W/p11/bf16.rs crates/core/machine/src/syscall/precompiles/tc_dot/bf16.rs
git diff --stat

export CARGO_TARGET_DIR=$W/target-bf16
stamp "chip tests (fp8 + bf16)"
cargo test --release -p sp1-core-machine --lib -- tc_dot 2>&1 | tee $W/p11-tests.log | filter
grep -q "test result: ok" $W/p11-tests.log && ! grep -q "FAILED\|panicked" $W/p11-tests.log

stamp "commit patch 0011"
git add -A crates
GIT_AUTHOR_DATE="2026-09-24T09:40:00+0000" GIT_COMMITTER_DATE="2026-09-24T09:40:00+0000" \
  git -c user.name="verity sp1-tcdot lane" -c user.email="lane@verity.local" commit -q -F $W/p11/COMMIT_MSG
HEAD=$(git rev-parse HEAD)
echo "fork $HEAD tree $(git rev-parse 'HEAD^{tree}')"
rm -rf $W/patch-0011
git format-patch -q -1 HEAD --start-number 11 -o $W/patch-0011
ls $W/patch-0011

stamp "sp1-gpu-server -> home-par/.sp1/bin"
mkdir -p $W/home-par/.sp1/bin
(CARGO_TARGET_DIR=$W/target-server cargo install --locked --force --root $W/home-par/.sp1 --path sp1-gpu/crates/server 2>&1 \
  | grep -v -E "^\\s+(Compiling|Downloaded|Downloading) " | tail -3)
test -x $W/home-par/.sp1/bin/sp1-gpu-server
sha256sum $W/home-par/.sp1/bin/sp1-gpu-server
echo $HEAD > $W/home-par/server-fork-head

stamp "host (cuda, stream-operands) at $HEAD"
ln -sfn $F $S/backends/sp1/tcdot/sp1
export VERITY_TCDOT_FORK_HEAD=$HEAD CARGO_TARGET_DIR=$W/target-tcdot
cd $S/backends/sp1/tcdot
cargo build --release -p verity-tcdot-host --features cuda,stream-operands 2>&1 | grep -v "^warning: \\|^note: " | tail -3
H=$CARGO_TARGET_DIR/release/verity-tcdot-host
sha256sum $H

stamp "info"
SP1_PROVER=cpu RUST_LOG=error $H info

stamp "bare-execute 0..4096"
$H bare-execute --instances $W/bi --manifest-sha256 $MAN --lo 0 --hi 4096 --vus-per-read 64 \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps({k: d.get(k) for k in ("verdict","matches_expected","total_cycles","statement_sha256","routing")}))'

stamp "bare-execute --flip-y 7 on 0..64"
$H bare-execute --instances $W/bi --manifest-sha256 $MAN --lo 0 --hi 64 --flip-y 7 \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps({k: d[k] for k in ("verdict","matches_expected","flipped")}))'

stamp "bare-negatives"
$H bare-negatives --instances $W/bi --manifest-sha256 $MAN | tail -1

stamp "done"
