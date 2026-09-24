#!/usr/bin/env bash
# Fork patch 0010 (TC_DOT_BF16 constrains subnormal GroupSum outputs): the edited files in $W/p10 (same paths as in
# the fork) applied on the fork worktree $W/sp1-bf16 at 6096d886 (patch 0009), executor unit tests, cost/complexity
# artifacts regenerated, chip tests (fp8 + bf16, consistency, maximum cycle/padding), then a commit (lane identity,
# fixed dates) and its format-patch in $W/patch-0010.  Then the sp1-gpu-server under home-sub/.sp1/bin (the others
# stay) and the tcdot host (cuda, stream-operands), info, one full guest execution with its routing (the host fails
# unless the chip kernel equals tc::tc_dot on every chip step), one --flip-y and the 52 negatives.
set -euo pipefail
W=/workspace/sp1-tcdot
S=$W/src
F=$W/sp1-bf16
MAN=059103cf9bd55ee83cbd4bb14ae6db2f60db2cb4ddf85cdc22b1cecee6e4eeea
export PATH="$HOME/.sp1/bin:$HOME/.cargo/bin:/usr/local/cuda/bin:/usr/local/go/bin:$PATH"
export CUDACXX=/usr/local/cuda/bin/nvcc CUDA_ARCHS=80
stamp() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }
filter() { grep -E "^test |test result|^error|^warning: unused|panicked|FAILED|failures:" || true; }

stamp "fork 6096d886 + p10 files"
cd $F
test "$(git rev-parse HEAD)" = 6096d886e433ca854504ac0c97abf19ed17a7997
test -z "$(git status --porcelain --untracked-files=no)"
(cd $W/p10 && find crates -name '*.rs' -print0 | xargs -0 -I{} cp {} $F/{})
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
   test_maximum_cycle test_maximum_padding 2>&1 | tee $W/p10-tests.log | filter
grep -q "test result: ok" $W/p10-tests.log && ! grep -q "FAILED\|panicked" $W/p10-tests.log

stamp "commit patch 0010"
git add -A crates
GIT_AUTHOR_DATE="2026-09-24T09:10:00+0000" GIT_COMMITTER_DATE="2026-09-24T09:10:00+0000" \
  git -c user.name="verity sp1-tcdot lane" -c user.email="lane@verity.local" commit -q -F $W/p10/COMMIT_MSG
HEAD=$(git rev-parse HEAD)
echo "fork $HEAD tree $(git rev-parse 'HEAD^{tree}')"
rm -rf $W/patch-0010
git format-patch -q -1 HEAD --start-number 10 -o $W/patch-0010
ls $W/patch-0010

stamp "sp1-gpu-server -> home-sub/.sp1/bin"
mkdir -p $W/home-sub/.sp1/bin
(CARGO_TARGET_DIR=$W/target-server cargo install --locked --force --root $W/home-sub/.sp1 --path sp1-gpu/crates/server 2>&1 \
  | grep -v -E "^\\s+(Compiling|Downloaded|Downloading) " | tail -5)
test -x $W/home-sub/.sp1/bin/sp1-gpu-server
sha256sum $W/home-sub/.sp1/bin/sp1-gpu-server
echo $HEAD > $W/home-sub/server-fork-head

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
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps({k: d.get(k) for k in ("verdict","matches_expected","total_cycles","execute_seconds","statement_sha256","public_values","routing")}))'

stamp "bare-execute --flip-y 7 on 0..64"
$H bare-execute --instances $W/bi --manifest-sha256 $MAN --lo 0 --hi 64 --flip-y 7 \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps({k: d[k] for k in ("verdict","matches_expected","flipped")}))'

stamp "bare-negatives"
$H bare-negatives --instances $W/bi --manifest-sha256 $MAN | tail -1

stamp "done"
