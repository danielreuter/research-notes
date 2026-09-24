#!/usr/bin/env bash
# merge-postwave (CPU pod): validate the merged lane/post-wave tree in /workspace/src (`research pods sync`; `research run
# --source .` was killed on the laptop by mem_guardian's disk floor while archiving), run with --cwd /workspace/src.
#   setup   apt, rustup stable, sp1up v6.4.0 (succinct guest toolchain), uv (no-ops after setup.sh)
#   py      pytest backends/numerical/tests + tools/research/tests (uv workspace, dev group)
#   cargo   cargo check --release: ligero-verify; verity-gkr (default and --features babybear); verity-gkr-verify
#           (the SP1 crates run in sp1.sh from a git archive of the same commit)
#   tests   (not gating) cargo test --release of verity-gkr-verify
# Prints STAGE_RC[<name>]=<rc> per stage and a SUMMARY; exit 1 if any gating stage failed.
set -uo pipefail
export DEBIAN_FRONTEND=noninteractive
export PATH="$HOME/.sp1/bin:$HOME/.cargo/bin:$HOME/.local/bin:/usr/local/go/bin:$PATH"
SRC="$(pwd)"
W=/workspace/merge-postwave
L=${LOGS:-$W}   # per-run log dir (runs over two trees overlap); cargo targets stay shared under $W
mkdir -p "$W" "$L"
export CARGO_TARGET_DIR=$W/target
declare -A RC
stage() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }
run() {  # run NAME CMD...: log to $L/NAME.log, keep the tail
  local name=$1; shift
  stage "$name: $*"
  "$@" > "$L/$name.log" 2>&1
  local rc=$?
  grep -E "^(error|warning: unused)|FAILED|panicked|passed|failed|test result" "$L/$name.log" | cut -c1-240 | tail -25
  tail -3 "$L/$name.log" | cut -c1-240
  RC[$name]=$rc; echo "STAGE_RC[$name]=$rc"
}

stage "machine"; nproc; free -g | head -2; df -h /workspace | tail -1; echo "source: $SRC"; cat "$SRC/.research-source.json" 2>/dev/null; echo
for i in $(seq 1 90); do cargo prove --version >/dev/null 2>&1 && command -v uv >/dev/null && break; sleep 10; done  # setup.sh

stage "setup"
# curl / ca-certificates are on the image; listing them made apt upgrade curl from a security-pool URL that 404'd.
apt-get update -qq && apt-get install -y -qq --no-install-recommends \
  build-essential pkg-config libssl-dev clang libclang-dev cmake protobuf-compiler libprotobuf-dev \
  git jq golang-go time rsync >/dev/null; echo "apt rc=$?"
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
run check-sp1             bash -c "cd backends/sp1 && CARGO_TARGET_DIR=$W/target-sp1 cargo check --release --locked -p veritor-zk-host -p veritor-zk-common -p veritor-check-model --features veritor-zk-host/relation-bare"
run test-gkr-verify       bash -c "cd backends/gkr/verifier && cargo test --release --locked"
# needs the repo-root fixtures/ (bench-instances/v1 negatives, typed-obligation-v0), absent from sp1.sh's backends/sp1 archive
run test-sp1-common       bash -c "cd backends/sp1 && CARGO_TARGET_DIR=$W/target-sp1 cargo test --release --locked -p veritor-zk-common --features relation-bare"

stage "SUMMARY"
fail=0
for k in py-sync py-numerical py-research check-ligero-verify check-gkr check-gkr-babybear check-gkr-verify check-sp1 test-gkr-verify test-sp1-common; do
  echo "$k ${RC[$k]:-missing}"
  case $k in test-*) ;; *) [ "${RC[$k]:-1}" = 0 ] || fail=1 ;; esac
done
echo "GATING_FAIL=$fail"
exit $fail
