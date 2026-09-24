#!/usr/bin/env bash
# merge-postwave (CPU pod): validate the merged lane/post-wave tree shipped by `research run --source . --cwd source`.
#   setup   apt, rustup stable, sp1up v6.4.0 (succinct guest toolchain), uv
#   py      pytest backends/numerical/tests + tools/research/tests (uv workspace, dev group)
#   cargo   cargo check --release of every Rust crate the merges touched (+ ligero-verify and the gkr crate, per the brief):
#           ligero-verify; verity-gkr (default and --features babybear); verity-gkr-verify; backends/sp1 host/common/check-model
#           (default and relation-bare; the host's build.rs builds the guest ELF with the succinct toolchain); backends/sp1/tcdot
#           on the witness-operands fork (build_fork.sh OPERANDS=witness SKIP_SERVER=1; host --features stream-operands)
#   tests   (not gating) cargo test --release of verity-gkr-verify and veritor-zk-common --features relation-bare
# Prints STAGE_RC[<name>]=<rc> per stage and a SUMMARY; exit 1 if any gating stage failed.
set -uo pipefail
export DEBIAN_FRONTEND=noninteractive
export PATH="$HOME/.sp1/bin:$HOME/.cargo/bin:$HOME/.local/bin:/usr/local/go/bin:$PATH"
SRC="$(pwd)"
W=/workspace/merge-postwave
mkdir -p "$W"
export CARGO_TARGET_DIR=$W/target
declare -A RC
stage() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }
run() {  # run NAME CMD...: log to $W/NAME.log, keep the tail
  local name=$1; shift
  stage "$name: $*"
  "$@" > "$W/$name.log" 2>&1
  local rc=$?
  grep -E "^(error|warning: unused)|FAILED|panicked|passed|failed|test result" "$W/$name.log" | cut -c1-240 | tail -25
  tail -3 "$W/$name.log" | cut -c1-240
  RC[$name]=$rc; echo "STAGE_RC[$name]=$rc"
}

stage "machine"; nproc; free -g | head -2; df -h /workspace | tail -1; echo "source: $SRC"; git -C "$SRC" log -1 --oneline 2>/dev/null || true

stage "setup"
apt-get update -qq && apt-get install -y -qq --no-install-recommends \
  build-essential pkg-config libssl-dev clang libclang-dev cmake protobuf-compiler libprotobuf-dev \
  git curl ca-certificates jq golang-go time rsync >/dev/null
command -v rustup >/dev/null || curl -fsSL https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain stable >/dev/null
rustup toolchain install stable --profile minimal >/dev/null; rustc --version
if ! cargo prove --version 2>/dev/null | grep -q "6.4.0\|f66b4bf"; then
  curl -fsSL https://sp1up.succinct.xyz | bash >/dev/null
  "$HOME/.sp1/bin/sp1up" --version v6.4.0 > $W/sp1up.log 2>&1 || tail -20 $W/sp1up.log
fi
cargo prove --version
command -v uv >/dev/null || curl -fsSL https://astral.sh/uv/install.sh | sh >/dev/null
uv --version

cd "$SRC"
run py-sync uv sync --group dev
run py-numerical uv run --no-sync python -m pytest -q -rfEs -p no:cacheprovider backends/numerical/tests
run py-research  uv run --no-sync python -m pytest -q -rfEs -p no:cacheprovider tools/research/tests

run check-ligero-verify   bash -c "cd backends/ligero-verify && cargo check --release --locked"
run check-gkr             bash -c "cd backends/gkr && cargo check --release --locked"
run check-gkr-babybear    bash -c "cd backends/gkr && cargo check --release --locked --features babybear"
run check-gkr-verify      bash -c "cd backends/gkr/verifier && cargo check --release --locked"
run check-sp1             bash -c "cd backends/sp1 && cargo check --release --locked -p veritor-zk-host -p veritor-zk-common -p veritor-check-model"
run check-sp1-bare        bash -c "cd backends/sp1 && cargo check --release --locked -p veritor-zk-host --features relation-bare"
run tcdot-fork            env OPERANDS=witness SKIP_SERVER=1 SP1_TCDOT_ROOT=$W/sp1-tcdot bash backends/sp1/tcdot/build_fork.sh
run check-tcdot           bash -c "cd backends/sp1/tcdot && VERITY_TCDOT_FORK_HEAD=\$(cat FORK_HEAD_WIT) CARGO_TARGET_DIR=$W/target-tcdot cargo check --release --locked -p verity-tcdot-host --features stream-operands"

run test-gkr-verify       bash -c "cd backends/gkr/verifier && cargo test --release --locked"
run test-sp1-common       bash -c "cd backends/sp1 && cargo test --release --locked -p veritor-zk-common --features relation-bare"

stage "SUMMARY"
fail=0
for k in py-sync py-numerical py-research check-ligero-verify check-gkr check-gkr-babybear check-gkr-verify check-sp1 check-sp1-bare \
         tcdot-fork check-tcdot test-gkr-verify test-sp1-common; do
  echo "$k ${RC[$k]:-missing}"
  case $k in test-*) ;; *) [ "${RC[$k]:-1}" = 0 ] || fail=1 ;; esac
done
echo "GATING_FAIL=$fail"
exit $fail
