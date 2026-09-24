#!/usr/bin/env bash
# Fork patch 0007 (TC_DOT_BF16 operands as free witness values): the edits in $W/sp1-wit (uncommitted, on d14b4c6)
# applied in the fork worktree $W/sp1-bf16 (same path as before, so every build is incremental), executor unit tests,
# cost/complexity artifacts regenerated, chip tests, then a commit (lane identity, fixed dates) and its format-patch in
# $W/patch-0007.  Then the sp1-gpu-server under home-wit/.sp1/bin (home-bf16 and home-shard stay) and the tcdot host
# (target-tcdot), info, one full guest execution, one --flip-y and the 52 negatives.  Run only while no bench is proving.
set -euo pipefail
W=/workspace/sp1-tcdot
S=$W/src
F=$W/sp1-bf16
MAN=059103cf9bd55ee83cbd4bb14ae6db2f60db2cb4ddf85cdc22b1cecee6e4eeea
export PATH="$HOME/.sp1/bin:$HOME/.cargo/bin:/usr/local/cuda/bin:/usr/local/go/bin:$PATH"
export CUDACXX=/usr/local/cuda/bin/nvcc CUDA_ARCHS=80
stamp() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }
filter() { grep -E "^test |test result|^error|^warning: unused|panicked|FAILED|failures:" || true; }

stamp "fork d14b4c6 + the sp1-wit edits"
git -C $W/sp1-wit diff > $W/wit.diff
cd $F
git checkout -q --detach d14b4c6277536abd4121271eecd33e75bec83ff5
git apply $W/wit.diff
git diff --stat

export CARGO_TARGET_DIR=$W/target-bf16
stamp "executor unit tests (tc_dot)"
cargo test --release -p sp1-core-executor --lib tc_dot 2>&1 | filter

stamp "regenerate cost/complexity artifacts"
(cd crates/core/machine && cargo test --release -p sp1-core-machine --lib -- --ignored --exact \
   riscv::tests::write_core_air_costs riscv::tests::write_core_air_complexity 2>&1 | filter)
python3 - <<'EOF'
import json
for f in ["rv64im_costs.json", "rv64im_complexity.json"]:
    d = json.load(open(f"crates/core/executor/src/artifacts/{f}"))
    print(f, {k: d[k] for k in ["TcDot", "TcDotUser", "TcDotBf16", "TcDotBf16User"]})
EOF
git diff --stat

stamp "chip tests (fp8 + bf16, incl. consistency)"
cargo test --release -p sp1-core-machine --lib -- tc_dot core_air_cost_consistency core_air_complexity_consistency \
   test_maximum_cycle test_maximum_padding 2>&1 | filter

stamp "commit patch 0007"
git add -A crates
GIT_AUTHOR_DATE="2026-09-24T08:00:00+0000" GIT_COMMITTER_DATE="2026-09-24T08:00:00+0000" \
  git -c user.name="verity sp1-tcdot lane" -c user.email="lane@verity.local" commit -q -F $W/wit-commit-msg
HEAD=$(git rev-parse HEAD)
echo "fork $HEAD tree $(git rev-parse 'HEAD^{tree}')"
rm -rf $W/patch-0007
git format-patch -q -1 HEAD --start-number 7 -o $W/patch-0007
ls $W/patch-0007

stamp "sp1-gpu-server -> home-wit/.sp1/bin"
mkdir -p $W/home-wit/.sp1/bin
(CARGO_TARGET_DIR=$W/target-server cargo install --locked --force --root $W/home-wit/.sp1 --path sp1-gpu/crates/server 2>&1 \
  | grep -v -E "^\\s+(Compiling|Downloaded|Downloading) " | tail -5)
sha256sum $W/home-wit/.sp1/bin/sp1-gpu-server
echo $HEAD > $W/home-wit/server-fork-head

stamp "host (cuda)"
ln -sfn $F $S/backends/sp1/tcdot/sp1
export VERITY_TCDOT_FORK_HEAD=$HEAD CARGO_TARGET_DIR=$W/target-tcdot
cd $S/backends/sp1/tcdot
cargo build --release -p verity-tcdot-host --features cuda 2>&1 | grep -v "^warning: \\|^note: " | tail -5
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
